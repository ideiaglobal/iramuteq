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
from analysetxt import Alceste,  gramact, gramsup
from corpus import Corpus, copycorpus
from textaslexico import Lexico
from textstat import Stat
from tools import SubCorpus
import tempfile
######################################
import logging
log = logging.getLogger('iramuteq')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)
log.setLevel(logging.DEBUG)
#######################################



#cmd = iracmd.CmdLine(args=['-f','/home/pierre/workspace/iramuteq/corpus/lru2.txt','-t','alceste'])

AppliPath = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])))
if os.getenv('HOME') != None:
    user_home = os.getenv('HOME')
else:
    user_home = os.getenv('HOMEPATH')
UserConfigPath = os.path.abspath(os.path.join(user_home, '.iramuteq'))

class CmdLine :
    def __init__(self, args = None) :
        self.DictPath = ConstructDicoPath(AppliPath)
        self.ConfigPath = ConstructConfigPath(UserConfigPath)
        self.syscoding = sys.getdefaultencoding()
        self.TEMPDIR = tempfile.mkdtemp('iramuteq') 
        self.RscriptsPath = ConstructRscriptsPath(AppliPath)
        self.PathPath = ConfigParser()
        self.PathPath.read(self.ConfigPath['path'])        
        self.RPath = self.PathPath.get('PATHS', 'rpath')
        self.pref = RawConfigParser()
        self.pref.read(self.ConfigPath['preferences'])
        self.history = History(os.path.join(UserConfigPath, 'history.db'))

        parser = OptionParser()
    
        parser.add_option("-f", "--file", dest="filename", help="chemin du corpus", metavar="FILE", default=False)
        parser.add_option("-t", "--type", dest="type_analyse", help="type d'analyse", metavar="TYPE D'ANALYSE", default=False)
        parser.add_option("-c", "--conf", dest="configfile", help="chemin du fichier de configuration pour l'analyse", metavar="CONF", default=None)
        parser.add_option("-d", "--confcorp", dest="corpusconfigfile", help="chemin du fichier de configuration pour le corpus", metavar="CONF", default=None)
        parser.add_option("-e", "--enc", dest="encodage", help="encodage du corpus", metavar="ENC", default=locale.getpreferredencoding())
        parser.add_option("-l", "--lang", dest="language", help="langue du corpus", metavar="LANG", default='french')
        parser.add_option("-r", "--read", dest="read", help="lire un corpus", metavar="READ", default = False)
        parser.add_option("-b", "--build", action="store_true", dest="build", help = "construire un corpus", default = False)

        if args is None :
            (options, args) = parser.parse_args()
        else : 
            (options, args) = parser.parse_args(args)
        print args
        print options
        options.type_analyse
        if options.configfile is not None:
            config = DoConf(os.path.abspath(options.configfile)).getoptions()
        elif options.filename and options.type_analyse :
            config = DoConf(self.ConfigPath[options.type_analyse]).getoptions()
        elif options.read and options.type_analyse :
            config = DoConf(self.ConfigPath[options.type_analyse]).getoptions()
        elif options.read :
            pass
        elif options.filename and options.build :
            pass
        else :
            print 'rien a faire'
            return

        if options.filename or options.read :
            self.corpus_encodage = options.encodage
            self.corpus_lang = options.language
                

            ReadLexique(self, lang = options.language)
            self.expressions = ReadDicoAsDico(self.DictPath.get(options.language + '_exp', 'french_exp'))
            if options.filename :
                self.filename = os.path.abspath(options.filename)
                if options.corpusconfigfile is not None :
                    corpus_parametres = DoConf(options.corpusconfigfile).getoptions('corpus')
                else :
                    corpus_parametres = DoConf(self.ConfigPath['corpus']).getoptions()
                dire, corpus_parametres['filename'] = os.path.split(self.filename)
                corpus_parametres['originalpath'] = self.filename
                corpus_parametres['encoding'] = self.corpus_encodage
                corpus_parametres['syscoding'] = locale.getpreferredencoding()
                corpus_parametres['pathout'] = PathOut(self.filename, 'corpus').mkdirout()
                try :
                    corpus = BuildFromAlceste(self.filename, corpus_parametres, self.lexique, self.expressions).corpus
                except Exception, txt:
                    log.info('probleme lors de la construction: %s' %txt)
                    corpus = None
                    raise
                else :
                    self.history.add(corpus.parametres)
                    corpus = copycorpus(corpus)
            elif options.read :
                corpus = Corpus(self, parametres = DoConf(options.read).getoptions('corpus'), read = options.read)
                corpus.parametres['pathout'] = os.path.dirname(os.path.abspath(options.read))
                pathout = os.path.dirname(os.path.dirname(os.path.abspath(options.read)))
                self.corpus = corpus

            if corpus is not None :
                corpus.conn_all()
                #corpus = SubCorpus(self, corpus, [0,1,2,3,4,5,6,7])
                #corpus.conn_all()
                corpus.make_lems()
                corpus.parse_active(gramact, gramsup)
                #print corpus.getlemconcorde('de').fetchall()
#            log.warning('ATTENTION gethapaxuces')
#            MakeUciStat(corpus)
#            qfqsdf
            #corpus.gethapaxuces()
            #ucisize = corpus.getucisize()
            #ucisize = [`val` for val in ucisize]
            #uciet = [uci.etoiles[1] for uci in corpus.ucis]
            #res = zip(uciet, ucisize)
            #with open('ucisize.csv', 'w') as f :
            #    f.write('\n'.join(['\t'.join(val) for val in res]))
                #    self.content = f.read()
                #self.content = self.content.replace('\r','')
                if options.type_analyse == 'alceste' :
                    log.debug('ATTENTION : ANALYSE NG')
                        #print corpus.make_etoiles()
                        #zerzre
                    #corpus.read_corpus()
                    #corpus.parse_active(gramact, gramsup)
                    config['type'] = 'alceste'
                    self.Text = Alceste(self, corpus, parametres = config)
                #    self.Text = AnalyseAlceste(self, cmd = True, big = True)
                    #self.Text = AnalyseAlceste(self, cmd = True)
                elif options.type_analyse == 'pam' :
                    self.Text = PamTxt(self, cmd = True)
                elif options.type_analyse == 'afcuci' :
                    self.Text = AfcUci(self, cmd = True)
                elif options.type_analyse == 'stat' :
                    self.Text = Stat(self, corpus, parametres = {'type':'stat'})
                elif options.type_analyse == 'spec' :
                    self.Text = Lexico(self, corpus, config = {'type' : 'spec'})
            #print self.Text.corpus.hours, 'h', self.Text.corpus.minutes,'min', self.Text.corpus.seconds, 's'
#            self.Text.corpus.make_colored_corpus('colored.html')

if __name__ == '__main__':
    __name__ = 'Main'
    CmdLine()

