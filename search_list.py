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
from PrintRScript import barplot, dendroandbarplot
#---------------------------------------------------------------------------

#class List(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
#    def __init__(self, parent, ID, pos=wx.DefaultPosition,
#                 size=wx.DefaultSize, style=0):
#        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
#        listmix.ListCtrlAutoWidthMixin.__init__(self)

class SearchList(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin): #wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent,gparent, dlist,first, nbactives, nbetoiles, add_dendro=True):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.parent=parent
        self.gparent=gparent
        self.dlist=dlist
        self.add_dendro=add_dendro
        self.first = ['id','formes'] + first
        self.nbactives = nbactives
        self.nbetoiles = nbetoiles
        #wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)


        self.il = wx.ImageList(16, 16)

        self.sm_up = self.il.Add(getSmallUpArrowBitmap())
        self.sm_dn = self.il.Add(getSmallDnArrowBitmap())

        tID = wx.NewId()

        #self.list = List(self, tID,
        #                         style=wx.LC_REPORT 
        #                         | wx.BORDER_NONE
        #                         | wx.LC_EDIT_LABELS
        #                         | wx.LC_SORT_ASCENDING
        #                         )
        
        #self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        
        self.dlist = dlist 
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        
        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        
        
        self.itemDataMap = dlist
        self.itemIndexMap = dlist.keys()
        self.SetItemCount(len(dlist))
        listmix.ColumnSorterMixin.__init__(self, len(first)+2)

        self.PopulateList(dlist,first)
        self.SortListItems(1, False)
        self.do_greyline()
        
#-----------------------------------------------------------------------------------------    

    def PopulateList(self, dlist,first):
        first = ['id','formes']+first
        for i, name in enumerate(first) :
            self.InsertColumn(i, name, wx.LIST_FORMAT_LEFT)
        
        #for key in dlist :
        #    index = self.list.InsertStringItem(sys.maxint, '%5i' % key)
        #    for i, val in enumerate(dlist[key][1:]) :
        #        self.list.SetStringItem(index, i+1, str(dlist[key][i+1]))
        #    self.list.SetItemData(index, key)

        self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        for i in range(1,len(first)-1):
            self.SetColumnWidth(i, 130)
        
        if self.nbactives +  self.nbetoiles != len(dlist) :
            #there is supp data
            for i in range(self.nbactives, (len(dlist) - self.nbetoiles)) :
                item = self.GetItem(i)
                item.SetTextColour(wx.RED)
                self.SetItem(item)
        for i in range((len(dlist) - self.nbetoiles), len(dlist)) :
            item = self.GetItem(i)
            item.SetTextColour(wx.BLUE)
            self.SetItem(item)
        
    def do_greyline(self):
        for row in xrange(self.GetItemCount()):
            if row % 2 :
                self.SetItemBackgroundColour(row,(230,230,230))
            else :
                self.SetItemBackgroundColour(row,wx.WHITE)


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

    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index][col]
        return s

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex
        event.Skip()

    def OnRightClick(self, event):

        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupID1"):
#            self.popupID1 = wx.NewId()
            #self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            if self.add_dendro :
                self.id_adddendro = wx.NewId()
                self.Bind(wx.EVT_MENU, self.ongraphdendro, id = self.id_adddendro)
#            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            #self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)


        # make a menu
        menu = wx.Menu()
        # add some items
