#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012, Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ChdTxtPathOut, StatTxtPathOut, construct_simipath, PathOut
from layout import OpenCHDS, dolexlayout, StatLayout, WordCloudLayout, OpenCorpus, SimiLayout
from corpus import Corpus, copycorpus
from tableau import Tableau
import os
import shelve
from tabsimi import DoSimi
from functions import BugReport, DoConf
from tableau import Tableau
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
        elif self.conf.get('corpus', False) in self.parent.history.corpus :
            if self.conf['uuid'] in self.parent.history.analyses :
                intree  = True
            else :
                intree = False
            corpus = self.openanalyse()
            if self.conf.get('lem',1) :
               corpus.make_lems(True)
            else :
               corpus.make_lems(False)
            if not intree :
                self.parent.tree.AddAnalyse(self.conf, bold = True)
            else :
                self.parent.tree.GiveFocus(uuid = self.conf['uuid'], bold = True)
            self.doopen(corpus)
        else :
            corpus = None
            if isinstance(parametres, dict) :
                tableau = Tableau(parent, parametres['ira'])
            else :
                tableau = Tableau(parent, parametres)
            tableau.parametres = self.conf 
            tableau.dictpathout = PathOut(filename = tableau.parametres['filename'], dirout = self.conf['pathout'], analyse_type = self.conf['type'])
            tableau.dictpathout.basefiles(ChdTxtPathOut)
            tableau.read_tableau(tableau.dictpathout['db'])
            if self.parent.tree.IsInTree(uuid = self.conf['uuid']) :
                self.parent.tree.GiveFocus(uuid = self.conf['uuid'], bold = True)
            else :
                self.parent.tree.AddAnalyse(self.conf, bold = True)
            self.doopen(tableau)
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
            log.info('corpus is already opened 1')
            self.doopen(self.parent.history.openedcorpus[self.conf['uuid']])
        else :
            corpus = Corpus(self, parametres = self.conf, read = self.parent.history.history[self.parent.history.ordercorpus[self.conf['uuid']]]['ira'])
            self.parent.history.openedcorpus[self.conf['uuid']] = corpus
            self.opencorpus_analyses()
            self.doopen(corpus)

    def opencorpus_analyses(self) :
        log.info('open analysis')
        basepath = self.conf['pathout']
        analyses = []
        for root, subfolders, files in os.walk(basepath) :
            for folder in subfolders :
                if os.path.exists(os.path.join(folder, 'Analyse.ira')) :
                    analyse_conf = DoConf(os.path.join(folder, 'Analyse.ira')).getoptions()
                    analyse_conf = self.redopath(analyse_conf, os.path.join(folder, 'Analyse.ira'))
                    if analyse_conf['corpus'] == self.conf['uuid'] :
                        analyses.append(analyse_conf)
        if len(analyses) :
            self.parent.history.addmultiple(analyses)
        for analyse in analyses :
            self.parent.tree.AddAnalyse(analyse, bold = False)

    def openanalyse(self) :
        if self.conf['corpus'] in self.parent.history.openedcorpus :
            log.info('corpus is already opened 2')
            corpus = copycorpus(self.parent.history.openedcorpus[self.conf['corpus']])
        else :
            if os.path.exists(self.parent.history.history[self.parent.history.ordercorpus[self.conf['corpus']]]['ira']) :
                corpus = Corpus(self, parametres = DoConf(self.parent.history.history[self.parent.history.ordercorpus[self.conf['corpus']]]['ira']).getoptions('corpus'), read = self.parent.history.history[self.parent.history.ordercorpus[self.conf['corpus']]]['ira'])
                self.parent.history.openedcorpus[self.conf['corpus']] = corpus
        self.parent.history.add(self.conf)
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
        elif self.conf['type'] == 'gnepamatrix' :
            self.parent.ShowMenu(_("Spreadsheet analysis"))
            OpenCHDS(self.parent,  corpus, self.conf, Alceste = False)
        
