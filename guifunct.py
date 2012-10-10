# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2011 Pierre Ratinaud
#Lisense: GNU/GPL

import wx
import os
import sys
from copy import copy
import dialog
from listlex import *


def OnOpen(self, type):
        if type == "Data":
             wildcard = u"Fichiers supportés|*.ods;*.xls;*.csv;*.txt|Openoffice Clac|*.ods|Fichier excel|*.xls|Fichier csv|*.csv|Fichier texte|*.txt|Tous les fichiers|*"
        elif type == "Texte":
            wildcard = "Fichier texte|*.txt|Tous les fichiers|*"
        elif type == "Analyse":
            wildcard = "Fichier analyse/Corpus|*.ira;*.cira"
        defaultDir = self.PathPath.get('PATHS', 'lastpath')
        if defaultDir.strip() == '':
            defaultDir = self.UserConfigPath.replace('.iramuteq','')
        dlg = wx.FileDialog(
        self, message="Choisissez un fichier", defaultDir=defaultDir,
        defaultFile="", wildcard=wildcard, style=wx.OPEN | wx.CHANGE_DIR)
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK :
            fileName = dlg.GetFilename()
            path = dlg.GetPaths()
            dlg.Destroy()
            self.PathPath.set('PATHS', 'lastpath', os.path.dirname(path[0]))
            self.type = type
            return fileName, path
        else:
            dlg.Destroy()
            if type == "Data":
                return False, [False]
            elif type == "Texte":
                return False, [False]
            elif type == "Analyse":
                return [False]

def getfileextension(file) :
    return os.path.splitext(file)[1]

def get_table_param(self, filename) :
    if getfileextension(filename) == '.csv':
        dlg = dialog.FileOptionDialog(self, -1, u"Format du fichier", sep=True, size=(350, 200),
                     style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnParent()
        val = dlg.ShowModal()
        if val == wx.ID_OK:
            self.tableau.parametre['colsep'] = dlg.colsep[dlg.choice3.GetSelection()]
            self.tableau.parametre['txtsep'] = dlg.txtsep[dlg.choice4.GetSelection()]
            if self.tableau.parametre['colsep'] == 'tabulation' :
                self.tableau.parametre['colsep'] = '\t'
            self.tableau.parametre['filetype'] = 'csv'
        else :
            dlg.Destroy()
    elif  getfileextension(filename) == '.xls' :
        dlg = dialog.FileOptionDialog(self, -1, u"Format du fichier", sep=False, sheet = True, size=(350, 200),
                     style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnParent()
        val = dlg.ShowModal()
        if val == wx.ID_OK:    
            self.tableau.parametre['colsep'] = ';'
            self.tableau.parametre['txtsep'] = '\"'
            self.tableau.parametre['encodage'] = sys.getdefaultencoding()
            self.tableau.parametre['sheetnb'] = dlg.spin1.GetValue()
            self.tableau.parametre['filetype'] = 'xls'
        else :
            dlg.Destroy()
    elif getfileextension(filename) == '.ods':
        dlg = dialog.FileOptionDialog(self, -1, u"Format du fichier", sep=False, size=(350, 200),
                     style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnParent()
        val = dlg.ShowModal()
        if val == wx.ID_OK:          
            self.tableau.parametre['colsep'] = ';'
            self.tableau.parametre['txtsep'] = '\"'
            self.tableau.parametre['filetype'] = 'ods'
        else :
            dlg.Destroy()
    else :
        val = False
    if val == wx.ID_OK:       
        if dlg.radio_box_1.GetSelection() == 0:
            self.tableau.firstrowiscolnames = True
        else:
            self.tableau.firstrowiscolnames = False
        if dlg.radio_box_2.GetSelection() == 0:
            self.tableau.firstcolisrownames = True
        else:
            self.tableau.firstcolisrownames = False
        dlg.Destroy()

def getPage(ira) :
    if '_mgr' in dir(ira) :
        if not ira._mgr.GetPane('Text').IsShown() :
            if ira.nb.GetPageCount() >= 1:
                return ira.nb.GetPage(ira.nb.GetSelection())
            else :
                return None
        else :
            return None
    else :
        return None

def getCorpus(page) :
    if 'corpus' in page.__dict__:
        return copy(page.corpus)
    else :
        return None
            
class SelectColumn :
    def __init__(self, parent, dictcol, actives, pathout, selected = None) :
        self.ira = parent
        dial = dialog.SelectColDial(self.ira)
        listcol = ListForSpec(dial, self, dictcol, ['forme', 'eff'])
        dial.bSizer2.Add( listcol, 2, wx.ALL|wx.EXPAND, 5 )
        dial.m_sdbSizer2.AddButton( dial.m_sdbSizer2OK )
        dial.m_sdbSizer2.Realize()
        dial.bSizer2.Add( dial.m_sdbSizer2, 0, wx.EXPAND, 5 )
        dial.Layout()
        if selected is None :
            for row in xrange(listcol.list.GetItemCount()):
                listcol.list.Select(row)
        else :
            orderlex = dict([[listcol.getColumnText(i,0),i] for i in range(0,listcol.list.GetItemCount())])
            for row in selected :
                listcol.list.Select(orderlex[actives[row]])
        dial.CenterOnParent()
        val = dial.ShowModal()        
        last = listcol.list.GetFirstSelected()
        lastl = [listcol.list.GetFirstSelected()]
        indexes = [listcol.getColumnText(listcol.list.GetFirstSelected(),0)]
        while listcol.list.GetNextSelected(last) != -1:
            last = listcol.list.GetNextSelected(last)
            lastl.append(last)
            indexes.append(listcol.getColumnText(last,0))
        dial.Destroy()
        column = [actives.index(val) for val in indexes]
        column.sort()
        with open(pathout, 'w') as f :
            f.write('\n'.join([`val` for val in column]))

class PrepSimi :
    def __init__(self, parent, parametres, indices_simi) :    
        self.parametres = parametres
        self.dial = dialog.PrefSimi(parent, -1, self.parametres, indices_simi) 
        self.dial.CenterOnParent()
        self.val = self.dial.ShowModal()
        if self.val == wx.ID_OK :
            self.make_param()

    def make_param(self) :
        self.select = self.dial.check_colch.GetValue()
        if self.parametres.get('first', True) :
            keep_coord = False
        else :
            keep_coord = self.dial.check_coord.GetValue()
        param = {'coeff' : self.dial.choice1.GetSelection(),
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

