# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2011 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, construct_simipath
from corpus import Corpus
import os
from analysetxt import AnalyseText
from ConfigParser import RawConfigParser
from guifunct import getPage, getCorpus
from dialog import StatDialog
from functions import indices_simi, progressbar, treat_var_mod
from tableau import Tableau
from tabsimi import DoSimi
from PrintRScript import PrintRScript
import wx
from copy import copy

import logging

logger = logging.getLogger('iramuteq.textsimi')



class SimiTxt(AnalyseText): 
    def doanalyse(self) :
        self.indices = indices_simi
        self.makesimiparam()
        self.makefiles()
        prep = PrepSimi(self.ira, self.parametres, indices_simi)
        self.parametres = prep.parametres
        script = PrintSimScript(self)


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

    def makesimiparam(self) :
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
                          #'ira' : self.pathout['Analyse.ira']
                          }
        self.parametres.update(self.paramsimi)

    def makefiles(self) :
        self.actives, lim = self.corpus.make_actives_nb(self.parametres.get('max_actives',1500), 1)
        self.parametres['eff_min_forme'] = lim
        self.parametres['nbactives'] = len(self.actives)
        self.parametres['fromprof'] = True
        self.corpus.make_and_write_sparse_matrix_from_uces(self.actives, self.pathout['mat01.csv'], self.pathout['listeuce1.csv'])
        with open(self.pathout['actives.csv'], 'w') as f :
            f.write('\n'.join(self.actives).encode(self.ira.syscoding))

        self.listet = self.corpus.make_etoiles()
        self.listet.sort()
        self.parametres['stars'] = copy(self.listet)
        self.parametres['sfromchi'] = False

class PrepSimi :
    def _init_(self, parent, parametres, indices_simi) :    
        self.parametres = parametres
        self.dial = PrefSimi(parent, -1, self.parametres, indices_simi) 
        self.dial.CenterOnParent()
        self.val = self.dial.ShowModal()
        if self.val == wx.ID_OK :
            self.make_param()

    def make_param(self) :
        self.select = self.dial.check_colch.GetValue()
        param = {'coeff' : self.dial.choice1.GetSelection(),
                          'layout' : self.dial.choice2.GetSelection(),
                          'type' : self.dial.choice3.GetSelection(),
                          'arbremax' : self.dial.check1.GetValue(),
                          'coeff_tv' : self.dial.check_s_size.GetValue(),
                          'coeff_tv_nb' : self.dial.spin_tv.GetValue(),
                          'tvprop' : self.dial.check2.GetValue(),
                          'tvmin' : self.dial.spin_tvmin.GetValue(),
                          'tvmax' : self.dial.spin_tvmax.GetValue(),
                          'coeff_te' : self.dial.check3.GetValue(),
                          'coeff_temin' : self.dial.spin_temin.GetValue(),
                          'coeff_temax' : self.dial.spin_temax.GetValue(),
                          'label_e' : self.dial.check_elab.GetValue(),
                          'label_v' : self.dial.check_vlab.GetValue(),
                          'vcex' : self.dial.check_vcex.GetValue(),
                          'vcexmin' : self.dial.spin_vcexmin.GetValue(),
                          'vcexmax' : self.dial.spin_vcexmax.GetValue(),
                          'cex' : self.dial.spin_cex.GetValue(),
                          'seuil_ok' : self.dial.check_seuil.GetValue(),
                          'seuil' : self.dial.spin_seuil.GetValue(),
                          'cols' : self.dial.cols.GetColour(),
                          'cola' : self.dial.cola.GetColour(),
                          'width' : self.dial.spin_width.GetValue(),
                          'height' : self.dial.spin_height.GetValue(),
                          'first' : False,
                          'keep_coord' : keep_coord,
                          'alpha' : self.dial.slider_sphere.GetValue(),
                          'film' : self.dial.film.GetValue()
                          }
        if 'cexfromchi' in self.parametres :
            param['cexfromchi'] = self.dial.checkit.GetValue()
        if 'sfromchi' in self.parametres :
            param['sfromchi'] = self.dial.checki.GetValue()
        if 'vlabcolor' in self.parametres :
           param['vlabcolor'] = self.parametres['vlabcolor']
        if 'check_bystar' in dir(self.dial) :
            param['bystar'] = self.dial.check_bystar.GetValue()
            param['stars'] = self.parametres['stars']
        self.parametres.update(param)

