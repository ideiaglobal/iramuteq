#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012, Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ChdTxtPathOut, StatTxtPathOut, construct_simipath
from layout import OpenCHDS, dolexlayout, StatLayout, WordCloudLayout, OpenCorpus, SimiLayout
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
            self.path = parametres['ira']
        else :
            self.conf = DoConf(parametres).getoptions()
            self.path = parametres
            self.conf = self.redopath(self.conf, parametres)
        
        if self.conf['type'] == 'corpus' :
            corpus = self.opencorpus()
        elif self.conf['corpus'] in self.parent.history.history :
            corpus = self.openanalyse()
            if self.conf.get('lem',1) :
               corpus.make_lems(True)
            else :
               corpus.make_lems(False)
            self.doopen(corpus)
        else :
            corpus = None
        self.parent.history.addtab(self.conf)
    
    def redopath(self, conf, path) :
        #if not os.path.exists(conf['ira']) :
        conf['ira'] = os.path.realpath(path)
        conf['pathout'] = os.path.dirname(os.path.realpath(path))
        DoConf(conf['ira']).makeoptions([conf['type']], [conf])
        return conf
    
    def opencorpus(self) :
        if self.conf['uuid'] not in self.parent.history.history :
            self.parent.history.add(self.conf) 
            log.info('add to history')
            self.parent.tree.OnItemAppend(self.conf)
        if self.conf['uuid'] in self.parent.history.openedcorpus :
            log.info('corpus is already opened')
        else :
            corpus = Corpus(self, parametres = self.conf, read = self.parent.history.history[self.conf['uuid']]['ira'])
            self.parent.history.openedcorpus[self.conf['uuid']] = corpus
            self.opencorpus_analyses()
            self.doopen(corpus)

    def opencorpus_analyses(self) :
        basepath = self.conf['pathout']
        for root, subfolders, files in os.walk(basepath) :
            for folder in subfolders :
                if os.path.exists(os.path.join(folder, 'Analyse.ira')) :
                    analyse_conf = DoConf(os.path.join(folder, 'Analyse.ira')).getoptions()
                    analyse_conf = self.redopath(analyse_conf, os.path.join(folder, 'Analyse.ira'))
                    if analyse_conf['corpus'] == self.conf['uuid'] :
                        self.parent.history.add(analyse_conf)
                        self.parent.tree.AddAnalyse(analyse_conf, bold = False)

            #self.parent.tree.OnItemAppend(self.conf)
    def openanalyse(self) :
        if self.conf['corpus'] in self.parent.history.openedcorpus :
            log.info('corpus is already opened')
            corpus = self.parent.history.openedcorpus[self.conf['corpus']]
        else :
            if os.path.exists(self.parent.history.history[self.conf['corpus']]['ira']) :
                corpus = Corpus(self, parametres = DoConf(self.parent.history.history[self.conf['corpus']]['ira']).getoptions('corpus'), read = self.parent.history.history[self.conf['corpus']]['ira'])
                self.parent.history.openedcorpus[self.conf['corpus']] = corpus
        return corpus

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
        elif self.conf['type'] == 'simitxt' :
            self.parent.ShowMenu(_("Text analysis"))
            SimiLayout(self.parent, corpus, self.conf)
        elif self.conf['type'] == 'wordcloud' :
            self.parent.ShowMenu(_("Text analysis"))
            WordCloudLayout(self.parent, corpus, self.conf)
            #self.tableau = Tableau(self.parent, self.conf['ira'])
            #self.DictPathOut=construct_simipath(self.conf['pathout'])
            #self.tableau.dictpathout = self.DictPathOut
            #self.tableau.read_tableau(self.tableau.dictpathout['db'])
            #if self.tableau.parametre.get('corpus', False) :
            #    self.corpus=corpus
                #self.corpus.read_corpus_from_shelves(self.DictPathOut['corpus'])
            #    self.corpus.parametres['openpath'] = self.conf['pathout']
            #DoSimi(self.parent, self.conf, isopen = True, filename = self.conf['ira'], gparent = self, openfromprof=False) 
            
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


