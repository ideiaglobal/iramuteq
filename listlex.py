# -*- coding: utf-8 -*-

#----------------------------------------------------------------------------
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
import  wx.lib.mixins.listctrl  as  listmix
import cStringIO
import tempfile
from functions import exec_rcode, MessageImage
from chemins import ffr
from PrintRScript import barplot
from dialog import SearchDial
#---------------------------------------------------------------------------

#class List(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
#    def __init__(self, parent, ID, pos=wx.DefaultPosition,
#                 size=wx.DefaultSize, style=0):
#        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
#        listmix.ListCtrlAutoWidthMixin.__init__(self)

class ListForSpec(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent,gparent, dlist,first):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.parent=parent
        self.gparent=gparent
        self.dlist=dlist
        self.first = first

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

        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour((230, 230, 230))
        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour("light blue")
        
        self.dlist = dlist 

        i=0
        for name in first :
            self.InsertColumn(i,name,wx.LIST_FORMAT_LEFT)
            i+=1
            
        self.SetColumnWidth(0, 180)

        for i in range(1,len(first)-1):
            self.SetColumnWidth(i, len(first[i]) * 10)
        
        self.itemDataMap = dlist
        self.itemIndexMap = dlist.keys()
        self.SetItemCount(len(dlist))
        
        #listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, len(first))
        self.SortListItems(1, 0)
        
#-----------------------------------------------------------------------------------------    
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        
        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

#-----------------------------------------------------------------------------------------    
        
    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index][col]
        return s

    def OnGetItemAttr(self, item):
        if item % 2 :
            return self.attr1
        else :
            return self.attr2


    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)
    
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

    def GetItemData(self, item) :
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index]
        return s
    
    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items
        # redraw the list
        self.Refresh()
    
    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        event.Skip()

    def onsearch(self, evt) :
        self.dial = SearchDial(self, self, 0, True)
        self.dial.CenterOnParent()
        self.dial.ShowModal()
        self.dial.Destroy()
    
    def OnRightClick(self, event):

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popup_Tgen_glob = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnTgen_glob, id=self.popup_Tgen_glob)
        # make a menu
        menu = wx.Menu()
        # add some items
        menu.Append(self.popupID1, u"Formes associées")
        menu.Append(self.popupID2, u"Concordancier")
        menu.Append(self.popupID3, "Graphique")
        #menu.Append(self.popup_Tgen_glob, "Tgen global")

        self.PopupMenu(menu)
        menu.Destroy()


    def OnPopupOne(self, event):
        activenotebook = self.parent.nb.GetSelection()
        page = self.parent.nb.GetPage(activenotebook)
        corpus = page.corpus
        word = self.getColumnText(self.GetFirstSelected(), 0)
        lems = corpus.getlems()
        rep = []
        for forme in lems[word].formes :
             rep.append([corpus.getforme(forme).forme, corpus.getforme(forme).freq])
        win = message(self, -1, u"Formes associées", size=(300, 200), style=wx.DEFAULT_FRAME_STYLE)
        win.html = '<html>\n' + '<br>'.join([' : '.join([str(val) for val in forme]) for forme in rep]) + '\n</html>'
        win.HtmlPage.SetPage(win.html)
        win.Show(True)

    def OnPopupTwo(self, event):
        activenotebook = self.parent.nb.GetSelection()
        page = self.parent.nb.GetPage(activenotebook)
        item=self.getColumnText(self.GetFirstSelected(), 0)
        corpus = page.corpus
        win = message(self, -1, u"Concordancier", size=(600, 200),style = wx.DEFAULT_FRAME_STYLE)
        avap=60
        listmot = corpus.getlems()[item].formes       
        uce_ok = corpus.getlemuces(item)
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

    def OnPopupThree(self, event) :
        print self.GetFirstSelected()
        datas = [self.GetItemData(self.GetFirstSelected())]
        print datas
        last = self.GetFirstSelected()
        while self.GetNextSelected(last) != -1:
            last = self.GetNextSelected(last)
            data = self.GetItemData(last)
            datas += [data]
        colnames = self.first[1:]
        table = [[str(val) for val in line[1:]] for line in datas]
        rownames = [val[0] for val in datas]
        tmpgraph = tempfile.mktemp(dir=self.parent.TEMPDIR)

        txt = barplot(table, rownames, colnames, self.parent.RscriptsPath['Rgraph'], tmpgraph)

        tmpscript = tempfile.mktemp(dir=self.parent.TEMPDIR)
        file = open(tmpscript,'w')
        file.write(txt)
        file.close()
        exec_rcode(self.parent.RPath, tmpscript, wait = True)
        win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
        win.addsaveimage(tmpgraph)
        txt = "<img src='%s'>" % tmpgraph
        win.HtmlPage.SetPage(txt)
        win.Show(True)

    def OnTgen_glob(self, evt) :
        activenotebook = self.parent.nb.GetSelection()
        page = self.parent.nb.GetPage(activenotebook)
        corpus = page.corpus

        tmpgraph = tempfile.mktemp(dir=self.gparent.parent.TEMPDIR)
        intxt = """
        load("%s")
        """ % corpus.dictpathout['RData']
        intxt += """
        Tgen.glob = NULL
        tovire <- NULL
        for (i in 1:ncol(dmf)) {
            Tgen.glob <- rbind(Tgen.glob,colSums(dmf[which(specf[,i] > 3),]))
            tovire <- append(tovire, which(specf[,i] > 3))
        }
        rownames(Tgen.glob) <- colnames(dmf)
        Tgen.table <- dmf[-unique(tovire),]
        Tgen.table<- rbind(Tgen.table, Tgen.glob)
        spec.Tgen.glob <- AsLexico2(Tgen.table)
        spec.Tgen.glob <- spec.Tgen.glob[[1]][((nrow(Tgen.table)-ncol(Tgen.table))+1):nrow(Tgen.table),]
        di <- spec.Tgen.glob
        """
        txt = barplot('', '', '', self.gparent.parent.RscriptsPath['Rgraph'], tmpgraph, intxt = intxt) 
        tmpscript = tempfile.mktemp(dir=self.gparent.parent.TEMPDIR)
        with open(tmpscript, 'w') as f :
            f.write(txt)
        exec_rcode(self.gparent.parent.RPath, tmpscript, wait = True)
        win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
        win.addsaveimage(tmpgraph)
        txt = "<img src='%s'>" % tmpgraph
        win.HtmlPage.SetPage(txt)
        win.Show(True)



class message(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        #self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.HtmlPage=wx.html.HtmlWindow(self, -1)
        if "gtk2" in wx.PlatformInfo:
            self.HtmlPage.SetStandardFonts()
        self.HtmlPage.SetFonts('Courier','Courier')
        
        
        self.button_1 = wx.Button(self, -1, "Fermer")
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.__do_layout()
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.HtmlPage, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        sizer_2.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade
        
    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()
