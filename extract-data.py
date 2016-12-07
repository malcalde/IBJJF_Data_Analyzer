#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import sys
import re
import csv
import os
import traceback
import math
import html2text
import urllib2
import sqlite3
import hashlib
import timeit

from datetime import date

SHOW_SQL_STATEMENTS = False

CLASS_AGE_RANGE = {
    'MALE': {
        'MIGHTY-MITE 1': -4,
        'MIGHTY-MITE 2': -5,
        'MIGHTY-MITE 3': -6,
        'PEE-WEE 1': -7,
        'PEE-WEE 2': -8,
        'PEE-WEE 3': -9,
        'JUNIOR 1': -10,
        'JUNIOR 2': -11,
        'JUNIOR 3': -12,
        'TEEN 1': -13,
        'TEEN 2': -14,
        'TEEN 3': -15,
        'JUVENILE 1': -16,
        'JUVENILE 2': -17,
        'JUVENILE': -17,
        'ADULT': -18-6,
        'MASTER 1': -30-3,
        'MASTER 2': -36-3,
        'MASTER 3': -41-3,
        'MASTER 4': -46-3,
        'MASTER 5': -51-3,
        'MASTER 6': -56-1
    },
    'FEMALE': {
        'MIGHTY-MITE 1': -4,
        'MIGHTY-MITE 2': -5,
        'MIGHTY-MITE 3': -6,
        'PEE-WEE 1': -7,
        'PEE-WEE 2': -8,
        'PEE-WEE 3': -9,
        'JUNIOR 1': -10,
        'JUNIOR 2': -11,
        'JUNIOR 3': -12,
        'TEEN 1': -13,
        'TEEN 2': -14,
        'TEEN 3': -15,
        'JUVENILE 1': -16,
        'JUVENILE 2': -17,
        'JUVENILE': -17,
        'ADULT': -18,
        'MASTER 1': -30,
        'MASTER 2': -36,
        'MASTER 3': -41,
        'MASTER 4': -46,
        'MASTER 5': -51,
        'MASTER 6': -56
    }
}

my_db = None  
my_md5 = None

my_competition = None
my_competitor = None
my_helperCompetitorAge = None
my_academy = None
my_result = None
my_team = None

def whoAmI():
    stack = traceback.extract_stack()
    filename, codeline, funcName, text = stack[-2]
    return funcName

def getCompetitorAge(competitorID, competitorGender, competitorCategory, competitionYear):
    global my_helperCompetitorAge

    if len(competitorID) != len('ea644a4d1f1d0ba8df6534b7506222b5'):
        my_md5.update(competitorID.encode('ascii', 'ignore').replace("'", "\""))
        competitorID = my_md5.hexdigest()

    if False == my_helperCompetitorAge.has_key(competitorID): 
        age = int(competitionYear) + CLASS_AGE_RANGE[competitorGender][competitorCategory]
        my_helperCompetitorAge[competitorID] = {'year': competitionYear, 'category': competitorCategory, 'age': age}
    elif my_helperCompetitorAge[competitorID]['year'] < competitionYear:
        my_helperCompetitorAge[competitorID]['year'] = competitionYear
        if my_helperCompetitorAge[competitorID]['category'] != competitorCategory:
            age = int(competitionYear) + CLASS_AGE_RANGE[competitorGender][competitorCategory]
            my_helperCompetitorAge[competitorID]['age'] = age
            my_helperCompetitorAge[competitorID]['category'] = competitorCategory

    return my_helperCompetitorAge[competitorID]['age']

def printProgress(maxValue=-1, tag='R'):
    if -1 != maxValue: 
        printProgress.maxValue = maxValue
        printProgress.value = 0
        printProgress.progressPercent=-1
        printProgress.progressChar = tag 
    else:
        printProgress.value+=1
        progressPercent = int(100 * (1.0 * printProgress.value/printProgress.maxValue))
        if printProgress.progressPercent != progressPercent: 
            print "\t\t[" + (progressPercent * printProgress.progressChar) + ((100 - progressPercent) * " ") + "]"
            printProgress.progressPercent = progressPercent
        

