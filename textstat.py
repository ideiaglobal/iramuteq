#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012 Pierre Ratinaud
#License: GNU/GPL

#from chemins import ConstructPathOut, StatTxtPathOut, ffr
from chemins import PathOut
from analysetxt import AnalyseText
#from corpus import Corpus
from guifunct import getPage, getCorpus
from ConfigParser import RawConfigParser
from functions import sortedby, progressbar, CreateIraFile, exec_rcode, check_Rresult, DoConf
from dialog import StatDialog
from openanalyse import OpenAnalyse
#from ttparser import * 
import tempfile
from time import sleep
import wx
import os

import logging

logger = logging.getLogger('iramuteq.textstat')



class Stat(AnalyseText) :
    def doanalyse(self) :
        self.make_stats()

    def preferences(self) :
        return self.parametres

    def make_stats(self):
        if self.dlg :
            if not 'dlg' in dir(self) :
                self.dlg = progressbar(self, 7)

        formes = self.corpus.lems
        tot = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].freq > 1]
        tot = sortedby(tot, 2,1)
        tot = [[i, val] for i, val in enumerate(tot)]
        hapax = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].freq == 1]
        hapax = sortedby(hapax, 1, 1)
        hapax = [[i, val] for i, val in enumerate(hapax)]
        act = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].act == 1]
        act = sortedby(act, 2, 1)
        act = [[i, val] for i, val in enumerate(act)]
        supp = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].act == 2]        
        supp = sortedby(supp, 2, 1)

        supp = [[i, val] for i, val in enumerate(supp)]

        self.result = {u'total' : dict(tot), u'formes_actives' : dict(act), u'formes_supplémentaires' : dict(supp), u'hapax' : dict(hapax), u'glob' : ''}
        occurrences = sum([val[1][1] for val in tot]) + len(hapax)
        phapax = (float(len(hapax)) / float(occurrences)) * 100
        phapax_forme = (float(len(hapax)) / (float(len(formes)))) * 100
        moy_occu_mot = float(occurrences) / float(len(formes))
        txt = 'Globale\n'
        txt += 'nombre de textes : %i\n' % len(self.corpus.ucis)
        txt += 'nombre d\'occurrences : %i\n' % occurrences
        txt += 'nombre de formes : %i\n' % (len(formes))
        txt += 'moyenne d\'occurrences par forme : %.2f\n' % moy_occu_mot
        txt += 'nombre d\'hapax : %i (%.2f%% des occurrences - %.2f%% des formes)\n' % (len(hapax), phapax, phapax_forme)
        print float(occurrences), float(len(self.corpus.ucis))
        txt += 'moyenne d\'occurrences par texte : %.2f' % (float(occurrences)/float(len(self.corpus.ucis)))
        if self.dlg :
            self.dlg.Update(7, u'Ecriture...')
        self.result['glob'] = txt
        self.print_result()
        # for Zipf grap
        txt = """
        source("%s")
        tot <- read.csv2("%s", header = FALSE, row.names = 1)
        """ % (self.parent.RscriptsPath['Rgraph'], self.pathout['total.csv'])
        if len(hapax) :
            txt += """
            hapax <- read.csv2("%s", header = FALSE, row.names = 1)
            tot <- rbind(tot, hapax)
            """ % self.pathout['hapax.csv']
        txt += """
        open_file_graph("%s", width = 400, height = 400)
        plot(tot[,1], log = 'xy', xlab='log(rangs)', ylab = 'log(frequences)', col = 'red', pch=16)
        dev.off()
        """ % (self.pathout['zipf.png'])
        tmpscript = tempfile.mktemp(dir=self.parent.TEMPDIR)
        with open(tmpscript, 'w') as f :
            f.write(txt)
        pid = exec_rcode(self.parent.RPath, tmpscript, wait = False)
        while pid.poll() == None :
            sleep(0.2)
        check_Rresult(self.parent, pid)
        if self.dlg :
            self.dlg.Destroy()

    def print_result(self) :
        for key in self.result :
            if key != 'glob' :
                dico = self.result[key]
                toprint = [[dico[val][0],`dico[val][1]`, dico[val][2]] for val in dico]
                with open(self.pathout['%s.csv' % key], 'w') as f :
                    f.write('\n'.join([';'.join([val for val in ligne]) for ligne in toprint]).encode(self.parent.syscoding))
            else :
                with open(self.pathout['%s.txt' % 'glob'], 'w') as f :
                    f.write(self.result['glob'].encode(self.parent.syscoding))
