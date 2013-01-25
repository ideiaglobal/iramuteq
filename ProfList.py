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
import  wx.lib.mixins.listctrl  as  listmix
from tabsimi import DoSimi
from listlex import ListForSpec
from chemins import ConstructPathOut, ffr
from dialog import PrefExport, PrefUCECarac, SearchDial, message
from tableau import Tableau
from search_tools import SearchFrame
import webbrowser
import cStringIO
import tempfile
import codecs
from functions import exec_rcode, MessageImage, progressbar, treat_var_mod
from PrintRScript import barplot
from textclassechd import ClasseCHD
from shutil import copyfile

#---------------------------------------------------------------------------
class ProfListctrlPanel(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin, listmix.ColumnSorterMixin):
    def __init__(self, parent, gparent, profclasse, Alceste=False, cl=0):
        wx.ListCtrl.__init__( self, parent, -1, style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)

        self.parent = parent
        self.Alceste = Alceste
        self.Source = gparent
        self.cl = cl
        self.var_mod = {}

        line1 = profclasse.pop(0)
        classen = [line for line in profclasse if line[0] != '*' and line[0] != '*****']
        try :
            self.lenact = profclasse.index([u'*****', u'*', u'*', u'*', u'*', u'*', '', ''])
            profclasse.pop(self.lenact)
        except ValueError:
            try :
                self.lenact = profclasse.index([u'*', u'*', u'*', u'*', u'*', u'*', '', ''])
                profclasse.pop(self.lenact)
            except ValueError:
                self.lenact = len(profclasse)
        try :
            self.lensup = profclasse.index([u'*', u'*', u'*', u'*', u'*', u'*', '', ''])
            self.lensup = self.lensup - self.lenact
            profclasse.pop(self.lensup)
        except ValueError: 
            self.lensup = len(profclasse) - self.lenact
        self.lenet = len(profclasse) - (self.lenact + self.lensup)
