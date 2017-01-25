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

from search_youtube import *

from datetime import date

#from update_competitions import competitionYear

assert(len(sys.argv) > 1)
MY_TEAM = sys.argv[1]

DEBUG_SQL = False
DEBUG_COMPETITORID = 'NOBODY'

stm0 = "CREATE TABLE IF NOT EXISTS lk_belt as select distinct 0 id,  belt from result"
stm1 = "update competition set is_loaded=0 where id='%s'"

stmA = """ 
  select  distinct C.id competitionID, C.name competitionName, O.id competitorID, O.name competidor_name, R.rawID, R.belt, T.name
  from result R, competition C, academy T, competitor O, lk_belt L
  where 1=1
     and L.belt = R.belt
     and R.academyID = T.id
     and O.id = R.competitorID
     and R.competitionID=C.id
     and T.id = '%s'
     and C.is_loaded=0
     order by L.id desc, O. birth_year, O.name, C.year
"""

stmB = """
select distinct R.competitorID, C.name 
  from result R, competition T, academy A, competitor C, lk_medal M
where R.medal=M.id
  and C.id = R.competitorID
  and A.id = R.academyID
  and T.id=R.competitionID
  and R.competitorID != '%s'
  and R.rawID like ('%s')
  """

stmC = """
select C.name competitor, replace(A.name,'LAST UPDATED','???') academy, C.birth_year estimated_birth_year,  sum(1) competitions, sum(('N/A' != m.name)) medals,
             sum(('GOLD' == m.name)) medal_gold, sum(('SILVER' == m.name)) medal_silver, sum(('BRONZE' == m.name)) medal_bronze,
             sum(R.score) score,
             C.id competitorID,  sum(('N/A' != m.name) and (r.weight == 'OPEN CLASS')) medals_openclass, C.id competitorID
from result R, competition T, academy A, competitor C, lk_medal M
where R.medal=M.id
  and C.id = R.competitorID
  and A.id = R.academyID
  and T.is_loaded != 10
  and T.id=R.competitionID
  and C.id in %s
 group by  competitor
 order by score DESC, medal_gold DESC, medal_silver DESC, medal_bronze DESC, medals DESC, competitions DESC
"""

stmD = """
select T.name competition, T.year year, T.mode mode, A.name academy, C.name competitor, C.birth_year estimated_birth_year,
	   R.gender, R.belt, R.category, R.weight, m.name medal 
 from result R, competition T, academy A, competitor C, lk_medal M
where R.medal=M.id
  and C.id = R.competitorID
  and A.id = R.academyID
  and T.is_loaded = 1
  and T.id=R.competitionID 
  and R.competitorID = '%s'
 order by year desc, T.id desc
"""

stmE = "INSERT INTO result VALUES ('%s','%s','%s','%s','%s','%s','%s','%s',%s,'%s')"

stmF = "select * from result where competitionID ='%s' and competitorID = '%s'"

stmG = """
select C.name competitor, replace(A.name,'LAST UPDATED','???') academy, C.birth_year estimated_birth_year,  sum(1) competitions, sum(('N/A' != m.name)) medals,
             sum(('GOLD' == m.name)) medal_gold, sum(('SILVER' == m.name)) medal_silver, sum(('BRONZE' == m.name)) medal_bronze,
             sum(R.score) score,
             C.id competitorID, sum(('N/A' != m.name) and (r.weight == 'OPEN CLASS')) medals_openclass, C.id competitorID
from result R, competition T, academy A, competitor C, lk_medal M
where R.medal=M.id
  and C.id = R.competitorID
  and A.id = R.academyID
  and T.is_loaded != 10
  and T.id=R.competitionID
  and C.id = '%s'
 group by  competitor
 order by medal_gold DESC, medal_silver DESC, medal_bronze DESC, medals DESC, competitions DESC
"""

stmH = """
    select name from academy where id = '%s'
"""

stmI = """
    update competitor set score=%s where id='%s'
"""

stmJ = "select  belt,category,weight from result where competitionID = '%s' and competitorID = '%s'"

my_db = sqlite3.connect('data/my-ibjjf.db')
assert (my_db is not None),"Fail opening database"

my_db.execute(stm0)

if(len(sys.argv) > 2):
    for competitionID in sys.argv[2:]:
        my_db.execute(stm1%(competitionID)) 
             
