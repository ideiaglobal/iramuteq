#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2009-2010 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, simipath, ffr
from functions import print_liste, exec_rcode, read_list_file, check_Rresult, indices_simi, treat_var_mod
from dialog import SelectColDial, FreqDialog
from guifunct import PrefSimi
from analysematrix import AnalyseMatrix
from PrintRScript import PrintSimiScript
from listlex import *
import wx
#if wx.__version__ >= '2.11' :
#    import wx.lib.agw.aui as aui
#else :
#    import aui
import os
import tempfile
import datetime
from ConfigParser import RawConfigParser
from time import sleep
from uuid import uuid4


class DoSimi(AnalyseMatrix):
    def __init__(self, parent, param = None, isopen = False, fromprof = False, pathout = False, filename ='', gparent = False, wordgraph = False, listactives = False, actives = False, cmd = False, openfromprof=False, tableau = None):
#------------------------------------------------------------------- 
        self.fromprof = fromprof
        self.wordgraph = wordgraph
        self.listactives = listactives
        self.actives = actives
        self.openfromprof = openfromprof
        self.cmd = cmd
        if param is not None and fromprof:
            self.paramsimi = param
        else :
            self.paramsimi = {'coeff' : 0,
                          'layout' : 2,
                          'type_graph' : 1,
                          'arbremax' : 1,
                          'coeff_tv' : 0,
                          'coeff_tv_nb' : 10,
                          'tvprop' : 1,
                          'tvmin' : 5,
                          'tvmax' : 30,
                          'coeff_te' : 1,
                          'coeff_temin' : 1,
                          'coeff_temax' : 10,
                          'label_v': 1,
                          'label_e': 1,
                          'vcex' : 0,
                          'vcexmin' : 8,
                          'vcexmax' : 25,
                          'cex' : 10,
                          'seuil_ok' : 0,
                          'seuil' : 1,
                          'cols' : (255,0,0),
                          'cola' : (200,200,200),
                          'width' : 800,
                          'height' : 800,
                          'first' : True,
                          'keep_coord' : False,
                          'alpha' : 10,
                          'film' : False,
                          'svg' : 0,
                          'halo' : 0,
                          'com' : 0,
                          'communities' : 0,
                          }
        self.indices = indices_simi
        #if fromprof :
        #    self.parent = parent.parent
        #    self.Source = parent
        #else :
        self.parent = parent   
        self.Source = None
           
        self.RPath = self.parent.PathPath.get('PATHS', 'rpath')
        if not isopen :
            #if not fromprof :
            #    self.tableau = self.parent.tableau
            #else :
            #    self.tableau = parent.tableau
            if tableau is not None :
                self.tableau = tableau
            else : 
                self.tableau = parent.tableau
            self.tableau.parametre['mineff'] = 0
            if not fromprof :
                dialcol = FreqDialog(self.parent, -1, self.tableau.get_colnames(), u"Sélectionnez les colonnes", size=(600, 250))
                dialcol.CenterOnParent()            
                res = dialcol.ShowModal()
            else :
                res = wx.ID_OK
            if res == wx.ID_OK :
                if not self.actives :
                    self.tableau.selected_col = dialcol.list_box_1.GetSelections()
                    actives = self.tableau.getactlistfromselection(self.tableau.selected_col)
                else :
                    actives = self.actives
                self.tableau.make_listactives()
                actives = dict([[i, val] for i, val in enumerate(actives)])
                self.dial = PrefSimi(parent, -1, self.paramsimi, self.indices, wordlist = actives)
                self.dial.CenterOnParent()
                self.val = self.dial.ShowModal()
                if self.val == wx.ID_OK :
                    last = self.dial.listcol.GetFirstSelected()
                    lastl = [self.dial.listcol.GetFirstSelected()]
                    indexes = [self.dial.listcol.getColumnText(self.dial.listcol.GetFirstSelected(),0)]
                    while self.dial.listcol.GetNextSelected(last) != -1:
                        last = self.dial.listcol.GetNextSelected(last)
                        lastl.append(last)
                        indexes.append(self.dial.listcol.getColumnText(last,0))
                    self.column = [self.tableau.listactives.index(val) for val in indexes]
                    self.column.sort()
                    self.paramsimi = self.make_param()
                    self.parametres = self.paramsimi
                    self.parametres['type'] = 'simimatrix'
                    self.parametres['pathout'] = ConstructPathOut(self.tableau.parametre['filename'], 'SimiMatrix')
                    self.parametres['filename'] = self.tableau.parametres['filename']
                    self.dial.Destroy()
                    dlg = wx.ProgressDialog("Traitements",
                                   "Veuillez patienter...",
                                   maximum=4,
                                   parent=self.parent,
                                   style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME
                                    )
                    dlg.Center()
                    AnalyseMatrix.__init__(self, parent, self.tableau, self.paramsimi, dlg = dlg)
                else :
                    self.dial.Destroy()
            else :
                dialcol.Destroy()

    def doanalyse(self) :

        self.pathout.basefiles(simipath)
        with open(self.pathout['selected.csv'], 'w') as f :
             f.write('\n'.join([`val` for val in self.column]))

        count = 1
        keepGoing = self.dlg.Update(count)
    #----------------------------------------------------------------
        self.DictForme = {}
        self.Min = 10
        self.Linecontent = []
    #--------------------------------------------------------
        count += 1
        #if not self.fromprof :
            #self.pathout = ConstructPathOut(self.tableau.parametre['filename'], 'Simi')
            #self.DictPathOut = construct_simipath(self.pathout)
        self.parent.tableau.dictpathout = self.pathout
        self.dlg.Update(count, u"passage en O/1")
        self.parent.tableau.make_01_from_selection(self.tableau.selected_col)
            #self.Linecontent = parent.table
            #self.ListTo01Form()
        #else :
            #self.pathout = pathout
            #self.DictPathOut = construct_simipath(self.pathout)
        self.DictPathOut = self.pathout
            #self.DictPathOut['mat01'] = fromprof
        self.script = PrintSimiScript(self)
        self.script.make_script()
        #self.PrintScript()
        count += 1
        self.dlg.Update(count, u"R...") 
        #self.DoR(script.scriptout, dlg = self.dlg, message = 'R...')
        self.tmpfile = self.script.scriptout
        self.DoR(self.dlg)
        self.addgraph()
        self.tableau.save_tableau(self.pathout['db'])
        #self.make_ira()
        count += 1
        self.dlg.Update(count, u"") 
        self.dlg.Destroy()
        #self.dial.Destroy()
        #self.dolayout()
        if self.fromprof :
            fromprof = True
        else:
            fromprof = False
        #OpenAnalyse(self.parent, self.DictPathOut['ira'], False, simifromprof=fromprof)
