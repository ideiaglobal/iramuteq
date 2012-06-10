#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL

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

print 'TEST LOGGING'
import logging

logger = logging.getLogger('iramuteq.textstat')



class Stat(AnalyseText) :
    def doanalyse(self) :
        self.make_stats()

    def preferences(self) :
        dial = StatDialog(self, self.parent)
        dial.CenterOnParent()
        val = dial.ShowModal()
        if val == 5100 :
            if dial.radio_lem.GetSelection() == 0 :
                lem = 1
            else :
                lem = 0            
            self.parametres['lem'] = lem
            dial.Destroy()
            return self.parametres
        else :
            dial.Destroy()
            return None

    def make_stats(self):
        if self.dlg :
            if not 'dlg' in dir(self) :
                self.dlg = progressbar(self, 7)
        #if not self.lem :
        #    formes = self.corpus.formes
        #else :
        #    self.corpus.make_lems()
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
        #self.corpus.pathout = self.dictpathout
        #self.corpus.make_type_tot()

        self.result = {u'total' : dict(tot), u'formes_actives' : dict(act), u'formes_supplémentaires' : dict(supp), u'hapax' : dict(hapax), u'glob' : ''}
        occurrences = sum([val[1][1] for val in tot]) + len(hapax)
        phapax = (float(len(hapax)) / float(occurrences)) * 100
        phapax_forme = (float(len(hapax)) / (float(len(formes)))) * 100
        moy_occu_mot = float(occurrences) / float(len(formes))
        txt = 'Globale\n'
        txt += 'nombre d\'uci : %i\n' % len(self.corpus.ucis)
        txt += 'nombre d\'occurrences : %i\n' % occurrences
        txt += 'nombre de formes : %i\n' % (len(formes))
        txt += 'moyenne d\'occurrences par forme : %.2f\n' % moy_occu_mot
        txt += 'nombre d\'hapax : %i (%.2f%% des occurrences - %.2f%% des formes)\n' % (len(hapax), phapax, phapax_forme)
        print float(occurrences), float(len(self.corpus.ucis))
        txt += 'moyenne d\'occurrences par uci : %.2f' % (float(occurrences)/float(len(self.corpus.ucis)))
        if self.dlg :
             self.dlg.Update(7, u'Ecriture...')
        self.result['glob'] = txt
        self.print_result()
        # for Zipf grap
        txt = """
        source("%s")
        tot <- read.csv2("%s", header = FALSE, row.names = 1)
        hapax <- read.csv2("%s", header = FALSE, row.names = 1)
        tot <- rbind(tot, hapax)
        open_file_graph("%s", width = 400, height = 400)
        plot(log(tot[,1]), log = 'x', xlab='log(rangs)', ylab = 'log(frequences)', col = 'red', pch=16)
        dev.off()
        """ % (self.parent.RscriptsPath['Rgraph'], self.pathout['total.csv'], self.pathout['hapax.csv'], self.pathout['zipf.png'])
        tmpscript = tempfile.mktemp(dir=self.parent.TEMPDIR)
        with open(tmpscript, 'w') as f :
            f.write(txt)
        pid = exec_rcode(self.parent.RPath, tmpscript, wait = False)
        while pid.poll() == None :
            sleep(0.2)
        check_Rresult(self.parent, pid)
        #CreateIraFile(self.dictpathout, 0, corpname = os.path.basename(self.corpus.parametre['filename']), section = 'stat')
        if self.dlg :
            #OpenAnalyse(self.parent, self.pathout['Analyse.ira'])
            #self.DoLayout(self.parent)
            self.dlg.Destroy()

    def print_result(self) :
        for key in self.result :
            if key != 'glob' :
                dico = self.result[key]
                toprint = [[dico[val][0],`dico[val][1]`, dico[val][2]] for val in dico]
                #toprint = [[line[0], `line[1]`] for line in self.result[key]]
                with open(self.pathout['%s.csv' % key], 'w') as f :
                    f.write('\n'.join([';'.join([val for val in ligne]) for ligne in toprint]).encode(self.parent.syscoding))
            else :
                with open(self.pathout['%s.txt' % 'glob'], 'w') as f :
                    f.write(self.result['glob'].encode(self.parent.syscoding))
            self.parametres['pathout'] = self.pathout['Analyse.ira']
            DoConf().makeoptions(['stat'],[self.parametres], self.pathout['Analyse.ira'])


