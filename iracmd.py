#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2010 Pierre Ratinaud
#Lisense: GNU/GPL

import os
from optparse import OptionParser
import sys
reload(sys)
import locale
import codecs
sys.setdefaultencoding(locale.getpreferredencoding())
from chemins import ConstructConfigPath, ConstructDicoPath, ConstructRscriptsPath
from functions import ReadLexique, DoConf, History
from ConfigParser import *
#######################################
#from textchdalc import AnalyseAlceste
#from textdist import PamTxt
#from textafcuci import AfcUci
from textaslexico import Lexico
from textstat import Stat
import tempfile
######################################
print '#######LOGGING TEST###########'
import logging
log = logging.getLogger('iramuteq')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)
log.setLevel(logging.DEBUG)
#######################################

log.debug('----------TEST corpusNG-----------------')
from analysetxt import Alceste,  gramact, gramsup
from corpusNG import *



AppliPath = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])))
if os.getenv('HOME') != None:
    user_home = os.getenv('HOME')
else:
    user_home = os.getenv('HOMEPATH')
UserConfigPath = os.path.abspath(os.path.join(user_home, '.iramuteq'))

class CmdLine :
    def __init__(self) :
        self.DictPath = ConstructDicoPath(AppliPath)
        self.ConfigPath = ConstructConfigPath(UserConfigPath)
        self.syscoding = sys.getdefaultencoding()
        parser = OptionParser()
    
        parser.add_option("-f", "--file", dest="filename", help="chemin du corpus", metavar="FILE", default=False)
        parser.add_option("-t", "--type", dest="type_analyse", help="type d'analyse", metavar="TYPE D'ANALYSE", default='False')

        parser.add_option("-c", "--conf", dest="configfile", help="chemin du fichier de configuration", metavar="CONF", default=False)
        parser.add_option("-e", "--enc", dest="encodage", help="encodage du corpus", metavar="ENC", default=locale.getpreferredencoding())
        parser.add_option("-l", "--lang", dest="language", help="langue du corpus", metavar="LANG", default='french')
        parser.add_option("-r", "--read", dest="read", help="lire un corpus", metavar="READ", default = False)

        (options, args) = parser.parse_args()
        print args
        print options
        if options.configfile :
            self.ConfigPath[options.type_analyse] = os.path.abspath(options.configfile)
        self.TEMPDIR = tempfile.mkdtemp('iramuteq') 
        self.RscriptsPath = ConstructRscriptsPath(AppliPath)
        self.PathPath = ConfigParser()
        self.PathPath.read(self.ConfigPath['path'])        
        self.RPath = self.PathPath.get('PATHS', 'rpath')
        self.pref = RawConfigParser()
        self.pref.read(self.ConfigPath['preferences'])
        self.history = History(self.ConfigPath['history'])
        #self.history.write()
        if options.filename or options.read or options.build:
            self.corpus_encodage = options.encodage
            self.corpus_lang = options.language
                

            #print 'PAS DE CODECS POUR CABLE'
            ReadLexique(self, lang = options.language)
            self.expressions = ReadDicoAsDico(self.DictPath.get(options.language + '_exp', 'french_exp'))
            if options.filename :
                self.filename = os.path.abspath(options.filename)
                corpus_parametres = DoConf('/home/pierre/.iramuteq/corpus.cfg').getoptions('corpus')
                corpus_parametres['filename'] = self.filename
                corpus_parametres['encoding'] = self.corpus_encodage
                corpus_parametres['syscoding'] = 'utf8'
                corpus_parametres['pathout'] = PathOut(options.filename, 'corpus').dirout
                corpus = BuildFromAlceste(self.filename, corpus_parametres, self.lexique, self.expressions).corpus
                self.history.add(corpus.parametres)

                #with codecs.open(self.filename, 'r', self.corpus_encodage) as f:
            elif options.read :
                corpus = Corpus(self, parametres = DoConf(options.read).getoptions('corpus'), read = options.read)
                corpus.parametres['path'] = os.path.abspath(options.read)
                pathout = os.path.dirname(os.path.dirname(os.path.abspath(options.read)))


            corpus.conn_all()
            corpus.parse_active(gramact, gramsup)
                #    self.content = f.read()
                #self.content = self.content.replace('\r','')
            if options.type_analyse == 'alceste' :
                log.debug('ATTENTION : ANALYSE NG')
                    #print corpus.make_etoiles()
                    #zerzre
                #corpus.read_corpus()
                #corpus.parse_active(gramact, gramsup)
                Alceste(self, corpus)
            #    self.Text = AnalyseAlceste(self, cmd = True, big = True)
                #self.Text = AnalyseAlceste(self, cmd = True)
            elif options.type_analyse == 'pam' :
                self.Text = PamTxt(self, cmd = True)
            elif options.type_analyse == 'afcuci' :
                self.Text = AfcUci(self, cmd = True)
            elif options.type_analyse == 'stat' :
                self.Text = Stat(self, corpus, config = {'type' : 'stat'})
            elif options.type_analyse == 'spec' :
                self.Text = Lexico(self, corpus, config = {'type' : 'spec'})
            #print self.Text.corpus.hours, 'h', self.Text.corpus.minutes,'min', self.Text.corpus.seconds, 's'
#            self.Text.corpus.make_colored_corpus('colored.html')

if __name__ == '__main__':
    __name__ = 'Main'
    CmdLine()