#        else :
#            self.tableau = gparent.tableau
#            if 'corpus' in dir(gparent) :
#                self.Source = gparent
#            self.tableau.parametre['mineff'] = 0
#            self.DictPathOut = construct_simipath(os.path.abspath(os.path.dirname(filename)))
#            self.dolayout()
#            self.paramsimi['first'] = False
#            self.paramsimi['coeff'] = int(param.get('simi', 'indice'))
#            self.paramsimi['layout'] = int(param.get('simi', 'layout'))
#            self.paramsimi['seuil_ok'] = param.getboolean('simi', 'seuil_ok')
#            self.paramsimi['seuil'] = int(param.get('simi', 'seuil'))
#            if param.get('simi', 'wordgraph') == 'False' :
#                self.wordgraph = False
#            else :
#                self.wordgraph = param.get('simi', 'wordgraph')
#            if 'listet' in dir(self.tableau) :
#                self.paramsimi['stars'] = self.tableau.listet
#                self.paramsimi['bystar'] = False
#                self.paramsimi['cexfromchi'] = True
#                self.paramsimi['tvprop'] = False
#                self.paramsimi['sfromchi'] = False
#                self.paramsimi['coeff_te'] = True
#                self.paramsimi['coeff_tv'] = True
#                self.paramsimi['coeff_tv_nb'] = 0
#                self.paramsimi['label_e'] = False
#                self.paramsimi['width'] = 1000
#                self.paramsimi['height'] = 1000
         

    def make_param(self) :
        if self.paramsimi['first'] :
            keep_coord = False
        else :
            keep_coord = self.dial.check_coord.GetValue()
        #self.select = self.dial.check_colch.GetValue()

        paramsimi = {'coeff' : self.dial.choice1.GetSelection(),
                          'layout' : self.dial.choice2.GetSelection(),
                          'type_graph' : self.dial.choice3.GetSelection(),
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
                          'film' : self.dial.film.GetValue(),
                          'svg' : self.dial.choix_format.GetSelection(),
                          'halo' : self.dial.halo.GetValue(),
                          'com' : self.dial.comcheck.GetValue(),
                          'communities' :self.dial.choix_com.GetSelection(),
                          }
        if 'cexfromchi' in self.paramsimi :
            paramsimi['cexfromchi'] = self.dial.checkit.GetValue()
        if 'sfromchi' in self.paramsimi :
            paramsimi['sfromchi'] = self.dial.checki.GetValue()
        if 'vlabcolor' in self.paramsimi :
           paramsimi['vlabcolor'] = self.paramsimi['vlabcolor']
        if 'check_bystar' in dir(self.dial) :
            paramsimi['bystar'] = self.dial.check_bystar.GetValue()
            paramsimi['stars'] = self.paramsimi['stars']
        return paramsimi
        