#class Stat():
#    def __init__(self, parent, corpus, cmd = False, lem = True, exp = True):
#####################################################################   
#        logger.info('start text stat')
#        self.conf = None
#        self.parent = parent
#        self.type = 'alceste'
#        self.cmd = cmd
#        self.ConfigPath = parent.ConfigPath
#        self.DictPath = parent.DictPath
#        self.KeyConf = RawConfigParser()
#        self.KeyConf.read(self.ConfigPath['key'])
#        page = getPage(self.parent)
#        if page is not None :
#            self.corpus = getCorpus(page)
#            if self.corpus is not None :
#                self.pathout = ConstructPathOut(self.corpus.parametre['openpath'], 'Stat')
#                self.dictpathout = StatTxtPathOut(self.pathout)
#                self.val = wx.ID_OK
#        else :
#            self.corpus = Corpus(parent)
#            self.corpus.parametre['encodage'] = parent.corpus_encodage
#            self.corpus.parametre['lang'] = parent.corpus_lang
#            self.corpus.parametre['filename'] = parent.filename
#            self.pathout = ConstructPathOut(self.corpus.parametre['filename'], 'Stat')
#            self.dictpathout = StatTxtPathOut(self.pathout)
#            self.corpus.dictpathout = self.dictpathout
#            if not self.cmd :
#                dial = StatDialog(self,parent)
#                dial.CenterOnParent()
#                self.val = dial.ShowModal()
#            else :
#                self.val = wx.ID_OK
#            if self.val == wx.ID_OK :
#                if not self.cmd :
#                    if dial.radio_lem.GetSelection() == 0 : lem = True
#                    else : lem = False
#                    if dial.exp.GetSelection() == 0 : exp = True
#                    else : exp = False
#                    self.make_uce = dial.check_uce.GetValue()
#                    self.corpus.parametre['nbforme_uce'] = dial.spin_ctrl_4.GetValue()
#                    self.corpus.parametre['max_actives'] = dial.spin_max_actives.GetValue()
#                    self.corpus.parametre['eff_min_uce'] = self.corpus.parametre['nbforme_uce']
#                else :
#                    lem = True
#                    exp = True
#                    self.make_uce = False
#                    self.corpus.parametre['nbforme_uce'] = None
#                    self.corpus.parametre['eff_min_uce'] = None
#                self.corpus.parametre['lem'] = lem
#                self.corpus.parametre['expressions'] = exp
#                self.corpus.supplementaires = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "2"]
#                self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
#                self.make_corpus()
#
#        if self.val == wx.ID_OK :
#            if 'supplementaires' not in dir(self.corpus) :
#                print 'supplementaire'
#                self.corpus.supplementaires = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "2"]
#                print self.corpus.supplementaires
#            else :
#                print 'corpus supplementaires'
#                print self.corpus.supplementaires
#            if 'typeactive' not in dir(self.corpus) :
#                self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
#            self.make_stats()
#
#    def make_corpus(self) :
#        if not self.cmd :
#            self.dlg = progressbar(self, 7)
#        else :
#            self.dlg = None
#        self.corpus.content = self.parent.content
#        #print 'ATTENTION : FROM TT'
#        #prepare_for_treetagger(self.corpus, self.parent)
#        #get_ucis_from_tt(self.corpus)
#        #qsdfqsdf
#        ucis_txt, ucis_paras_txt = self.corpus.start_analyse(self.parent, dlg = self.dlg, cmd = self.cmd, fromtt = False)
#        #self.corpus.make_et_table()
#        #self.corpus.make_len_uce(self.corpus.get_tot_occ_from_ucis_txt(ucis_txt))
##        print 'ATTTTTENTION CHECK_DOUBLON'
##        self.corpus.check_double(ucis_txt)
#        del ucis_txt
#        
#        if not self.cmd :
#            self.dlg.Update(5, '%i UCI...' % len(ucis_paras_txt))
#        self.corpus.make_ucis_paras_uces(ucis_paras_txt, make_uce = self.make_uce)
#        del ucis_paras_txt
#
##        print 'ATTENTION EFF PAR UCI'
##        effuci = [[`i`, `len(uce)`] for i, uci in enumerate(self.corpus.ucis_paras_uces) for para in uci for uce in para]
##        with open('/home/pierre/fac/identite/taille_uci.csv', 'w') as f :
##            f.write('\n'.join([';'.join(val) for val in effuci]))
##        print effuci[0:30]
##        print max(effuci), min(effuci), float(sum(effuci))/float(len(effuci))
##        qsdfqsdfqsd
#
#
#        if self.corpus.para_coords != [[] for val in self.corpus.para_coords] :
#            self.corpus.parametre['para'] = True
#        else :
#            self.corpus.parametre['para'] = False
#        self.corpus.make_etoiles(self.corpus.para_coords)
#
#        print 'len(ucis_paras_uces', len(self.corpus.ucis_paras_uces)
#        
#        if not self.cmd :
#            self.dlg.Update(6, u'Dictionnaires')
#        uces, orderuces = self.corpus.make_forms_and_uces()
#        self.corpus.make_lems(self.parent.lexique)
#
#    def make_stats(self):
#        if not self.cmd :
#            if not 'dlg' in dir(self) :
#                self.dlg = progressbar(self, 7)
#        if not self.corpus.parametre['lem'] :
#            formes = self.corpus.formes
#        else :
#            formes = self.corpus.make_lem_eff()
#        tot = [[forme, formes[forme][0], formes[forme][2]] for forme in formes if formes[forme][0] > 1]
#        tot = sortedby(tot, 2,1)
#        tot = [[i, val] for i, val in enumerate(tot)]
#        hapax = [[forme, formes[forme][0], formes[forme][2]] for forme in formes if formes[forme][0] == 1]
#        hapax = sortedby(hapax, 1, 1)
#        hapax = [[i, val] for i, val in enumerate(hapax)]
#        act = [[forme, formes[forme][0], formes[forme][2]] for forme in formes if formes[forme][2] in self.corpus.typeactive]
#        act = sortedby(act, 2, 1)
#        act = [[i, val] for i, val in enumerate(act)]
#        supp = [[forme, formes[forme][0], formes[forme][2]] for forme in formes if formes[forme][2] in self.corpus.supplementaires]
#        supp = sortedby(supp, 2, 1)
#        supp = [[i, val] for i, val in enumerate(supp)]
#        self.corpus.dictpathout = self.dictpathout
#        #self.corpus.make_type_tot()
#
#        self.result = {u'total' : dict(tot), u'formes_actives' : dict(act), u'formes_supplémentaires' : dict(supp), u'hapax' : dict(hapax), u'glob' : ''}
#        occurrences = sum([val[1][1] for val in tot]) + len(hapax)
#        phapax = (float(len(hapax)) / float(occurrences)) * 100
#        phapax_forme = (float(len(hapax)) / (float(len(formes)) + len(hapax))) * 100
#        moy_occu_mot = float(occurrences) / float(len(formes))
#        txt = 'Globale\n'
#        txt += 'nombre d\'uci : %i\n' % len(self.corpus.ucis)
#        txt += 'nombre d\'occurrences : %i\n' % occurrences
#        txt += 'nombre de formes : %i\n' % (len(formes) + len(hapax))
#        txt += 'moyenne d\'occurrences par forme : %.2f\n' % moy_occu_mot
#        txt += 'nombre d\'hapax : %i (%.2f%% des occurrences - %.2f%% des formes)\n' % (len(hapax), phapax, phapax_forme)
#        print float(occurrences), float(len(self.corpus.ucis))
#        txt += 'moyenne d\'occurrences par uci : %.2f' % (float(occurrences)/float(len(self.corpus.ucis)))
#        if not self.cmd :
#             self.dlg.Update(7, u'Ecriture...')
#        self.result['glob'] = txt
#        self.print_result()
#        # for Zipf grap
#        txt = """
#        source("%s")
#        tot <- read.csv2("%s", header = FALSE, row.names = 1)
#        hapax <- read.csv2("%s", header = FALSE, row.names = 1)
#        tot <- rbind(tot, hapax)
#        open_file_graph("%s", width = 400, height = 400)
#        plot(log(tot[,1]), log = 'x', xlab='log(rangs)', ylab = 'log(frequences)', col = 'red', pch=16)
#        dev.off()
#        """ % (self.parent.RscriptsPath['Rgraph'], ffr(os.path.join(self.pathout, 'total.csv')), ffr(os.path.join(self.pathout, 'hapax.csv')), self.dictpathout['zipf'])
#        tmpscript = tempfile.mktemp(dir=self.parent.TEMPDIR)
#        with open(tmpscript, 'w') as f :
#            f.write(txt)
#        pid = exec_rcode(self.parent.RPath, tmpscript, wait = False)
#        while pid.poll() == None :
#            sleep(0.2)
#        check_Rresult(self.parent, pid)
#        self.corpus.save_corpus(self.dictpathout['db'])
#        CreateIraFile(self.dictpathout, 0, corpname = os.path.basename(self.corpus.parametre['filename']), section = 'stat')
#        if not self.cmd :
#            OpenAnalyse(self.parent, self.dictpathout['ira'])
#            #self.DoLayout(self.parent)
#            self.dlg.Destroy()
#
#    def print_result(self) :
#        for key in self.result :
#            if key != 'glob' :
#                dico = self.result[key]
#                toprint = [[dico[val][0],`dico[val][1]`, dico[val][2]] for val in dico]
#                #toprint = [[line[0], `line[1]`] for line in self.result[key]]
#                output = open(os.path.join(self.pathout,'%s.csv' % key), 'w')
#                output.write('\n'.join([';'.join([val for val in ligne]) for ligne in toprint]))
#                output.close()
#            else :
#                output = open(os.path.join(self.pathout,'%s.txt' % 'glob'), 'w')
#                output.write(self.result['glob'])
#                output.close()
