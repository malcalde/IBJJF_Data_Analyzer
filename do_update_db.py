#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import sys
import re
import csv
import os
import threading
import thread
import traceback
import math
import html2text
import urllib2
import sqlite3
import hashlib
import timeit
import requests
import argparse
import googlemaps
import ConfigParser
import Queue

from bs4 import BeautifulSoup
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

SCORE_LOCATION = {
    'world': 7,
    'worldmaster': 7,
    'european': 4,
    'pan': 4,
    'master': 4,
    'brazilian': 3,
    'asian': 3,
    'american': 2,
    'southamerican': 2, 
    'panpacific': 2,
    'pro': 2,
    'britain': 1,
    'japanese': 1,
    'spain': 1,
}

SCORE_YEAR = {
    0: 3,
    1: 3,
    2: 2,
    3: 1
}

SCORE_MEDAL = {
    "0": 0,
    "1": 9,
    "2": 3,
    "3": 1
}

SCORE_MEDAL_OPENCLASS = {
    "0": 0,
    "1": 4.5,
    "2": 1.5,
    "3": 0.5
}

ENGLISH_MONTHS = {
    'january': '01',  
    'february': '02',
    'march': '03',
    'april': '04',
    'may': '05',
    'june': '06',
    'july': '07',
    'august': '08',
    'september': '09',
    'october': '10',
    'november': '11',
    'december': '12'
}

FORWARD_MONTH = {
    '01': '02',  
    '02': '03',
    '03': '04',
    '04': '05',
    '05': '06',
    '06': '07',
    '07': '08',
    '08': '09',
    '09': '10',
    '10': '11',
    '11': '11',
    '12': '00'
}

BACKWARD_MONTH = {
    '01': '12',  
    '02': '01',
    '03': '02',
    '04': '03',
    '05': '04',
    '06': '05',
    '07': '06',
    '08': '07',
    '09': '08',
    '10': '09',
    '11': '10',
    '12': '11'
}

my_db = None  
my_md5 = None

my_db_inserted = 0
my_db_updated = 0

my_db_cheating = 0

my_competition = None
my_competitor = None
my_helperCompetitorAge = None
my_academy = None
my_result = None
my_team = None

my_map_api_key = None

my_queue = None

def whoAmI():
    stack = traceback.extract_stack()
    filename, codeline, funcName, text = stack[-2]
    return funcName

def getCompetitionLocation(url):
    global my_map_api_key
    
    geocode = None
    
    parser = 'html5lib'

    s = requests.session()
    r = s.get(url)
 
    soup = BeautifulSoup(r.text, parser)
    
    my_address = ""
    address = soup.find_all(['address'])
    for _addr in address:
        if _addr.string is not None:
            my_address = "%s%s"%(my_address, unicode(_addr.string))
        else: 
            my_address = "%s%s"%(my_address, str(_addr))
        my_address = my_address.replace('<address>', '')
        my_address = my_address.replace('</address>', '')
        my_address = my_address.replace('<br/>', '')
        my_address = my_address.replace('\n', ' ')
        my_address = my_address.replace('\t', ' ')
        my_address = my_address.replace('  ', ' ')
        my_address = my_address.strip()
    
    if "" != my_address:
        gmaps = googlemaps.Client(key=my_map_api_key)
        for geomap in gmaps.geocode(my_address):
        	geocode = (geomap['geometry']['location']['lat'], geomap['geometry']['location']['lng'])
		break
    
    return geocode

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

