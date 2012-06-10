#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL


from wx.lib import sheet
import wx


class MySheet(sheet.CSheet):
    def __init__(self, parent):
        sheet.CSheet.__init__(self, parent)
        self.parent=parent
        self.row = self.col = 0

    def OnGridSelectCell(self, event):
        self.row, self.col = event.GetRow(), event.GetCol()
        value =  self.GetColLabelValue(self.col) + self.GetRowLabelValue(self.row)
        event.Skip()
        
    def Populate(self,content):
        c=0
        for r in content:
            c+=1
        nrow=len(content)
        print 'nrow', nrow
        self.SetNumberRows(nrow)
        ncol=len(content[1])
        print 'ncol',ncol
        self.SetNumberCols(ncol)
        for y in range(0,nrow):
            for i in range(0,ncol):
                self.SetCellValue(y,i,str(content[y][i]))