def processData(data, suffix=None):
    global total, hkey

    assert len(data) == 4, "Error en formato de line X/Y/W/Z"
    
    hkey = ''

    for i in range(0,len(data)):
        data[i] = data[i].replace('#### ','').strip()
        hkey += data[i] + "_" 

    if suffix is not None:
        hkey = suffix + "_" + hkey
                               
    hkey = hkey.replace(' ', '_')
    hkey = hkey[:len(hkey)-1]
    hkey = hkey.upper()
    
    return hkey
    

def extractByAcademy(url):
    data = None
    category = None
    academy = None
    academyID = None
    competitorID = None

    url_parts = url.split('-')

    competitionID = url_parts[0]
    competitionLocation = url_parts[1]
    competitionMode = url_parts[2]
    competitionYear = url_parts[3].replace('\n','')
    competitionName = url.replace('\n','')

    try:
        url = "https://www.ibjjfdb.com/ChampionshipResults/%s/PublicAcademyRegistration?lang=en-US"%(competitionID)
        print "[INFO] Processing event '%s' (by academy dimension) '%s'"%(competitionName, url)

        h2t = html2text.HTML2Text()
        h2t.ignore_links = True
        h2t.bypass_tables = False
        urlcon = urllib2.urlopen(url)

        http_message = urlcon.info()
        minetype = http_message.type # 'text/plain'
        
        if minetype != "text/html":
            print "Invalid minetype for competition %s (%s)"%(competitionID, minetype)
            return

        html = urlcon.read()
        lines = h2t.handle(html.decode('utf8'))  
        lines = lines.split("\n")
    except Exception, e: 
        print "[ERROR] Processing event(by academy dimension) '%s - %s'"%(url, e)
        return 

    insertOrUpdateCompetition(competitionID, competitionName, competitionLocation, competitionYear, competitionMode)     
    
    printProgress(maxValue=len(lines), tag='A')
    for line in lines:
        line = line.replace('(','')
        line = line.replace(')','')
        line = line.replace('###','')
        line = line.upper()
        line = line.strip()

        printProgress()

        if line == '': continue
        if line.startswith('## '): continue
        if line == '---': continue

        if line.count('/') == 3:
            category = line.upper().split('/')
            _rowID = processData(category)
        elif line.startswith('**TOTAL:**'):
            try:
                line = line.replace('**Total:**','')
            except ValueError:
                print "Value Error at line '%s' in %s\n"%(line,whoAmI())
            academy = None
            category = None
        else:
            if academy is not None and category is not None:
                academyID = insertOrUpdateAcademy(academy)
            
                competitorAge = getCompetitorAge(line.strip(),category[2],category[1],competitionYear)
                competitorID = insertOrUpdateCompetitor(line, competitorAge)

                rowID = competitionID + "_" + _rowID + "_" + competitorID
                insertOrUpdateResult(rowID, competitionID, academyID, competitorID, category[0],category[1], category[2], category[3],0)
            if academy is None:    
                academy = line    
        
    del lines[:]

