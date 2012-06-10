#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, ChdTxtPathOut
from OptionAlceste import OptionAlc
import wx
import os
from ConfigParser import RawConfigParser
import sys
from functions import sortedby, print_liste, CreateIraFile, exec_rcode, ReadDicoAsDico, check_Rresult
from dialog import PrefGraph
from layout import OpenCHDS, PrintRapport
from PrintRScript import RchdTxt, AlcesteTxtProf
from openanalyse import OpenAnalyse
from corpus import Corpus
from guifunct import getPage, getCorpus
from time import time, sleep

class AnalyseAlceste :
    def __init__(self,parent, cmd = False, big = False):
        self.conf = None
        self.parent = parent
        self.type = 'alceste'
        self.cmd = cmd
        self.big = big
        #page = getPage(self.parent)
        #if page is not None :
        #    self.corpus = getCorpus(page)
        #    print self.corpus.parametre
        #else :
        try :
            self.corpus = Corpus(parent)
            self.corpus.parametre['encodage'] = parent.corpus_encodage
            self.corpus.parametre['lang'] = parent.corpus_lang
            self.corpus.parametre['filename'] = parent.filename
            self.ConfigPath = parent.ConfigPath
            self.DictPath = parent.DictPath
            self.AlcesteConf = RawConfigParser()
            self.AlcesteConf.read(self.ConfigPath['alceste'])
            self.KeyConf = RawConfigParser()
            self.KeyConf.read(self.ConfigPath['key'])
            if not cmd :
                self.dial = OptionAlc(self, parent)
                self.dial.CenterOnParent()
                self.val = self.dial.ShowModal()
                self.print_alceste_parametre()
                self.dial.Destroy()
            else :
                self.val = wx.ID_OK
            if self.val == wx.ID_OK :
                pathout = ConstructPathOut(self.corpus.parametre['filename'], 'alceste')
                self.dictpathout = ChdTxtPathOut(pathout)
                self.read_alceste_parametre()
                self.KeyConf.read(self.ConfigPath['key'])
                self.corpus.supplementaires = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "2"]
                self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
                self.make_analyse()
        except AttributeError :
            wx.MessageBox(u'Vous devez charger un corpus\nFichier -> Ouvrir un texte', u'Pas de corpus', wx.OK|wx.ICON_INFORMATION)
            self.val = False

    def load_corpus(self):
        self.corpus.read_formes()
        self.corpus.read_lems()
        self.corpus.read_ucis_paras_uces()
        self.corpus.read_parametre()

    def print_alceste_parametre(self): 
        self.conf = RawConfigParser()
        self.conf.read(self.parent.ConfigPath['alceste'])
        lem = self.dial.radio_1.GetSelection()
        expressions = self.dial.radio_exp.GetSelection()
        if lem == 0 : lem = 'True'
        else : lem = 'False'
        if expressions == 0 : expressions = 'True'
        else : expressions = 'False'
        self.AlcesteConf.set('ALCESTE','lem',lem)
        self.AlcesteConf.set('ALCESTE', 'expressions', expressions)
        self.AlcesteConf.set('ALCESTE', 'classif_mode', str(self.dial.radio_box_2.GetSelection()))
        self.AlcesteConf.set('ALCESTE', 'tailleuc1', str(self.dial.spin_ctrl_1.GetValue()))
        self.AlcesteConf.set('ALCESTE', 'tailleuc2', str(self.dial.spin_ctrl_2.GetValue()))
        self.AlcesteConf.set('ALCESTE', 'nbforme_uce', str(self.dial.spin_ctrl_3.GetValue()))
        self.AlcesteConf.set('ALCESTE', 'mincl', str(self.dial.spin_ctrl_4.GetValue()))
        self.AlcesteConf.set('ALCESTE', 'minforme', str(self.dial.spin_ctrl_5.GetValue()))
        self.AlcesteConf.set('ALCESTE', 'nbcl_p1', str(self.dial.spin_nbcl.GetValue()))
        self.AlcesteConf.set('ALCESTE', 'max_actives', str(self.dial.spin_max_actives.GetValue()))
        with open(self.parent.ConfigPath['alceste'], 'w') as f:
            self.AlcesteConf.write(f)
        with open(self.parent.ConfigPath['key'], 'w') as f:
            self.KeyConf.write(f)
    
    def read_alceste_parametre(self) :
        self.conf = RawConfigParser()
        self.conf.read(self.parent.ConfigPath['alceste'])
        for option in self.conf.options('ALCESTE') :
            if self.conf.get('ALCESTE', option).isdigit() :
                self.corpus.parametre[option] = int(self.conf.get('ALCESTE', option))
            else :
                self.corpus.parametre[option] = self.conf.get('ALCESTE', option)
            
        list_bool = ['lem', 'expressions']
        for var in list_bool :
            if self.corpus.parametre[var] == 'True' :
                self.corpus.parametre[var] = True
            else : 
                self.corpus.parametre[var] = False

    def make_analyse(self) :
        t1 = time()
        if not self.big :
            self.corpus.content = self.parent.content
            if not self.cmd :
                self.dlg = wx.ProgressDialog("Traitements",
                                             "Veuillez patienter...",
                                             maximum=9,
                                             parent=self.parent,
                                             style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT
                                             )
                self.dlg.Center()
            else :
                self.dlg = None
            ucis_txt, ucis_paras_txt = self.corpus.start_analyse(self.parent, dlg = self.dlg, cmd = self.cmd) 
    #        #print('ATTENTION PHRASE')
    #        #ucis_paras_txt = self.corpus.make_ucis_paras_txt_phrases(para_coords, ucis_lines, ucis_txt)
    #        del ucis_lines
    
            #FIXME
            self.corpus.make_len_uce(self.corpus.get_tot_occ_from_ucis_txt(ucis_txt))
            del ucis_txt
            
            if not self.cmd :
                self.dlg.Update(5, '%i ucis - Construction des uces' % len(self.corpus.ucis))
    
            if self.corpus.parametre['classif_mode'] in [0,1] :
                self.corpus.make_ucis_paras_uces(ucis_paras_txt, make_uce = True)
                #self.corpus.make_ucis_paras_uces_sentences(ucis_paras_txt, make_uce = True)
            else :
                self.corpus.make_ucis_paras_uces(ucis_paras_txt, make_uce = False)
            del ucis_paras_txt
    
            print 'len(ucis_paras_uces', len(self.corpus.ucis_paras_uces)
            
            if not self.cmd :
                self.dlg.Update(6, u'Dictionnaires')
            uces, orderuces = self.corpus.make_forms_and_uces()
    
            print len(uces)
            print len(orderuces)
            self.corpus.ucenb = len(uces)
            print 'len(uces)',len(uces)
            #ucis_paras_uces_lems = self.corpus.make_ucis_paras_uces_lems(lexique)
            self.corpus.make_lems(self.parent.lexique)
            
            #----------------------------------------------
            #self.corpus.make_eff_min_forme()
            #self.corpus.parametre['max_actives'] = 1500
            self.corpus.min_eff_formes()
            #----------------------------------------------
    
            self.corpus.make_var_actives() 
    
            self.corpus.make_var_supp()
            
            if not self.cmd :
                self.dlg.Update(7, u'Creation des tableaux')
            if self.corpus.parametre['classif_mode'] == 1 :
                #tabuc1 = self.corpus.make_sparse_matrix_with_uce(orderuces)
                #self.corpus.write_sparse_matrix(self.dictpathout['TableUc1'], tabuc1, len(orderuces), len(self.corpus.actives))
                #print time() - tps1
                #tps2 = time()
                self.corpus.make_and_write_sparse_matrix_from_uce(orderuces, self.dictpathout['TableUc1'])
                #print time() - tps2
    
                #tabuc1 = self.corpus.make_table_with_uce(orderuces)
                uc1 = None
                uces1 = [[uce, orderuces[uce]] for uce in orderuces]
                uces1 = sortedby(uces1, 1)
                self.corpus.lenuc1 = len(uces1)
                #uces1.sort()
                self.corpus.write_tab([[u'uce',u'uc']] + [[i, i] for i in range(0,len(uces))], self.dictpathout['listeuce1'])
            elif  self.corpus.parametre['classif_mode'] == 0 :
                self.corpus.lenuc1, uces_uc1 = self.corpus.make_uc(uces, orderuces, self.corpus.parametre['tailleuc1'])
                print 'len uc1 : ', self.corpus.lenuc1
                uces1 = [[uce,uces_uc1[uce]] for uce in orderuces]
                uces1 = sortedby(uces1, 1)
                self.corpus.write_tab([[u'uce',u'uc']] + [[i, val[1]] for i, val in enumerate(uces1)], self.dictpathout['listeuce1'])
                #tabuc1 = self.corpus.make_tab_uc(uces_uc1, uc1)
                self.corpus.make_and_write_sparse_matrix_from_uc(uces_uc1, self.dictpathout['TableUc1'])
            elif self.corpus.parametre['classif_mode'] == 2 :
                #tabuc1 = self.corpus.make_table_with_uci()
                self.corpus.make_and_write_sparse_matrix_from_uci(self.dictpathout['TableUc1'])
                uc1 = None
                uces1 = [[uce, orderuces[uce]] for uce in orderuces]
                uces1 = sortedby(uces1, 1)
                self.corpus.lenuc1 = len(uces1)
                self.corpus.write_tab([[u'uce',u'uc']] + [[i, i] for i in range(0,len(orderuces))], self.dictpathout['listeuce1'])
    
            #self.corpus.write_sparse_matrix(self.dictpathout['TableUc1'], tabuc1, len(orderuces), len(self.corpus.actives))
            #self.corpus.write_tab(tabuc1,self.dictpathout['TableUc1'])
    
            if self.corpus.parametre['classif_mode'] == 0 : 
                self.corpus.lenuc2, uces_uc2 = self.corpus.make_uc(uces, orderuces, self.corpus.parametre['tailleuc2'])
                print 'len uc2 :', self.corpus.lenuc2
                #tabuc2 = self.corpus.make_tab_uc(uces_uc2, uc2)
                self.corpus.make_and_write_sparse_matrix_from_uc(uces_uc2, self.dictpathout['TableUc2'])            
                #self.corpus.write_tab(tabuc2, self.dictpathout['TableUc2'])
                uces2 = [[uce, uces_uc2[uce]] for uce in orderuces]
                uces2 = sortedby(uces2, 1)
                self.corpus.write_tab([[u'uce',u'uc']] + [[i, val[1]] for i, val in enumerate(uces2)], self.dictpathout['listeuce2'])
            
            if sys.platform == 'win32' :
                try :
                    if self.parent.pref.getboolean('iramuteq', 'R_mem') :
                        R_max_mem = self.parent.pref.getint('iramuteq','R_max_mem')
                    else :
                        R_max_mem = False
                except :
                    R_max_mem = False
            else :
                R_max_mem = False
            RchdTxt(self.dictpathout, self.parent.RscriptsPath, self.corpus.parametre['mincl'], self.corpus.parametre['classif_mode'], nbt = self.corpus.parametre['nbcl_p1'] - 1, libsvdc = self.parent.pref.getboolean('iramuteq','libsvdc'), libsvdc_path = self.parent.pref.get('iramuteq','libsvdc_path'), R_max_mem = R_max_mem)
            
            pid = exec_rcode(self.parent.RPath,self.dictpathout['Rchdtxt'],wait = False)
            while pid.poll() == None :
                if not self.cmd :
                    self.dlg.Pulse(u'CHD...')
                    sleep(0.2)
                else :
                    sleep(0.2)
            check_Rresult(self.parent, pid)
            if not self.cmd : 
                self.dlg.Update(7, u'Profils')
            ucecl = self.corpus.read_uce_from_R(self.dictpathout['uce'])
            ucecl0 = [cl for uce,cl in ucecl if cl != 0]
            clnb = len(list(set(ucecl0)))
            classes = [cl for uce, cl in ucecl]
            uces1 = [val for val, i in uces1]
            
            self.corpus.make_lc(uces1, classes, clnb)
            self.corpus.build_profile(clnb, classes, self.corpus.actives, self.dictpathout['Contout']) 
            
            #passives = [lem for lem in self.corpus.lems if lem not in self.corpus.actives]
            self.corpus.build_profile(clnb, classes, self.corpus.supp, self.dictpathout['ContSupOut'])
            
            self.corpus.make_etoiles(self.corpus.para_coords)
    
            self.corpus.build_profile_et(clnb, classes, uces1, self.dictpathout['ContEtOut'])
            
            AlcesteTxtProf(self.dictpathout, self.parent.RscriptsPath, clnb, '0.9')
            
            pid = exec_rcode(self.parent.RPath, self.dictpathout['RTxtProfGraph'],wait = False)
            while pid.poll() == None :
                if not self.cmd :
                    self.dlg.Pulse(u'AFC...')
                    sleep(0.2)
                else :
                    pass
            check_Rresult(self.parent, pid)
            
            self.corpus.dictpathout = self.dictpathout
            
            if not self.cmd :
                self.dlg.Update(8, u'rapport')
    
            temps = time() - t1
            self.corpus.minutes, self.corpus.seconds = divmod(temps, 60)
            self.corpus.hours, self.corpus.minutes = divmod(self.corpus.minutes, 60)        
    
            PrintRapport(self.corpus, 'txt')
            
            CreateIraFile(self.dictpathout, clnb, os.path.basename(self.corpus.parametre['filename']))
            
            self.corpus.save_corpus(self.dictpathout['db'])
     
            afc_graph_list = [[os.path.basename(self.dictpathout['AFC2DL_OUT']), u'Variables actives - coordonnées - facteurs 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DSL_OUT']), u'variables supplémentaires - coordonnées - facteurs 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DEL_OUT']), u'Variables illustratives - Coordonnées - facteur 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DCL_OUT']), u'Classes - Coordonnées - facteur 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DCoul']), u'Variables actives - Corrélation - facteur 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DCoulSup']), u'Variables supplémentaires - Corrélation - facteur 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DCoulEt']), u'Variables illustratives - Corrélations - facteur 1 / 2'],
                          [os.path.basename(self.dictpathout['AFC2DCoulCl']), u'Classes - Corrélations - facteurs 1 / 2'],]
            chd_graph_list = [[os.path.basename(self.dictpathout['dendro1']), u'dendrogramme à partir de chd1']]
            if self.corpus.parametre['classif_mode'] == 0 :
                chd_graph_list.append([os.path.basename(self.dictpathout['dendro2']), u'dendrogramme à partir de chd2'])
            chd_graph_list.append([os.path.basename(self.dictpathout['arbre1']), u'chd1'])
            if self.corpus.parametre['classif_mode'] == 0 :
                chd_graph_list.append([os.path.basename(self.dictpathout['arbre2']), u'chd2'])
            print_liste(self.dictpathout['liste_graph_afc'],afc_graph_list)
            print_liste(self.dictpathout['liste_graph_chd'],chd_graph_list)
            if not self.cmd :
                self.dlg.Update(9, u'fin')
                self.dlg.Destroy()
                OpenAnalyse(self.parent, self.dictpathout['ira'])  
        else :
            self.corpus.make_big()
