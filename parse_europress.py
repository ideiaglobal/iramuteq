# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2014 Pierre Ratinaud
#License: GNU/GPL


#from BeautifulSoup import BeautifulSoup
import codecs
import os
from HTMLParser import HTMLParser


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

def makedate(date):
    year = date[0:4]
    month = date[4:6]
    day = date[6:]
    return [year, month, day]


# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        #print "Encountered a start tag:", tag
        if tag == 'span' :
            if len(attrs) > 0 :
                if attrs[0][1] == 'DocPublicationName' :
                    #print 'DocPublicationName'
                    self.headercount = 0
                    self.currentattr = 'DocPublicationName'
                elif attrs[0][1] == 'DocHeader' :
                    self.headercount += 1
                    self.currentattr = 'DocHeader'
                elif attrs[0][1] in ['TitreArticleVisu', 'titreArticleVisu'] :
                    self.outfile.write('\n\n')
                    self.meta.append('\n')
                    self.outfile.write(' '.join(self.meta).encode('utf8', errors='replace'))
                    self.meta = [u'****']
                    self.nb += 1
                    self.currentattr = 'TitreArticleVisu'
                elif attrs[0][1] == 'PubliC_lblNodoc' :
                    self.currentattr = 'PubliC_lblNodoc'
        elif tag == 'table' :
            self.currentattr = None
        elif tag == 'div' :
            if len(attrs)>0 :
                if attrs[0][1] == 'publiC-lblNodoc' :
                    self.currentattr = 'PubliC_lblNodoc'
        elif tag == 'p' :
            if len(attrs) > 0 :
                if attrs[0][1] == 'titreArticleVisu' :
        #            self.outfile.write('\n\n')
        #            self.meta.append('\n')
        #            self.outfile.write(' '.join(self.meta).encode('utf8', errors='replace'))
        #            self.meta = [u'****']
        #            self.nb += 1
                    self.currentattr = 'TitreArticleVisu'

    def handle_endtag(self, tag):
        pass
        #print "Encountered an end tag :", tag
    def handle_data(self, data):
        if self.currentattr == 'DocPublicationName' :
            #print data
            PublicationName = data.strip().replace(' ', '_').replace('(','').replace(')','').replace('-','').replace('.','').replace('/','').replace("'",'').replace(';', '').replace(':', '').replace(u'·','').lower()
            PublicationName = PublicationName.split(',')[0]
            self.meta.append(u'*source_' + PublicationName)
            self.currentattr = None
#        elif self.currentattr == 'DocHeader' :
#            date = finddate(data)
#            if date is not None :
#                self.meta += [u'*date_' + '-'.join(date), u'*am_' + '-'.join(date[0:2]), u'*annee_' + date[0]]
        elif self.currentattr == 'TitreArticleVisu' :
            #print data
            if data.startswith(u'©') :
                self.currentattr = None
                return
            self.content.append(' '.join(data.replace('\n', ' ').split()) + ' ')
            #self.outfile.write(' '.join(data.replace('\n', ' ').split()).encode('utf8', errors='replace') + ' ')
        elif self.currentattr == 'PubliC_lblNodoc' :
            date = data[5:13]
            date = makedate(date)
            self.meta += [u'*date_' + '-'.join(date), u'*am_' + '-'.join(date[0:2]), u'*annee_' + date[0]]
            self.meta.append('\n')
            self.outfile.write('\n\n')
            self.outfile.write(' '.join(self.meta).encode('utf8', errors='replace'))
            self.outfile.write(' '.join(self.content).encode('utf8'))
            self.content = []
            self.meta = [u'****']
            self.nb += 1
            self.currentattr = None
    
    def doinit(self, outfile):
        self.currentattr = None
        self.meta = [u'****']
        self.content = []
        self.nb = 0
        self.outfile = outfile
        print 'init ok'
        

def ParseEuropress(txtdir, fileout, encodage_in, encodage_out) :
        files = []
        for root, subfolders, subfiles in os.walk(txtdir) :
            nf = [os.path.join(root, f) for f in subfiles if f.split('.')[-1] in ['html', 'HTML'] ]
            nf.sort()
            files += nf
        if len(files) == 0 :
            return 'nofile'
        tot = 0
        parser = MyHTMLParser()
        with open(fileout,'w') as outf : 
            for f in files : 
                print f
                parser.doinit(outf)
                with codecs.open(f, 'rU', encodage_in) as infile : 
                    content = infile.read() 
                    content = HTMLParser().unescape(content)
                parser.feed(content)
                tot += parser.nb
        return tot

#ParseEuropress('/home/pierre/fac/etudiant/DeNadai/corpus_loi_travail',
#               '/home/pierre/fac/etudiant/DeNadai/corpus_loi_W.txt', 'utf8', 'utf8')     
