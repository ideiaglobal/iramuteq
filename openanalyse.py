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
#from ConfigParser import *
#from tabsimi import DoSimi
from functions import BugReport, DoConf
import logging

log = logging.getLogger('iramuteq.openanalyse')

class OpenAnalyse():
    def __init__(self, parent, parametres, Alceste=True, simifromprof = False):
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
        elif self.conf['corpus'] in self.parent.history.corpus :
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
        conf['ira'] = os.path.realpath(path)
        conf['pathout'] = os.path.dirname(os.path.realpath(path))
        DoConf(conf['ira']).makeoptions([conf['type']], [conf])
        return conf
    
    def opencorpus(self) :
        log.info('open corpus')
        if self.conf['uuid'] not in self.parent.history.corpus :
            self.parent.history.add(self.conf) 
            log.info('add to history')
            self.parent.tree.OnItemAppend(self.conf)
        if self.conf['uuid'] in self.parent.history.openedcorpus :
            log.info('corpus is already opened')
            self.doopen(self.parent.history.openedcorpus[self.conf['uuid']])
        else :
            corpus = Corpus(self, parametres = self.conf, read = self.parent.history.history[self.parent.history.ordercorpus[self.conf['uuid']]]['ira'])
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

    def openanalyse(self) :
        if self.conf['corpus'] in self.parent.history.openedcorpus :
            log.info('corpus is already opened')
            corpus = self.parent.history.openedcorpus[self.conf['corpus']]
        else :
            if os.path.exists(self.parent.history.history[self.parent.history.ordercorpus[self.conf['corpus']]]['ira']) :
                corpus = Corpus(self, parametres = DoConf(self.parent.history.history[self.parent.history.ordercorpus[self.conf['corpus']]]['ira']).getoptions('corpus'), read = self.parent.history.history[self.parent.history.ordercorpus[self.conf['corpus']]]['ira'])
                self.parent.history.openedcorpus[self.conf['corpus']] = corpus
        return corpus

    def doopen(self, corpus) :
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
        elif self.conf['type'] == 'simitxt' or self.conf['type'] == 'clustersimitxt' :
            self.parent.ShowMenu(_("Text analysis"))
            SimiLayout(self.parent, corpus, self.conf)
        elif self.conf['type'] == 'wordcloud' :
            self.parent.ShowMenu(_("Text analysis"))
            WordCloudLayout(self.parent, corpus, self.conf)