def updateCompetitorScoreForCompetition(competitionID, competitionName=""):
    
    print "[INFO] Updating competitor scores for competition %s %s"%(competitionID, competitionName)
    rounds = {}
   
    filter = " 1 = 0 "	 
    stm = "select competitionID, belt, category, gender,weight, count(1) from result  where competitionID = '%s' group by competitionID, belt, category, gender,weight"
    for row in my_db.execute(stm%(competitionID)):
        if int(row[5]) < 4:
            my_key = "%s-%s-%s-%s-%s"%(row[0], row[1], row[2].replace(' ', '_'), row[3], row[4].replace('-','_'))
            rounds[my_key] = int(row[5])
            filter = filter + " OR rawID like '%s%s'"%(my_key,'%')
    
    filter = "(%s)"%(filter)
    stm = "select count(1) from result R, competition C where R.medal != 0 and C.id = R.competitionID and R.competitionID = '%s' and %s"
    for row in my_db.execute(stm%(competitionID, filter)):
        printProgress(row[0], 'U')
    
    stm = "select R.id, R.competitionID, R.belt, R.category, R.gender, R.weight, R. medal, C.name, C.location, C.year from result R, competition C where R.medal != 0 and C.id = R.competitionID and R.competitionID = '%s'  and %s"
    for row in my_db.execute(stm%(competitionID, filter)):
        printProgress()
        my_key = "%s-%s-%s-%s-%s"%(row[1], row[2], row[3].replace(' ', '_'), row[4], row[5].replace('-','_'))
        if rounds.has_key(my_key):
            score  = getCompetitorScore(row[7], row[8], row[9], row[5].replace('-','_'), row[6], rounds[my_key])
            if 0 == score:
                try:
                    stm = "insert into cheating_result(id, competitionID, belt, category, gender, weight, medal) values('%s','%s','%s', '%s','%s','%s', %s)"
                    my_db.execute(stm%(my_key,row[1], row[2], row[3], row[4], row[5],row[6]))
                except: pass
            my_db.execute("UPDATE result set score=%s and id='%s'"%(score, row[0]))
            
    my_db.commit()

def getCompetitorScore(competitionName, competitionLocation, competitionYear, weight, medal, rounds=1000):
    global my_db_cheating
    score = 0.0

    my_score_year = (date.today().year - int(competitionYear))
    if SCORE_YEAR.has_key(my_score_year): 
        my_score_year = SCORE_YEAR[my_score_year]
    else:
        my_score_year = my_score_year - 2
        my_score_year = 1.0 / (my_score_year * my_score_year)
    
    my_score_location = 0.5
    if SCORE_LOCATION.has_key(competitionLocation.lower()): 
        my_score_location = SCORE_LOCATION[competitionLocation.lower()]
    elif "international" in competitionName.lower():
        my_score_location = 1.0
    
    medal = str(medal)
    my_score_medal = 0
    if SCORE_MEDAL.has_key(medal): 
        my_score_medal = SCORE_MEDAL[medal]
        if int(rounds) - int(medal) < 1:
            my_score_medal = 0
            my_db_cheating = my_db_cheating + 1
            
    if "open" in weight.lower():
        if SCORE_MEDAL_OPENCLASS.has_key(medal): 
             my_score_medal += SCORE_MEDAL_OPENCLASS[medal]
             
    score = my_score_year * my_score_location * my_score_medal
    
    return score

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
        hkey += data[i] + "-" 

    if suffix is not None:
        hkey = suffix + "-" + hkey
                               
    hkey = hkey.replace(' ', '-')
    hkey = hkey[:len(hkey)-1]
    hkey = hkey.upper()
    
    return hkey
    