def extractByDivision(url):
    data = None
    category = None
    academyID = None
    competitorID = None 

    url_parts = url.split('-')

    competitionID = url_parts[0]
    competitionLocation = url_parts[1]
    competitionMode = url_parts[2]
    competitionYear = url_parts[3].replace('\n','')
    competitionName = url.replace('\n','')

    try:
        url = "https://www.ibjjfdb.com/ChampionshipResults/%s/PublicRegistrations?lang=en-US"%(competitionID)
        print "[INFO] Processing event '%s' (by division dimension) '%s'"%(competitionName, url)

        h2t = html2text.HTML2Text()
        h2t.ignore_links = True
        h2t.bypass_tables = False
        urlcon = urllib2.urlopen(url)

        http_message = urlcon.info()
        minetype = http_message.type # 'text/plain'
        
        if minetype != "text/html":
            print "Invalid minetype for competition %s (%s)"%(competitionID, minetype)
            return

        html = urlcon.read()
        lines = h2t.handle(html.decode('utf8'))  
        lines = lines.split("\n")
    except Exception, e: 
        print "[ERROR] Processing event(by division dimension) '%s - %s'"%(url, e)
        return

    insertOrUpdateCompetition(competitionID, competitionName, competitionLocation, competitionYear, competitionMode)

    printProgress(maxValue=len(lines), tag='D')
    for line in lines:
        line = line.replace('(','')
        line = line.replace(')','')
        line = line.replace('###','')
        line = line.upper()
        line = line.strip()

        printProgress()

        if line == '---|---': continue
        
        if line.count('/') == 3:
            category = line.upper().split('/')
            _rowID = processData(category) 
        elif line.count('|') == 1:
            line_data  = line.split("|")
            academyID = None 
            competitorID = None
            if line_data[0].strip() != '' or line_data[0].strip() != '---':
                academyID = insertOrUpdateAcademy(line_data[0].strip())
            if line_data[1].strip() != '': 
                line_data[1] = line_data[1].strip()

                competitorAge = getCompetitorAge(line.strip(),category[2],category[1],competitionYear)
                competitorID = insertOrUpdateCompetitor(line_data[1].strip(), competitorAge) 

            if category is not None and academyID is not None and competitorID is not None:
                rowID = competitionID + "_" + _rowID + "_" + competitorID
                insertOrUpdateResult(rowID, competitionID, academyID, competitorID, category[0],category[1], category[2], category[3],0)    
        elif line.startswith('**Total:**'):
            try:
                category = None
                line = line.replace('**Total:**','')
                if my_category.strip() == '': continue

                #print "Found total competitors '%s': %s"%(my_category, line)
            except Exception,e:
                print "Value Error (%s) at line '%s' in %s\n"%(e, line,whoAmI())
        
    del lines[:]

def extractFromResults(url):
    start_time = timeit.default_timer()

    data = None
    category = None
    club = None

    url_parts = url.split('-')

    competitionID = url_parts[0]
    competitionLocation = url_parts[1]
    competitionMode = url_parts[2].upper()
    competitionYear = url_parts[3].replace('\n','')
    competitionName = url.replace('\n','') 

    if True == my_competition.has_key(competitionID) and my_competition[competitionID]:
        print "Competition (%s) %s-%s already loaded."%(competitionID, competitionLocation, competitionYear) 
        return

    extractByAcademy(url)
    extractByDivision(url)  

    try:
        url = "https://www.ibjjfdb.com/ChampionshipResults/%s/PublicResults?lang=en-US"%(competitionID)
        print "[INFO] Processing event '%s' (by result dimension) '%s'"%(competitionName, url)

        h2t = html2text.HTML2Text()
        h2t.ignore_links = True
        h2t.bypass_tables = False
        urlcon = urllib2.urlopen(url)

        http_message = urlcon.info()
        minetype = http_message.type # 'text/plain'
        
        if minetype != "text/html":
            print "Invalid minetype for competition %s (%s)"%(competitionID, minetype)
            return

        html = urlcon.read()
        lines = h2t.handle(html.decode('utf8'))  
        lines = lines.split("\n")
    except Exception, e: 
        print "[ERROR] Processing event(by results dimension) '%s - %s'"%(url, e)
        return

    insertedResult = 0    
    rowID = ''

    printProgress(maxValue=len(lines), tag='R')
    for line in lines:
        printProgress()

        line = line.strip()

        if line.count('/') == 3:
            category = line.upper().split('/')
            _rowID = processData(category) 
        elif line.count(' \- '): 
            data = line.strip().upper().split(' \- ')

            if (len(data)  != 3):
                print "[WARN] Invalid athlete line %s"%(data) 
                continue
            
            competitorID = data[1]
            academyID = data[2]
            position = data[0].strip()

            academyID = insertOrUpdateAcademy(academyID)

            competitorAge = getCompetitorAge(competitorID,category[2],category[1],competitionYear)
            competitorID = insertOrUpdateCompetitor(competitorID, competitorAge)

            rowID = competitionID + "_" + _rowID + "_" + competitorID

            insertOrUpdateResult(rowID, competitionID, academyID, competitorID, category[0],category[1], category[2], category[3],position)
            insertedResult += 1
        elif line.startswith("## "):
            competitionName = line.replace('## ', '').strip()
            insertOrUpdateCompetition(competitionID, competitionName, competitionLocation, competitionYear, competitionMode)   
        else: pass #print "[unknown line]: %s"%(line)   

    if insertedResult > 0:
        ellapsed_time = timeit.default_timer() - start_time
        print "[INFO] Processed %s lines of event '%s' in %.2f sg."%(len(lines),competitionName, ellapsed_time)    
        markCompetitionAsLoaded(competitionID)             
    del lines[:]


