#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2013 Pierre Ratinaud
#License: GNU/GPL


import os
import xml.sax
import glob



#infiledir = '/home/pierre/TXM/corpus/voeux-bin/txm/VOEUX/'
#fileout = 'VOEUXExportfromTXM.txt'


class TXMParser(xml.sax.ContentHandler) :
    def __init__(self, fileout, encodage_out) :
        self.fileout = fileout
        self.encodage_out = encodage_out
        self.sent = []

    def startElement(self, name, attrs) :
        self.name = name
        if name == 'title' :
            pass
        if name == 's' :
            pass
        if name == 'taxonomy' :
            pass
        if name == 'text' :
            self.text2stars(attrs)
        if name == 'w' :
            pass

    def endElement(self, name) :
        if name == 's' or name == 'w' :
            self.printsent()
        if name == 'p' :
            self.printsent()
            self.fileout.write('\n')
          
    def characters(self, content) :
        if self.name == 'txm:form' :
            if content not in [u'', u' ', u'\n', '\r'] :
                self.sent.append(content.rstrip('\n\r'))
            #self.fileout.write(content.encode('utf8'))

    def text2stars(self, attrs) :
        stars = ['_'.join(val).replace(' ', '_').replace("'", '_').replace('/','').replace('.','').replace(';', '').replace(':', '').replace(u'·','') for val in attrs.items()]
        stars = [''.join([u'*', val]) for val in stars]
        stars = u'**** ' + ' '.join(stars)
        self.fileout.write(stars.encode(self.encodage_out))
        self.fileout.write('\n')

    def printsent(self) :
        if self.sent != [] :
            sent = ' ' + ' '.join(self.sent)
            for val in [u' .', u' ,', u' ;', u' :', u' ?', u' !', u' -'] :
                sent = sent.replace(val, val.strip())
            sent = sent.replace("' ", "'")
            self.fileout.write(sent.encode(self.encodage_out))
        self.sent = []



class TXM2IRA :
    def __init__(self, pathin, fileout, encodage_in, encodage_out) :
        parser = xml.sax.make_parser()
        files = glob.glob(os.path.join(pathin,'*.xml'))
        with open(fileout, 'w') as fout :
            parser.setContentHandler(TXMParser(fout, encodage_out))
            for f in files :
                parser.parse(open(f, 'r'))
                fout.write('\n\n')
        print 'done'

#TXM2IRA(infiledir, fileout)