my_db.commit()

srcs = open("my-fake_results.txt", "r")
for row in srcs:
    row = row.strip()
    if row == '': continue
    
    if (not row.startswith('#')):
        index = 0
        row_parts = row.split('-')
        
        competitionID = row_parts[index]
        index +=1
        
        academyID = row_parts[index]
        index +=1
        
        belt = row_parts[index]
        index +=1
        
        category = row_parts[index]
        index +=1
        if category == 'MASTER' or category == 'JUVENILE' or category == 'PEE-WEE':
            category = category + '_' + row_parts[index]
            index +=1
        
        gender = row_parts[index]
        index +=1
        
        weight = row_parts[index]
        index +=1
        
        competitorID = row_parts[index]
        index +=1
        
        if len(row_parts) != index:
            weight = weight + '_' + competitorID
            competitorID = row_parts[index]
        
        row = row.replace("-" + academyID, "")
        row = row.replace('-#','')
        row = row.replace('LIGHT-FEATHER','LIGHT_FEATHER')
        row = row.replace('MEDIUM-HEAVY','MEDIUM_HEAVY')
        row = row.replace('ULTRA-HEAVY','ULTRA_HEAVY')
        row = row.replace('SUPER-HEAVY','SUPER_HEAVY')
        row = row.replace('OPEN CLASS','OPEN_CLASS')
        row = row.replace('MASTER-1','MASTER_1')
        row = row.replace('MASTER-2','MASTER_2')
        row = row.replace('MASTER-3','MASTER_3')
        row = row.replace('MASTER-4','MASTER_4')
        row = row.replace('MASTER-5','MASTER_5')
        row = row.replace('MASTER-6','MASTER_6')  
        row = row.replace('_#','').strip()
    
        rowID  ="FAKE_" + row
        try:
            result_exists = False
            for row_f in my_db.execute(stmF%(competitionID, competitorID)):
                result_exists = True
                assert False
                
            if False ==  result_exists:  
                my_db.execute(stmE%((rowID, competitionID, academyID, competitorID, belt, category, gender, weight, 0,row)))
                #print "[INFO] Inserting fake result (%s,%s,%s,%s,%s,%s)"%(competitionID,belt,category,gender,weight,competitorID)
                if DEBUG_SQL or competitorID == DEBUG_COMPETITORID:
                    print 100*'*'
                    print stmE%((rowID, competitionID, academyID, competitorID, belt, category, gender, weight, 0,row))
                    print 100*'*' 
                my_db.execute(stmE%((rowID, competitionID, academyID, competitorID, belt, category, gender, weight, 0,row)))
        except: pass

my_db.commit()

competitionID = None
competitionName = None
competitorID = None
competitionName = None
resultFilter = None

MY_TEAM_NAME = None
for row_h in my_db.execute(stmH%(MY_TEAM)):
    MY_TEAM_NAME = row_h[0]
    
if MY_TEAM_NAME is None:
    print "# Not foudn record for academy: '%s'.\n' "%(MY_TEAM)
    sys.exit(1)

print "# Informe competiciones - Team: '%s'.\n' "%(MY_TEAM_NAME)

if DEBUG_SQL or competitorID == DEBUG_COMPETITORID:
    print 100*'='
    print stmA%(MY_TEAM)
    print 100*'='

my_competitors = []

