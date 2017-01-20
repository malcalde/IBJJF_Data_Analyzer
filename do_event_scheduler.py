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
import bs4
import datetime
import unicodedata
import time
import subprocess

from datetime import date


URL = "http://events.ibjjf.com/sportos/application/orderfight/index.php?idevent=%s&dayofevent=%s&temp=true"

WEEK = [u'Monday',u'Tuesday', u'Wednesday', u'Thursday', u'Friday', u'Saturday', u'Sunday']

DEBUG_SQL = False 

stm_A = "CREATE TABLE IF NOT EXISTS  %s(id text PRIMARY KEY ASC, eventID text, competitionID text, competitorID_A text, competitorID_B text, belt text, category text, gender text, weight text, winner text, day text, time text, phase text, slot text, hash text)"

stm_C  = """
    select  distinct  competitorID, O.name competidor_name, R.belt, R.gender, R.weight, R.category
      from result R, competition C, academy T, competitor O, lk_belt L
     where 1=1
       and L.belt = R.belt
       and R.academyID = T.id
       and O.id = R.competitorID
       and R.competitionID=C.id
       and T.id = '%s'
       and C.id = '%s'
"""

stm_D = "delete from %s"

stm_E = """
    insert into %s(id, eventID ,competitionID, competitorID_A, competitorID_B, belt, category, gender, weight, winner, day, time, phase, slot, hash)
    values('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s','%s','%s','%s','%s','%s')
"""

stm_F = "select *  from competitor where lower(replace(name, ' ', '')) = '%s'"


def get_categories():
    my_categories = {}
    
    if DEBUG_SQL:
        print 100*'='
        print stm_C%(stm_A%(MY_COMPETITION,MY_TEAM))
        print 100*'='
        
    for row in my_db.execute(stm_C%(MY_TEAM, MY_COMPETITION)):
        key_category = "%s_%s_%s_%s"%(row[5], row[3], row[2], row[4])
        key_category = key_category.encode('ascii', 'ignore')
        key_category = key_category.lower()
        key_category = key_category.replace(' ','')
        
        key_competitor = row[1]
        key_competitor = key_competitor.encode('ascii', 'ignore')
        key_competitor = key_competitor.lower().replace(' ','')
        
        if False == my_categories.has_key(key_category):
            my_categories[key_category] = {}
            
        my_categories[key_category][key_competitor] = {'id': row[0], 'name': row[1], "status": ""}
     
    return my_categories
        

def get_eventdays():
    event_days = {}
    
    html = urllib2.urlopen(URL%(MY_EVENT,"1")).read()
    soup = bs4.BeautifulSoup(html, "lxml")
    
    days = soup.find(id="seletor-dias")
    days = days.find_all("a")
    for day in days:
        try: 
            day_key = day.string.split('-')[1].replace(' ', '')
            event_days[day_key] = day['href']
        except: pass
    return event_days

def strip_accents(text):
    """
    Strip accents from input String.

    :param text: The input string.
    :type text: String.

    :returns: The processed String.
    :rtype: String.
    """
    try:
        text = unicode(text, 'utf-8')
    except : # unicode is a default on python 3 
        pass
    text = unicodedata.normalize('NFD', text)
    text = text.encode('ascii', 'ignore')
    text = text.decode("utf-8")
    return str(text)
    
        