def insertOrUpdateAcademy(academy):
    global my_academy, my_competition, my_competitor, my_result

    academy = academy.encode('ascii', 'ignore').replace("'", "\"")

    if True == my_academy.has_key(academy):
        return my_academy[academy]

    my_md5.update(academy)
    rowID = my_md5.hexdigest()
    stm = "INSERT INTO academy VALUES ('%s','%s')"%(rowID, academy)
    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()

    my_academy[academy] = rowID

    return rowID

def insertOrUpdateCompetition(id, name, location, year, mode):
    global my_academy, my_competition, my_competitor, my_result

    if False == my_competition.has_key(id):
        stm = "INSERT INTO competition VALUES ('%s','%s','%s',%s, '%s', %s)"%(id, name,location, year, mode, '0')
    elif False == my_competition[id]:
        stm = "UPDATE competition SET name='%s', location='%s', year=%s, mode='%s', is_loaded=0 WHERE id = '%s'"%(name, location, year, mode,id)
    else: return

    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()

    my_competition[id] = False

def markCompetitionAsLoaded(id):
    global my_academy, my_competition, my_competitor, my_result

    stm = "UPDATE competition SET is_loaded = 1 WHERE id ='%s'"%(id)
    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()

    my_competition[id] = True

def insertOrUpdateCompetitor(name, competitorYear=0):
    global my_academy, my_competition, my_competitor, my_result

    name = name.encode('ascii', 'ignore').replace("'", "\"") 

    if True == my_competitor.has_key(name):
        return my_competitor[name]
    
    my_md5.update(name)
    rowID = my_md5.hexdigest()

    if False == my_competitor.has_key(name):
        stm = "INSERT INTO competitor VALUES ('%s','%s', %s)"%(rowID, name, competitorYear)
    else: 
        stm = "UPDATE competitor SET birth_year=%s WHERE birth_year < %s AND id = '%s'"%(year,year,rowID)

    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()

    my_competitor[name] = rowID

    return rowID

def insertOrUpdateResult(id, competitionID, academyID, competitorID, belt, category, gender, weight, position):
    global my_academy, my_competition, my_competitor, my_result

    id = id.replace('_#','').strip()

    my_md5.update(id)
    rowID = my_md5.hexdigest()
    if True == my_result.has_key(id): rowID = my_result[id]

    belt = belt.replace('#','').strip()
    category = category.replace('#','').strip()
    gender = gender.replace('#','').strip()
    weight = weight.replace('#','').strip()

    if False == my_result.has_key(rowID):
        stm = "INSERT INTO result VALUES ('%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s')"%(rowID, competitionID, academyID, competitorID, belt, category, gender, weight, position,id)
    elif 0 != position: 
        stm = "UPDATE result SET medal=%s WHERE id='%s'"%(position, rowID)
    else: 
        return

    if SHOW_SQL_STATEMENTS: print stm

    try:
        my_db.execute(stm)
        my_db.commit()
    except sqlite3.IntegrityError, e:
        print "[WARN] Why %s(%s) or %s(%s) not found in cache? "%(rowID, my_result.has_key(rowID), id, my_result.has_key(id))

    my_result[id] = rowID
    my_result[rowID] = position

    return rowID