for row in my_db.execute(stmA%(MY_TEAM)):
    if "%s_%s"%(row[0], row[2]) in my_competitors: 
        continue
    my_competitors.append("%s_%s"%(row[0], row[2])) 
    
    if competitorID != row[2] or competitorID is None: 
        my_record = ""
        if competitorID is not None: print "\n%s"%(80*'-')
        #My record 
        for row_t in my_db.execute(stmG%(row[2])):
            if row_t[3] > 1:
                my_medals = ""
                if ((row_t[5]+ row_t[6] + row_t[7])):
                    my_medals = "(%s,%s,%s)"%(row_t[5], row_t[6], row_t[7])
                my_record = "* __Record__: _%s medallas en %s IBJJF competition_ record %s - __exito__: %.2f - __score__: %.2f."%(row_t[4], (row_t[3]-1), my_medals, 100.0 * (1.0 * (row_t[4]-row_t[10])/(row_t[3]-1)), row_t[8])
                my_db.execute(stmI%(row_t[8], row_t[11]))
        
        print "## Competidor: %s\n%s"%(row[3].title(), my_record)
        competitionID = None
    else: 
        print "[ERROR] Failed check team condition (%s != %s or %s is None)"%(competitorID,row[2],competitorID)
        continue
         
    if competitionID != row[0]:
        my_class = ""
        for row_jjj in my_db.execute(stmJ%(row[0],row[2])):
                my_class = " [%s/%s/%s]"%(row_jjj[0], row_jjj[1], row_jjj[2])
        print "\n### Competicion: %s%s.\n"%(row[1], my_class) 

    competitionID = row[0]
    competitionName = row[1]
    competitorID = row[2]
    competitionName = row[3]
    resultFilter = row[4].replace(row[2],'%')
    
    if DEBUG_SQL or competitorID == DEBUG_COMPETITORID:
        print 100*'='
        print stmB%(competitorID, resultFilter)
        print 100*'='

    oponents = {}
    
    filterOponents = "('IMPOSSIBLEISNOTHING'"
    for row_o in my_db.execute(stmB%(competitorID, resultFilter)): 
        filterOponents += ",'%s'"%(row_o[0])
    filterOponents += ")"
 
    if DEBUG_SQL or competitorID == DEBUG_COMPETITORID:
        print 100*'='
        print stmC%(filterOponents)
        print 100*'='
        
    for row_t in my_db.execute(stmC%(filterOponents)):
        if row_t[3] > 1:
            oponents[row_t[9]] = row_t[0].title()
            print "* Oponente: (%s) %s - %s medallas en %s competiciones (%s,%s,%s) - %.2f %% exito - score: %.2f."%(row_t[1].title(), row_t[0].title(), 
                     row_t[4], (row_t[3]-1), row_t[5], row_t[6], row_t[7], 100.0 * (1.0 * (row_t[4]-row_t[10])/(row_t[3]-1)), row_t[8])
            
            my_db.execute(stmI%(row_t[8], row_t[11]))
            
            videos = doYoutubeSearch("BJJ + \"%s\""%(row_t[0].title()), 3)
            if (len(videos) > 0):
                for row_v in videos:
                    print "\t* [%s](https://www.youtube.com/watch?v=%s)"%(row_v[0].encode('ascii', 'ignore'), row_v[1].encode('ascii', 'ignore'))
            
            videos = doYoutubeSearch("GRAPPLING + \"%s\""%(row_t[0].title()), 3)
            if (len(videos) > 0):
                for row_v in videos:
                    print "\t* [%s](https://www.youtube.com/watch?v=%s)"%(row_v[0].encode('ascii', 'ignore'), row_v[1].encode('ascii', 'ignore'))
            
                    
            if row_t[4] > 1:
                videos = doYoutubeSearch("IBJJF + \"%s\""%(row_t[0].title()), 3)
                if (len(videos) > 0):
                    for row_v in videos:
                        print "\t* [%s](https://www.youtube.com/watch?v=%s)"%(row_v[0].encode('ascii', 'ignore'), row_v[1].encode('ascii', 'ignore'))
             
        else:
            print "* Oponente: (%s) %s - _NO SE ENCONTRO EXPERIENCIA PREVIA_."%(row_t[1].title(), row_t[0].title())
    
    my_db.commit()        

    print "\n#### Historial oponentes.\n"
    for row_op in oponents.keys():
        print "* Oponente: %s."%(oponents[row_op])
        
        if DEBUG_SQL or competitorID == DEBUG_COMPETITORID:
            print 100*'='
            print stmD%(row_op)
            print 100*'='
            
        for row_opd in my_db.execute(stmD%(row_op)):
            medal = row_opd[10].replace("N/A","")
            medal = medal.replace("GOLD"," - Medalla de ORO")
            medal = medal.replace("SILVER"," - Medalla de PLATA")
            medal = medal.replace("BRONZE","- Medalla de BRONCE")
            print "\t* [%s] '%s' %s - (%s/%s/%s)."%(row_opd[1], row_opd[0], medal, row_opd[7].lower(), row_opd[8].lower(), row_opd[9].lower())
            
sys.exit(0)            
my_db.execute("delete from result where id like 'FAKE%%'")
my_db.commit()