#        print self.lenact, self.lensup, self.lenet
        for i,  line in enumerate(classen) :
            line[0] = i
        dictdata = dict(zip([i for i in range(0,len(classen))], classen))

        if self.lenact != 0 :
            self.la = [dictdata[i][6] for i in range(0, self.lenact)]
            self.lchi = [dictdata[i][4] for i in range(0, self.lenact)]
            self.lfreq = [dictdata[i][1] for i in range(0, self.lenact)]
        else :
            self.la = []
            self.lchi = []
            self.lfreq = []
        self.tmpchi = None
            
        #adding some art
        self.il = wx.ImageList(16, 16)
        a={"sm_up":"GO_UP","sm_dn":"GO_DOWN","w_idx":"WARNING","e_idx":"ERROR","i_idx":"QUESTION"}
        for k,v in a.items():
            s="self.%s= self.il.Add(wx.ArtProvider_GetBitmap(wx.ART_%s,wx.ART_TOOLBAR,(16,16)))" % (k,v)
            exec(s)
        self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

        #adding some attributes (colourful background for each item rows)
        self.attr1 = wx.ListItemAttr()
        self.attr1.SetBackgroundColour((220, 220, 220))
        self.attrsg = wx.ListItemAttr()
        self.attrsg.SetBackgroundColour((230, 230, 230))
        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour((190, 249, 236))
        self.attr2s = wx.ListItemAttr()
        self.attr2s.SetBackgroundColour((211, 252, 244))        
        self.attr3 = wx.ListItemAttr()
        self.attr3.SetBackgroundColour((245, 180, 180))
        self.attr3s = wx.ListItemAttr()
        self.attr3s.SetBackgroundColour((245, 190, 190))


        self.InsertColumn(0, "num", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(1, "eff. uce", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(2, "eff. total", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(3, "pourcentage", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(4, "chi2", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(5, "Type", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(6, "forme", wx.LIST_FORMAT_RIGHT)
        self.InsertColumn(7, "p", wx.LIST_FORMAT_RIGHT)
        

        self.SetColumnWidth(0, 60)
        self.SetColumnWidth(1, 70)
        self.SetColumnWidth(2, 80)
        self.SetColumnWidth(3, 100)
        self.SetColumnWidth(4, 70)
        self.SetColumnWidth(5, 60)
        self.SetColumnWidth(6, 140)
        self.SetColumnWidth(7, wx.LIST_AUTOSIZE)

        #These two should probably be passed to init more cleanly
        #setting the numbers of items = number of elements in the dictionary
        self.itemDataMap = dictdata
        self.itemIndexMap = dictdata.keys()
        self.SetItemCount(len(dictdata))
        
        #mixins
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        listmix.ColumnSorterMixin.__init__(self, len(classen[0]))

        #sort by genre (column 2), A->Z ascending order (1)
        self.SortListItems(0, 1)

        #events
        #self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
        #self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
        #self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)
        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)

        # for wxMSW
        self.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)

        # for wxGTK
        self.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)

        #for searching
        search_id = wx.NewId()
        searchall_id = wx.NewId()
        self.parent.Bind(wx.EVT_MENU, self.onsearch, id = search_id)
        self.parent.Bind(wx.EVT_MENU, self.onsearchall, id = searchall_id)
        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), search_id),
                                              (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), searchall_id)])
        self.SetAcceleratorTable(self.accel_tbl)



    def OnColClick(self,event):
        event.Skip()

    def OnItemSelected(self, event):
        self.currentItem = event.m_itemIndex

    def OnItemActivated(self, event):
        self.currentItem = event.m_itemIndex

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def OnItemDeselected(self, evt):
        pass
    #---------------------------------------------------
    # These methods are callbacks for implementing the
    # "virtualness" of the list...

    def OnGetItemText(self, item, col):
        index=self.itemIndexMap[item]
        s = self.itemDataMap[index][col]
        return s

    def OnGetItemImage(self, item):
        index=self.itemIndexMap[item]
        genre=self.itemDataMap[index][2]

        if genre=="Rock":
            return self.w_idx
        elif genre=="Jazz":
            return self.e_idx
        elif genre=="New Age":
            return self.i_idx
        else:
            return -1

    def OnGetItemAttr(self, item):
        index=self.itemIndexMap[item]
        if index < self.lenact :
            if item % 2 :
                return self.attr1
            else :
                return self.attrsg
        elif index >= self.lenact and index < (self.lenact + self.lensup) :
            if item % 2 :
                return self.attr2
            else :
                return self.attr2s
        elif index >= (self.lenact + self.lensup) :
            if item % 2 :
                return self.attr3
            else :
                return self.attr3s
        else :
            return None

    #---------------------------------------------------
    # Matt C, 2006/02/22
    # Here's a better SortItems() method --
    # the ColumnSorterMixin.__ColumnSorter() method already handles the ascending/descending,
    # and it knows to sort on another column if the chosen columns have the same value.

    def SortItems(self,sorter=cmp):
        items = list(self.itemDataMap.keys())
        items.sort(sorter)
        self.itemIndexMap = items
        
        # redraw the list
        self.Refresh()

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetListCtrl(self):
        return self

    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
    def GetSortImages(self):
        return (self.sm_dn, self.sm_up)

    def onsearch(self, evt) :
        self.dial = SearchDial(self, self, 6, True)
        self.dial.CenterOnParent()
        self.dial.ShowModal()
        self.dial.Destroy()

    def onsearchall(self, evt) :
        if 'FrameSearch' not in dir(self.Source) :
            self.Source.FrameSearch = SearchFrame(self.parent, -1, u"Rechercher...", self.Source.corpus)
        self.dial = SearchDial(self, self.Source.FrameSearch.liste, 1, False)
        self.dial.CenterOnParent()
        self.dial.ShowModal()
        self.dial.Destroy()

    def OnRightClick(self, event):

        # only do this part the first time so the events are only bound once
        if self.Alceste:
            if not hasattr(self, "popupID1"):
                self.popupID1 = wx.NewId()
                self.popupID2 = wx.NewId()
                self.popupID3 = wx.NewId()
                self.popupID4 = wx.NewId()
                self.popupID5 = wx.NewId()
                self.popupID6 = wx.NewId()
                self.popupID7 = wx.NewId()
                self.popupID8 = wx.NewId()
                self.popupID9 = wx.NewId()
                #self.popupID10 = wx.NewId()
                self.popupIDgraph = wx.NewId()
                self.idseg = wx.NewId()
                self.iducecarac = wx.NewId()
                self.idtablex = wx.NewId()
                self.idchimod = wx.NewId()
                self.idwordgraph = wx.NewId()
                self.popup_proxe = wx.NewId()
                self.idlexdendro = wx.NewId()
                self.idexport = wx.NewId()
            #    self.export_classes = wx.NewId()
   
                self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
                self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
                self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
                self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
                self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
                self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
                self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
                self.Bind(wx.EVT_MENU, self.OnPopupHeight, id=self.popupID8)
                self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
                #self.Bind(wx.EVT_MENU, self.OnPopupSpec, id=self.popupID10)
                self.Bind(wx.EVT_MENU, self.on_graph, id=self.popupIDgraph)
                self.Bind(wx.EVT_MENU, self.on_segments, id=self.idseg)
                self.Bind(wx.EVT_MENU, self.on_uce_carac, id = self.iducecarac)
                self.Bind(wx.EVT_MENU, self.on_tablex, id = self.idtablex)
                self.Bind(wx.EVT_MENU, self.quest_var_mod, id = self.idchimod)
                self.Bind(wx.EVT_MENU, self.onwordgraph, id = self.idwordgraph)
                self.Bind(wx.EVT_MENU, self.onproxe, id = self.popup_proxe)
                self.Bind(wx.EVT_MENU, self.onlexdendro, id = self.idlexdendro)
                self.Bind(wx.EVT_MENU, self.onexport, id = self.idexport)
             #  self.Bind(wx.EVT_MENU, self.on_export_classes, id = self.export_classes)
   #            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
    
            # make a menu
            menu = wx.Menu()
            menu.Append(self.popupID1, u"Formes associées")
            menu.Append(self.idtablex, u"Chi2 par classe")
            menu.Append(self.idlexdendro, u"Chi2 par classe + dendro")
            menu.Append(self.idchimod, u"Chi2 modalités de la variable")
            menu.Append(self.idwordgraph, u"Graphe du mot")
            #menu.Append(self.export_classes, u"Exporter le corpus...") 
            
            #menu.Append(self.popupID10, u"Spécificités")

            menu_conc = wx.Menu()
            menu_conc.Append(self.popupID2, u"dans les uce de la classe")
            menu_conc.Append(self.popupID3, u"dans les uce classées")
            menu_conc.Append(self.popupID4, u"dans toutes les uce")
            menu.AppendMenu(-1, u"Concordancier", menu_conc) 
            menu_cnrtl = wx.Menu()      
            menu_cnrtl.Append(self.popupID5, u"Définition")
            menu_cnrtl.Append(self.popupID6, u"Etymologie")
            menu_cnrtl.Append(self.popupID7, u"Synonymie")
            menu_cnrtl.Append(self.popupID8, u"Antonymie")
            menu_cnrtl.Append(self.popupID9, u"Morphologie")
            menu_cnrtl.Append(self.popup_proxe, u"Proxémie")
            menu.AppendMenu(-1, u"Outils du CNRTL", menu_cnrtl)
            menu.AppendSeparator()
            menu.Append(self.popupIDgraph, u"Graphe de la classe")
            menu.Append(self.idseg, u"Segments répétés")
            menu.Append(self.iducecarac, u"UCE caractéristiques")
            menu.Append(self.idexport, 'Partitionner...')
            #menu.Append(self.popupID2, u"Concordancier")
    #        menu.Append(self.popupID3, "recharger")
    
            self.PopupMenu(menu)
            menu.Destroy()
        elif 'tableau' in dir(self.Source) :
            if not hasattr(self, "pop1"):
                self.pop1 = wx.NewId()
                self.pop2 = wx.NewId()
                self.pop3 = wx.NewId()
                self.Bind(wx.EVT_MENU, self.quest_simi, id=self.pop1)
                self.Bind(wx.EVT_MENU, self.on_tablex, id=self.pop2)
                self.Bind(wx.EVT_MENU, self.quest_var_mod, id=self.pop3)

            menu = wx.Menu()
            menu.Append(self.pop2, u"Chi2 par classe")
            menu.Append(self.pop3, u"Chi2 modalités de la variable")
            menu.AppendSeparator()
            menu.Append(self.pop1, u"Graph de la classe")
            self.PopupMenu(menu)
            menu.Destroy()

    def onexport(self, evt) :
        if 'corpus' in dir(self.Source):
            corpus = self.Source.corpus
        ClasseCHD(self.parent, corpus, self.cl)

    def getselectedwords(self) :
        words = [self.getColumnText(self.GetFirstSelected(), 6)]
        last = self.GetFirstSelected()
        while self.GetNextSelected(last) != -1:
            last = self.GetNextSelected(last)
            words.append(self.getColumnText(last, 6))
        return words

    def quest_var_mod(self, evt) :
        if 'corpus' in dir(self.Source):
            corpus = self.Source.corpus
            if self.var_mod == {} :
                self.var_mod = self.Source.corpus.make_etoiles_dict()
        else :
            corpus = self.Source.tableau
            if self.var_mod == {} :
                self.var_mod = treat_var_mod([val for val in corpus.actives] + [val for val in corpus.sups])
        with codecs.open(self.Source.pathout['chisqtable'], 'r', corpus.parametres['syscoding']) as f :
            chistable = [line.replace('\n','').replace('\r','').replace('"','').replace(',','.').split(';') for line in f]
        title = chistable[0]
        title.pop(0)
        chistable.pop(0)
        vchistable = [line[1:] for line in chistable]
        fchistable = [line[0] for line in chistable]
        word = self.getselectedwords()[0]
        if len(word.split('_')) > 1 :
            var = word.split('_')
            words = ['_'.join([var[0],word]) for word in self.var_mod[var[0]]]
            words.sort()
            tableout = []
            kwords = []
            for word in words :
                if word in fchistable :
                    tableout.append(vchistable[fchistable.index(word)])
                    kwords.append(word)
            tmpgraph = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
            txt = barplot(tableout, kwords, title, self.Source.parent.RscriptsPath['Rgraph'], tmpgraph)
            tmpscript = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
            file = open(tmpscript,'w')
            file.write(txt)
            file.close()
            exec_rcode(self.Source.parent.RPath, tmpscript, wait = True)
            win = MessageImage(self,u"Graphique", size=(700, 500))
            win.addsaveimage(tmpgraph)
            txt = "<img src='%s'>" % tmpgraph
            win.HtmlPage.SetPage(txt)
            win.Show(True)
        else :
            dial = wx.MessageDialog(self, u"Ce n'est pas une forme du type variable_modalité", u"Problème", wx.OK | wx.ICON_WARNING)
            dial.CenterOnParent()
            dial.ShowModal()
            dial.Destroy()

    def quest_simi(self, evt) :
        tableau = self.Source.tableau
        tab = tableau.make_table_from_classe(self.cl, self.la)
        pathout = ConstructPathOut(os.path.join(self.Source.pathout, 'simi_classe_%i' %self.cl))
        self.filename = os.path.join(pathout,'mat01.csv')
        tableau.printtable(self.filename, tab)
        del tab
        paramsimi = {'coeff' : 0,
                          'layout' : 2,
                          'type' : 1,
                          'arbremax' : 1,
                          'coeff_tv' : 1,
                          'coeff_tv_nb' : 0,
                          'tvprop' : 0,
                          'tvmin' : 5,
                          'tvmax' : 30,
                          'coeff_te' : 1,
                          'coeff_temin' : 1,
                          'coeff_temax' : 10,
                          'label_v': 1,
                          'label_e': 1,
                          'vcex' : 0,
                          'vcexmin' : 10,
                          'vcexmax' : 25,
                          'cex' : 10,
                          'cexfromchi' : True,
                          'sfromchi': False,
                          'seuil_ok' : 0,
                          'seuil' : 1,
                          'cols' : (255,0,0),
                          'cola' : (200,200,200),
                          'width' : 1000,
                          'height' : 1000,
                          'first' : True,
                          'keep_coord' : True,
                          'alpha' : 20,
                          'film': False,
                          }
