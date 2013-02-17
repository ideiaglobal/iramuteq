# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------
# Name:         ListCtrl.py
# Author:       Pierre Ratinaud
# 

#comes from ListCtrl.py from the demo tool of wxPython:
# Author:       Robin Dunn & Gary Dumer
#
# Created:
# Copyright:    (c) 1998 by Total Control Software
# Licence:      wxWindows license
#----------------------------------------------------------------------------

import os
import sys
import  wx
from dialog import SearchDial, message
import wx.lib.mixins.listctrl as listmix 
from operator import itemgetter

#---------------------------------------------------------------------------

class ListPanel(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, gparent, dlist):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.parent = parent
        self.gparent = gparent
        self.source = gparent
        self.dlist = dlist
        #wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
        
        search_id = wx.NewId()
        self.parent.Bind(wx.EVT_MENU, self.onsearch, id = search_id)
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), search_id)])
        self.SetAcceleratorTable(self.accel_tbl)
        
        self.il = wx.ImageList(16, 16)
        a={"sm_up":"GO_UP","sm_dn":"GO_DOWN","w_idx":"WARNING","e_idx":"ERROR","i_idx":"QUESTION"}
        for k,v in a.items():
            s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
            exec(s)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        tID = wx.NewId()

        
#-----------------------------------------------------------------------------------------    
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour((230, 230, 230))
        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour("light blue")

        
        self.InsertColumn(0, 'forme', wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(1, 'nb', wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(2, 'type', wx.LIST_FORMAT_RIGHT)
        #self.InsertColumn(3, '', wx.LIST_FORMAT_RIGHT)

        self.SetColumnWidth(0, 150)   
        self.SetColumnWidth(1, 100)  
        self.SetColumnWidth(2, 100)
        #self.SetColumnWidth(3, wx.LIST_AUTOSIZE)

        self.itemDataMap = dlist
        self.itemIndexMap = dlist.keys()
        self.SetItemCount(len(dlist))

        #self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick, self)
        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        #listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, 3)
        self.SortListItems(1, False)
        #self.do_greyline()

        #self.currentItem = 0

    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index][col]
        return s

    def OnGetItemAttr(self, item):
        #index=self.itemIndexMap[item]
        #genre=self.itemDataMap[index][2]
        if item % 2 :
            return self.attr1
        else :
            return self.attr2

    def OnColClick(self, event):
        pass
        #self.do_greyline()
        
    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items
        
        # redraw the list
        self.Refresh()


    def OnRightDown(self, event):
        x = event.GetX()
        y = event.GetY()
        item, flags = self.HitTest((x, y))

        if flags & wx.LIST_HITTEST_ONITEM:
            self.Select(item)

        event.Skip()


    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()


    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        event.Skip()

    def onsearch(self, evt) :
        self.dial = SearchDial(self, self, 0, True)
        self.dial.CenterOnParent()
        self.dial.Show()
        #self.dial.Destroy()

    def OnRightClick(self, event):

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
 #           self.popupID3 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
#            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)

        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, u"Formes associées")
        menu.Append(self.popupID2, u"Concordancier")
#        menu.Append(self.popupID3, "recharger")

        self.PopupMenu(menu)
        menu.Destroy()


    def OnPopupOne(self, event):
        corpus = self.gparent.corpus
        word = self.getColumnText(self.GetFirstSelected(), 0)
        lems = corpus.getlems()
        rep = []
        for forme in lems[word].formes :
             rep.append([corpus.getforme(forme).forme, corpus.getforme(forme).freq])
        rep.sort(key = itemgetter(1), reverse = True)
        win = message(self, u"Formes associées", (300, 200))
        win.html = '<html>\n' + '<br>'.join([' : '.join([str(val) for val in forme]) for forme in rep]) + '\n</html>'
        win.HtmlPage.SetPage(win.html)
        win.Show(True)

    def OnPopupTwo(self, event):
        corpus = self.gparent.corpus
        win = message(self, u"Concordancier", (750, 600))
        avap = 60
        item = self.getColumnText(self.GetFirstSelected(), 0)
        listmot = corpus.getlems()[item].formes
        #uce_ok = [corpus.formes[corpus.idformes[forme].forme][1] for forme in listmot]
        uce_ok = corpus.getlemuces(item)#list(set([tuple(val) for line in uce_ok for val in line]))
        txt = '<h1>Concordancier</h1>'
        res = corpus.getconcorde(uce_ok)
        for uce in res :
            ucetxt = ' '+uce[1]+' '
            txt += ' '.join(corpus.ucis[corpus.getucefromid(uce[0]).uci].etoiles) + '<br>'
            for forme in listmot :
                forme = corpus.getforme(forme).forme
                ucetxt = ucetxt.replace(' '+forme+' ', '<font color=red> ' + forme + ' </font>')
            txt += ucetxt + '<br><br>'
        win.HtmlPage.SetPage(txt) 
        win.Show(True)