def getCompetitions(withPastCompetition=True, hardcodedCompetitions=[]):
    competitions = []
    competitionIDs = []
    
    url_results = 'http://ibjjf.org/results'
    parser = 'html5lib'

    s = requests.session()
    r = s.get(url_results)
 
    soup = BeautifulSoup(r.text, parser)
    data = soup.find_all(['h3','a'])

    valid_link0 = re.compile('http:\/\/static.ibjjfdb\.com\/Campeonato\/[0-9]\/*')
    valid_link1 = re.compile('http(s)?:\/\/www.ibjjfdb.com\/ChampionshipResults\/[0-9]*\/PublicResults')

    competitionID = None
    competitionYear = None
    competitionMode = None
    competitionTitle = None
    competitionName  = None
    
    if withPastCompetition:
        for item in data:
            try:
                if 'h3' == item.name:
                    competitionName = item.contents[0]
                    if competitionName is None: continue
                    
                    competitionName = competitionName.lower()
                    
                    if -1 == competitionName.find('no-gi'):
                        competitionMode = 'gi'
                    else:
                        competitionMode = 'nogi'
                        
                    competitionName = competitionName.replace(' no-gi', '')
                    competitionName = competitionName.replace(' gi ', '')
                    competitionName = competitionName.replace('championship', '')
                    competitionName = competitionName.replace('ibjjf', '')
                    competitionName = competitionName.replace(' bjj ', '')
                    competitionName = competitionName.replace(' pro ', '')
                    competitionName = competitionName.replace('jiu-jitsu', '')
                    competitionName = competitionName.replace('master', '')
                    competitionName = competitionName.replace('international', '')
                    competitionName = competitionName.replace('open', '')
                    competitionName = competitionName.replace('kids', '')
                    competitionName = competitionName.replace('national', '')
                    competitionName = competitionName.replace('winter', '')
                    competitionName = competitionName.replace('spring', '')
                    competitionName = competitionName.replace('autumn', '')
                    competitionName = competitionName.replace('summer', '')
                    competitionName = competitionName.replace('fall', '')
                    competitionName = competitionName.replace('nogi', '')
                    competitionName = competitionName.encode('ascii', 'ignore')
                    competitionName = competitionName.replace(' ', '')
                    competitionName = competitionName.strip()
                        
                    if competitionTitle != competitionName:
                        competitionTitle = competitionName
                         
                if 'a' == item.name:
                    href = item.get ('href')
                    if href is None: continue
                    
                    if (valid_link0.match(href)) or(valid_link1.match(href)) :
                        competitionID = href.replace('http://static.ibjjfdb.com/Campeonato/','')
                        competitionID = competitionID.replace('https://www.ibjjfdb.com/ChampionshipResults/','')
                        competitionID = competitionID.replace('/en-US/Results.pdf','')
                        competitionID = competitionID.replace('/PublicResults','')
                        competitionYear = item.contents[0]
                        competition = "%06d-%s-%s-%s"%(int(competitionID), competitionName, competitionMode, competitionYear)
                        print '\n\t* %s'%(competition)
                        if competitionID not in competitionIDs:
                            competitions.append(competition)
                            competitionIDs.append(competitionID)
            except Exception,e: 
                pass
                #print "[ERROR] Exception in getting competitions (%s)"%(e)
    
    urls_upcoming = ['http://ibjjf.org/upcoming-events/']
    
    for url_upcoming in urls_upcoming:
        r = None
        try:
            r = s.get(url_upcoming)
            soup = BeautifulSoup(r.text, parser)
            
            for other_link in soup.find_all('a',{ "class" : "page" }):
                if False == other_link.has_attr('href'): continue
                href = str(other_link['href'])
                if href not in urls_upcoming:
                    urls_upcoming.append(href)     
        except ConnectionError,e: 
            print"[ERROR] Connection error to page %s"%(url_upcoming)
            return competitions
        
        data_links = soup.find_all(['li'])
        
        print '\n# getting upcoming events (%s)'%(url_upcoming)
        for link in data_links:
            competitionID = None
            competitionName = None
            competitionMode = None
            competitionTitle = None
            competitionDay = None
            competitionMonth = None
            competitionURL = None
            
            data_a = link.find_all(['a'])
            for a in data_a:
                if False == a.has_attr('href'): continue
                
                href = str(a['href'])
                if a.has_attr('class') and 'register_now_link'in a['class']:
                    competitionID = href
                    competitionID = competitionID.replace('http://www.ibjjfdb.com/Championships/Championship/Details/','')
                    competitionID = competitionID.replace('https://www.ibjjfdb.com/Championships/Championship/Details/','')
                    competitionID = competitionID[0: competitionID.find('/')]
                    competitionID = "%06d"%(int(competitionID))
                    
                elif href.startswith('http://ibjjf.org/championship/'):
                    competitionURL = href
                    competitionTitle = href.replace('http://ibjjf.org/championship/','')
                    competitionTitle = competitionTitle.replace('/','')
                    
                    if -1 != competitionTitle.find('no-gi'):
                        competitionMode='nogi'
                    else:
                        competitionMode = 'gi'
                    
                    competitionName = competitionTitle 
                    competitionName = competitionName.lower()  
                    competitionName = competitionName.replace(' no-gi ', '')
                    competitionName = competitionName.replace(' gi ', '')
                    competitionName = competitionName.replace('championship', '')
                    competitionName = competitionName.replace('ibjjf', '')
                    competitionName = competitionName.replace(' bjj ', '')
                    competitionName = competitionName.replace(' pro ', '')
                    competitionName = competitionName.replace('jiu-jitsu', '')
                    competitionName = competitionName.replace('master', '')
                    competitionName = competitionName.replace('international', '')
                    competitionName = competitionName.replace('open', '')
                    competitionName = competitionName.replace('kids', '')
                    competitionName = competitionName.replace('national', '')
                    competitionName = competitionName.replace('winter', '')
                    competitionName = competitionName.replace('spring', '')
                    competitionName = competitionName.replace('autumn', '')
                    competitionName = competitionName.replace('summer', '')
                    competitionName = competitionName.replace('fall', '')
                    competitionName = competitionName.replace('nogi', '')
                    competitionName = competitionName.replace('-', '')
                    competitionName = competitionName.replace(' ', '')
                    competitionName = competitionName.encode('ascii', 'ignore')
                    competitionName = competitionName.strip()
                        
                    data_address = link.find('big')
                    if data_address is not None:
                        data_address = data_address.find('address')
                        data_address = data_address.string
                        data_address =  data_address.replace('\n','')
                        competitionYear = data_address[0: data_address.find('-')]
                        competitionMonth = competitionYear[0: competitionYear.find(' ')]
                        competitionMonth = ENGLISH_MONTHS[competitionMonth.lower().strip()]
                        if -1 != competitionYear.find('th'):
                            competitionDay = competitionYear[competitionYear.find(' ')+1: competitionYear.find('th')]
                            competitionDay = competitionDay.split('th')
                            competitionDay = competitionDay[0]
                        elif -1 != competitionYear.find('st'):
                            competitionDay = competitionYear[competitionYear.find(' ')+1: competitionYear.find('st')]
                            competitionDay = competitionDay.split('st')
                            competitionDay = competitionDay[0]
                            #if "31" == competitionDay: competitionMonth = BACKWARD_MONTH[competitionMonth]
                        elif -1 != competitionYear.find('nd'):
                            competitionDay = competitionYear[competitionYear.find(' ')+1: competitionYear.find('nd')]
                            competitionDay = competitionDay.split('nd')
                            competitionDay = competitionDay[0]
                        #else: print competitionDay
                        competitionDay = competitionDay.strip()
                        competitionYear = competitionYear[competitionYear.rfind(',')+1:]
                        competitionYear = competitionYear.replace('*', '')
                        competitionYear = competitionYear.replace(' ', '')
                        competitionYear = competitionYear.strip()
                        
                        competitionDay = "%02d%02d%04d"%(int(competitionDay),int(competitionMonth),int(competitionYear))
                        markCompetitionAs(competitionID, False) 
                        
                        
                    
            if competitionID is not None:
                competition = "%s-%s-%s-%s-%s-%s"%(competitionID, competitionName, competitionMode, competitionYear,  competitionDay, competitionURL)
                print '\n\t* %s'%(competition)
                if competitionID not in competitionIDs:
                                competitions.append(competition)
                                competitionIDs.append(competitionID)
          
    
    for hardcoded_competition in hardcodedCompetitions:
        if hardcoded_competition not in competitions: 
            competitions.append(hardcoded_competition)
            
    #end method     
    return competitions

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
    competitionURL = None
    competitionDay = None
    
    if (len(url_parts) > 4): 
        competitionDay = url_parts[4]
    if (len(url_parts) > 5): 
        competitionURL = url_parts[5]
    competitionName = "%s_%s_%s_%s"%(competitionID, competitionLocation, competitionMode, competitionYear)

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

    insertOrUpdateCompetition(competitionID, competitionName, competitionLocation, competitionYear, competitionMode, competitionDay, competitionURL)     
    
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

                rowID = competitionID + "-" + _rowID + "-" + competitorID
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
    competitionURL = None
    competitionDay = None
    
    if (len(url_parts) > 4): 
        competitionDay = url_parts[4]
    if (len(url_parts) > 5): 
        competitionURL = url_parts[5]
    competitionName = "%s_%s_%s_%s"%(competitionID, competitionLocation, competitionMode, competitionYear)

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

    insertOrUpdateCompetition(competitionID, competitionName, competitionLocation, competitionYear, competitionMode, competitionDay, competitionURL)

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
                rowID = competitionID + "-" + _rowID + "-" + competitorID
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
    competitionMode = url_parts[2]
    competitionYear = url_parts[3].replace('\n','')
    competitionURL = None
    competitionDay = None
    
    if (len(url_parts) > 4): 
        competitionDay = url_parts[4]
    if (len(url_parts) > 5): 
        competitionURL = url_parts[5]
        
    competitionName = "%s_%s_%s_%s"%(competitionID, competitionLocation, competitionMode, competitionYear)


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
                #print "[WARN] Invalid athlete line %s"%(data) 
                continue
            
            competitorID = data[1]
            academyID = data[2]
            position = data[0].strip()

            academyID = insertOrUpdateAcademy(academyID)

            competitorAge = getCompetitorAge(competitorID,category[2],category[1],competitionYear)
            competitorID = insertOrUpdateCompetitor(competitorID, competitorAge)

            rowID = competitionID + "-" + _rowID + "-" + competitorID
            
            score  = getCompetitorScore(competitionName, competitionLocation, competitionYear, category[3], position)
            insertOrUpdateResult(rowID, competitionID, academyID, competitorID, category[0],category[1], category[2], category[3],position, score)
            insertedResult += 1
        elif line.startswith("## "):
            competitionName = line.replace('## ', '').strip()
            insertOrUpdateCompetition(competitionID, competitionName, competitionLocation, competitionYear, competitionMode, competitionDay, competitionURL)   
        else: pass #print "[unknown line]: %s"%(line)   

    if insertedResult > 0:
        ellapsed_time = timeit.default_timer() - start_time
        print "[INFO] Processed %s lines of event '%s' in %.2f sg."%(len(lines),competitionName, ellapsed_time)
        updateCompetitorScoreForCompetition(competitionID, competitionName)
        if (4 == len(url_parts)):
            markCompetitionAs(competitionID)             
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

