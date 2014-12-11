# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2014 Pierre Ratinaud
#License: GNU/GPL


#from BeautifulSoup import BeautifulSoup
import codecs
import os
from HTMLParser import HTMLParser


infile = '/home/pierre/workspace/iramuteq/dev/europress/DocActionPrintSave.aspx.html'

with codecs.open(infile, 'r', 'utf8') as f :
    html = f.read()

mois = {u'janvier' : '01', 
        u'février' : '02',
        u'mars' : '03',
        u'avril' : '04', 
        u'mai' : '05',
        u'juin' : '06',
        u'juillet' : '07',
        u'août' : '08',
        u'septembre' : '09',
        u'octobre' : '10',
        u'novembre' : '11',
        u'décembre' : '12', 
        u'january' : '01',
        u'february': '02',
        u'march' : '03',
        u'april': '04',
        u'may': '05',
        u'june' : '06',
        u'july': '07',
        u'august': '08',
        u'september' : '09',
        u'october': '10',
        u'november': '11',
        u'december': '12'}


def finddate(data):
    data = data.split()
    try :
        day = int(data[0])
        year = int(data[2])
        month = mois[data[1]]
    except :
        return None
    else :
        return [`year`, month, '%02d' % day]
    

# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag
        if tag == 'span' :
            if attrs[0][1] == 'DocPublicationName' :
                self.headercount = 0
                self.currentattr = 'DocPublicationName'
            elif attrs[0][1] == 'DocHeader' :
                self.headercount += 1
                self.currentattr = 'DocHeader'
            elif attrs[0][1] == 'TitreArticleVisu' :
                self.outfile.write('\n\n')
                self.meta.append('\n')
                self.outfile.write(' '.join(self.meta).encode('utf8', errors='replace'))
                self.meta = [u'****']
                self.nb += 1
                self.currentattr = 'TitreArticleVisu'
        elif tag == 'table' :
            self.currentattr = None
    def handle_endtag(self, tag):
        pass
        #print "Encountered an end tag :", tag
    def handle_data(self, data):
        if self.currentattr == 'DocPublicationName' :
            PublicationName = data.replace(' ', '_').replace('(','').replace(')','').replace('.','').replace('/','').replace("'",'').lower()
            PublicationName = PublicationName.split(',')[0]
            self.meta.append(u'*source_' + PublicationName)
        elif self.currentattr == 'DocHeader' :
            date = finddate(data)
            if date is not None :
                self.meta += [u'*date_' + '-'.join(date), u'*am_' + '-'.join(date[0:2]), u'*annee_' + date[0]]
        elif self.currentattr == 'TitreArticleVisu' :
            if data.startswith(u'©') :
                self.currentattr = None
                return
            self.outfile.write(' '.join(data.replace('\n', ' ').split()).encode('utf8', errors='replace') + ' ')
    
    def doinit(self, outfile):
        self.currentattr = None
        self.meta = [u'****']
        self.nb = 0
        self.outfile = outfile
        

class ParseEuropress :
    def __init__(self, txtdir, fileout, encodage_in, encodage_out) :
        files = []
        for root, subfolders, subfiles in os.walk(txtdir) :
            nf = [os.path.join(root, f) for f in subfiles if f.split('.')[-1] == 'html']
            nf.sort()
            files += nf
        tot = 0
        parser = MyHTMLParser()
        with open(fileout,'w') as outf : 
            for f in files : 
                print f
                parser.doinit(outf)
                with codecs.open(f, 'rU', encodage_in) as infile : 
                    content = infile.read() 
                parser.feed(content)
                tot += parser.nb
                print 'ok', parser.nb, 'articles', ' - total : ', tot   
                
#ParseEuropress('/home/pierre/fac/lerass/mariage/press', '/home/pierre/workspace/iramuteq/dev/europress/corpus_out.txt', 'utf8', 'utf8')     
        #print "Encountered some data  :", data
# instantiate the parser and fed it some HTML
#outfile = '/home/pierre/workspace/iramuteq/dev/europress/corpus_out.txt'
#parser = MyHTMLParser()
#with open(outfile, 'w') as f :
#    parser.doinit(f)
#    parser.feed(html)