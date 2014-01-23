#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import sys
import re

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

def parseLTObjects(LTObjects, pageNo, lines=[]):
    
    for LTObject in LTObjects:
        if isinstance(LTObject, LTTextBox) or isinstance(LTObject, LTTextLine):
            for line in LTObject.get_text().split('\n'):
                lines.append(line.upper().strip())
        elif isinstance(LTObject, LTFigure):
            parseLTObjects(LTObject.objs, pageNo, lines)
        else:
            print "LT Type %s\n"%(LTObject)    
    return lines

def extractByAcademy():

    tmp = None
    club = None
    item = None
    
    fp = open('../RegistrationsByAcademy.pdf', 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    document.initialize(None)
    
    if not document.is_extractable: raise Exception()#PDFTextExtractionNotAllowed()
    
    record = 1	 
    rsrcmgr = PDFResourceManager()
    
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    
    pages = PDFPage.create_pages(document)
    for page in pages:
        interpreter.process_page(page)
        layout = device.get_result() 
        lines = parseLTObjects(layout,1)
        
        for line in lines:
            if line.count('/') == 3:
                if club is None: club = tmp 
                data = line.split('/')

                hkey = ''
                for i in range(0,len(data)):
                    data[i] = data[i].strip()
                    hkey += data[i] + '_' 
                               
                hkey = hkey.replace(' ', '_')
                
                if False == knowledge.has_key(club): knowledge[club] = dict()

                if knowledge[club].has_key(hkey):
                    knowledge[club][hkey][4] += 1
                else:
                    knowledge[club][hkey] = data
                    knowledge[club][hkey].append(1)

		if knowledge[club][hkey][4] > record:
		    print "New record on %s at category %s with %i players\n"%(club,hkey,knowledge[club][hkey][4])
		    record = knowledge[club][hkey][4]
		print "{%s-%s}Processing line %s\n"%(club,hkey,line)
            else:
                tmp = line
                if line <> '': club = None
            
def extractByCategory():
    pass

def dumpKnowledge():
    for c in knowledge.keys():
        for h in knowledge[c].keys():
            line = c + ',' + knowledge[c][h][0] + ',' + knowledge[c][h][1] +',' + knowledge[c][h][2] +',' + knowledge[c][h][3] + ',' + str(knowledge[c][h][4])
            print line,",0,0,0\n" 
        
if __name__ == '__main__':
    extractByAcademy()

    dumpKnowledge()
    