#    def make_ira(self):
#        self.tableau.save_tableau(self.DictPathOut['db'])
#        conf = RawConfigParser()
#        conf.read(self.DictPathOut['ira'])
#        if not 'simi' in conf.sections() :
#            conf.add_section('simi')
#        date = datetime.datetime.now().ctime()
#        if self.fromprof :
#            conf.set('simi', 'corpus', self.Source.corpus.parametres['uuid'])
#        conf.set('simi', 'uuid', str(uuid4()))
#        conf.set('simi', 'date', str(date))
#        conf.set('simi', 'indice', self.paramsimi['coeff'])
#        conf.set('simi','layout', self.paramsimi['layout'])
#        conf.set('simi', 'seuil_ok', self.paramsimi['seuil_ok'])
#        conf.set('simi', 'seuil', str(self.paramsimi['seuil']))
#        conf.set('simi', 'wordgraph', self.wordgraph)
#        fileout = open(self.DictPathOut['ira'], 'w')
#        conf.write(fileout)
#        fileout.close()
#        
    def addgraph(self) :
        if self.parametres['type_graph'] == 1:
            if self.parametres['svg'] :
                filename, ext = os.path.splitext(self.script.filename)
                fileout = filename + '.svg'
            else :
                fileout = self.script.filename
            if os.path.exists(self.DictPathOut['liste_graph']):
                graph_simi = read_list_file(self.DictPathOut['liste_graph'])
                graph_simi.append([os.path.basename(fileout), self.script.txtgraph])
            else :
                graph_simi = [[os.path.basename(fileout), self.script.txtgraph]]
            print_liste(self.DictPathOut['liste_graph'], graph_simi)
        
    def DoR(self, dlg):
        if self.paramsimi['type'] == 1 :
            graph = False
            wait = False
        else : 
            graph = True
            wait = True
        pid = exec_rcode(self.RPath, self.tmpfile, wait = wait, graph = graph)
        if self.paramsimi['type'] == 1 :
            while pid.poll() == None :
                    if not self.cmd :
                        dlg.Pulse(u'R ...')
                        sleep(0.2)
                    else :
                        sleep(0.2)
            check_Rresult(self.parent, pid)
    