#        self.tableau.actives = {}
#        self.tableau.lchi = self.lchi
#        self.tableau.chi = {}
#        for i, val in enumerate(self.la) :
#            self.tableau.actives[val] = [self.lfreq[i]]
#            self.tableau.chi[val] = [self.lchi[i]]
                          
        act = {}
        self.tableau.chi = {}
        self.tableau.lchi = self.lchi
        self.tableau.parametre['fromprof'] = True
        for i, val in enumerate(self.la) :
            act[val] = [self.lfreq[i]]
            self.tableau.chi[val] = [self.lchi[i]]
        DoSimi(self, param = paramsimi, fromprof = ffr(self.filename), pathout = pathout, listactives = self.la, actives = act)

    def onwordgraph(self, evt):
        word = self.getColumnText(self.GetFirstSelected(), 6)
        if self.tmpchi is None :
            self.tmpchi = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
            with open(self.tmpchi, 'w') as f:
                f.write('\n'.join([str(val) for val in self.lchi]))
        index = self.la.index(word)
        parametres = {'type' : 'clustersimitxt', 
                        'pathout' : self.Source.parametres['pathout'],
                        'word' : index ,
                        'lem' : self.Source.parametres['lem'],
                        'tmpchi' : self.tmpchi}
        #try :
        self.parent.SimiFromCluster(self.parent, self.Source.corpus, self.la, self.cl - 1, parametres = parametres, dlg = progressbar(self, 4))
        #except :
        #    print 'not acitve'

    def on_graph(self, evt):
        if self.tmpchi is None :
            self.tmpchi = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
            with open(self.tmpchi, 'w') as f:
                f.write('\n'.join([str(val) for val in self.lchi]))
        parametres = {'type' : 'clustersimitxt', 
                        'pathout' : self.Source.parametres['pathout'],
                        'lem' : self.Source.parametres['lem'],
                        'tmpchi' : self.tmpchi}

        self.parent.SimiFromCluster(self.parent, self.Source.corpus, self.la, self.cl - 1, parametres = parametres, dlg = progressbar(self, 4))
        #dlg = progressbar(self, 2)
        #corpus = self.Source.corpus
        #uces = corpus.lc[self.cl-1]
        #dlg.Update(1, u'Tableau...')
        ##tab = corpus.make_table_with_classe(uces, self.la)
        #pathout = ConstructPathOut(self.Source.pathout.dirout+'/', 'simi_classe_%i' %self.cl)
        #self.filename = os.path.join(pathout,'mat01.csv')
        #dlg.Update(2, u'Ecriture...')
        ##corpus.write_tab(tab, self.filename)
        ##del tab
        #corpus.make_and_write_sparse_matrix_from_classe(self.la, uces, self.filename)
        #dlg.Destroy()
        #paramsimi = {'coeff' : 0,
        #                  'layout' : 2,
        #                  'type' : 1,
        #                  'arbremax' : 1,
        #                  'coeff_tv' : 1,
        #                  'coeff_tv_nb' : 0,
        #                  'tvprop' : 0,
        #                  'tvmin' : 5,
        #                  'tvmax' : 30,
        #                  'coeff_te' : 1,
        #                  'coeff_temin' : 1,
        #                  'coeff_temax' : 10,
        #                  'label_v': 1,
        #                  'label_e': 0,
        #                  'vcex' : 0,
        #                  'vcexmin' : 10,
        #                  'vcexmax' : 25,
        #                  'cex' : 10,
        #                  'cexfromchi' : True,
        #                  'sfromchi': False,
        #                  'seuil_ok' : 0,
        #                  'seuil' : 1,
        #                  'cols' : (255,0,0),
        #                  'cola' : (200,200,200),
        #                  'width' : 1000,
        #                  'height' : 1000,
        #                  'first' : True,
        #                  'keep_coord' : True,
        #                  'alpha' : 20,
        #                  'film': False,
        #                  }
        #self.tableau = Tableau(self.parent, '')
        #self.tableau.listactives = self.la
        #self.tableau.actives = {}
        #self.tableau.lchi = self.lchi
        #self.tableau.chi = {}
        #self.tableau.parametre['fromprof'] = True
        #for i, val in enumerate(self.la) :
        #    self.tableau.actives[val] = [self.lfreq[i]]
        #    self.tableau.chi[val] = [self.lchi[i]]
        #DoSimi(self, param = paramsimi, fromprof = ffr(self.filename), pathout = pathout)

    def on_segments(self,evt) :
        dlg = progressbar(self, 2)
        corpus = self.Source.corpus
        uces = corpus.lc[self.cl-1]
        l = []
        dlg.Update(1, u'Segments...')
        for i in range(2,10) :
            li = corpus.find_segments_in_classe(uces, i, 1000)
            if li == [] :
                break
            else :
                l += li
        l.sort(reverse = True)
        d = {}
        dlg.Update(2, 'Tri...')
        for i, line in enumerate(l) :
            d[i] = [line[1],line[0], line[2]]
        first = ['','','']
        para={'dico': d,'fline':first}
        dlg.Destroy()
        win = wliste(self, -1, u"Segments répétés - Classe %i" % self.cl, d, first, size=(600, 500))
        win.Show(True)

    def on_uce_carac(self,evt) :
        dial = PrefUCECarac(self, self.parent)
        dial.CenterOnParent()
        if dial.ShowModal() == wx.ID_OK :
            limite = dial.spin_eff.GetValue()
            atype = dial.radio_type.GetSelection()
            dlg = progressbar(self,maxi = 4)
            corpus = self.Source.corpus
            uces = corpus.lc[self.cl-1]
            tab = corpus.make_table_with_classe(uces, self.la)
            tab.pop(0)
            dlg.Update(2, u'score...')
            if atype == 0 :
                ntab = [round(sum([self.lchi[i] for i, word in enumerate(line) if word == 1]),2) for line in tab]
            else :
                ntab = [round(sum([self.lchi[i] for i, word in enumerate(line) if word == 1])/float(sum(line)),2) if sum(line)!=0 else 0 for line in tab]
            ntab2 = [[ntab[i], uces[i]] for i, val in enumerate(ntab)]
            del ntab
            ntab2.sort(reverse = True)
            ntab2 = ntab2[:limite]
            nuces = [val[1] for val in ntab2]
            dlg.Update(3, u'concordancier...')
            #ucestxt = [corpus.ucis_paras_uces[val[1][0]][val[1][1]][val[1][2]] for val in ntab2]
            ucestxt1 = [row for row in corpus.getconcorde(nuces)]
            ucestxt = []
            ucis_txt = []
            for uce in ucestxt1 :
                ucetxt = ' '+uce[1]+' '
                ucis_txt.append(' '.join(corpus.ucis[corpus.getucefromid(uce[0]).uci].etoiles) + '<br>')
                for lem in self.la :
                    listmot = corpus.getlems()[lem].formes
                    for id in listmot :
                        forme = corpus.getforme(id).forme
                        ucetxt = ucetxt.replace(' '+forme+' ', '<font color=red> ' + forme + ' </font>')
                ucestxt.append(ucetxt)        
            #ucestxt = [corpus.make_concord(self.la, ' '.join(uce), 'red') for uce in ucestxt]
            dlg.Update(4, u'texte...')
            #ucis_txt = [' '.join(corpus.ucis[val[1][0]][0]) for val in ntab2]
            win = message(self, u"UCE caractéristiques - Classe %i" % self.cl, (750, 600))
            win.html = '<html>\n' + '<br><br>'.join(['<br>'.join([ucis_txt[i], 'score : ' + str(ntab2[i][0]), ucestxt[i]]) for i in range(0,len(ucestxt))]) + '\n</html>'
            win.HtmlPage.SetPage(win.html)
            dlg.Destroy()
            win.Show(True)
    
    def on_tablex(self, evt):
        if 'corpus' in dir(self.Source):
            corpus = self.Source.corpus
        else :
            corpus = self.Source.tableau
        with codecs.open(self.Source.pathout['chisqtable'], 'r', corpus.parametres['syscoding']) as f :
            chistable = [line.replace('\n','').replace('\r','').replace('"','').replace(',','.').split(';') for line in f]
        title = chistable[0]
        title.pop(0)
        chistable.pop(0)
        vchistable = [line[1:] for line in chistable]
        fchistable = [line[0] for line in chistable]
        words = self.getselectedwords()
        tableout = [vchistable[fchistable.index(word)] for word in words]
        tmpgraph = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
        nbcl = len(title)
        nbwords = len(words)
        txt = barplot(tableout, words, title, self.Source.parent.RscriptsPath['Rgraph'], tmpgraph)
        tmpscript = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
        file = open(tmpscript,'w')
        file.write(txt)
        file.close()
        exec_rcode(self.Source.parent.RPath, tmpscript, wait = True)
        w = 100 + (20 * nbwords) + (100 * nbcl)
        h = 100 + (nbwords * 15)
        if w > 1100 : w = 1100
        if h > 800 : h = 800
        if h < 450 : h = 450
        win = MessageImage(self, u"Graphique", size=(w, h))
        win.addsaveimage(tmpgraph)
        txt = "<img src='%s'>" % tmpgraph
        win.HtmlPage.SetPage(txt)
        win.Show(True)

    def onlexdendro(self, evt):
        if 'corpus' in dir(self.Source):
            corpus = self.Source.corpus
        else :
            corpus = self.Source.tableau
        with codecs.open(self.Source.pathout['chisqtable'], 'r', corpus.parametres['syscoding']) as f :
            chistable = [line.replace('\n','').replace('\r','').replace('"','').replace(',','.').split(';') for line in f]
        title = chistable[0]
        title.pop(0)
        chistable.pop(0)
        vchistable = [line[1:] for line in chistable]
        fchistable = [line[0] for line in chistable]
        words = self.getselectedwords()
        tableout = [vchistable[fchistable.index(word)] for word in words]
        tmpgraph = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
        txttable = 'c(' + ','.join([','.join(line) for line in tableout]) + ')'
        rownames = 'c("' + '","'.join(words) + '")'
        colnames = 'c("' + '","'.join(title) + '")'
        nbcl = len(title)
        rownb = len(words)
        txt = """
        load("%s")
        di <- matrix(data=%s, nrow=%i, byrow = TRUE)
        rownames(di)<- %s
        colnames(di) <- %s
        library(ape)
        source("%s")
        height <- (30*ncol(di)) + (15*nrow(di))
        height <- ifelse(height <= 400, 400, height)
        width <- 500
        open_file_graph("%s", width=width, height=height)
        plot.dendro.lex(tree.cut1$tree.cl, di)
        """ % (self.Source.pathout['Rdendro'], txttable, rownb, rownames, colnames, self.Source.parent.RscriptsPath['Rgraph'], ffr(tmpgraph))
        tmpscript = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
        file = open(tmpscript,'w')
        file.write(txt)
        file.close()
        exec_rcode(self.Source.parent.RPath, tmpscript, wait = True)
        win = MessageImage(self, u"Graphique", size=(700, 500))
        win.addsaveimage(tmpgraph)
        txt = "<img src='%s'>" % tmpgraph
        win.HtmlPage.SetPage(txt)
        win.Show(True)


    def make_concord(self, uces, title, color = 'red') :
        corpus = self.Source.corpus
        ListWord = [self.getColumnText(self.GetFirstSelected(), 6)]
        last = self.GetFirstSelected()
        while self.GetNextSelected(last) != -1:
            last = self.GetNextSelected(last)
            ListWord.append(self.getColumnText(last, 6))
        listmot = [forme for item in ListWord for forme in corpus.getlems()[item].formes]
        win = message(self, title, size=(750, 600))
        toshow = ['<html>\n<H1>Concordancier</H1>\n']
        toshow.append('<h3><font color=%s>' % color + ' '.join(ListWord) + '</font></h3><br>')
        duce = {}
        ucef = []
        for word in ListWord : 
            ucef += list(set(corpus.getlemuces(word)).intersection(uces))
        ucef = list(set(ucef))
        ucef.sort()
        res = corpus.getconcorde(ucef)
        txt = '<br>'.join(toshow) +'<br><br>'
        for uce in res :
            ucetxt = ' '+uce[1]+' '
            txt += ' '.join(corpus.ucis[corpus.getucefromid(uce[0]).uci].etoiles) + '<br>'
            for forme in listmot:
                forme = corpus.getforme(forme).forme
                ucetxt = ucetxt.replace(' '+forme+' ', '<font color=red> ' + forme + ' </font>')
            txt += ucetxt + '<br><br>'
        win.HtmlPage.SetPage(txt)
        return win

    def OnPopupTwo(self, event):
        corpus = self.Source.corpus
        uces = corpus.lc[self.cl-1]
        win = self.make_concord(uces, "Concordancier - Classe %i" % self.cl)
        win.Show(True)
    
    def OnPopupThree(self, event):
        corpus = self.Source.corpus
        uces = [classe[i] for classe in corpus.lc for i in range(0,len(classe))]
        win = self.make_concord(uces, "Concordancier - UCE classées")
        win.Show(True)
        
    def OnPopupFour(self, event):
        corpus = self.Source.corpus
        uces = [classe[i] for classe in corpus.lc for i in range(0,len(classe))] + corpus.lc0
        win = self.make_concord(uces, "Concordancier - Toutes les UCE")
        win.Show(True)

    def OnPopupFive(self, event):
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lk = "http://www.cnrtl.fr/definition/" + word
        webbrowser.open(lk)

    def OnPopupSix(self, event):  
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lk = "http://www.cnrtl.fr/etymologie/" + word
        webbrowser.open(lk)
        
    def OnPopupSeven(self, event):        
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lk = "http://www.cnrtl.fr/synonymie/" + word
        webbrowser.open(lk)
        
    def OnPopupHeight(self, event):  
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lk = "http://www.cnrtl.fr/antonymie/" + word
        webbrowser.open(lk)
        
    def OnPopupNine(self, event):            
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lk = "http://www.cnrtl.fr/morphologie/" + word
        webbrowser.open(lk)

    def onproxe(self, evt) :
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lk = "http://www.cnrtl.fr/proxemie/" + word
        webbrowser.open(lk)