def monitor_matches(day, url, categories, scheduler):
    global my_competitors, my_scores, my_dashboard, my_fights, tmp_fights
    
    dayID = WEEK.index(day.strip())
     
    #my_db.execute(stm_A%"match")
    #my_db.execute(stm_A%"z_match")
    #my_db.commit()
    
    #my_db.execute(stm_D%"z_match")
    #my_db.commit()
    
    try:
        html = urllib2.urlopen(url).read()
        soup = bs4.BeautifulSoup(html, "lxml")
    except Exception, e:
        print "[ERROR] Processing %s - %s"%(url,e)
        time.sleep(30)
        return
    
    for category in categories.keys():
        category_data = category.split('_')
        
        match_table = soup.find_all(id=category)
        for match_table_item in match_table:
            if match_table_item is  None: continue
            
            
            match_fight_related = 0
            match_fight = match_table_item.find(class_='branco')
            if match_fight is not None and match_fight.children is not None:
                match_fight_id = 0
                for x in match_fight.children: 
                    x = x.split(' ')
                    match_fight_id = int(x[len(x) -1])
                
                if 0 != match_fight_id:
                    match_fighter_a = None
                    match_fighter_a = match_table_item.find(class_='nome1')
                    if match_fighter_a is not None and match_fighter_a.children is not None:
                        for x in match_fighter_a.children: 
                            x = strip_accents(x)
                            match_fighter_a = x.encode('ascii', 'ignore')
                            match_fighter_a = match_fighter_a.replace('\\n','')
                            match_fighter_a = match_fighter_a.replace("'", "\"")
                            match_fighter_a = match_fighter_a.split('(')[0]
                            match_fighter_a = match_fighter_a.strip()
                            match_fighter_a_id = match_fighter_a.lower()
                            match_fighter_a_id = match_fighter_a_id.replace(' ','')
                            
                            if match_fighter_a_id.startswith('winoffight'):
                                match_fight_related = match_fighter_a_id[0:match_fighter_a_id.find(',')]
                                match_fight_related =match_fight_related.replace('winoffight','')
                                match_fighter_a_id = None
                                
                            if match_fighter_a_id is not None and False == my_competitors.has_key(match_fighter_a_id):
                                for row_f in my_db.execute(stm_F%(match_fighter_a_id)):
                                    my_competitors[match_fighter_a_id] = row_f[0]
                                    my_scores[match_fighter_a_id] = row_f[3]
                                    
                                if False == my_competitors.has_key(match_fighter_a_id) and categories[category].has_key(match_fighter_a_id): 
                                    print "[WARN] Not found competitor %s"%(match_fighter_a_id)
                                
                                if True == my_scores.has_key(match_fighter_a_id) and my_scores[match_fighter_a_id] is not None:
                                    match_fighter_a = "%s{%s}"%(match_fighter_a, my_scores[match_fighter_a_id])
                    
                    match_fighter_b = None
                    match_fighter_b = match_table_item.find(class_='nome2')
                    if match_fighter_b is not None and match_fighter_b.children is not None:
                        for x in match_fighter_b.children: 
                            x = strip_accents(x)
                            match_fighter_b = x.encode('ascii', 'ignore')
                            match_fighter_b = match_fighter_b.replace('\n','')
                            match_fighter_a = match_fighter_a.replace("'", "\"")
                            match_fighter_b = match_fighter_b.split('(')[0]
                            match_fighter_b = match_fighter_b.strip()
                            match_fighter_b_id = match_fighter_b.lower()
                            match_fighter_b_id = match_fighter_b_id.replace(' ','')
                            
                            if match_fighter_b_id.startswith('winoffight'):
                                match_fight_related = match_fighter_b_id[0: match_fighter_b_id.find(',')]
                                match_fight_related =match_fight_related.replace('winoffight','')
                                match_fighter_b_id = None
                                
                            if match_fighter_b_id is not None and  False == my_competitors.has_key(match_fighter_b_id):
                                for row_f in my_db.execute(stm_F%(match_fighter_b_id)):
                                    my_competitors[match_fighter_b_id] = row_f[0]
                                    my_scores[match_fighter_b_id] = row_f[3]
                                
                                if False == my_competitors.has_key(match_fighter_b_id) and categories[category].has_key(match_fighter_b_id): 
                                    print "[WARN] Not found competitor %s"%(match_fighter_b_id)
                                
                                if True == my_scores.has_key(match_fighter_b_id) and my_scores[match_fighter_b_id] is not None:
                                    match_fighter_b = "%s{%s}"%(match_fighter_b, my_scores[match_fighter_b_id])
                    
                    if categories[category].has_key(match_fighter_a_id) or categories[category].has_key(match_fighter_b_id):
                        
                        if categories[category].has_key(match_fighter_a_id):
                            my_match_fighter = match_fighter_a_id
                            my_match_fighter_name = match_fighter_a
                        else:
                            my_match_fighter = match_fighter_b_id
                            my_match_fighter_name = match_fighter_b
                            
                        tmp_fights[my_match_fighter] = match_fight_id
                            
                        match_fight_time = '???'
                        match_fight_calling = '???'
                        match_fight_phase = '???'
                        match_fight_status = ""
                        try:
                            match_fight_time = match_table_item.find(class_='day')
                            match_fight_time = match_fight_time.string.strip()
                            match_fight_calling = match_table_item.find(class_='fight calling')
                            #fight waiting1
                            match_fight_calling = match_fight_calling.find('span')
                            match_fight_calling = match_fight_calling.string.strip()
                            match_fight_phase = match_table_item.find(class_='fase')
                            match_fight_phase = match_fight_phase.find('span')
                            match_fight_phase = match_fight_phase.string.strip()
                            
                            if match_table_item.find(class_='fight calling') is not None:
                                match_fight_status = ""
                            elif match_table_item.find(class_='fight fighting') is not None:
                                match_fight_status = "{Fighting}" 
                            elif match_table_item.find(class_='fight waiting1') is not None:
                                match_fight_status = "{Waiting for %s}"%(match_fighter_a)
                            elif match_table_item.find(class_='fight waiting1') is not None:
                                match_fight_status = "{Waiting for %s}"%(match_fighter_b)
                        except: pass
                        scheduler["%s_%s"%(dayID,match_fight_time)] = "%s[%s - %s] Fight(%s/%s/%s) %s vs. %s"%(match_fight_status,day,match_fight_time, match_fight_id, match_fight_phase, match_fight_calling, match_fighter_a, match_fighter_b)
                        my_dashboard[match_fight_id] = "%s[%s - %s] Fight(%s/%s/%s) %s vs. %s"%(match_fight_status,day,match_fight_time, match_fight_id, match_fight_phase, match_fight_calling, match_fighter_a, match_fighter_b)
                        
                        if False == my_fights.has_key(my_match_fighter): my_fights[my_match_fighter] = match_fight_id
                            
                        if my_fights[my_match_fighter] != tmp_fights[my_match_fighter]: 
                            subprocess.Popen(["notify-send", "%s Go ahead to fight %s (%s)!!!!" % my_match_fighter_name, match_fight_id, match_fight_time])
                            my_fights[my_match_fighter] = tmp_fights[my_fights]                  
                        
                        
                        if categories[category][my_match_fighter]["status"] != match_fight_status:
                            subprocess.Popen(["notify-send", scheduler["%s_%s"%(dayID,match_fight_time)]])
                            categories[category][my_match_fighter]["status" ] = match_fight_status
                            
                        try:
                            pass
                        except: pass
                    
                        #id text PRIMARY KEY ASC, eventID text, competitionID text, 
                        #competitorID_A text, competitorID_B text, belt text, category text, gender text, weight text, winner text, day text, time text, phase text, slot text, metric integer, hash text)"

    
    my_db.commit()
    
