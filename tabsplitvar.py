#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2014 Pierre Ratinaud
#License: GNU/GPL

import os
import wx
from chemins import ffr, FFF
import tempfile
from time import sleep
from analysematrix import AnalyseMatrix
from functions import exec_rcode, check_Rresult
from dialog import FreqDialog
from PrintRScript import PrintRScript
from tableau import Tableau

class SplitMatrixFromVar(AnalyseMatrix):
    def doparametres(self, dlg=None) :
        if dlg is None :
            return
        else :
            dial = FreqDialog(self.parent, self.tableau.get_colnames(), u"Column", size=(350, 200), showNA = False)
            dial.CenterOnParent()
            val = dial.ShowModal()
            if val == wx.ID_OK :
                self.parametres['colsel'] = dial.m_listBox1.GetSelections()
                self.parametres['header'] = dial.header
                self.parametres['tohistory'] = False
            else :
                self.parametres = None
            dial.Destroy()
                
    def doanalyse(self):
        newtabs = self.tableau.splitfromvar(self.parametres['colsel'][0])
        for mod in newtabs :
            tab = Tableau(self.ira, os.path.join(self.tableau.pathout['%s.csv' % mod]).replace(u'*',''))
            if not os.path.exists(tab.pathout.dirout) :
                os.mkdir(tab.pathout.dirout)
            tab.linecontent = newtabs[mod] 
            tab.make_content_simple()
            tab.parametres['matrix'] = tab.parametres['uuid']
            self.ira.tree.OnItemAppend(tab.parametres, select = False)