# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2011 Pierre Ratinaud
#Lisense: GNU/GPL

import wx
import os
import sys
from copy import copy
import dialog

def OnOpen(self, type):
        if type == "Data":
             wildcard = u"Fichiers supportés|*.ods;*.xls;*.csv;*.txt|Openoffice Clac|*.ods|Fichier excel|*.xls|Fichier csv|*.csv|Fichier texte|*.txt|Tous les fichiers|*"
        elif type == "Texte":
            wildcard = "Fichier texte|*.txt|Tous les fichiers|*"
        elif type == "Analyse":
            wildcard = "Fichier analyse|*.ira"
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
            
