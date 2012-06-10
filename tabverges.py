#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2012 Pierre Ratinaud
#Lisense: GNU GPL

import os
import string
import wx
import os
import sys
import tempfile
from chemins import ffr,FFF
import wx.lib.sized_controls as sc
from time import sleep
from functions import exec_rcode, check_Rresult
from dialog import ChiDialog

class Verges :
    def __init__(self,parent):
        self.parent = parent
        self.tableau = self.parent.tableau
        chioption = { 'valobs' : True,
                      'valtheo' : True,
                      'resi' : False,
                      'contrib' : True,
                      'pourcent' : False,
                      'pourcentl' : True,
                      'pourcentc' : True,
                      'graph' : True,
                      }
        self.dlg = ChiDialog(parent, -1, u"Chi2", chioption, size=(400, 350),
                     style = wx.DEFAULT_DIALOG_STYLE
                     )
        self.dlg.CenterOnParent()
        self.check_val()

    def check_val(self) :
        self.val = self.dlg.ShowModal()
        if self.val==wx.ID_OK :
                self.ColSel1 = self.dlg.list_box_1.GetSelections()
                self.ColSel2 = self.dlg.list_box_2.GetSelections()
                if len(self.ColSel1) != len(self.ColSel2) :
                    print 'pas meme taille'
                    self.check_val()
                else :
                    self.dotable()

    def dotable(self) :
        table_assoc = self.tableau.select_col(self.ColSel1)
        table_rank = self.tableau.select_col(self.ColSel2)
        
        
                