class PrintSimiScript(PrintRScript) :
    def make_script(self) :
        self.load(['igraph', 'proxy', 'Matrix'])
        self.source([self.analyse.parent.RscriptsPath['simi'], self.analyse.parent.RscriptsPath['Rgraph']])
        txt = """
        dm.path <- "%s"
        cn.path <- "%s"
        selected.col <- "%s"
        """ % (self.pathout['mat01.csv'], self.pathout['actives.csv'], self.pathout['selected.csv'])
        
        txt += """
        dm <- dm[, selected.col+1]
        """
        if self.parametres['coeff'] == 0 :
            method = 'cooc'
            txt += """
            method <- 'cooc'
            mat <- make.a(dm)
            """
        else :
            txt += """
            dm <- as.matrix(dm)
            """
        if self.parametres['coeff'] == 1 :
            method = 'prcooc'
            txt += """
            method <- 'Russel'
            mat <- simil(dm, method = 'Russel', diag = TRUE, upper = TRUE, by_rows = FALSE)
            """
        elif self.analyses.indices[self.parametres['coeff']] == 'binomial' :
            method = 'binomial'
            txt += """
            method <- 'binomial'
            mat <- binom.sim(dm)
            """
        else :
            method = self.types[self.paramsimi['coeff']]
            txt += """
            method <-"%s"
            mat <- simil(dm, method = method, diag = TRUE, upper = TRUE, by_rows = FALSE)
            """ % self.analyse.indices[self.parametres['coeff']]
        txt += """
        mat <- as.matrix(stats::as.dist(mat,diag=TRUE,upper=TRUE))
        mat[is.na(mat)] <- 0
        mat[is.infinite(mat)] <- 0
        """
        if self.parametres['layout'] == 0 : layout = 'random'
        if self.parametres['layout'] == 1 : layout = 'circle'
        if self.parametres['layout'] == 2 : layout = 'frutch'
        if self.parametres['layout'] == 3 : layout = 'kawa'
        if self.parametres['layout'] == 4 : layout = 'graphopt'
        
        txt += """
        eff <- colSums(dm)
        g.ori <- graph.adjacency(mat, mode='lower', weighted = TRUE)
        w.ori <- E(g.ori)$weight
        if (max.tree) {
            if (method == 'cooc') {
                E(g.ori)$weight <- 1 / w.ori
            } else {
                E(g.ori)$weigth <- 1 - w.ori
            }
            g.max <- minimum.spanning.tree(g.ori)
            if (method == 'cooc') {
                E(g.max)$weight <- 1 / E(g.max)$weight
            } else {
                E(g.max)$weight <- 1 - E(g.max)$weight
            }
            g.toplot <- g.max
        } else {
            g.toplot <- g.ori
        }
        """
            


        self.tableau = Tableau(self.parent, '')
        self.tableau.listactives = self.actives
        self.tableau.parametre['fromtxt'] = True
        self.corpus.lems_eff = dict([[lem,[self.corpus.lems[lem].freq]] for lem in self.actives])
        #print('ATTENTION  ETOILES')
        #self.paramsimi['bystar'] = True
        self.tableau.listet = copy(self.listet)
        #self.paramsimi['cexfromchi'] = True
        #self.paramsimi['vlabcolor'] = True
        self.tableau.actives = copy(self.corpus.lems_eff)
        DoSimi(self, fromprof = self.pathout['mat01.csv'], param = self.paramsimi, pathout = self.pathout.dirout)

