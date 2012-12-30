#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2012, Pierre Ratinaud
#Lisense: GNU GPL

import wx
import wx.lib.agw.customtreectrl as CT
import logging
from openanalyse import OpenAnalyse
from corpusNG import Corpus, copycorpus
from functions import DoConf


log = logging.getLogger('iramuteq.tree')
#from agw import customtreectrl as CT

class InfoDialog ( wx.Dialog ):
    
    def __init__( self, parent, txt, parametres ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Informations", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.Size( 400,200 ), wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_panel2 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText4 = wx.StaticText( self.m_panel2, wx.ID_ANY, txt, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer2.Add( self.m_staticText4, 0, wx.ALL, 5 )
        
        
        self.m_panel2.SetSizer( bSizer2 )
        self.m_panel2.Layout()
        bSizer2.Fit( self.m_panel2 )
        bSizer1.Add( self.m_panel2, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        for val in parametres :
            fgSizer1.Add( wx.StaticText( self.m_panel1, wx.ID_ANY, val[0], wx.DefaultPosition, wx.DefaultSize, 0 ), 0, wx.ALL, 0)
            fgSizer1.Add( wx.StaticText( self.m_panel1, wx.ID_ANY, val[1], wx.DefaultPosition, wx.DefaultSize, 0 ), 0, wx.ALL, 0)
            fgSizer1.Add( wx.StaticLine( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL ), 0, wx.EXPAND |wx.ALL, 0)
            fgSizer1.Add( wx.StaticLine( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL ), 0, wx.EXPAND|wx.ALL, 0)

        self.m_panel1.SetSizer( fgSizer1 )
        self.m_panel1.Layout()
        fgSizer1.Fit( self.m_panel1 )
        bSizer1.Add( self.m_panel1, 0, wx.EXPAND |wx.ALL, 3 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
    
    def __del__( self ):
        pass


class LeftTree(CT.CustomTreeCtrl):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize,
                 style=wx.SUNKEN_BORDER|wx.WANTS_CHARS,
                 agwStyle=CT.TR_HAS_BUTTONS|CT.TR_HAS_VARIABLE_ROW_HEIGHT):

        CT.CustomTreeCtrl.__init__(self, parent, id, pos, size, style, agwStyle)
        self.log = log
        alldata = dir(CT)
        treestyles = []
        events = []
        for data in alldata:
            if data.startswith("TR_"):
                treestyles.append(data)
            elif data.startswith("EVT_"):
                events.append(data)
        self.parent = parent
        self.events = events
        self.styles = treestyles
        self.item = None
        
        il = wx.ImageList(16, 16)

#        for items in ArtIDs[1:-1]:
#            bmp = wx.ArtProvider_GetBitmap(eval(items), wx.ART_TOOLBAR, (16, 16))
#            il.Add(bmp)

#        smileidx = il.Add(images.Smiles.GetBitmap())
#        numicons = il.GetImageCount()

        #self.AssignImageList(il)
        self.count = 0
        self.log = log

        self.history = parent.history
        self.h = self.history.history
        self.root = self.AddRoot("Iramuteq")

        if not(self.GetAGWWindowStyleFlag() & CT.TR_HIDE_ROOT):
            self.SetPyData(self.root, None)
            self.SetItemImage(self.root, 24, CT.TreeItemIcon_Normal)
            self.SetItemImage(self.root, 13, CT.TreeItemIcon_Expanded)

        #textctrl = wx.TextCtrl(self, -1, "I Am A Simple\nMultiline wx.TexCtrl", style=wx.TE_MULTILINE)
        #self.gauge = wx.Gauge(self, -1, 50, style=wx.GA_HORIZONTAL|wx.GA_SMOOTH)
        #self.gauge.SetValue(0)
        #combobox = wx.ComboBox(self, -1, choices=["That", "Was", "A", "Nice", "Holyday!"], style=wx.CB_READONLY|wx.CB_DROPDOWN)

        #textctrl.Bind(wx.EVT_CHAR, self.OnTextCtrl)
        #combobox.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        #lenArtIds = len(ArtIDs) - 2
        for x in range(len(self.history.corpora)) :
            if 'corpus_name' in self.h[self.history.order[x]] :
                key = 'corpus_name'
            else :
                key = 'name'
            child = self.AppendItem(self.root, self.h[self.history.order[x]][key])
            #if x == 1:
            #    child = self.AppendItem(self.root, "Item %d" % x + "\nHello World\nHappy wxPython-ing!")
            #    self.SetItemBold(child, True)
            #else:
            #    child = self.AppendItem(self.root, "Item %d" % x)
            self.SetPyData(child, self.h[self.history.order[x]])
            self.SetItemImage(child, 24, CT.TreeItemIcon_Normal)
            self.SetItemImage(child, 13, CT.TreeItemIcon_Expanded)

            #if random.randint(0, 3) == 0:
            #    self.SetItemLeftImage(child, random.randint(0, lenArtIds))

            #for y in range(5):
            #    if y == 0 and x == 1:
            #        last = self.AppendItem(child, "item %d-%s" % (x, chr(ord("a")+y)), ct_type=2, wnd=self.gauge)
            #    elif y == 1 and x == 2:
            #        last = self.AppendItem(child, "Item %d-%s" % (x, chr(ord("a")+y)), ct_type=1, wnd=textctrl)
            #        if random.randint(0, 3) == 1:
            #            self.SetItem3State(last, True)
            #            
            #    elif 2 < y < 4:
            #        last = self.AppendItem(child, "item %d-%s" % (x, chr(ord("a")+y)))
            #    elif y == 4 and x == 1:
            #        last = self.AppendItem(child, "item %d-%s" % (x, chr(ord("a")+y)), wnd=combobox)
            #    else:
            if 'corpus_name' in self.h[self.history.order[x]] :
                if 'analyses' in self.h[self.history.order[x]] :
                    for y in self.h[self.history.order[x]]['analyses'] :
                        last = self.AppendItem(child, y['name'], ct_type=0)
                            
                        self.SetPyData(last, y)
                        self.SetItemImage(last, 24, CT.TreeItemIcon_Normal)
                        self.SetItemImage(last, 13, CT.TreeItemIcon_Expanded)
    
            #    if random.randint(0, 3) == 0:
            #        self.SetItemLeftImage(last, random.randint(0, lenArtIds))
                    
            #for z in range(len(self.history[x]) - 1):

#                if z > 2:
#                    item = self.AppendItem(last,  "item %d-%s-%d" % (x, chr(ord("a")+y), z), ct_type=0)
#                    #if random.randint(0, 3) == 1:
#                    #    self.SetItem3State(item, True)
#                elif 0 < z <= 2:
#                    item = self.AppendItem(last,  "item %d-%s-%d" % (x, chr(ord("a")+y), z), ct_type=0)
#                elif z == 0:
#                    item = self.AppendItem(last,  "item %d-%s-%d" % (x, chr(ord("a")+y), z))
#                    #self.SetItemHyperText(item, True)
#                self.SetPyData(item, None)
#                self.SetItemImage(item, 28, CT.TreeItemIcon_Normal)
#                self.SetItemImage(item, 28, CT.TreeItemIcon_Selected)

             #       if random.randint(0, 3) == 0:
             #           self.SetItemLeftImage(item, random.randint(0, lenArtIds))

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDClick)
        #self.Bind(wx.EVT_IDLE, self.OnIdle)

        self.eventdict = {'EVT_TREE_BEGIN_DRAG': self.OnBeginDrag, 'EVT_TREE_BEGIN_LABEL_EDIT': self.OnBeginEdit,
                          'EVT_TREE_BEGIN_RDRAG': self.OnBeginRDrag, 'EVT_TREE_DELETE_ITEM': self.OnDeleteItem,
                          'EVT_TREE_END_DRAG': self.OnEndDrag, 'EVT_TREE_END_LABEL_EDIT': self.OnEndEdit,
                          'EVT_TREE_ITEM_ACTIVATED': self.OnActivate, 'EVT_TREE_ITEM_CHECKED': self.OnItemCheck,
                          'EVT_TREE_ITEM_CHECKING': self.OnItemChecking, 'EVT_TREE_ITEM_COLLAPSED': self.OnItemCollapsed,
                          'EVT_TREE_ITEM_COLLAPSING': self.OnItemCollapsing, 'EVT_TREE_ITEM_EXPANDED': self.OnItemExpanded,
                          'EVT_TREE_ITEM_EXPANDING': self.OnItemExpanding, 'EVT_TREE_ITEM_GETTOOLTIP': self.OnToolTip,
                          'EVT_TREE_ITEM_MENU': self.OnItemMenu, 'EVT_TREE_ITEM_RIGHT_CLICK': self.OnRightDown,
                          'EVT_TREE_KEY_DOWN': self.OnKey, 'EVT_TREE_SEL_CHANGED': self.OnSelChanged,
                          'EVT_TREE_SEL_CHANGING': self.OnSelChanging, "EVT_TREE_ITEM_HYPERLINK": self.OnHyperLink}

        mainframe = wx.GetTopLevelParent(self)
        
        if not hasattr(mainframe, "leftpanel"):
            self.Bind(CT.EVT_TREE_ITEM_EXPANDED, self.OnItemExpanded)
            self.Bind(CT.EVT_TREE_ITEM_COLLAPSED, self.OnItemCollapsed)
            self.Bind(CT.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
            self.Bind(CT.EVT_TREE_SEL_CHANGING, self.OnSelChanging)
            self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
            self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        else:
            for combos in mainframe.treeevents:
                self.BindEvents(combos)

        if hasattr(mainframe, "leftpanel"):
            self.ChangeStyle(mainframe.treestyles)

        if not(self.GetAGWWindowStyleFlag() & CT.TR_HIDE_ROOT):
            self.SelectItem(self.root)
            self.Expand(self.root)


    def BindEvents(self, choice, recreate=False):

        value = choice.GetValue()
        text = choice.GetLabel()
        
        evt = "CT." + text
        binder = self.eventdict[text]

        if value == 1:
            if evt == "CT.EVT_TREE_BEGIN_RDRAG":
                self.Bind(wx.EVT_RIGHT_DOWN, None)
                self.Bind(wx.EVT_RIGHT_UP, None)
            self.Bind(eval(evt), binder)
        else:
            self.Bind(eval(evt), None)
            if evt == "CT.EVT_TREE_BEGIN_RDRAG":
                self.Bind(wx.EVT_RIGHT_DOWN, self.OnRightDown)
                self.Bind(wx.EVT_RIGHT_UP, self.OnRightUp)


    def ChangeStyle(self, combos):

        style = 0
        for combo in combos:
            if combo.GetValue() == 1:
                style = style | eval("CT." + combo.GetLabel())

        if self.GetAGWWindowStyleFlag() != style:
            self.SetAGWWindowStyleFlag(style)
            

    def OnCompareItems(self, item1, item2):
        
        t1 = self.GetItemText(item1)
        t2 = self.GetItemText(item2)
        

        if t1 < t2:
            return -1
        if t1 == t2:
            return 0

        return 1

    
    def OnIdle(self, event):

    #    if self.gauge:
    #        try:
    #            if self.gauge.IsEnabled() and self.gauge.IsShown():
    #                self.count = self.count + 1

    #                if self.count >= 50:
    #                    self.count = 0

    #                self.gauge.SetValue(self.count)

    #        except:
    #            self.gauge = None

        event.Skip()


    def CloseItem(self, itemParent = None, uuid = None) :
        if itemParent is None :
            itemParent = self.root
        child, cookie = self.GetFirstChild(itemParent)
        while child :
            pydata = self.GetPyData(child)
            if pydata['uuid'] == uuid :
                self.SetItemBold(child, False)
                break
            self.CloseItem(child, uuid)
            child, cookie = self.GetNextChild(itemParent, cookie)

    def GiveFocus(self, itemParent = None, uuid = None) :
        if itemParent is None :
            itemParent = self.root
        child, cookie = self.GetFirstChild(itemParent)
        while child :
            pydata = self.GetPyData(child)
            if pydata['uuid'] == uuid :
                self.SelectItem(child)
                break
            self.GiveFocus(child, uuid)
            child, cookie = self.GetNextChild(itemParent, cookie)

    def OnRightDown(self, event):
        
        pt = event.GetPosition()
        item, flags = self.HitTest(pt)

        if item:
            self.item = item
            #self.log.info("OnRightClick: %s, %s, %s" % (self.GetItemText(item), type(item), item.__class__) + "\n")
            self.SelectItem(item)


    def OnRightUp(self, event):

        item = self.item
        
        if not item:
            event.Skip()
            return

        if not self.IsItemEnabled(item):
            event.Skip()
            return

        # Item Text Appearance
        ishtml = self.IsItemHyperText(item)
        back = self.GetItemBackgroundColour(item)
        fore = self.GetItemTextColour(item)
        isbold = self.IsBold(item)
        font = self.GetItemFont(item)

        # Icons On Item
        normal = self.GetItemImage(item, CT.TreeItemIcon_Normal)
        selected = self.GetItemImage(item, CT.TreeItemIcon_Selected)
        expanded = self.GetItemImage(item, CT.TreeItemIcon_Expanded)
        selexp = self.GetItemImage(item, CT.TreeItemIcon_SelectedExpanded)

        # Enabling/Disabling Windows Associated To An Item
        haswin = self.GetItemWindow(item)

        # Enabling/Disabling Items
        enabled = self.IsItemEnabled(item)

        # Generic Item's Info
        children = self.GetChildrenCount(item)
        itemtype = self.GetItemType(item)
        text = self.GetItemText(item)
        pydata = self.GetPyData(item)
        
        self.current = item
        self.itemdict = {"ishtml": ishtml, "back": back, "fore": fore, "isbold": isbold,
                         "font": font, "normal": normal, "selected": selected, "expanded": expanded,
                         "selexp": selexp, "haswin": haswin, "children": children,
                         "itemtype": itemtype, "text": text, "pydata": pydata, "enabled": enabled}
        
        menu = wx.Menu()
        info = menu.Append(wx.ID_ANY, "Informations")
        menu.AppendSeparator()

        if 'corpus_name' in pydata :
            stat = menu.Append(wx.ID_ANY, u"Statistiques")
            spec = menu.Append(wx.ID_ANY, u"Spécificté et AFC")
            classification = wx.Menu()
            alceste = classification.Append(wx.ID_ANY, u"Méthode ALCESTE")
            pam = classification.Append(wx.ID_ANY, u"Par matrice des distances")
            menu.AppendMenu(-1, u"Classification", classification)
            simi = menu.Append(wx.ID_ANY, u"Analyse de similitude")
            wdc = menu.Append(wx.ID_ANY, u"Nuage de mots")
            menu.AppendSeparator()
            self.Bind(wx.EVT_MENU, self.OnAlceste, alceste)
            self.Bind(wx.EVT_MENU, self.OnPam, pam)
            self.Bind(wx.EVT_MENU, self.OnStat, stat)
            self.Bind(wx.EVT_MENU, self.OnSpec, spec)
            self.Bind(wx.EVT_MENU, self.OnSimiTxt, simi)
            self.Bind(wx.EVT_MENU, self.OnWordCloud, wdc)

        itemdelete = menu.Append(wx.ID_ANY, "Supprimer de l'historique")
        if item == self.GetRootItem():
            itemdelete.Enable(False)
        #item11 = menu.Append(wx.ID_ANY, "Prepend An Item")
        #item12 = menu.Append(wx.ID_ANY, "Append An Item")

        #self.Bind(wx.EVT_MENU, self.OnItemBackground, item1)
        #self.Bind(wx.EVT_MENU, self.OnItemForeground, item2)
        #self.Bind(wx.EVT_MENU, self.OnItemBold, item3)
        #self.Bind(wx.EVT_MENU, self.OnItemFont, item4)
        #self.Bind(wx.EVT_MENU, self.OnItemHyperText, item5)
        #self.Bind(wx.EVT_MENU, self.OnEnableWindow, item6)
        #self.Bind(wx.EVT_MENU, self.OnDisableItem, item7)
        #self.Bind(wx.EVT_MENU, self.OnItemIcons, item8)
        self.Bind(wx.EVT_MENU, self.OnItemInfo, info)
        self.Bind(wx.EVT_MENU, self.OnItemDelete, itemdelete)
        #self.Bind(wx.EVT_MENU, self.OnItemPrepend, item11)
        #self.Bind(wx.EVT_MENU, self.OnItemAppend, item12)
        
        self.PopupMenu(menu)
        menu.Destroy()

    def getcorpus(self, itemdict):
        if itemdict['pydata']['uuid'] in self.parent.history.openedcorpus :
            return copycorpus(self.parent.history.openedcorpus[itemdict['pydata']['uuid']])
        else :
            return Corpus(self.parent, parametres = DoConf(itemdict['pydata']['ira']).getoptions('corpus'), read = True)

    def OnSpec(self, evt) :
        self.parent.OnTextSpec(evt, self.getcorpus(self.itemdict))

    def OnStat(self, evt) :
        self.parent.OnTextStat(evt, self.getcorpus(self.itemdict))
        
    def OnAlceste(self, evt) :
        self.parent.OnTextAlceste(evt, self.getcorpus(self.itemdict))

    def OnPam(self, evt) :
        print 'rien'

    def OnSimiTxt(self, evt) :
        self.parent.OnSimiTxt(evt, self.getcorpus(self.itemdict))

    def OnWordCloud(self, evt) :
        self.parent.OnWordCloud(evt, self.getcorpus(self.itemdict))

    def OnItemBackground(self, event):

        colourdata = wx.ColourData()
        colourdata.SetColour(self.itemdict["back"])
        dlg = wx.ColourDialog(self, colourdata)
        
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            col1 = data.GetColour().Get()
            self.SetItemBackgroundColour(self.current, col1)
        dlg.Destroy()


    def OnItemForeground(self, event):

        colourdata = wx.ColourData()
        colourdata.SetColour(self.itemdict["fore"])
        dlg = wx.ColourDialog(self, colourdata)
        
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetColourData()
            col1 = data.GetColour().Get()
            self.SetItemTextColour(self.current, col1)
        dlg.Destroy()


    def OnItemBold(self, event):

        self.SetItemBold(self.current, not self.itemdict["isbold"])


    def OnItemFont(self, event):

        data = wx.FontData()
        font = self.itemdict["font"]
        
        if font is None:
            font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
            
        data.SetInitialFont(font)

        dlg = wx.FontDialog(self, data)
        
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.SetItemFont(self.current, font)

        dlg.Destroy()
        

    def OnItemHyperText(self, event):

        self.SetItemHyperText(self.current, not self.itemdict["ishtml"])


    def OnEnableWindow(self, event):

        enable = self.GetItemWindowEnabled(self.current)
        self.SetItemWindowEnabled(self.current, not enable)


    def OnDisableItem(self, event):

        self.EnableItem(self.current, False)
        

    def OnItemIcons(self, event):

        bitmaps = [self.itemdict["normal"], self.itemdict["selected"],
                   self.itemdict["expanded"], self.itemdict["selexp"]]

        wx.BeginBusyCursor()        
        dlg = TreeIcons(self, -1, bitmaps=bitmaps)
        wx.EndBusyCursor()
        dlg.ShowModal()


    def SetNewIcons(self, bitmaps):

        self.SetItemImage(self.current, bitmaps[0], CT.TreeItemIcon_Normal)
        self.SetItemImage(self.current, bitmaps[1], CT.TreeItemIcon_Selected)
        self.SetItemImage(self.current, bitmaps[2], CT.TreeItemIcon_Expanded)
        self.SetItemImage(self.current, bitmaps[3], CT.TreeItemIcon_SelectedExpanded)


    def OnItemInfo(self, event):

        itemtext = self.itemdict["text"]
        numchildren = str(self.itemdict["children"])
        itemtype = self.itemdict["itemtype"]
        pydata = self.itemdict['pydata']
        #if 'analyses' in pydata :
        #    toshow = dict([[val, pydata[val]] for val in pydata if val not in['analyses', 'isload']])
        #else :
        toshow = pydata['ira']
        toshow = DoConf(toshow).getoptions()
        txt = DoConf().totext(toshow)
        parametres = [val.split('\t\t:') for val in txt.splitlines()]
        parametres.sort()

        if itemtype == 0:
            itemtype = "Normal"
        elif itemtype == 1:
            itemtype = "CheckBox"
        else:
            itemtype = "RadioButton"

        dlg = InfoDialog(self, itemtext, parametres)
        dlg.ShowModal()
        dlg.Destroy()
                
        

    def OnItemDelete(self, event):

        strs = "Are You Sure You Want To Delete Item " + self.GetItemText(self.current) + "?"
        dlg = wx.MessageDialog(None, strs, 'Deleting Item', wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_QUESTION)

        if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
            dlg.Destroy()
            return

        dlg.Destroy()
        
        pydata = self.itemdict['pydata']
        if 'corpus_name' in pydata :
            self.history.delete(pydata['uuid'], True)
        else :
            self.history.delete(pydata['uuid'])
        self.DeleteChildren(self.current)
        self.Delete(self.current)
        self.current = None
        


    def OnItemPrepend(self, event):

        dlg = wx.TextEntryDialog(self, "Please Enter The New Item Name", 'Item Naming', 'Python')

        if dlg.ShowModal() == wx.ID_OK:
            newname = dlg.GetValue()
            newitem = self.PrependItem(self.current, newname)
            self.EnsureVisible(newitem)

        dlg.Destroy()

    def AddAnalyse(self, parametres, itemParent = None, bold = True) :
        uuid = parametres['corpus']
        if itemParent is None :
            itemParent = self.root
        child, cookie = self.GetFirstChild(itemParent)
        corpus = None
        while child :
            pydata = self.GetPyData(child)
            if pydata['uuid'] == uuid :
                corpus = child
                break
            self.GiveFocus(child, uuid)
            child, cookie = self.GetNextChild(itemParent, cookie)
        #item = self.AppendItem(child, parametres['name'])
        if corpus is not None : 
            item = self.AppendItem(corpus, parametres['name'])
        else :
            item = self.AppendItem(self.root, parametres['name'])
        self.SetPyData(item, parametres)
        self.SetItemImage(item, 24, CT.TreeItemIcon_Normal)
        self.SetItemImage(item, 13, CT.TreeItemIcon_Expanded)
        self.SetItemBold(item, bold)
        
    def OnItemAppend(self, item):
        child = self.AppendItem(self.root, item['corpus_name'])
        self.SetPyData(child, item)
        self.history.addtab(item)
        self.SetItemImage(child, 24, CT.TreeItemIcon_Normal)
        self.SetItemImage(child, 13, CT.TreeItemIcon_Expanded)
        self.SetItemBold(child, True)
        
        #dlg = wx.TextEntryDialog(self, "Please Enter The New Item Name", 'Item Naming', 'Python')

        #if dlg.ShowModal() == wx.ID_OK:
        #    newname = dlg.GetValue()
        #    newitem = self.AppendItem(self.current, newname)
        #    self.EnsureVisible(newitem)
        

        #dlg.Destroy()
        

    def OnBeginEdit(self, event):
        
        #self.log.info("OnBeginEdit" + "\n")
        # show how to prevent edit...
        item = event.GetItem()
        if item and self.GetItemText(item) == "The Root Item":
            wx.Bell()
            #self.log.info("You can't edit this one..." + "\n")

            # Lets just see what's visible of its children
            cookie = 0
            root = event.GetItem()
            (child, cookie) = self.GetFirstChild(root)

            while child:
                #self.log.info("Child [%s] visible = %d" % (self.GetItemText(child), self.IsVisible(child)) + "\n")
                (child, cookie) = self.GetNextChild(root, cookie)

            event.Veto()


    def OnEndEdit(self, event):
        
        #self.log.info("OnEndEdit: %s %s" %(event.IsEditCancelled(), event.GetLabel()))
        # show how to reject edit, we'll not allow any digits
        for x in event.GetLabel():
            if x in string.digits:
                #self.log.info(", You can't enter digits..." + "\n")
                event.Veto()
                return
            
        self.log.info("\n")


    def OnLeftDClick(self, event):
        
        pt = event.GetPosition()
        item, flags = self.HitTest(pt)
        pydata = self.GetPyData(item)
        if pydata['uuid'] in self.parent.history.opened :
            for i in range(self.parent.nb.GetPageCount()) :
                page = self.parent.nb.GetPage(i)
                if 'parametres' in dir(page) :
                    if page.parametres['uuid'] == pydata['uuid'] :
                        self.parent.nb.SetSelection(i)
                        break
        else :
            OpenAnalyse(self.parent, pydata)
            self.SetItemBold(item, True)
        #if item and (flags & CT.TREE_HITTEST_ONITEMLABEL):
        #    if self.GetAGWWindowStyleFlag() & CT.TR_EDIT_LABELS:
        #        self.log.info("OnLeftDClick: %s (manually starting label edit)"% self.GetItemText(item) + "\n")
                
                #self.EditLabel(item)
        #    else:
        #        pydata = self.GetPyData(item)
        #        print pydata
        #        self.log.info("OnLeftDClick: Cannot Start Manual Editing, Missing Style TR_EDIT_LABELS\n")

        event.Skip()                
        

    def OnItemExpanded(self, event):
        
        item = event.GetItem()
        if item:
            self.log.info("OnItemExpanded: %s" % self.GetItemText(item) + "\n")


    def OnItemExpanding(self, event):
        
        item = event.GetItem()
        if item:
            self.log.info("OnItemExpanding: %s" % self.GetItemText(item) + "\n")
            
        event.Skip()

        
    def OnItemCollapsed(self, event):

        item = event.GetItem()
        if item:
            self.log.info("OnItemCollapsed: %s" % self.GetItemText(item) + "\n")
            

    def OnItemCollapsing(self, event):

        item = event.GetItem()
        if item:
            self.log.info("OnItemCollapsing: %s" % self.GetItemText(item) + "\n")
    
        event.Skip()

        
    def OnSelChanged(self, event):
        item = event.GetItem()
        pydata = self.GetPyData(item)
        if pydata is not None :
            if pydata['uuid'] in self.parent.history.opened :
                for i in range(self.parent.nb.GetPageCount()) :
                    page = self.parent.nb.GetPage(i)
                    if 'parametres' in dir(page) :
                        if page.parametres['uuid'] == pydata['uuid'] :
                            self.parent.nb.SetSelection(i)
                            break

        #self.item = event.GetItem()
        #if self.item:
        #    self.
            #self.log.info("OnSelChanged: %s" % self.GetItemText(self.item))
        #    if wx.Platform == '__WXMSW__':
               # self.log.info(", BoundingRect: %s" % self.GetBoundingRect(self.item, True) + "\n")
       #        pass
        event.Skip()


    def OnSelChanging(self, event):

        item = event.GetItem()
        olditem = event.GetOldItem()
        
        if item:
            if not olditem:
                olditemtext = "None"
            else:
                olditemtext = self.GetItemText(olditem)
            self.log.info("OnSelChanging: From %s" % olditemtext + " To %s" % self.GetItemText(item) + "\n")
                
        event.Skip()


    def OnBeginDrag(self, event):

        self.item = event.GetItem()
        if self.item:
            self.log.info("Beginning Drag..." + "\n")

            event.Allow()


    def OnBeginRDrag(self, event):

        self.item = event.GetItem()
        if self.item:
            self.log.info("Beginning Right Drag..." + "\n")

            event.Allow()
        

    def OnEndDrag(self, event):

        self.item = event.GetItem()
        if self.item:
            self.log.info("Ending Drag!" + "\n")

        event.Skip()            


    def OnDeleteItem(self, event):

        item = event.GetItem()

        if not item:
            return

        self.log.info("Deleting Item: %s" % self.GetItemText(item) + "\n")
        event.Skip()
        

    def OnItemCheck(self, event):

        item = event.GetItem()
        self.log.info("Item " + self.GetItemText(item) + " Has Been Checked!\n")
        event.Skip()


    def OnItemChecking(self, event):

        item = event.GetItem()
        self.log.info("Item " + self.GetItemText(item) + " Is Being Checked...\n")
        event.Skip()
        

    def OnToolTip(self, event):

        item = event.GetItem()
        if item:
            event.SetToolTip(wx.ToolTip(self.GetItemText(item)))


    def OnItemMenu(self, event):

        item = event.GetItem()
        if item:
            self.log.info("OnItemMenu: %s" % self.GetItemText(item) + "\n")
    
        event.Skip()


    def OnKey(self, event):

        keycode = event.GetKeyCode()
        keyname = keyMap.get(keycode, None)
                
        if keycode == wx.WXK_BACK:
            self.log.info("OnKeyDown: HAHAHAHA! I Vetoed Your Backspace! HAHAHAHA\n")
            return

        if keyname is None:
            if "unicode" in wx.PlatformInfo:
                keycode = event.GetUnicodeKey()
                if keycode <= 127:
                    keycode = event.GetKeyCode()
                keyname = "\"" + unichr(event.GetUnicodeKey()) + "\""
                if keycode < 27:
                    keyname = "Ctrl-%s" % chr(ord('A') + keycode-1)
                
            elif keycode < 256:
                if keycode == 0:
                    keyname = "NUL"
                elif keycode < 27:
                    keyname = "Ctrl-%s" % chr(ord('A') + keycode-1)
                else:
                    keyname = "\"%s\"" % chr(keycode)
            else:
                keyname = "unknown (%s)" % keycode
                
        self.log.info("OnKeyDown: You Pressed '" + keyname + "'\n")

        event.Skip()
        
        
    def OnActivate(self, event):
        
        if self.item:
            self.log.info("OnActivate: %s" % self.GetItemText(self.item) + "\n")

        event.Skip()

        
    def OnHyperLink(self, event):

        item = event.GetItem()
        if item:
            self.log.info("OnHyperLink: %s" % self.GetItemText(self.item) + "\n")
            

    def OnTextCtrl(self, event):

        char = chr(event.GetKeyCode())
        self.log.info("EDITING THE TEXTCTRL: You Wrote '" + char + \
                       "' (KeyCode = " + str(event.GetKeyCode()) + ")\n")
        event.Skip()


    def OnComboBox(self, event):

        selection = event.GetEventObject().GetValue()
        self.log.info("CHOICE FROM COMBOBOX: You Chose '" + selection + "'\n")
        event.Skip()
