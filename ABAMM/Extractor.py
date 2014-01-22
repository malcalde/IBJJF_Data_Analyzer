#!/usr/bin/env python

'''
Created on 22/01/2014

@author: malcalde
'''

import sys

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


def parseLTObjects(LTObjects, pageNo, lines=[]):
    
    for LTObject in LTObjects:
        if isinstance(LTObject, LTTextBox) or isinstance(LTObject, LTTextLine):
            lines.append(LTObject.get_text())
        elif isinstance(LTObject, LTFigure):
            parseLTObjects(LTObject.objs, pageNo, lines)
        else:
            print "LT Type %\n"%(LTObject.class)    
    return lines

def extractByAcademy():
    fp = open('../RegistrationsByAcademy.pdf', 'rb')
    parser = PDFParser(fp)
    document = PDFDocument(parser)
    document.initialize(None)
    
    if not document.is_extractable: raise Exception()#PDFTextExtractionNotAllowed()
     
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
            print line
    

def extractByCategory():
    pass

if __name__ == '__main__':
    extractByAcademy()
    