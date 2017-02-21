#!/usr/bin/env python

'''
Created on Feb 19, 2017

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
import argparse
import googlemaps
import ConfigParser

from do_youtube_search import *

from datetime import date

DEBUG_SQL = False

my_db = sqlite3.connect('data/my-ibjjf.db')
assert (my_db is not None),"Fail opening database"

STM_02 = """
select T.name competition, T.year year, T.mode mode, T.date, T.is_loaded, A.name academy, C.name competitor, C.birth_year estimated_birth_year,
             R.gender, R.belt, R.category, R.weight, m.name medal, R.score score, R.round rounds
from result R, competition T, academy A, competitor C, lk_medal M
where R.medal=M.id
and A.id = R.academyID
and T.id=R.competitionID
and  R.competitorID = C.id
and C.id = '%s'
order by R.competitionID desc
"""

STM_01 = """
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
  and C.id = '%s'
 group by  competitor
 order by score DESC, medal_gold DESC, medal_silver DESC, medal_bronze DESC, medals DESC, competitions DESC
"""

def run_competitor_report(row):
    print "\n## [Competidor] %s (score: %s)\n----\n"%(row[1], row[3])
    for row_01 in my_db.execute(STM_01%(row[0])):
        competitions = (row_01[3]-1)
        if 0 == competitions: competitions = 1
        print "* %s - %s medallas en %s competiciones (%s,%s,%s) - %.2f %% exito - score: %.2f."%(row_01[0].title(), row_01[4], competitions, row_01[5], row_01[6], row_01[7],
                                                                                                       100.0 * (1.0 * (row_01[4]-row_01[10])/(competitions)), row_01[8])
        print "\n### Historial"
        for row_02 in my_db.execute(STM_02%(row[0])):
            competition_date  ="%06d"%(row_02[3])
            competition_date = "%s/%s/%s"%(competition_date[0:2],competition_date[2:4], competition_date[5:])
            
            medal = ""
            if 'N/A' != row_02[12]: medal = " medal: %s"%(row_02[12])
            
            score  = ""
            if 0 < row_02[13]: score = " score: %.2f"%(row_02[13])
            
            cheater  = ""
            if 'GOLD' == row_02[12] and 0 == row_02[14]: cheater = " CHEATER!!!!"
            if 'SILVER' == row_02[12] and 1 == row_02[14]: cheater = " CHEATER!!!!"
            if 'BRONZE' == row_02[12] and 3 == row_02[14]: cheater = " CHEATER!!!!"
            
            if 1 == row_02[4]:
                print " * [%s - %s] mode: %s team: %s belt: %s weight: %s class :%s %s %s %s"%(row_02[1], row_02[0], row_02[2], row_02[5], row_02[9], row_02[10], row_02[11], medal, score, cheater) 
            else:
                print " * [%s - %s] mode: %s team: %s belt: %s weight: %s class :%s"%(row_02[1], row_02[0], row_02[2], row_02[5], row_02[9], row_02[10], row_02[11])
                
        videos = []
        videos.extend(doYoutubeSearch("BJJ + \"%s\""%(row_01[0].title()), 3))
        videos.extend(doYoutubeSearch("GRAPPLING + \"%s\""%(row_01[0].title()), 3))
        videos.extend(doYoutubeSearch("IBJJF + \"%s\""%(row_01[0].title()), 3))
        if (len(videos) > 0):
            print "### Youtube videos for '%s'"%(row_01[0].title())
            for video in videos:
                print "\t* [%s](https://www.youtube.com/watch?v=%s)"%(video[0].encode('ascii', 'ignore'), video[1].encode('ascii', 'ignore'))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some values.')
    parser.add_argument('--competitor', help='competitor ID', action='append')
    
    args = parser.parse_args()
    
    if (args.competitor):
        start_time = timeit.default_timer()
        print "# Perfil competidor"
        for competitorID in args.competitor:
           for row in my_db.execute("select * from competitor where id='%s' or name  like '%s%s%s'"%(competitorID, '%', competitorID, '%')):
               run_competitor_report(row)
    
        ellapsed_time = timeit.default_timer() - start_time
        print "\n\nProcesado - informe de competidores: _(%.2f sg)_.\n "%(ellapsed_time)