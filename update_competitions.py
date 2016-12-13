#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import re
import requests
from bs4 import BeautifulSoup

url = 'http://ibjjf.org/results'
parser = 'html5lib'

s = requests.session()
r = s.get(url)
 
soup = BeautifulSoup(r.text, parser)

data = soup.find_all(['h3','a'])

valid_link = re.compile('http:\/\/static.ibjjfdb\.com\/Campeonato\/[0-9]\/*')

competitionID = None
competitionYear = None
competitionMode = None
competitionTitle = None
competitionName  = None

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
                
                print "%s-%s-%s-%s"%(competitionID, competitionName, competitionMode, competitionYear)
    except: pass
