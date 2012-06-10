# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2011 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, construct_simipath
from corpus import Corpus
import os
from ConfigParser import RawConfigParser
from guifunct import getPage, getCorpus
from dialog import StatDialog
from functions import indices_simi, progressbar, treat_var_mod
from tableau import Tableau
from tabsimi import DoSimi
import wx
from copy import copy

class SimiTxt :
    def __init__(self, parent, cmd = False, param = None):
        self.parent = parent
        self.cmd = cmd
        self.ConfigPath = parent.ConfigPath
        self.DictPath = parent.DictPath
        self.KeyConf = RawConfigParser()
        self.KeyConf.read(self.ConfigPath['key'])
        self.indices = indices_simi
        self.paramsimi = {'coeff' : 0,
                          'layout' : 2,
                          'type' : 1,
                          'arbremax' : 1,
                          'coeff_tv' : 1,
                          'coeff_tv_nb' : 0,
                          'tvprop' : 0,
                          'tvmin' : 5,
                          'tvmax' : 30,
                          'coeff_te' : 1,
                          'coeff_temin' : 1,
                          'coeff_temax' : 10,
                          'label_v': 1,
                          'label_e': 0,
                          'vcex' : 1,
                          'cexfromchi' : False,
                          'vcexmin' : 10,
                          'vcexmax' : 25,
                          'cex' : 10,
                          'seuil_ok' : 0,
                          'seuil' : 1,
                          'cols' : (255,0,0),
                          'cola' : (200,200,200),
                          'width' : 1000,
                          'height' : 1000,
                          'bystar' : False,
                          'first' : True,
                          'keep_coord' : True,
                          'alpha' : 20,
                          'film': False,
                          }
        page = getPage(self.parent)
        if page is not None :
            self.corpus = getCorpus(page)
            if self.corpus is not None :
                self.pathout = ConstructPathOut(self.corpus.parametre['openpath'], 'simitxt')
                self.dictpathout = construct_simipath(self.pathout)
                self.val = wx.ID_OK
                self.make_table()
                self.make_simi()
        else :
            self.corpus = Corpus(parent)
            self.corpus.content = self.parent.content
            self.corpus.parametre['encodage'] = parent.corpus_encodage
            self.corpus.parametre['lang'] = parent.corpus_lang
            self.corpus.parametre['filename'] = parent.filename
            self.corpus.parametre['eff_min_uce'] = None
            self.pathout = ConstructPathOut(self.corpus.parametre['filename'], 'simitxt')
            self.dictpathout = construct_simipath(self.pathout)
            dial = StatDialog(self, self.parent)
            dial.check_uce.SetValue(True)
            dial.check_uce.Enable(False)
            dial.OnCheckUce(wx.EVT_MENU)
            self.val = dial.ShowModal()
            if self.val == wx.ID_OK :
                with open(self.parent.ConfigPath['key'], 'w') as f:
                    self.KeyConf.write(f)
                if dial.radio_lem.GetSelection() == 0 : lem = True
                else : lem = False
                if dial.exp.GetSelection() == 0 : exp = True
                else : exp = False
                dial.Destroy()
                self.corpus.parametre['lem'] = lem
                self.corpus.parametre['expressions'] = exp
                self.corpus.parametre['nbforme_uce'] = dial.spin_ctrl_4.GetValue()
                self.corpus.parametre['eff_min_forme'] = dial.spin_ctrl_5.GetValue()
                self.corpus.parametre['max_actives'] = dial.spin_max_actives.GetValue()
                self.make_corpus()
                self.make_table()
                self.make_simi()
            else :
                dial.Destroy()

    def make_corpus(self) :
        print 'make corpus'
        if not self.cmd :
            dlg = progressbar(self, maxi = 6)
        self.corpus.supplementaires = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "2"]
        self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
        ucis_txt, ucis_paras_txt = self.corpus.start_analyse(self.parent, dlg = dlg, cmd = self.cmd)
        del ucis_txt
    
        if not self.cmd :
            dlg.Update(5, '%i ucis - Construction des uces' % len(ucis_paras_txt))
        self.corpus.make_ucis_paras_uces(ucis_paras_txt, make_uce = True)
        del ucis_paras_txt

        if self.corpus.para_coords != [[] for val in self.corpus.para_coords] :
            self.corpus.parametre['para'] = True
        else :
            self.corpus.parametre['para'] = False
        self.corpus.make_etoiles(self.corpus.para_coords)
        print 'len(ucis_paras_uces)', len(self.corpus.ucis_paras_uces)

        if not self.cmd :
            dlg.Update(6, u'Dictionnaires')
        uces, self.orderuces = self.corpus.make_forms_and_uces()
        self.corpus.ucenb = len(uces)
        self.corpus.make_lems(self.parent.lexique)

        self.corpus.make_var_actives() 
        self.corpus.make_var_supp()
        self.corpus.lems_eff = self.corpus.make_lem_eff()

        #variables = treat_var_mod(listet)
        #print(variables)
        #self.corpus.write_etoiles(self.dictpathout['etoiles'])
        if not self.cmd :
            dlg.Destroy()
                
    def make_table(self) :
        if 'orderuces' not in dir(self) :
            self.orderuces = [(i,j,k) for i, uci in enumerate(self.corpus.ucis_paras_uces) for j, para in enumerate(uci) for k, uce in enumerate(para)]
            self.orderuces = dict([[val, i] for i, val in enumerate(self.orderuces)])
            self.corpus.ucenb = len(self.orderuces)
        #tabuc1 = self.corpus.make_table_with_uce(self.orderuces)
        #tabuc1.insert(0,self.corpus.actives)
        #tabuc1 = self.corpus.make_sparse_matrix_with_uce(self.orderuces)
        #self.corpus.write_sparse_matrix(self.dictpathout['mat01'], tabuc1, self.corpus.ucenb, len(self.corpus.actives))
        if self.corpus.actives is None :
            self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
            self.corpus.min_eff_formes()
            self.corpus.make_var_actives()
        self.corpus.make_and_write_sparse_matrix_from_uce(self.orderuces, self.dictpathout['mat01'])
        #self.corpus.write_tab(tabuc1,self.dictpathout['mat01'])

    def make_simi(self) :
        self.tableau = Tableau(self.parent, '')
        self.tableau.listactives = self.corpus.actives
        self.tableau.parametre['fromtxt'] = True
        if 'lems_eff' not in dir(self.corpus) :
            self.corpus.lems_eff = self.corpus.make_lem_eff()
        #print('ATTENTION  ETOILES')
        #self.paramsimi['bystar'] = True
        self.listet = self.corpus.get_unique_etoiles()
        self.listet.sort()
        self.tableau.listet = copy(self.listet)
        self.paramsimi['stars'] = copy(self.listet)
        #self.paramsimi['cexfromchi'] = True
        self.paramsimi['sfromchi'] = False
        #self.paramsimi['vlabcolor'] = True
        self.tableau.actives = dict([[lem, self.corpus.lems_eff[lem]] for lem in self.corpus.actives])
        self.corpus.save_corpus(self.dictpathout['corpus']) 
        DoSimi(self, fromprof = self.dictpathout['mat01'], param = self.paramsimi, pathout = self.pathout)