def insertOrUpdateCompetition(id, name, location, year, mode, day=None, url=None):
    global my_academy, my_competition, my_competitor, my_result, my_competition_geolocation
    
    geo_lat = 0
    geo_lng = 0
    
    if day is None:  day = "0101%s"%(year)

    if url is not None:
        geocode = getCompetitionLocation(url)
        if geocode is not None and "0" != geocode[0] and "0" != geocode[1]:
            geo_lat = geocode[0]
            geo_lng = geocode[1]
            my_competition_geolocation[id] = geocode
    
    if my_competition_geolocation.has_key(id):
        geo_lat = my_competition_geolocation[id][0]
        geo_lng = my_competition_geolocation[id][1]

    mode = mode.upper()
    if False == my_competition.has_key(id):
        stm = "INSERT INTO competition VALUES ('%s','%s','%s',%s, %s, '%s', %s, %s, %s)"%(id, name, location, year, day, mode, geo_lat, geo_lng, '0')
    elif False == my_competition[id]:
        stm = "UPDATE competition SET name='%s', location='%s', year=%s, mode='%s', date=max(date,%s), lat=max(lat,%s), lng=max(lng,%s), is_loaded=0 WHERE id = '%s'"%(name, location, year, mode, day, geo_lat, geo_lng, id)
    else: return

    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()

    my_competition[id] = False