def createTeam():
    global my_team
    team = None
    
    srcs = open("my-team-data.txt", "r")
    for row in srcs:
        row = row.replace('\n','')
        match = re.match(r"\[.*\]", row)
        if match is not None:
            team = row.upper()
            team = team.replace('[','')
            team = team.replace(']','')
        else:
            for cow in my_db.execute("SELECT * FROM competitor where name = '%s'"%(row)):
                if False == my_team.has_key(cow[0]):
                    print "[INFO] new team '%s' member: %s"%(team,cow[1])
                    stm = "INSERT INTO team VALUES ('%s', '%s')"%(team,cow[0])
                    my_db.execute(stm)
            my_db.commit()

def initialiseDB():
    global my_academy, my_competition, my_competitor, my_result, my_team, my_helperCompetitorAge

    stm = 'CREATE TABLE IF NOT EXISTS academy(id  text PRIMARY KEY ASC, name text)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS competition(id text PRIMARY KEY ASC, name text, location text, year integer, mode text, is_loaded integer)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS competitor(id  text PRIMARY KEY ASC, name text, birth_year integer)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS result(id text PRIMARY KEY ASC, competitionID text, academyID text, competitorID text, belt text, category text, gender text, weight text, medal integer, rawID text)'
    my_db.execute(stm)
    stm = "CREATE TABLE IF NOT EXISTS team(id text, competitorID text)" 
    my_db.execute(stm)
    stm = "CREATE TABLE IF NOT EXISTS lk_medal as select 0 id,'N/A' name union select 1,'GOLD' union select 2,'SILVER' union select 3,'BRONZE'"
    my_db.execute(stm)
    my_db.commit()

    stm = """CREATE VIEW IF NOT EXISTS v_result as 
            select T.name competition, T.year year, T.mode mode, A.name academy, C.name competitor, C.birth_year estimated_birth_year,
                   R.gender, R.belt, R.category, R.weight, m.name medal 
             from result R, competition T, academy A, competitor C, lk_medal M
            where R.medal=M.id
              and C.id = R.competitorID
	          and A.id = R.academyID
              and T.id=R.competitionID
    """
    my_db.execute(stm)
    my_db.commit()

    stm = """CREATE VIEW IF NOT EXISTS v_team_competition as 
             select printf("%s_%s_%s_%s_%s_%",R.competitionID, R.belt,R.category, R.gender,R.weight) pattern, 
                    R.competitionID, R.competitorID
                from result R, team T
               where R.competitorID = T.competitorID
    """
    #my_db.execute(stm)
    #my_db.commit()

    for row in my_db.execute('SELECT * FROM academy'):
        my_academy[row[1]] = row[0] 
    
    for row in my_db.execute('SELECT * FROM competition'):
        my_competition[row[0]] = False
        if 1 == row[5]: my_competition[row[0]] = True

    for row in my_db.execute('SELECT * FROM competitor'):
        my_competitor[row[1]] = row[0]
    
    for row in my_db.execute('SELECT * FROM team'):
            my_team[row[1]] = row[0]

    for row in my_db.execute('select R.*, C.year from result R, competition C where C.id=R.competitionID'):
        my_result[row[9]] = row[8]
        my_result[row[0]] = row[8]

        #competitorAge = getCompetitorAge(row[3],row[6], row[5],row[10])
        #insertOrUpdateCompetitor(row[3], competitorAge)

if __name__ == '__main__':
    start_time = timeit.default_timer()

    my_competition = {}  
    my_competitor = {}
    my_academy = {}
    my_result = {}
    my_team = {}
    my_helperCompetitorAge = {}

    my_db = sqlite3.connect('data/my-ibjjf.db')
    my_md5 = hashlib.md5()

    initialiseDB()

    if True: 
        srcs = open("my-competition-data.txt", "r")
        for row in srcs:
            if (row.startswith('#')):
                print " "
                print "#####################################################"
                print row[:-1]
                print "#####################################################"
            elif 3 == row.count('-'): 
                extractFromResults(row)
   	
	createTeam()                                 
        my_db.close()                      
    

    ellapsed_time = timeit.default_timer() - start_time
    print "[INFO] Source data processed %.2f sg."%(ellapsed_time)  
