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
            else :
                self.parametres = None
            dial.Destroy()
                
    def doanalyse(self):
        newtabs = self.tableau.splitfromvar(self.parametres['colsel'][0])
        for mod in newtabs :
            fout = self.tableau.pathout['%s.csv' % mod].replace(u'*','')
            with open(fout, 'w') as f :
                f.write('\n'.join(['\t'.join(line) for line in newtabs[mod]]).encode(self.parent.syscoding))
        print 'done!'