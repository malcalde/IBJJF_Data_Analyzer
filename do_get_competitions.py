#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import re
import requests
from bs4 import BeautifulSoup

url_results = 'http://ibjjf.org/results'
parser = 'html5lib'

s = requests.session()
r = s.get(url_results)
 
soup = BeautifulSoup(r.text, parser)

data = soup.find_all(['h3','a'])

valid_link = re.compile('http:\/\/static.ibjjfdb\.com\/Campeonato\/[0-9]\/*')

competitionID = None
competitionYear = None
competitionMode = None
competitionTitle = None
competitionName  = None

events = []

for item in data:
    try:
        if 'h3' == item.name:
            competitionName = item.contents[0]
            if competitionName is None: continue
            
            competitionName = competitionName.lower()
            
            if -1 == competitionName.find(' no-gi '):
                competitionMode = 'gi'
            else:
                competitionMode = 'nogi'
                
            competitionName = competitionName.replace(' no-gi ', '')
            competitionName = competitionName.replace(' gi ', '')
            competitionName = competitionName.replace('championship', '')
            competitionName = competitionName.replace('ibjjf', '')
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
            competitionName = competitionName.replace(' ', '')
            competitionName = competitionName.strip()
                
            if competitionTitle != competitionName:
                print '\n# %s'%(item.contents[0])
                competitionTitle = competitionName
                 
        if 'a' == item.name:
            href = item.get ('href')
            if href is None: continue
            
            if (valid_link.match(href)):
                competitionID = href.replace('http://static.ibjjfdb.com/Campeonato/','')
                competitionID = competitionID.replace('/en-US/Results.pdf','')
                
                competitionYear = item.contents[0]
                
                events.append("%s-%s-%s-%s"%(competitionID, competitionName, competitionMode, competitionYear))
    except: pass


url_upcoming = 'http://ibjjf.org/upcoming-events/'
r = s.get(url_upcoming) 
soup = BeautifulSoup(r.text, parser)

data_links = soup.find_all(['li'])

for link in data_links:
    competitionID = None
    competitionName = None
    competitionMode = None
    competitionTitle = None
    competitionLocation = None
    
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
            competitionTitle = href.replace('http://ibjjf.org/championship/','')
            competitionTitle = competitionTitle.replace('/','')
            
            if -1 != competitionTitle.find('no-gi'):
                competitionMode='nogi'
            else:
                competitionMode = 'gi'
            
            competitionName = competitionTitle    
            competitionName = competitionName.replace(' no-gi ', '')
            competitionName = competitionName.replace(' gi ', '')
            competitionName = competitionName.replace('championship', '')
            competitionName = competitionName.replace('ibjjf', '')
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
            competitionName = competitionName.replace('-', '')
            competitionName = competitionName.replace(' ', '')
            competitionName = competitionName.strip()
                
            data_address = link.find('big')
            if data_address is not None:
                data_address = data_address.find('address')
                competitionLocation = data_address.string
                competitionLocation =  competitionLocation.replace('\n','')
                competitionYear = competitionLocation[0: competitionLocation.find('-')]
                competitionYear = competitionYear[competitionYear.find(',')+1:]
                competitionYear = competitionYear.replace(' ', '')
                
            
    if competitionID is not None:
        print "CompetitionID: %s"%(competitionID)
        print "CompetitionName: %s"%(competitionName)
        print "CompetitionMode: %s"%(competitionMode)
        print "CompetitionTitle: %s"%(competitionTitle)
        print "CompetitionLocation: %s"%(competitionLocation)
        print "CompetitionYear: %s"%(competitionYear)
        events.append("%s-%s-%s-%s-%s"%(competitionID, competitionName, competitionMode, competitionYear, href))
        