#

#---------------------------------------------------------------------------
#class ProfListctrl(wx.ListCtrl, listmix.ListCtrlAutoWidthMixin):
#    def __init__(self, parent, ID, pos=wx.DefaultPosition,
#                 size=wx.DefaultSize, style=0):
#        wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
#        listmix.ListCtrlAutoWidthMixin.__init__(self)
#
#
#class ProfListctrlPanel(wx.Panel, listmix.ColumnSorterMixin):
#    def __init__(self, parent, gparent, ProfClasse, Alceste=False, cl=0):
#        self.parent = parent
#        classe = ProfClasse
#        self.cl = cl
#        self.Source = gparent
#        if 'tableau' in dir(self.Source):
#            self.tableau = self.Source.tableau
#        self.Alceste = Alceste
#        self.var_mod = {}
#        
#
#        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
#        
#        search_id = wx.NewId()
#        searchall_id = wx.NewId()
#        self.parent.Bind(wx.EVT_MENU, self.onsearch, id = search_id)
#        self.parent.Bind(wx.EVT_MENU, self.onsearchall, id = searchall_id)
#        self.accel_tbl = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('F'), search_id),
#                                              (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, ord('F'), searchall_id)])
#        self.SetAcceleratorTable(self.accel_tbl)
#       
#        self.il = wx.ImageList(16, 16)
##        self.idx1 = self.il.Add(images.getSmilesBitmap())
#        self.sm_up = self.il.Add(getSmallUpArrowBitmap())
#        self.sm_dn = self.il.Add(getSmallDnArrowBitmap())
#        tID = wx.NewId()
#
#        self.list = ProfListctrl(self, tID,
#                                 style=wx.LC_REPORT 
#                                 | wx.BORDER_NONE
#                                 | wx.LC_EDIT_LABELS
#                                 | wx.LC_SORT_ASCENDING
#                                 )
#        line1 = classe.pop(0)
#        limit = 0
#        limitsup = 0
#        i = 0
#        dictdata = {}
#        classen = [line for line in classe if line[0] != '*' and line[0] != '*****']
#        if len(classen) == 0 :
#            lenact = 0
#            lensup = 0
#            lenet = 0
#        else :
#            lenact = [i for i,b in enumerate(classe) if b[0] == '*****']
#            if lenact == [] :
#                lensup = 0
#                lenact = [i for i,b in enumerate(classe) if b[0] == '*']
#                if lenact == [] :
#                    lenact = len(classen)
#                    lenet = 0
#                else :
#                    lenact = 0
#                    lenet = len(classen)
#            else :
#                lenact = lenact[0]
#                lensup = [i for i,b in enumerate(classe[1:]) if b[0] == '*']
#                if lensup != [] :
#                   lensup = lensup[0] - lenact
#                   lenet = len(classen) - lensup
#                else :
#                   lensup == 0
#                   lenet = len(classen)
#        debsup = lenact
#                
#        self.lenact = lenact
#
#        debet = lenact + lensup
#        dictdata = dict(zip([i for i in range(0,len(classen))], classen))
#        self.list.SetImageList(self.il, wx.IMAGE_LIST_SMALL)
#        
#        self.PopulateList(dictdata, debet, debsup, Alceste)
#
#        self.Bind(wx.EVT_SIZE, self.OnSize)
#        self.Bind(wx.EVT_LIST_COL_CLICK, self.OnColClick)
#        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected, self.list)
#
#        # for wxMSW
#        self.list.Bind(wx.EVT_COMMAND_RIGHT_CLICK, self.OnRightClick)
#
#        # for wxGTK
#        self.list.Bind(wx.EVT_RIGHT_UP, self.OnRightClick)
#        self.itemDataMap = dictdata
#        listmix.ColumnSorterMixin.__init__(self, 8)
#        self.do_greyline()
##-----------------------------------------------------------------------------------------    
#
#    def PopulateList(self, dictdata, limit, limitsup, Alceste):
#        
#        
#            # for normal, simple columns, you can add them like this:
#        self.list.InsertColumn(0, "num", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(1, "eff. uce", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(2, "eff. total", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(3, "pourcentage", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(4, "chi2", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(5, "Type", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(6, "forme", wx.LIST_FORMAT_RIGHT)
#        self.list.InsertColumn(7, "p", wx.LIST_FORMAT_RIGHT)
#        
#        for key in dictdata : #.iteritems():
#                index = self.list.InsertStringItem(sys.maxint, '%4i' % key)
#                i = 1
#                for val in dictdata[key][1:]:
#                    self.list.SetStringItem(index, i, str(dictdata[key][i]))
#                    i += 1
#                self.list.SetItemData(index, key)
#
#        self.list.SetColumnWidth(0, 60)
#        self.list.SetColumnWidth(1, 70)
#        self.list.SetColumnWidth(2, 80)
#        self.list.SetColumnWidth(3, 100)
#        self.list.SetColumnWidth(4, 70)
#        self.list.SetColumnWidth(5, wx.LIST_AUTOSIZE)
#        self.list.SetColumnWidth(6, wx.LIST_AUTOSIZE)
#        self.list.SetColumnWidth(7, wx.LIST_AUTOSIZE)
#
#        # show how to change the colour of a couple items
#        for i in range(limitsup, limit):
#            item = self.list.GetItem(i)
#            item.SetTextColour(wx.RED) 
#            self.list.SetItem(item)
#        
#        for i in range(limit, len(dictdata)):
#            item = self.list.GetItem(i)
#            item.SetTextColour(wx.BLUE)
#            self.list.SetItem(item)          
#        
#        if self.lenact != 0 :
#            self.la = [self.getColumnText(i,6) for i in range(0, self.lenact)]
#            self.lchi = [float(self.getColumnText(i,4)) for i in range(0, self.lenact)]
#            self.lfreq = [int(self.getColumnText(i,1)) for i in range(0, self.lenact)]
#        else :
#            self.la = []
#            self.lchi = []
#            self.lfreq = []
#
#    def do_greyline(self):
#        for row in xrange(self.list.GetItemCount()):
#            if row % 2 :
#                self.list.SetItemBackgroundColour(row, (230, 230, 230))
#            else :
#                self.list.SetItemBackgroundColour(row, wx.WHITE)
#
#
#    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
#    def GetListCtrl(self):
#        return self.list
#
#    # Used by the ColumnSorterMixin, see wx/lib/mixins/listctrl.py
#    def GetSortImages(self):
#        return (self.sm_dn, self.sm_up)
#
#
#    def OnRightDown(self, event):
#        x = event.GetX()
#        y = event.GetY()
#        item, flags = self.list.HitTest((x, y))
#
#        if flags & wx.LIST_HITTEST_ONITEM:
#            self.list.Select(item)
#
#        event.Skip()
#
#
#    def getColumnText(self, index, col):
#        item = self.list.GetItem(index, col)
#        return item.GetText()
#
#
#    def OnItemSelected(self, event):
#        self.currentItem = event.m_itemIndex
#        event.Skip()
#
#    def onsearch(self, evt) :
#        self.dial = SearchDial(self, self, 6, True)
#        self.dial.CenterOnParent()
#        self.dial.ShowModal()
#        self.dial.Destroy()
#
#    def onsearchall(self, evt) :
#        if 'FrameSearch' not in dir(self.Source) :
#            self.Source.FrameSearch = SearchFrame(self.parent, -1, u"Rechercher...", self.Source.corpus)
#        self.dial = SearchDial(self, self.Source.FrameSearch.liste, 1, False)
#        self.dial.CenterOnParent()
#        self.dial.ShowModal()
#        self.dial.Destroy()
#
#    def OnRightClick(self, event):
#
#        # only do this part the first time so the events are only bound once
#        if self.Alceste:
#            if not hasattr(self, "popupID1"):
#                self.popupID1 = wx.NewId()
#                self.popupID2 = wx.NewId()
#                self.popupID3 = wx.NewId()
#                self.popupID4 = wx.NewId()
#                self.popupID5 = wx.NewId()
#                self.popupID6 = wx.NewId()
#                self.popupID7 = wx.NewId()
#                self.popupID8 = wx.NewId()
#                self.popupID9 = wx.NewId()
#                #self.popupID10 = wx.NewId()
#                self.popupIDgraph = wx.NewId()
#                self.idseg = wx.NewId()
#                self.iducecarac = wx.NewId()
#                self.idtablex = wx.NewId()
#                self.idchimod = wx.NewId()
#                self.idwordgraph = wx.NewId()
#                self.popup_proxe = wx.NewId()
#                self.idlexdendro = wx.NewId()
#                self.idexport = wx.NewId()
#            #    self.export_classes = wx.NewId()
#   
#                self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
#                self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
#                self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
#                self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
#                self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
#                self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
#                self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
#                self.Bind(wx.EVT_MENU, self.OnPopupHeight, id=self.popupID8)
#                self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
#                #self.Bind(wx.EVT_MENU, self.OnPopupSpec, id=self.popupID10)
#                self.Bind(wx.EVT_MENU, self.on_graph, id=self.popupIDgraph)
#                self.Bind(wx.EVT_MENU, self.on_segments, id=self.idseg)
#                self.Bind(wx.EVT_MENU, self.on_uce_carac, id = self.iducecarac)
#                self.Bind(wx.EVT_MENU, self.on_tablex, id = self.idtablex)
#                self.Bind(wx.EVT_MENU, self.quest_var_mod, id = self.idchimod)
#                self.Bind(wx.EVT_MENU, self.onwordgraph, id = self.idwordgraph)
#                self.Bind(wx.EVT_MENU, self.onproxe, id = self.popup_proxe)
#                self.Bind(wx.EVT_MENU, self.onlexdendro, id = self.idlexdendro)
#                self.Bind(wx.EVT_MENU, self.onexport, id = self.idexport)
#              #  self.Bind(wx.EVT_MENU, self.on_export_classes, id = self.export_classes)
#    #            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
#    
#            # make a menu
#            menu = wx.Menu()
#            menu.Append(self.popupID1, u"Formes associées")
#            menu.Append(self.idtablex, u"Chi2 par classe")
#            menu.Append(self.idlexdendro, u"Chi2 par classe + dendro")
#            menu.Append(self.idchimod, u"Chi2 modalités de la variable")
#            menu.Append(self.idwordgraph, u"Graphe du mot")
#            #menu.Append(self.export_classes, u"Exporter le corpus...") 
#            
#            #menu.Append(self.popupID10, u"Spécificités")
#
#            menu_conc = wx.Menu()
#            menu_conc.Append(self.popupID2, u"dans les uce de la classe")
#            menu_conc.Append(self.popupID3, u"dans les uce classées")
#            menu_conc.Append(self.popupID4, u"dans toutes les uce")
#            menu.AppendMenu(-1, u"Concordancier", menu_conc) 
#            menu_cnrtl = wx.Menu()      
#            menu_cnrtl.Append(self.popupID5, u"Définition")
#            menu_cnrtl.Append(self.popupID6, u"Etymologie")
#            menu_cnrtl.Append(self.popupID7, u"Synonymie")
#            menu_cnrtl.Append(self.popupID8, u"Antonymie")
#            menu_cnrtl.Append(self.popupID9, u"Morphologie")
#            menu_cnrtl.Append(self.popup_proxe, u"Proxémie")
#            menu.AppendMenu(-1, u"Outils du CNRTL", menu_cnrtl)
#            menu.AppendSeparator()
#            menu.Append(self.popupIDgraph, u"Graphe de la classe")
#            menu.Append(self.idseg, u"Segments répétés")
#            menu.Append(self.iducecarac, u"UCE caractéristiques")
#            menu.Append(self.idexport, 'Partitionner...')
#            #menu.Append(self.popupID2, u"Concordancier")
#    #        menu.Append(self.popupID3, "recharger")
#    
#            self.PopupMenu(menu)
#            menu.Destroy()
#        elif 'tableau' in dir(self.Source) :
#            if not hasattr(self, "pop1"):
#                self.pop1 = wx.NewId()
#                self.pop2 = wx.NewId()
#                self.pop3 = wx.NewId()
#                self.Bind(wx.EVT_MENU, self.quest_simi, id=self.pop1)
#                self.Bind(wx.EVT_MENU, self.on_tablex, id=self.pop2)
#                self.Bind(wx.EVT_MENU, self.quest_var_mod, id=self.pop3)
#
#            menu = wx.Menu()
#            menu.Append(self.pop2, u"Chi2 par classe")
#            menu.Append(self.pop3, u"Chi2 modalités de la variable")
#            menu.AppendSeparator()
#            menu.Append(self.pop1, u"Graph de la classe")
#            self.PopupMenu(menu)
#            menu.Destroy()
#
#    def onexport(self, evt) :
#        if 'corpus' in dir(self.Source):
#            corpus = self.Source.corpus
#        ClasseCHD(self.parent, corpus, self.cl)
#
#    def quest_var_mod(self, evt) :
#        if 'corpus' in dir(self.Source):
#            corpus = self.Source.corpus
#            if self.var_mod == {} :
#                self.var_mod = treat_var_mod([val for val in corpus.make_etoiles()])
#        else :
#            corpus = self.Source.tableau
#            if self.var_mod == {} :
#                self.var_mod = treat_var_mod([val for val in corpus.actives] + [val for val in corpus.sups])
#        with codecs.open(self.Source.pathout['chisqtable'], 'r', corpus.parametres['syscoding']) as f :
#            chistable = [line.replace('\n','').replace('\r','').replace('"','').replace(',','.').split(';') for line in f]
#        title = chistable[0]
#        title.pop(0)
#        chistable.pop(0)
#        vchistable = [line[1:] for line in chistable]
#        fchistable = [line[0] for line in chistable]
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        if len(word.split('_')) > 1 :
#            var = word.split('_')[0]
#            words = [word for word in self.var_mod[var]]
#            words.sort()
#            tableout = []
#            kwords = []
#            for word in words :
#                if word in fchistable :
#                    tableout.append(vchistable[fchistable.index(word)])
#                    kwords.append(word)
#            tmpgraph = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
#            txt = barplot(tableout, kwords, title, self.Source.parent.RscriptsPath['Rgraph'], tmpgraph)
#            tmpscript = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
#            file = open(tmpscript,'w')
#            file.write(txt)
#            file.close()
#            exec_rcode(self.Source.parent.RPath, tmpscript, wait = True)
#            win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
#            win.addsaveimage(tmpgraph)
#            txt = "<img src='%s'>" % tmpgraph
#            win.HtmlPage.SetPage(txt)
#            win.Show(True)
#        else :
#            dial = wx.MessageDialog(self, u"Ce n'est pas une forme du type variable_modalité", u"Problème", wx.OK | wx.ICON_WARNING)
#            dial.CenterOnParent()
#            dial.ShowModal()
#            dial.Destroy()
#
#    def quest_simi(self, evt) :
#        tableau = self.Source.tableau
#        tab = tableau.make_table_from_classe(self.cl, self.la)
#        pathout = ConstructPathOut(self.Source.pathout+'/', 'simi_classe_%i' %self.cl)
#        self.filename = os.path.join(pathout,'mat01.csv')
#        tableau.printtable(self.filename, tab)
#        del tab
#        paramsimi = {'coeff' : 0,
#                          'layout' : 2,
#                          'type' : 1,
#                          'arbremax' : 1,
#                          'coeff_tv' : 1,
#                          'coeff_tv_nb' : 0,
#                          'tvprop' : 0,
#                          'tvmin' : 5,
#                          'tvmax' : 30,
#                          'coeff_te' : 1,
#                          'coeff_temin' : 1,
#                          'coeff_temax' : 10,
#                          'label_v': 1,
#                          'label_e': 1,
#                          'vcex' : 0,
#                          'vcexmin' : 10,
#                          'vcexmax' : 25,
#                          'cex' : 10,
#                          'cexfromchi' : True,
#                          'sfromchi': False,
#                          'seuil_ok' : 0,
#                          'seuil' : 1,
#                          'cols' : (255,0,0),
#                          'cola' : (200,200,200),
#                          'width' : 1000,
#                          'height' : 1000,
#                          'first' : True,
#                          'keep_coord' : True,
#                          'alpha' : 20,
#                          'film': False,
#                          }
##        self.tableau.actives = {}
##        self.tableau.lchi = self.lchi
##        self.tableau.chi = {}
##        for i, val in enumerate(self.la) :
##            self.tableau.actives[val] = [self.lfreq[i]]
##            self.tableau.chi[val] = [self.lchi[i]]
#                          
#        act = {}
#        self.tableau.chi = {}
#        self.tableau.lchi = self.lchi
#        self.tableau.parametre['fromprof'] = True
#        for i, val in enumerate(self.la) :
#            act[val] = [self.lfreq[i]]
#            self.tableau.chi[val] = [self.lchi[i]]
#        DoSimi(self, param = paramsimi, fromprof = ffr(self.filename), pathout = pathout, listactives = self.la, actives = act)
#
#    def onwordgraph(self, evt):
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        dlg = progressbar(self, 2)
#        corpus = self.Source.corpus
#        uces = corpus.lc[self.cl-1]
#        dlg.Update(1, u'Tableau...')
#        #tab = corpus.make_table_with_classe(uces, self.la)
#        pathout = ConstructPathOut(self.Source.pathout.dirout + '/' , 'simi_%s' % word)
#        self.filename = os.path.join(pathout,'mat01.csv')
#        dlg.Update(2, u'Ecriture...')
#        #corpus.write_tab(tab, self.filename)
#        #del tab
#        corpus.make_and_write_sparse_matrix_from_classe(self.la, uces, self.filename)
#        dlg.Destroy()
#        paramsimi = {'coeff' : 0,
#                          'layout' : 2,
#                          'type' : 1,
#                          'arbremax' : 0,
#                          'coeff_tv' : 1,
#                          'coeff_tv_nb' : 0,
#                          'tvprop' : 0,
#                          'tvmin' : 5,
#                          'tvmax' : 30,
#                          'coeff_te' : 1,
#                          'coeff_temin' : 1,
#                          'coeff_temax' : 10,
#                          'label_v': 1,
#                          'label_e': 0,
#                          'vcex' : 1,
#                          'vcexmin' : 10,
#                          'vcexmax' : 25, 
#                          'cex' : 10,
#                          'seuil_ok' : 1,
#                          'seuil' : 1,
#                          'cols' : (255,0,0),
#                          'cola' : (200,200,200),
#                          'width' : 600,
#                          'height' : 600,
#                          'first' : True,
#                          'keep_coord' : True,
#                          'alpha' : 20,
#                          'film': False,
#                          }
#        self.tableau = Tableau(self.parent, '')
#        self.tableau.listactives = self.la
#        self.tableau.actives = {}
#        for i, val in enumerate(self.la) :
#            self.tableau.actives[val] = [self.lfreq[i]]
#        DoSimi(self, param = paramsimi, fromprof = ffr(self.filename), pathout = pathout, wordgraph = word)
#
#
    def OnPopupOne(self, event):
        corpus = self.Source.corpus
        #print 'ATTENTION PRINT ET TABLE'
        #corpus.make_et_table()
        word = self.getColumnText(self.GetFirstSelected(), 6)
        lems = corpus.getlems()
        uces = corpus.lc[self.cl-1]
        rep = []
        #FIXME : donner aussi eff reel a la place de nb uce
        for forme in lems[word].formes :
            ucef = list(set(corpus.getworduces(forme)).intersection(uces))
            #ucef = [uce for uce in corpus.formes[forme][1] if uce in uces]
            if ucef != [] :
                nb = len(ucef)
                rep.append([corpus.getforme(forme).forme, nb])
        win = message(self, u"Formes associées", wx.Size(300, 200))
        win.html = '<html>\n' + '<br>'.join([' : '.join([str(val) for val in forme]) for forme in rep]) + '\n</html>'
        win.HtmlPage.SetPage(win.html)
        win.Show(True)