def markCompetitionAs(id, loaded= True):
    global my_academy, my_competition, my_competitor, my_result
    
    status = "1"
    if False == loaded: status = "0"

    stm = "UPDATE competition SET is_loaded = %s WHERE id ='%s'"%(status, id)
    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()
    
    
    if my_competition.has_key(id): 
        my_competition[id] = loaded
        if loaded:
            print "[INFO] Mark %s competition as DONE"%(id)

def insertOrUpdateCompetitor(name, competitorYear=0, academyID=0):
    global my_academy, my_competition, my_competitor, my_result

    name = name.encode('ascii', 'ignore').replace("'", "\"") 

    if True == my_competitor.has_key(name):
        return my_competitor[name]
    
    my_md5.update(name)
    rowID = my_md5.hexdigest()

    if False == my_competitor.has_key(name):
        stm = "INSERT INTO competitor VALUES ('%s','%s', %s, 0)"%(rowID, name, competitorYear)
    else: 
        stm = "UPDATE competitor SET birth_year=%s WHERE birth_year < %s AND id = '%s'"%(year,year,rowID)

    if SHOW_SQL_STATEMENTS: print stm

    my_db.execute(stm)
    my_db.commit()

    my_competitor[name] = rowID

    return rowID

def insertOrUpdateResult(id, competitionID, academyID, competitorID, belt, category, gender, weight, position, score=0):
    global my_academy, my_competition, my_competitor, my_result, my_db_inserted, my_db_updated

    id = id.replace('-#','')
    
    id = id.replace('LIGHT-FEATHER','LIGHT_FEATHER')
    id = id.replace('MEDIUM-HEAVY','MEDIUM_HEAVY')
    id = id.replace('ULTRA-HEAVY','ULTRA_HEAVY')
    id = id.replace('SUPER-HEAVY','SUPER_HEAVY')
    id = id.replace('OPEN CLASS','OPEN_CLASS')
    
    id = id.replace('MASTER-1','MASTER_1')
    id = id.replace('MASTER-2','MASTER_2')
    id = id.replace('MASTER-3','MASTER_3')
    id = id.replace('MASTER-4','MASTER_4')
    id = id.replace('MASTER-5','MASTER_5')
    id = id.replace('MASTER-6','MASTER_6')
    
    id = id.replace('_#','').strip()

    my_md5.update(id)
    rowID = my_md5.hexdigest()
    if True == my_result.has_key(id): rowID = my_result[id]

    belt = belt.replace('#','').strip()
    category = category.replace('#','').strip()
    gender = gender.replace('#','').strip()
    weight = weight.replace('#','').strip()
    

    if False == my_result.has_key(rowID):
        stm = "INSERT INTO result VALUES ('%s','%s','%s','%s','%s','%s','%s','%s',%s,%s,'%s')"%(rowID, competitionID, academyID, competitorID, belt, category, gender, weight, position,score,id)
        my_db_inserted += 1
    elif 0 != position: 
        stm = "UPDATE result SET medal=%s, score=%s WHERE id='%s'"%(position, score, rowID)
        my_db_updated += 1
    else: 
        return

    if SHOW_SQL_STATEMENTS: print stm

    try:
        my_db.execute(stm)
        my_db.commit()
    except sqlite3.IntegrityError, e:
        #print "[WARN] Why %s(%s) or %s(%s) not found in cache? "%(rowID, my_result.has_key(rowID), id, my_result.has_key(id))
        pass

    my_result[id] = rowID
    my_result[rowID] = position

    return rowID

