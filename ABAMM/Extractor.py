#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import sys
import re
import csv

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
#from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage

knowledge = dict()

academy = dict()
belt = dict()
gender = dict()
category = dict()
weight = dict()

total = 0

def parseLTObjects(LTObjects, pageNo, lines=[]):
    
    for LTObject in LTObjects:
        if isinstance(LTObject, LTTextBox) or isinstance(LTObject, LTTextLine):
            for line in LTObject.get_text().split('\n'):
                lines.append(line.encode('ascii', 'ignore').upper().strip())
        elif isinstance(LTObject, LTFigure):
            parseLTObjects(LTObject.objs, pageNo, lines)
        else:
            print "LT Type %s\n"%(LTObject)    
    return lines

def processData(data, count=False):
    global total

    hkey = ""

    #poner assert a la longitud
    for i in range(0,len(data)):
        data[i] = data[i].strip()
        hkey += data[i] + "_" 
                               
        hkey = hkey.replace(' ', '_')
        hkey = hkey[:len(hkey)-1]
    
    #annotate results (if proceed)
    if count:
        if False == belt.has_key(data[0]): belt[data[0]] = 1
        belt[data[0]] += 1

        if False == category.has_key(data[1]): category[data[1]] = 1
        category[data[1]] += 1

        if False == gender.has_key(data[2]): gender[data[2]] = 1
        gender[data[2]] += 1

        if False == weight.has_key(data[3]): weight[data[3]] = 1
        weight[data[3]] += 1
	
	total += 1
    
    return hkey
        
def extractByAcademy():

    tmp = None
    club = None
    item = None
    
    fp = open('../RegistrationsByAcademy.pdf', 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    document.initialize(None)
    
    if not document.is_extractable: raise Exception()#PDFTextExtractionNotAllowed()
    
    pageno = 0	 
    rsrcmgr = PDFResourceManager()
    
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    pages = PDFPage.create_pages(document)
    for page in pages:
        interpreter.process_page(page)
        layout = device.get_result() 
        lines = parseLTObjects(layout,pageno)

        pageno += 1
        #print "Processing page %i\n"%(pageno)
        
        for line in lines:
            if line.count('/') == 3:
                if club is None: club = tmp 
                data = line.split('/')

                hkey = processData(data, True)
            
                if False == knowledge.has_key(club): knowledge[club] = dict()

                if knowledge[club].has_key(hkey):
                    knowledge[club][hkey][4] += 1
                else:
                    knowledge[club][hkey] = data
                    knowledge[club][hkey].append(1)
                    
                #print "{%s-%s}Processing line %s - %i\n"%(club,hkey,line, knowledge[club][hkey][4])
            elif line.startswith('TOTAL'):
                academy[club] = int(line.replace('TOTAL:','').strip())
		club = None
            else:
                tmp = line.strip()
                
        del lines[:]
            
def extractByCategory():
    
    data = None
    hkey = None
    
    fp = open('../RegistrationsByCategoryAndAcademy.pdf', 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    document.initialize(None)
    
    if not document.is_extractable: raise Exception()#PDFTextExtractionNotAllowed()
    
    pageno = 0	 
    rsrcmgr = PDFResourceManager()
    
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    pages = PDFPage.create_pages(document)
    for page in pages:
        interpreter.process_page(page)
        layout = device.get_result() 
        lines = parseLTObjects(layout,pageno)

        pageno += 1
        print "Processing page %i\n"%(pageno)
        
        for line in lines:
            if line.count('/') == 3:
                data = line.split('/')

                hkey = ''
                for i in range(0,len(data)):
                    data[i] = data[i].strip()
                    hkey += data[i] + '_' 
                               
                hkey = hkey.replace(' ', '_')
                hkey = hkey[:len(hkey)-1]
                
            elif line.startswith('TOTAL'):
                hkey = None
                print "Limpieza"
            else:
                line = line.strip()
                if hkey is not None:
                    if True == knowledge.has_key(line): print "TODO contabilizar competidor"
                    print "Competidor en club {%s} para categoria %s\n"%(line, hkey)
                    
        del lines[:]
       
def extractFromResults():
    pass
 
def dumpKnowledge():
    with open('../data/data.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        for c in knowledge.keys():
            for h in knowledge[c].keys():
                writer.writerow([c,knowledge[c][h][0],knowledge[c][h][1],knowledge[c][h][2],knowledge[c][h][3],knowledge[c][h][4]])

def dumpBelts():
    with open('../data/belts.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        for c in belt.keys():
            writer.writerow([c,belt[c], 1.0 * belt[c]/total])

def dumpCategories():
    with open('../data/categories.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        for c in category.keys():
            writer.writerow([c,category[c], 1.0 * category[c]/total])

def dumpGenders():
    with open('../data/genders.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        for c in gender.keys():
            writer.writerow([c,gender[c], 1.0 * gender[c]/total])

def dumpWeights():
    with open('../data/weights.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        for c in weight.keys():
            writer.writerow([c,weight[c], 1.0 * weight[c]/total])

def dumpAcademy():
    with open('../data/academies.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='"', quoting=csv.QUOTE_ALL)
        for c in academy.keys():
            writer.writerow([c,academy[c], 1.0 * academy[c]/total])
                            
if __name__ == '__main__':
    extractByAcademy()
    #extractByCategory()
                            
    dumpKnowledge()
    dumpBelts()
    dumpCategories()
    dumpGenders()
    dumpAcademy()	
    dumpWeights()                        
                            
    