assert(len(sys.argv) > 2)
MY_TEAM = 'fb45077e4e17a516ab3aca56c9c01363'#sys.argv[3]
MY_EVENT = '440'#sys.argv[2]
MY_COMPETITION = '000652'#sys.argv[1]

my_competitors = {}
my_scores = {}
my_dashboard = {}
my_fights = {}
tmp_fights = {}

if __name__ == '__main__':
    my_db = sqlite3.connect('data/my-ibjjf.db')
    assert (my_db is not None),"Fail opening database"
    
    categories = get_categories()
    
    current = datetime.datetime.now()
    current_day = current.weekday()
    current_day = WEEK[current_day]
    while True:
        my_scheduler = {}
        tmp_fights = {}
        days = get_eventdays()
        for day in days.keys():
            if WEEK.index(day) < WEEK.index(current_day) : continue
            
            print "[INFO] Updating championship day %s"%(day)
            monitor_matches(day, days[day], categories, my_scheduler)
            
        losses = [val for val in my_fights.keys() if val not in tmp_fights]
        
        for lose in losses:
            subprocess.Popen(["notify-send", "LOST - %s"%(my_dashboard[lose])])
            
        for key in sorted(my_scheduler):
            print "-%s"% my_scheduler[key]
        
        if len(my_scheduler):
            print 3*"\n"    
        time.sleep(5)
          
    my_db.close()
