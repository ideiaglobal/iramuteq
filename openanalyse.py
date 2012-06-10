#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012, Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ChdTxtPathOut, StatTxtPathOut, construct_simipath
from layout import OpenCHDS, dolexlayout, StatLayout, WordCloudLayout, OpenCorpus
#from corpus import Corpus
from corpusNG import Corpus, copycorpus
from tableau import Tableau
import os
import shelve
from ConfigParser import *
from tabsimi import DoSimi
from functions import BugReport, DoConf
import logging

log = logging.getLogger('iramuteq.openanalyse')

class OpenAnalyse():
    def __init__(self, parent, parametres, Alceste=True, simifromprof = False):
        #self.conf = RawConfigParser()
        #self.conf.read(filename)
        log.info('OpenAnalyse')
        self.parent = parent
        if isinstance(parametres, dict) :
            self.conf = DoConf(parametres['ira']).getoptions()
        else :
            self.conf = DoConf(parametres).getoptions()
        
        if self.conf.get('corpus', '!!') in self.parent.history.history :
            if self.conf.get('corpus', '!!') in self.parent.history.openedcorpus :
                log.info('corpus is already opened')
                corpus = copycorpus(self.parent.history.openedcorpus[self.conf['corpus']]) 
            else :
                if os.path.exists(self.parent.history.history[self.conf['corpus']]['ira']) :
                    corpus = Corpus(self, parametres = DoConf(self.parent.history.history[self.conf['corpus']]['ira']).getoptions('corpus'), read = self.parent.history.history[self.conf['corpus']]['ira'])
                self.parent.history.openedcorpus[self.conf['corpus']] = corpus
            if self.conf.get('lem',1) :
               corpus.make_lems(True)
            else :
               corpus.make_lems(False)
        else :
            corpus = None
        self.doopen(corpus)
        self.parent.history.addtab(self.conf)
        
    def doopen(self, corpus) :
        print self.conf
        if self.conf['type'] == 'corpus' :
            self.parent.ShowMenu(_("Text analysis"))
            OpenCorpus(self.parent, self.conf) 
        elif self.conf['type'] == 'stat' :
            self.parent.ShowMenu(_("Text analysis"))
            StatLayout(self.parent, corpus, self.conf)
        elif self.conf['type'] == 'spec' :
            self.parent.ShowMenu(_("Text analysis"))
            dolexlayout(self.parent, corpus, self.conf)
        elif self.conf['type'] == 'alceste' :
            self.parent.ShowMenu(_("Text analysis"))
            OpenCHDS(self.parent,  corpus, self.conf, Alceste = True)
        elif self.conf['type'] == 'simi' :
            print 'simi'
#        try :
#            #if self.conf['type'] in ['analyse','lexico','stat','wordcloud'] :
#            #    self.corpus = Corpus(parent)
#            if 'analyse' in self.conf.sections() :
#                DictPathOut=ChdTxtPathOut(os.path.dirname(filename))
#                self.pathout = os.path.dirname(filename)
#                self.DictPathOut=DictPathOut
#                #self.corpus = Corpus(parent)
#                self.corpus.dictpathout = self.DictPathOut
#                self.corpus.read_corpus_from_shelves(self.DictPathOut['db'])
#                self.corpus.parametre['analyse'] = 'alceste'
#                self.corpus.make_lem_type_list()
#    #            print 'EXTRACT NR'
#    #            self.corpus.extractnr()
#                Alceste=True
#                #self.corpus.save_corpus(self.corpus.dictpathout['db'])
#                #self.corpus.make_uci_stat()
#                #self.corpus.make_et_table()
#                #self.corpus.prof_type()
#                #self.corpus.make_type_tot()
#                #self.corpus.make_size_uci()
#                #self.corpus.get_stat_by_cluster()
#                OpenCHDS(parent, self, filename, Alceste)
#                self.parent.ShowMenu(_("Text analysis"))
#                self.parent._mgr.Update()
#            elif 'questionnaire' in self.conf.sections() :
#                self.DictPathOut=ChdTxtPathOut(os.path.dirname(filename))
#                self.pathout = os.path.dirname(filename)
#                self.tableau = Tableau(parent, filename)
#                self.tableau.dictpathout = self.DictPathOut
#                self.tableau.read_tableau(self.tableau.dictpathout['db'])
#                OpenCHDS(parent, self, filename, False)
#            elif 'simi' in self.conf.sections():
#                self.tableau = Tableau(parent, filename)
#                self.DictPathOut=construct_simipath(os.path.abspath(os.path.dirname(filename)))
#                self.tableau.dictpathout = self.DictPathOut
#                self.tableau.read_tableau(self.tableau.dictpathout['db'])
#                if self.tableau.parametre.get('fromtxt', False) :
#                    self.corpus=Corpus(parent)
#                    self.corpus.read_corpus_from_shelves(self.DictPathOut['corpus'])
#                    self.corpus.parametre['openpath'] = os.path.dirname(filename)
#                    self.parent.ShowMenu(_("Text analysis"))
#                DoSimi(parent, self.conf, isopen = True, filename = filename, gparent = self, openfromprof=simifromprof) 
#            elif 'lexico' in self.conf.sections():
#                print 'lexico'
#                #self.corpus = Corpus(parent)
#                self.corpus.dictpathout = StatTxtPathOut(os.path.dirname(filename))
#                self.parent.ShowMenu(_("Text analysis"))
#                dolexlayout(parent, self, filename)
#            elif 'stat' in self.conf.sections():
#                print 'stat'
#                #self.corpus = Corpus(parent)
#                self.corpus.dictpathout = StatTxtPathOut(os.path.dirname(filename))
#                self.parent.ShowMenu(_("Text analysis"))
#                StatLayout(parent, self, filename)
#            elif 'chd_dist_quest' in self.conf.sections():
#                self.DictPathOut = ChdTxtPathOut(os.path.dirname(filename))
#                self.pathout = os.path.dirname(filename)
#                self.tableau = Tableau(parent, filename)
#                self.tableau.dictpathout = self.DictPathOut
#                self.tableau.read_tableau(self.tableau.dictpathout['db'])
#                OpenCHDS(parent, self, filename, False)
#            elif 'wordcloud' in self.conf.sections() :
#                self.corpus.dictpathout = StatTxtPathOut(os.path.dirname(filename))
#                self.corpus.read_corpus_from_shelves(self.corpus.dictpathout['db'])
#                self.parent.ShowMenu(_("Text analysis"))
#                WordCloudLayout(parent, self, filename)
#            if self.conf.sections()[0] in ['analyse','lexico','stat','wordcloud'] :
#                self.corpus.parametre['openpath'] = os.path.dirname(filename)
#        except :
#            BugReport(self.parent)


