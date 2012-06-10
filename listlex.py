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

class List(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, parent, ID, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
        listmix.ListCtrlAutoWidthMixin.__init__(self)

class ListForSpec(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent,gparent, dlist,first):
        self.parent=parent
        self.gparent=gparent
        self.dlist=dlist
        self.first = first
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)

        search_id = wx.NewId()
        self.parent.Bind(wx.EVT_MENU, self.onsearch, id = search_id)
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), search_id)])
        self.SetAcceleratorTable(self.accel_tbl)

        self.il = wx.ImageList(16, 16)

        self.sm_up = self.il.Add(getSmallUpArrowBitmap())
        self.sm_dn = self.il.Add(getSmallDnArrowBitmap())

        tID = wx.NewId()

        self.list = List(self, tID,
                                 style=wx.LC_REPORT 
                                 | wx.BORDER_NONE
                                 | wx.LC_EDIT_LABELS
                                 | wx.LC_SORT_ASCENDING
                                 )
        
        self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
        
        self.dlist = dlist 
        self.PopulateList(dlist,first)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
        
        # for wxMSW
        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
        
        
        self.itemDataMap = dlist
        listmix.ColumnSorterMixin.__init__(self, len(first))
        self.SortListItems(1, False)
        self.do_greyline()
        
#-----------------------------------------------------------------------------------------    

    def PopulateList(self, dlist,first):
        i=0
        for name in first :
            self.list.InsertColumn(i,name,wx.LIST_FORMAT_LEFT)
            i+=1
        ct=0
        for key,data in dlist.iteritems() :
            ct+=1
            index = self.list.InsertStringItem(sys.maxint, str(data[0]))
            i=1
            for val in data[1:]:
                self.list.SetStringItem(index, i, str(data[i]))
                i+=1

            self.list.SetItemData(index, key)
            
        self.list.SetColumnWidth(0, wx.LIST_AUTOSIZE)
        for i in range(1,len(first)-1):
            self.list.SetColumnWidth(i, 130)
        
    def do_greyline(self):
        for row in xrange(self.list.GetItemCount()):
            if row % 2 :
                self.list.SetItemBackgroundColour(row,(230,230,230))
            else :
                self.list.SetItemBackgroundColour(row,wx.WHITE)


    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self.list

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)


    def OnRightDown(self, event):
        x = event.GetX()
        y = event.GetY()
        item, flags = self.list.HitTest((x, y))

        if flags & wx.LIST_HITTEST_ONITEM:
            self.list.Select(item)

        event.Skip()

    def getColumnText(self, index, col):
        item = self.list.GetItem(index, col)
        return item.GetText()

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
        word = self.getColumnText(self.list.GetFirstSelected(), 0)
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
        item=self.getColumnText(self.list.GetFirstSelected(), 0)
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
#        for uce in uce_ok:
#            content = ' '+' '.join(corpus.ucis_paras_uces[uce[0]][uce[1]][uce[2]])+' '
#            for form in listmot :
#                sp = ''
#                i = 0
#                forme = ' ' + form + ' '
#                while i < len(content):
#                    coordword = content[i:].find(forme)
#                    if coordword != -1 and i == 0:
#                        txt += '<br><b>' + ' '.join(corpus.ucis[uce[0]][0]) + '</b><br>'
#                        if coordword < avap:
#                            sp = '&nbsp;' * (avap - coordword)
#                            deb = i
#                        else:
#                            deb = i + coordword - avap
#                        if len(content) < i + coordword + avap:
#                            fin = len(content) - 1
#                        else:
#                            fin = i + coordword + avap
#                        txt += '<TT>' + sp + content[deb:fin].replace(forme, '<font color=red>' + forme + '</font>') + '</TT><br>'
#                        i += coordword + len(forme)
#                        sp = ''
#                    elif coordword != -1 and i != 0 :
#                        if coordword < avap:
#                            sp = '&nbsp;' * (avap - coordword)
#                            deb = i
#                        else:
#                            deb = i + coordword - avap
#                        if len(content) < i + coordword + avap:
#                            fin = len(content) - 1
#                        else:
#                            fin = i + coordword + avap
#                        txt += '<TT>' + sp + content[deb:fin].replace(forme, '<font color=red>' + forme + '</font>') + '</TT><br>'
#                        i += coordword + len(forme)
#                        sp = ''                   
#                    else:
#                        i = len(content)
#                        sp = ''
        win.HtmlPage.SetPage(txt)
        win.Show(True)

    def OnPopupThree(self, event) :
        datas = [self.dlist[self.list.GetItemData(self.list.GetFirstSelected())]]
        last = self.list.GetFirstSelected()
        while self.list.GetNextSelected(last) != -1:
            last = self.list.GetNextSelected(last)
            data = self.dlist[self.list.GetItemData(last)]
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

    def OnSize(self, event):
        w,h = self.GetClientSizeTuple()
        self.list.SetDimensions(0, 0, w, h)
        
    def OnColClick(self,event):
        self.do_greyline()

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