#        menu.Append(self.popupID1, u"Formes associées")
        #menu.Append(self.popupID2, u"Concordancier")
        menu.Append(self.popupID3, "Graphique")
        if self.add_dendro :
            menu.Append(self.id_adddendro, u"Graphique + dendrogramme")

        self.PopupMenu(menu)
        menu.Destroy()


    def OnPopupOne(self, event):
        activenotebook = self.parent.nb.GetSelection()
        page = self.parent.nb.GetPage(activenotebook)
        corpus = page.corpus
        word = self.getColumnText(self.GetFirstSelected(), 0)
        lems = corpus.lems
        rep = []
        for forme in lems[word] :
             rep.append([forme, corpus.formes[forme][0]])
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
        listmot = corpus.lems[item]
        uce_ok = [corpus.formes[forme][1] for forme in listmot]
        uce_ok = list(set([tuple(val) for line in uce_ok for val in line]))
        txt = '<h1>Concordancier</h1>'
        for uce in uce_ok:
            content = ' '+' '.join(corpus.ucis_paras_uces[uce[0]][uce[1]][uce[2]])+' '
            for form in listmot :
                sp = ''
                i = 0
                forme = ' ' + form + ' '
                while i < len(content):
                    coordword = content[i:].find(forme)
                    if coordword != -1 and i == 0:
                        txt += '<br><b>' + ' '.join(corpus.ucis[uce[0]][0]) + '</b><br>'
                        if coordword < avap:
                            sp = '&nbsp;' * (avap - coordword)
                            deb = i
                        else:
                            deb = i + coordword - avap
                        if len(content) < i + coordword + avap:
                            fin = len(content) - 1
                        else:
                            fin = i + coordword + avap
                        txt += '<TT>' + sp + content[deb:fin].replace(forme, '<font color=red>' + forme + '</font>') + '</TT><br>'
                        i += coordword + len(forme)
                        sp = ''
                    elif coordword != -1 and i != 0 :
                        if coordword < avap:
                            sp = '&nbsp;' * (avap - coordword)
                            deb = i
                        else:
                            deb = i + coordword - avap
                        if len(content) < i + coordword + avap:
                            fin = len(content) - 1
                        else:
                            fin = i + coordword + avap
                        txt += '<TT>' + sp + content[deb:fin].replace(forme, '<font color=red>' + forme + '</font>') + '</TT><br>'
                        i += coordword + len(forme)
                        sp = ''                   
                    else:
                        i = len(content)
                        sp = ''
        win.HtmlPage.SetPage(txt)
        win.Show(True)

    def OnPopupThree(self, event) :
        datas = [self.dlist[self.GetItemData(self.GetFirstSelected())]]
        last = self.GetFirstSelected()
        while self.GetNextSelected(last) != -1:
            last = self.GetNextSelected(last)
            data = self.dlist[self.GetItemData(last)]
            datas += [data]
        colnames = self.first[2:]
        rownames = [val[1] for val in datas]
        table = [[str(val) for val in line[2:]] for line in datas]
        tmpgraph = tempfile.mktemp(dir=self.parent.parent.TEMPDIR)
        txt =  barplot(table, rownames, colnames, self.parent.parent.RscriptsPath['Rgraph'], tmpgraph)
        tmpscript = tempfile.mktemp(dir=self.parent.parent.TEMPDIR)
        with open(tmpscript,'w') as f :
            f.write(txt)
        exec_rcode(self.parent.parent.RPath, tmpscript, wait = True)
        win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
        win.addsaveimage(tmpgraph)
        txt = "<img src='%s'>" % tmpgraph
        win.HtmlPage.SetPage(txt)
        win.Show(True)

    def ongraphdendro(self, evt) :
        corpus = self.parent.corpus
        datas = [self.dlist[self.GetItemData(self.GetFirstSelected())]]
        last = self.GetFirstSelected()
        while self.GetNextSelected(last) != -1:
            last = self.GetNextSelected(last)
            data = self.dlist[self.GetItemData(last)]
            datas += [data]
        colnames = self.first[2:]
        rownames = [val[1] for val in datas]
        table = [[str(val) for val in line[2:]] for line in datas]
        tmpgraph = tempfile.mktemp(dir=self.parent.parent.TEMPDIR)
        txt =  dendroandbarplot(table, rownames, colnames, self.parent.parent.RscriptsPath['Rgraph'], tmpgraph, dendro=corpus.dictpathout['Rdendro'])
        tmpscript = tempfile.mktemp(dir=self.parent.parent.TEMPDIR)
        with open(tmpscript,'w') as f :
            f.write(txt)
        exec_rcode(self.parent.parent.RPath, tmpscript, wait = True)
        win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
        win.addsaveimage(tmpgraph)
        txt = "<img src='%s'>" % tmpgraph
        win.HtmlPage.SetPage(txt)
        win.Show(True)

    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.SetDimensions(0, 0, w, h)
        
    def OnColClick(self,event):
        self.do_greyline()

class message(wx.Frame):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyFrame.__init__
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
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


def getSmallUpArrowData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00<IDAT8\x8dcddbf\xa0\x040Q\xa4{h\x18\xf0\xff\xdf\xdf\xffd\x1b\x00\xd3\
\x8c\xcf\x10\x9c\x06\xa0k\xc2e\x08m\xc2\x00\x97m\xd8\xc41\x0c \x14h\xe8\xf2\
\x8c\xa3)q\x10\x18\x00\x00R\xd8#\xec\xb2\xcd\xc1Y\x00\x00\x00\x00IEND\xaeB`\
\x82' 

def getSmallUpArrowBitmap():
    return wx.BitmapFromImage(getSmallUpArrowImage())

def getSmallUpArrowImage():
    stream = cStringIO.StringIO(getSmallUpArrowData())
    return wx.ImageFromStream(stream)

#----------------------------------------------------------------------
def getSmallDnArrowData():
    return \
"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00HIDAT8\x8dcddbf\xa0\x040Q\xa4{\xd4\x00\x06\x06\x06\x06\x06\x16t\x81\
\xff\xff\xfe\xfe'\xa4\x89\x91\x89\x99\x11\xa7\x0b\x90%\ti\xc6j\x00>C\xb0\x89\
\xd3.\x10\xd1m\xc3\xe5*\xbc.\x80i\xc2\x17.\x8c\xa3y\x81\x01\x00\xa1\x0e\x04e\
?\x84B\xef\x00\x00\x00\x00IEND\xaeB`\x82" 

def getSmallDnArrowBitmap():
    return wx.BitmapFromImage(getSmallDnArrowImage())

def getSmallDnArrowImage():
    stream = cStringIO.StringIO(getSmallDnArrowData())
    return wx.ImageFromStream(stream)