#
#    def on_graph(self, evt):
#        dlg = progressbar(self, 2)
#        corpus = self.Source.corpus
#        uces = corpus.lc[self.cl-1]
#        dlg.Update(1, u'Tableau...')
#        #tab = corpus.make_table_with_classe(uces, self.la)
#        pathout = ConstructPathOut(self.Source.pathout.dirout+'/', 'simi_classe_%i' %self.cl)
#        self.filename = os.path.join(pathout,'mat01.csv')
#        dlg.Update(2, u'Ecriture...')
#        #corpus.write_tab(tab, self.filename)
#        #del tab
#        corpus.make_and_write_sparse_matrix_from_classe(self.la, uces, self.filename)
#        dlg.Destroy()
#        paramsimi = {'coeff' : 0,
#                          'layout' : 2,
#                          'type' : 1,
#                          'arbremax' : 1,
#                          'coeff_tv' : 1,
#                          'coeff_tv_nb' : 0,
#                          'tvprop' : 0,
#                          'tvmin' : 5,
#                          'tvmax' : 30,
#                          'coeff_te' : 1,
#                          'coeff_temin' : 1,
#                          'coeff_temax' : 10,
#                          'label_v': 1,
#                          'label_e': 0,
#                          'vcex' : 0,
#                          'vcexmin' : 10,
#                          'vcexmax' : 25,
#                          'cex' : 10,
#                          'cexfromchi' : True,
#                          'sfromchi': False,
#                          'seuil_ok' : 0,
#                          'seuil' : 1,
#                          'cols' : (255,0,0),
#                          'cola' : (200,200,200),
#                          'width' : 1000,
#                          'height' : 1000,
#                          'first' : True,
#                          'keep_coord' : True,
#                          'alpha' : 20,
#                          'film': False,
#                          }
#        self.tableau = Tableau(self.parent, '')
#        self.tableau.listactives = self.la
#        self.tableau.actives = {}
#        self.tableau.lchi = self.lchi
#        self.tableau.chi = {}
#        self.tableau.parametre['fromprof'] = True
#        for i, val in enumerate(self.la) :
#            self.tableau.actives[val] = [self.lfreq[i]]
#            self.tableau.chi[val] = [self.lchi[i]]
#        DoSimi(self, param = paramsimi, fromprof = ffr(self.filename), pathout = pathout)
#
#    def on_segments(self,evt) :
#        dlg = progressbar(self, 2)
#        corpus = self.Source.corpus
#        uces = corpus.lc[self.cl-1]
#        l = []
#        dlg.Update(1, u'Segments...')
#        for i in range(2,10) :
#            li = corpus.find_segments_in_classe(uces, i, 1000)
#            if li == [] :
#                break
#            else :
#                l += li
#        l.sort(reverse = True)
#        d = {}
#        dlg.Update(2, 'Tri...')
#        for i, line in enumerate(l) :
#            d[i] = [line[1],line[0], line[2]]
#        first = ['','','']
#        para={'dico': d,'fline':first}
#        dlg.Destroy()
#        win = wliste(self, -1, u"Segments répétés - Classe %i" % self.cl, d, first, size=(600, 500))
#        win.Show(True)
#
#    def on_uce_carac(self,evt) :
#        dial = PrefUCECarac(self, self.parent)
#        dial.CenterOnParent()
#        if dial.ShowModal() == wx.ID_OK :
#            limite = dial.spin_eff.GetValue()
#            atype = dial.radio_type.GetSelection()
#            dlg = progressbar(self,maxi = 4)
#            corpus = self.Source.corpus
#            uces = corpus.lc[self.cl-1]
#            tab = corpus.make_table_with_classe(uces, self.la)
#            tab.pop(0)
#            dlg.Update(2, u'score...')
#            if atype == 0 :
#                ntab = [round(sum([self.lchi[i] for i, word in enumerate(line) if word == 1]),2) for line in tab]
#            else :
#                ntab = [round(sum([self.lchi[i] for i, word in enumerate(line) if word == 1])/float(sum(line)),2) if sum(line)!=0 else 0 for line in tab]
#            ntab2 = [[ntab[i], uces[i]] for i, val in enumerate(ntab)]
#            del ntab
#            ntab2.sort(reverse = True)
#            ntab2 = ntab2[:limite]
#            nuces = [val[1] for val in ntab2]
#            dlg.Update(3, u'concordancier...')
#            #ucestxt = [corpus.ucis_paras_uces[val[1][0]][val[1][1]][val[1][2]] for val in ntab2]
#            ucestxt1 = [row for row in corpus.getconcorde(nuces)]
#            ucestxt = []
#            ucis_txt = []
#            for uce in ucestxt1 :
#                ucetxt = ' '+uce[1]+' '
#                ucis_txt.append(' '.join(corpus.ucis[corpus.getucefromid(uce[0]).uci].etoiles) + '<br>')
#                for lem in self.la :
#                    listmot = corpus.getlems()[lem].formes
#                    for id in listmot :
#                        forme = corpus.getforme(id).forme
#                        ucetxt = ucetxt.replace(' '+forme+' ', '<font color=red> ' + forme + ' </font>')
#                ucestxt.append(ucetxt)        
#            #ucestxt = [corpus.make_concord(self.la, ' '.join(uce), 'red') for uce in ucestxt]
#            dlg.Update(4, u'texte...')
#            #ucis_txt = [' '.join(corpus.ucis[val[1][0]][0]) for val in ntab2]
#            win = message(self, -1, u"UCE caractéristiques - Classe %i" % self.cl, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE)
#            win.html = '<html>\n' + '<br><br>'.join(['<br>'.join([ucis_txt[i], 'score : ' + str(ntab2[i][0]), ucestxt[i]]) for i in range(0,len(ucestxt))]) + '\n</html>'
#            win.HtmlPage.SetPage(win.html)
#            dlg.Destroy()
#            win.Show(True)
#    
#    def on_tablex(self, evt):
#        if 'corpus' in dir(self.Source):
#            corpus = self.Source.corpus
#        else :
#            corpus = self.Source.tableau
#        with codecs.open(self.Source.pathout['chisqtable'], 'r', corpus.parametres['syscoding']) as f :
#            chistable = [line.replace('\n','').replace('\r','').replace('"','').replace(',','.').split(';') for line in f]
#        title = chistable[0]
#        title.pop(0)
#        chistable.pop(0)
#        vchistable = [line[1:] for line in chistable]
#        fchistable = [line[0] for line in chistable]
#        words = [self.getColumnText(self.list.GetFirstSelected(), 6)]
#        tableout = [vchistable[fchistable.index(words[0])]]
#        last = self.list.GetFirstSelected()
#        while self.list.GetNextSelected(last) != -1:
#            last = self.list.GetNextSelected(last)
#            word = self.getColumnText(last, 6)
#            words.append(word)
#            tableout.append(vchistable[fchistable.index(word)])
#        tmpgraph = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
#        nbcl = len(title)
#        txt = barplot(tableout, words, title, self.Source.parent.RscriptsPath['Rgraph'], tmpgraph)
#        tmpscript = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
#        file = open(tmpscript,'w')
#        file.write(txt)
#        file.close()
#        
#        exec_rcode(self.Source.parent.RPath, tmpscript, wait = True)
#        win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
#        win.addsaveimage(tmpgraph)
#        txt = "<img src='%s'>" % tmpgraph
#        win.HtmlPage.SetPage(txt)
#        win.Show(True)
#
#    def onlexdendro(self, evt):
#        if 'corpus' in dir(self.Source):
#            corpus = self.Source.corpus
#        else :
#            corpus = self.Source.tableau
#        with codecs.open(self.Source.pathout['chisqtable'], 'r', corpus.parametres['syscoding']) as f :
#            chistable = [line.replace('\n','').replace('\r','').replace('"','').replace(',','.').split(';') for line in f]
#        title = chistable[0]
#        title.pop(0)
#        chistable.pop(0)
#        vchistable = [line[1:] for line in chistable]
#        fchistable = [line[0] for line in chistable]
#        words = [self.getColumnText(self.list.GetFirstSelected(), 6)]
#        tableout = [vchistable[fchistable.index(words[0])]]
#        last = self.list.GetFirstSelected()
#        while self.list.GetNextSelected(last) != -1:
#            last = self.list.GetNextSelected(last)
#            word = self.getColumnText(last, 6)
#            words.append(word)
#            tableout.append(vchistable[fchistable.index(word)])
#        tmpgraph = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
#        txttable = 'c(' + ','.join([','.join(line) for line in tableout]) + ')'
#        rownames = 'c("' + '","'.join(words) + '")'
#        colnames = 'c("' + '","'.join(title) + '")'
#        nbcl = len(title)
#        rownb = len(words)
#        txt = """
#        load("%s")
#        di <- matrix(data=%s, nrow=%i, byrow = TRUE)
#        rownames(di)<- %s
#        colnames(di) <- %s
#        library(ape)
#        source("%s")
#        height <- (30*ncol(di)) + (15*nrow(di))
#        height <- ifelse(height <= 400, 400, height)
#        width <- 500
#        open_file_graph("%s", width=width, height=height)
#        plot.dendro.lex(tree.cut1$tree.cl, di)
#        """ % (self.Source.pathout['Rdendro'], txttable, rownb, rownames, colnames, self.Source.parent.RscriptsPath['Rgraph'], ffr(tmpgraph))
#        tmpscript = tempfile.mktemp(dir=self.Source.parent.TEMPDIR)
#        file = open(tmpscript,'w')
#        file.write(txt)
#        file.close()
#        exec_rcode(self.Source.parent.RPath, tmpscript, wait = True)
#        win = MessageImage(self, -1, u"Graphique", size=(700, 500),style = wx.DEFAULT_FRAME_STYLE)
#        win.addsaveimage(tmpgraph)
#        txt = "<img src='%s'>" % tmpgraph
#        win.HtmlPage.SetPage(txt)
#        win.Show(True)
#
#
#    def make_concord(self, uces, title, color = 'red') :
#        corpus = self.Source.corpus
#        ListWord = [self.getColumnText(self.list.GetFirstSelected(), 6)]
#        last = self.list.GetFirstSelected()
#        while self.list.GetNextSelected(last) != -1:
#            last = self.list.GetNextSelected(last)
#            ListWord.append(self.getColumnText(last, 6))
#        listmot = [forme for item in ListWord for forme in corpus.getlems()[item].formes]
#        win = message(self, -1, title, size=(600, 500), style=wx.DEFAULT_FRAME_STYLE)
#        toshow = ['<html>\n<H1>Concordancier</H1>\n']
#        toshow.append('<h3><font color=%s>' % color + ' '.join(ListWord) + '</font></h3><br>')
#        duce = {}
#        ucef = []
#        for word in ListWord : 
#            ucef += list(set(corpus.getlemuces(word)).intersection(uces))
#        ucef = list(set(ucef))
#        ucef.sort()
#        res = corpus.getconcorde(ucef)
#        txt = '<br>'.join(toshow) +'<br><br>'
#        for uce in res :
#            ucetxt = ' '+uce[1]+' '
#            txt += ' '.join(corpus.ucis[corpus.getucefromid(uce[0]).uci].etoiles) + '<br>'
#            for forme in listmot:
#                forme = corpus.getforme(forme).forme
#                ucetxt = ucetxt.replace(' '+forme+' ', '<font color=red> ' + forme + ' </font>')
#            txt += ucetxt + '<br><br>'
#        win.HtmlPage.SetPage(txt)
#        return win
#
#    def OnPopupTwo(self, event):
#        corpus = self.Source.corpus
#        uces = corpus.lc[self.cl-1]
#        win = self.make_concord(uces, "Concordancier - Classe %i" % self.cl)
#        win.Show(True)
#    
#    def OnPopupThree(self, event):
#        corpus = self.Source.corpus
#        uces = [classe[i] for classe in corpus.lc for i in range(0,len(classe))]
#        win = self.make_concord(uces, "Concordancier - UCE classées")
#        win.Show(True)
#        
#    def OnPopupFour(self, event):
#        corpus = self.Source.corpus
#        uces = [classe[i] for classe in corpus.lc for i in range(0,len(classe))] + corpus.lc0
#        win = self.make_concord(uces, "Concordancier - Toutes les UCE")
#        win.Show(True)
#
#    def OnPopupFive(self, event):
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        lk = "http://www.cnrtl.fr/definition/" + word
#        webbrowser.open(lk)
#
#    def OnPopupSix(self, event):  
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        lk = "http://www.cnrtl.fr/etymologie/" + word
#        webbrowser.open(lk)
#        
#    def OnPopupSeven(self, event):        
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        lk = "http://www.cnrtl.fr/synonymie/" + word
#        webbrowser.open(lk)
#        
#    def OnPopupHeight(self, event):  
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        lk = "http://www.cnrtl.fr/antonymie/" + word
#        webbrowser.open(lk)
#        
#    def OnPopupNine(self, event):            
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        lk = "http://www.cnrtl.fr/morphologie/" + word
#        webbrowser.open(lk)
#
#    def onproxe(self, evt) :
#        word = self.getColumnText(self.list.GetFirstSelected(), 6)
#        lk = "http://www.cnrtl.fr/proxemie/" + word
#        webbrowser.open(lk)
#
#    def OnSize(self, event):
#        w, h = self.GetClientSizeTuple()
#        self.list.SetDimensions(0, 0, w, h)
#        
#    def OnColClick(self, event):
#        self.do_greyline()
#
#
#class wliste(wx.Frame):
#    def __init__(self, parent, id, title, d, fline, size=(600, 500)):
#        wx.Frame.__init__(self, parent, id)
#        self.liste = ListForSpec(self, parent, d, fline)
#        self.button_1 = wx.Button(self, -1, "Fermer")
#        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
#        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
#        self.__do_layout()
#
#    def __do_layout(self):
#        sizer_1 = wx.BoxSizer(wx.VERTICAL)
#        sizer_2 = wx.BoxSizer(wx.VERTICAL)
#        sizer_2.Add(self.liste, 1, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
#        sizer_2.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ADJUST_MINSIZE, 0)
#        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
#        self.SetAutoLayout(True)
#        self.SetSizer(sizer_1)
#        self.Layout()
#        
#    def OnCloseMe(self, event):
#        self.Close(True)
#
#    def OnCloseWindow(self, event):
#        self.Destroy()
#
#class message(wx.Dialog):
#    def __init__(self, parent, title, size, save = True):
#        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = size, style = wx.DEFAULT_DIALOG_STYLE )
#	self.save = save	
#        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
#
#        self.html = ""
#        self.HtmlPage=wx.html.HtmlWindow(self, -1)
#        self.HtmlPage.SetMinSize( size )
#        if "gtk2" in wx.PlatformInfo:
#            self.HtmlPage.SetStandardFonts()
#        self.HtmlPage.SetFonts('Courier','Courier')
#
#        self.button_1 = wx.Button(self, wx.ID_CANCEL)
#
#        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
#        if self.save :
#            self.button_2 = wx.Button(self, wx.ID_SAVE)
#            self.Bind(wx.EVT_BUTTON, self.OnSavePage, self.button_2)
#        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
#        self.__do_layout()
#
#    def __do_layout(self):
#        sizer_2 = wx.BoxSizer(wx.VERTICAL)
#        sizer_2.Add(self.HtmlPage, 0, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
#        m_sdbSizer1 = wx.StdDialogButtonSizer()
#        m_sdbSizer1.AddButton(  self.button_1 )
#        if self.save :
#            m_sdbSizer1.AddButton(  self.button_2 )
#        m_sdbSizer1.Realize()
#        sizer_2.Add(m_sdbSizer1, 1, wx.EXPAND, 5)
#        self.SetSizer(sizer_2)
#        self.Layout()
#        sizer_2.Fit( self )
#
#    def OnSavePage(self, evt) :
#        dlg = wx.FileDialog(
#            self, message="Enregistrer sous...", defaultDir=os.getcwd(),
#            defaultFile="concordancier.html", wildcard="html|*.html", style=wx.SAVE | wx.OVERWRITE_PROMPT
#            )
#        dlg.SetFilterIndex(2)
#        dlg.CenterOnParent()
#        if dlg.ShowModal() == wx.ID_OK:
#            path = dlg.GetPath()
#            with open(path, 'w') as f :
#                f.write(self.html)
#
#    def OnCloseMe(self, event):
#        self.Close(True)
#
#    def OnCloseWindow(self, event):
#        self.Destroy()