#class SimiTxt :
#    def __init__(self, parent, cmd = False, param = None):
#        self.parent = parent
#        self.cmd = cmd
#        self.ConfigPath = parent.ConfigPath
#        self.DictPath = parent.DictPath
#        self.KeyConf = RawConfigParser()
#        self.KeyConf.read(self.ConfigPath['key'])
#        self.indices = indices_simi
#        self.paramsimi = {'coeff' : 0,
#                          'layout' : 2,
#                          'type' : 1,
#                          'arbremax' : 1,
#                          'coeff_tv' : 1,
#                          'coeff_tv_nb' : 0,
#                          'tvprop' : 0,
#                          'tvmin' : 5,
#                          'tvmax' : 30,
#                          'coeff_te' : 1,
#                          'coeff_temin' : 1,
#                          'coeff_temax' : 10,
#                          'label_v': 1,
#                          'label_e': 0,
#                          'vcex' : 1,
#                          'cexfromchi' : False,
#                          'vcexmin' : 10,
#                          'vcexmax' : 25,
#                          'cex' : 10,
#                          'seuil_ok' : 0,
#                          'seuil' : 1,
#                          'cols' : (255,0,0),
#                          'cola' : (200,200,200),
#                          'width' : 1000,
#                          'height' : 1000,
#                          'bystar' : False,
#                          'first' : True,
#                          'keep_coord' : True,
#                          'alpha' : 20,
#                          'film': False,
#                          }
#        page = getPage(self.parent)
#        if page is not None :
#            self.corpus = getCorpus(page)
#            if self.corpus is not None :
#                self.pathout = ConstructPathOut(self.corpus.parametre['openpath'], 'simitxt')
#                self.dictpathout = construct_simipath(self.pathout)
#                self.val = wx.ID_OK
#                self.make_table()
#                self.make_simi()
#        else :
#            self.corpus = Corpus(parent)
#            self.corpus.content = self.parent.content
#            self.corpus.parametre['encodage'] = parent.corpus_encodage
#            self.corpus.parametre['lang'] = parent.corpus_lang
#            self.corpus.parametre['filename'] = parent.filename
#            self.corpus.parametre['eff_min_uce'] = None
#            self.pathout = ConstructPathOut(self.corpus.parametre['filename'], 'simitxt')
#            self.dictpathout = construct_simipath(self.pathout)
#            dial = StatDialog(self, self.parent)
#            dial.check_uce.SetValue(True)
#            dial.check_uce.Enable(False)
#            dial.OnCheckUce(wx.EVT_MENU)
#            self.val = dial.ShowModal()
#            if self.val == wx.ID_OK :
#                with open(self.parent.ConfigPath['key'], 'w') as f:
#                    self.KeyConf.write(f)
#                if dial.radio_lem.GetSelection() == 0 : lem = True
#                else : lem = False
#                if dial.exp.GetSelection() == 0 : exp = True
#                else : exp = False
#                dial.Destroy()
#                self.corpus.parametre['lem'] = lem
#                self.corpus.parametre['expressions'] = exp
#                self.corpus.parametre['nbforme_uce'] = dial.spin_ctrl_4.GetValue()
#                self.corpus.parametre['eff_min_forme'] = dial.spin_ctrl_5.GetValue()
#                self.corpus.parametre['max_actives'] = dial.spin_max_actives.GetValue()
#                self.make_corpus()
#                self.make_table()
#                self.make_simi()
#            else :
#                dial.Destroy()
#
#    def make_corpus(self) :
#        print 'make corpus'
#        if not self.cmd :
#            dlg = progressbar(self, maxi = 6)
#        self.corpus.supplementaires = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "2"]
#        self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
#        ucis_txt, ucis_paras_txt = self.corpus.start_analyse(self.parent, dlg = dlg, cmd = self.cmd)
#        del ucis_txt
#    
#        if not self.cmd :
#            dlg.Update(5, '%i ucis - Construction des uces' % len(ucis_paras_txt))
#        self.corpus.make_ucis_paras_uces(ucis_paras_txt, make_uce = True)
#        del ucis_paras_txt
#
#        if self.corpus.para_coords != [[] for val in self.corpus.para_coords] :
#            self.corpus.parametre['para'] = True
#        else :
#            self.corpus.parametre['para'] = False
#        self.corpus.make_etoiles(self.corpus.para_coords)
#        print 'len(ucis_paras_uces)', len(self.corpus.ucis_paras_uces)
#
#        if not self.cmd :
#            dlg.Update(6, u'Dictionnaires')
#        uces, self.orderuces = self.corpus.make_forms_and_uces()
#        self.corpus.ucenb = len(uces)
#        self.corpus.make_lems(self.parent.lexique)
#
#        self.corpus.make_var_actives() 
#        self.corpus.make_var_supp()
#        self.corpus.lems_eff = self.corpus.make_lem_eff()
#
#        #variables = treat_var_mod(listet)
#        #print(variables)
#        #self.corpus.write_etoiles(self.dictpathout['etoiles'])
#        if not self.cmd :
#            dlg.Destroy()
#                
#    def make_table(self) :
#        if 'orderuces' not in dir(self) :
#            self.orderuces = [(i,j,k) for i, uci in enumerate(self.corpus.ucis_paras_uces) for j, para in enumerate(uci) for k, uce in enumerate(para)]
#            self.orderuces = dict([[val, i] for i, val in enumerate(self.orderuces)])
#            self.corpus.ucenb = len(self.orderuces)
#        #tabuc1 = self.corpus.make_table_with_uce(self.orderuces)
#        #tabuc1.insert(0,self.corpus.actives)
#        #tabuc1 = self.corpus.make_sparse_matrix_with_uce(self.orderuces)
#        #self.corpus.write_sparse_matrix(self.dictpathout['mat01'], tabuc1, self.corpus.ucenb, len(self.corpus.actives))
#        if self.corpus.actives is None :
#            self.corpus.typeactive = [option for option in self.KeyConf.options('KEYS') if self.KeyConf.get('KEYS', option) == "1"]
#            self.corpus.min_eff_formes()
#            self.corpus.make_var_actives()
#        self.corpus.make_and_write_sparse_matrix_from_uce(self.orderuces, self.dictpathout['mat01'])
#        #self.corpus.write_tab(tabuc1,self.dictpathout['mat01'])
#
#    def make_simi(self) :
#        self.tableau = Tableau(self.parent, '')
#        self.tableau.listactives = self.corpus.actives
#        self.tableau.parametre['fromtxt'] = True
#        if 'lems_eff' not in dir(self.corpus) :
#            self.corpus.lems_eff = self.corpus.make_lem_eff()
#        #print('ATTENTION  ETOILES')
#        #self.paramsimi['bystar'] = True
#        self.listet = self.corpus.get_unique_etoiles()
#        self.listet.sort()
#        self.tableau.listet = copy(self.listet)
#        self.paramsimi['stars'] = copy(self.listet)
#        #self.paramsimi['cexfromchi'] = True
#        self.paramsimi['sfromchi'] = False
#        #self.paramsimi['vlabcolor'] = True
#        self.tableau.actives = dict([[lem, self.corpus.lems_eff[lem]] for lem in self.corpus.actives])
#        self.corpus.save_corpus(self.dictpathout['corpus']) 
#        DoSimi(self, fromprof = self.dictpathout['mat01'], param = self.paramsimi, pathout = self.pathout)
