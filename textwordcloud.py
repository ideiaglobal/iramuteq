#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL

from analysetxt import AnalyseText
from guifunct import getPage, getCorpus, SelectColumn
from ConfigParser import RawConfigParser
from functions import sortedby, progressbar, CreateIraFile, exec_rcode, check_Rresult, MessageImage
from dialog import StatDialog, PrefWordCloud
from PrintRScript import WordCloudRScript
#from ttparser import * 
import tempfile
from time import sleep
import wx
import os
import logging

logger = logging.getLogger('iramuteq.textwordcloud')


class WordCloud(AnalyseText):
    def doanalyse(self) :
        self.parametres['type'] = 'wordcloud'
        #FIXME
        limit = 3
        self.make_option()
        if self.parametres['mode'] == 2 :
            self.actives = self.corpus.make_actives_limit(limit, 1)
            self.actives += self.corpus.make_actives_limit(limit, 2)
        elif self.parametres['mode'] == 0 :
            self.actives = self.corpus.make_actives_limit(limit, 1)
        elif self.parametres['mode'] == 1 :
            self.actives = self.corpus.make_actives_limit(limit, 2)
        dictcol = dict([[i, [act, self.corpus.getlemeff(act)]] for i, act in enumerate(self.actives)]) 
        SelectColumn(self.ira, dictcol, self.actives, self.pathout['selected.csv'], dlg = True)
        self.make_wordcloud()
        script = WordCloudRScript(self)
        script.make_script()
        self.doR(script.scriptout)
    
    def make_option(self) :
        dial = PrefWordCloud(self.ira)
        dial.CenterOnParent()
        res = dial.ShowModal()
        if res == wx.ID_OK :
            self.parametres['width'] = dial.spin_L.GetValue()
            self.parametres['height'] = dial.spin_H.GetValue()
            self.parametres['maxword'] = dial.spin_maxword.GetValue()
            self.parametres['mincex'] = float(dial.spin_mincex.GetValue())/float(10)
            self.parametres['maxcex'] = float(dial.spin_maxcex.GetValue())/float(10)
            self.parametres['col_text'] = dial.color_text.GetColour()
            self.parametres['col_bg'] = dial.color_bg.GetColour()
            self.parametres['mode'] = dial.typeformeschoice.GetSelection()
            outgraph = os.path.join(os.path.dirname(self.pathout['zipf.png']), 'nuage_')
            nb = 1
            while os.path.exists(outgraph + str(nb) + '.png') :
                nb += 1
            self.parametres['graphout'] = outgraph + str(nb) + '.png'


    def make_wordcloud(self) :
        act = ['\t'.join([act, `self.corpus.getlemeff(act)`]) for act in self.actives]
        with open(self.pathout['actives_eff.csv'], 'w') as f :
            f.write('\n'.join(act).encode(self.ira.syscoding))
       ####################################################################        
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
#                self.pathout = ConstructPathOut(self.corpus.parametre['openpath'], 'WordCloud')
#                self.dictpathout = StatTxtPathOut(self.pathout)
#                self.val = wx.ID_OK
#        else :
#            self.corpus = Corpus(parent)
#            self.corpus.parametre['encodage'] = parent.corpus_encodage
#            self.corpus.parametre['lang'] = parent.corpus_lang
#            self.corpus.parametre['filename'] = parent.filename
#            self.pathout = ConstructPathOut(self.corpus.parametre['filename'], 'WordCloud')
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
#                self.corpus.supplementaires = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "2"]
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
#        ucis_txt, ucis_paras_txt = self.corpus.start_analyse(self.parent, dlg = self.dlg, cmd = self.cmd, fromtt = False)
#        del ucis_txt
#        
#        if not self.cmd :
#            self.dlg.Update(5, '%i UCI...' % len(ucis_paras_txt))
#        self.corpus.make_ucis_paras_uces(ucis_paras_txt, make_uce = self.make_uce)
#        del ucis_paras_txt
#
#        if self.corpus.para_coords != [[] for val in self.corpus.para_coords] :
#            self.corpus.parametre['para'] = True
#        else :
#            self.corpus.parametre['para'] = False
#        self.corpus.make_etoiles(self.corpus.para_coords)
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
#        act = [[forme, formes[forme][0], formes[forme][2]] for forme in formes if formes[forme][2] in
#                self.corpus.typeactive]
#        act = sortedby(act, 2, 1)
#        act = [[val[0], `val[1]`, val[2]] for val in act]
#        with open(os.path.join(self.pathout, 'actives.csv'), 'w') as f:
#            f.write('\n'.join([';'.join(line) for line in act]))
#        #act = [[i, val] for i, val in enumerate(act)]
#        self.corpus.dictpathout = self.dictpathout
#        #self.corpus.make_type_tot()
#
#        if not self.cmd :
#            self.dlg.Destroy()
#            pref = PrefWordCloud(self.parent)
#            pref.CenterOnParent()
#            res = pref.ShowModal()
#        else :
#            res = wx.ID_OK
#        if res == wx.ID_OK :
#            self.dlg = progressbar(self, 3)
#            width = pref.spin_L.GetValue()
#            height = pref.spin_H.GetValue()
#            maxword = pref.spin_maxword.GetValue()
#            mincex = float(pref.spin_mincex.GetValue())/float(10)
#            maxcex = float(pref.spin_maxcex.GetValue())/float(10)
#            col_text = pref.color_text.GetColour()
#            col_bg = pref.color_bg.GetColour()
#            col_text = str(col_text).replace(')', ', max=255)')
#            col_bg = str(col_bg).replace(')', ', max=255)')
#            outgraph = os.path.join(os.path.dirname(self.dictpathout['zipf']), 'nuage_')
#            nb = 1
#            while os.path.exists(outgraph + str(nb) + '.png') :
#                nb += 1
#            outgraph = outgraph + str(nb) + '.png'
#
#            txt = """
#            source("%s")
#            library(wordcloud)
#            act <- read.csv2("%s", header = FALSE, row.names = 1)
#            maxword <- %i
#            maxtoprint <- ifelse(nrow(act) > maxword, maxword, nrow(act))
#            toprint <- act[1:maxtoprint,]
#            open_file_graph("%s", width = %i, height = %i)
#            par(bg=rgb%s)
#            wordcloud(row.names(toprint), toprint[,1], scale=c(%f,%f), random.order=FALSE, colors=rgb%s) 
#            dev.off()
#            """ % (self.parent.RscriptsPath['Rgraph'], ffr(os.path.join(self.pathout, 'actives.csv')), maxword, ffr(outgraph), width, height, col_bg, maxcex, mincex, col_text)
#            tmpscript = tempfile.mktemp(dir=self.parent.TEMPDIR)
#            with open(tmpscript, 'w') as f :
#                f.write(txt)
#            pid = exec_rcode(self.parent.RPath, tmpscript, wait = False)
#            while pid.poll() == None :
#                self.dlg.Pulse('R...')
#                sleep(0.2)
#            check_Rresult(self.parent, pid)
#            self.corpus.save_corpus(self.dictpathout['db'])
#            CreateIraFile(self.dictpathout, 0, corpname = os.path.basename(self.corpus.parametre['filename']), section =
#                    'wordcloud')
#            #win = MessageImage(self.parent, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
#            #win.imagename = "nuage.png"
#            #win.addsaveimage(outgraph)
#            #txt = "<img src='%s'>" % FFF(outgraph).replace('//','/')
#            #win.HtmlPage.SetPage(txt)
#            #win.Show(True)
#            if not self.cmd :
#                #OpenAnalyse(self.parent, self.dictpathout['ira'])
#                #self.DoLayout(self.parent)
#                OpenAnalyse(self.parent, self.dictpathout['ira'])
#                self.dlg.Update(7, 'fini')
#                self.dlg.Destroy()