def fixUnknownAcademy():
    stm = """
     select distinct R.competitorID, R. academyID
       from result R, competition C
      where academyID != '%s'
        and  competitorID in (select distinct competitorID from result where academyID = '%s')
      order by C.year
    """%(my_academy['LAST UPDATED'], my_academy['LAST UPDATED'])
   
    for row in my_db.execute(stm):
        stm = "update result set academyID='%s' where academyID='%s' and competitorID='%s'"%(row[1], my_academy['LAST UPDATED'], row[0])
        my_db.execute(stm)
        
    my_db.commit()
        
    
def initialiseDB():
    global my_academy, my_competition, my_competitor, my_result, my_team, my_helperCompetitorAge

    stm = 'CREATE TABLE IF NOT EXISTS academy(id  text PRIMARY KEY ASC, name text)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS competition(id text PRIMARY KEY ASC, name text, location text, year integer, date integer, mode text, lat numeric, lng numeric, is_loaded integer)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS competitor(id  text PRIMARY KEY ASC, name text, birth_year integer, score integer)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS result(id text PRIMARY KEY ASC, competitionID text, academyID text, competitorID text, belt text, category text, gender text, weight text, medal integer, score numeric, rawID text)'
    my_db.execute(stm)
    stm = "CREATE TABLE IF NOT EXISTS team(id text, competitorID text, competitorName text)" 
    my_db.execute(stm)
    stm = "CREATE TABLE IF NOT EXISTS lk_medal as select 0 id,'N/A' name union select 1,'GOLD' union select 2,'SILVER' union select 3,'BRONZE'"
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_competitionID on result(competitionID)'
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_academyID on result(academyID)'
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_competitorID on result(competitorID)' 
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_belt on result(belt)'
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_category on result(category)'
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_weight on result(weight)'
    my_db.execute(stm)
    stm = 'create index if not exists idx_result_rawID on result (rawid)'
    my_db.execute(stm)
    stm = 'CREATE TABLE IF NOT EXISTS cheating_result(id text PRIMARY KEY ASC, competitionID text, belt text, category text, gender text, weight text, medal integer)'
    my_db.execute(stm)
    

    my_db.commit()

    stm = """CREATE VIEW IF NOT EXISTS v_result as 
            select T.name competition, T.year year, T.mode mode, A.name academy, C.name competitor, C.birth_year estimated_birth_year,
                   R.gender, R.belt, R.category, R.weight, m.name medal, R.score score
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

    for row in my_db.execute('select * from competition where is_loaded=0'):
        stm = "delete from result where competitionID = '%s'"%(row[0])
        r = my_db.execute(stm).rowcount
        print "[INFO] Purged %d temporary results for competition %s"%(r,row[1]) 
    my_db.commit()

    for row in my_db.execute('SELECT * FROM academy'):
        my_academy[row[1]] = row[0] 
    my_academy['LAST UPDATED'] = 'UNKNOWN'
    
    for row in my_db.execute('SELECT * FROM competition order by year, date'):
        my_competition[row[0]] = False
        if 1 == row[8]: 
            my_competition[row[0]] = True
        if 0 != row[6] and 0 != row[7]:
            my_competition_geolocation[row[0]] = (row[6], row[7])

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
    
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--closed-events', help='if True also update bd with past events', nargs='?', type=bool, default=False)
    parser.add_argument('--fix-score-for-cheaters', help='if True update score for detect cheater competitors', nargs='?', type=bool, default=False)
    parser.add_argument('--competition', help='competition ID', action='append')

    args = parser.parse_args()
    
    start_time = timeit.default_timer()
 
    my_competition = {}
    my_competition_geolocation = {}  
    my_competitor = {}
    my_academy = {}
    my_result = {}
    my_team = {}
    my_helperCompetitorAge = {} 

    my_db = sqlite3.connect('data/my-ibjjf.db')
    my_md5 = hashlib.md5()

    initialiseDB()
     
    hardcoded_competitions = []
    if (args.competition):
        for competitionID in args.competition:
           for row in my_db.execute("select * from competition where id='%s'"%(competitionID)):
               competition = "%s-%s-%s-%s"%(row[0], row[2], row[5], row[3])
               hardcoded_competitions.append(competition)
    
    config = ConfigParser.RawConfigParser()
    config.read('my_ibjjf_data_analyzer.cfg')
    my_map_api_key = config.get('GOOGLE','MAPS_APP_KEY')
    
   	
    for competition in getCompetitions((False != args.closed_events), hardcoded_competitions):
        extractFromResults(competition)
    
    if False != args.fix_score_for_cheaters:	
    	for row in my_db.execute('select distinct id, name from competition where id not in (select distinct competitionID from cheating_result) order by id'):
        	updateCompetitorScoreForCompetition(row[0], row[1])
    
    fixUnknownAcademy()  
    
    if 0 < (my_db_inserted + my_db_updated) or False:
        for row in my_db.execute('select competitorID, sum(score) from result group by competitorID'):
            my_db.execute("update competitor set score=%s where id='%s'"%(row[1], row[0]))
             
        my_db.commit()
                              
    my_db.close()                      
    

    ellapsed_time = timeit.default_timer() - start_time
    print "[INFO] Source data (inserted: %d, updated: %d, cheating: %d)processed in %.2f sg."%(my_db_inserted, my_db_updated, my_db_cheating, ellapsed_time)  
