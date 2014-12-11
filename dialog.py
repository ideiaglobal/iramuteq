#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#License: GNU/GPL
import  wx
import  wx.lib.colourselect as csel
import wx.lib.sized_controls as sc
import wx.lib.filebrowsebutton as filebrowse
import locale
from functions import DoConf, exec_rcode
import os
from shutil import copyfile
from PrintRScript import barplot
import tempfile
import sys
from KeyFrame import AlcOptFrame
#---------------------------------------------------------------------------
provider = wx.SimpleHelpProvider()
wx.HelpProvider_Set(provider)

#---------------------------------------------------------------------------


encodages = [[u'cp1252',u'Western Europe'], [u'utf-8',u'all languages'], [u'MacRoman',u'Western Europe'], [u'ascii', u'English'], [u'big5', u'Traditional Chinese'], [u'big5hkscs', u'Traditional Chinese'], [u'cp037', u'English'], [u'cp424', u'Hebrew'], [u'cp437', u'English'], [u'cp500', u'Western Europe'], [u'cp737', u'Greek'], [u'cp775', u'Baltic languages'], [u'cp850', u'Western Europe'], [u'cp852', u'Central and Eastern Europe'], [u'cp855', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'cp856', u'Hebrew'], [u'cp857', u'Turkish'], [u'cp860', u'Portuguese'], [u'cp861', u'Icelandic'], [u'cp862', u'Hebrew'], [u'cp863', u'Canadian'], [u'cp864', u'Arabic'], [u'cp865', u'Danish, Norwegian'], [u'cp866', u'Russian'], [u'cp869', u'Greek'], [u'cp874', u'Thai'], [u'cp875', u'Greek'], [u'cp932', u'Japanese'], [u'cp949', u'Korean'], [u'cp950', u'Traditional Chinese'], [u'cp1006', u'Urdu'], [u'cp1026', u'Turkish'], [u'cp1140', u'Western Europe'], [u'cp1250', u'Central and Eastern Europe'], [u'cp1251', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'cp1253', u'Greek'], [u'cp1254', u'Turkish'], [u'cp1255', u'Hebrew'], [u'cp1256', u'Arabic'], [u'cp1257', u'Baltic languages'], [u'cp1258', u'Vietnamese'], [u'euc_jp', u'Japanese'], [u'euc_jis_2004', u'Japanese'], [u'euc_jisx0213', u'Japanese'], [u'euc_kr', u'Korean'], [u'gb2312', u'Simplified Chinese'], [u'gbk', u'Unified Chinese'], [u'gb18030', u'Unified Chinese'], [u'hz', u'Simplified Chinese'], [u'iso2022_jp', u'Japanese'], [u'iso2022_jp_1', u'Japanese'], [u'iso2022_jp_2', u'Jp, K, S C, WE, G'], [u'iso2022_jp_2004', u'Japanese'], [u'iso2022_jp_3', u'Japanese'], [u'iso2022_jp_ext', u'Japanese'], [u'iso2022_kr', u'Korean'], [u'latin_1', u'West Europe'], [u'iso8859_2', u'Central and Eastern Europe'], [u'iso8859_3', u'Esperanto, Maltese'], [u'iso8859_4', u'Baltic languages'], [u'iso8859_5', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'iso8859_6', u'Arabic'], [u'iso8859_7', u'Greek'], [u'iso8859_8', u'Hebrew'], [u'iso8859_9', u'Turkish'], [u'iso8859_10', u'Nordic languages'], [u'iso8859_13', u'Baltic languages'], [u'iso8859_14', u'Celtic languages'], [u'iso8859_15', u'Western Europe'], [u'iso8859_16', u'South-Eastern Europe'], [u'johab', u'Korean'], [u'koi8_r', u'Russian'], [u'koi8_u', u'Ukrainian'], [u'mac_cyrillic', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'mac_greek', u'Greek'], [u'mac_iceland', u'Icelandic'], [u'mac_latin2', u'Central and Eastern Europe'], [u'mac_turkish', u'Turkish'], [u'ptcp154', u'Kazakh'], [u'shift_jis', u'Japanese'], [u'shift_jis_2004', u'Japanese'], [u'shift_jisx0213', u'Japanese'], [u'utf_32', u'all languages'], [u'utf_32_be', u'all languages'], [u'utf_32_le', u'all languages'], [u'utf_16', u'all languages'], [u'utf_16_be', u'all languages (BMP only)'], [u'utf_16_le', u'all languages (BMP only)'], [u'utf_7', u'all languages'], [u'utf_8_sig', u'all languages']]

class FileOptionDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, sep=False, sheet = False, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid_sizer = wx.FlexGridSizer(0, 2, 2, 2)
##############################

        label = wx.StaticText(self, -1, _(u"First line is header").decode('utf8'))
        label.SetHelpText(_(u"First line is header").decode('utf8'))
        grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        on = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
        self.radio_box_1 = wx.RadioBox(self, -1, u"", choices=on, majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.radio_box_1.SetHelpText(_(u"First line is header").decode('utf8'))
        grid_sizer.Add(self.radio_box_1, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

##############################

        label = wx.StaticText(self, -1, _(u"First column is an id").decode('utf8'))
        label.SetHelpText(_(u"First column is an id").decode('utf8'))
        grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        on = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
        self.radio_box_2 = wx.RadioBox(self, -1, u"", choices=on, majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.radio_box_2.SetHelpText(_(u"First column is an id").decode('utf8'))
        grid_sizer.Add(self.radio_box_2, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

##############################
        if sep:
            label = wx.StaticText(self, -1, _(u"Column separator").decode('utf8'))
            label.SetHelpText(_(u"Column separator").decode('utf8'))
            grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.colsep = [";", "tabulation", ","]
            self.choice3 = wx.Choice(self, -1, (100, 50), choices=self.colsep)
            self.choice3.SetHelpText(_(u"Column separator").decode('utf8'))
            grid_sizer.Add(self.choice3, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
    
    ##############################
    
            label = wx.StaticText(self, -1, _(u"Text separator").decode('utf8'))
            label.SetHelpText(_(u"Text separator").decode('utf8'))
            grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.txtsep = ["\"", "'"]
            self.choice4 = wx.Choice(self, -1, (100, 50), choices=self.txtsep)
            self.choice4.SetHelpText(_(u"Text separator").decode('utf8'))
            grid_sizer.Add(self.choice4, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.choice3.SetSelection(0)
            self.choice4.SetSelection(0)
            self.text = wx.StaticText(self, -1, _(u"Characters set").decode('utf8'))
            grid_sizer.Add(self.text, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.le = [enc[0].lower() for enc in encodages] 
            self.list_encodages = wx.Choice(self, -1, (25, 30), choices=[' - '.join(encodage) for encodage in encodages])
            if locale.getpreferredencoding().lower() == 'mac-roman' :
                enc = self.le.index('macroman')
            else :
                try :
                    enc = self.le.index(sys.getdefaultencoding().lower())
                except ValueError:
                    enc = self.le.index('utf-8')
            self.list_encodages.SetSelection(enc)
            grid_sizer.Add(self.list_encodages, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        elif sheet :
            label = wx.StaticText(self, -1, u"Feuille ")
            grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.spin1 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=500)
            grid_sizer.Add(self.spin1, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        sizer.Add(grid_sizer, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)


        line = wx.StaticLine(self, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)


class ClusterNbDialog(wx.Dialog):
    def __init__(
            self, LIST_CLASSE, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)

        # Now continue with the normal construction of the dialog
        # contents
        sizer = wx.BoxSizer(wx.VERTICAL)

        label = wx.StaticText(self, -1, u"Résultats de la classification")
        label.SetHelpText("This is the help text for the label")
        sizer.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)

        label = wx.StaticText(self, -1, u"Choisissez le nombre de classes")
        label.SetHelpText("This is the help text for the label")
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        LIST_CLASSE_OK = []
        if type(LIST_CLASSE) != float :
            for i in LIST_CLASSE :
                LIST_CLASSE_OK.append(str(i))
        else :
            LIST_CLASSE_OK.append(str(LIST_CLASSE))
        self.list_box_1 = wx.ListBox(self, -1, choices=LIST_CLASSE_OK, style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.list_box_1.SetHelpText("Here's some help text for field #1")
        box.Add(self.list_box_1, 1, wx.ALIGN_CENTRE | wx.ALL, 5)

        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)


###############################
        line = wx.StaticLine(self, -1, size=(20, -1), style=wx.LI_HORIZONTAL)
        sizer.Add(line, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT | wx.TOP, 5)

        btnsizer = wx.StdDialogButtonSizer()
        
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            btnsizer.AddButton(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

class CHDDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE | wx.CANCEL
            ):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)
       
        self.colsep = parent.colsep
        self.Box = 1
        self.content = parent.content[:]
        self.header = parent.header[:]
        LABELLIST = []
        for i in self.header:
            if len(i) > 60 :
                LABELLIST.append(i[0:60])
            else:
                LABELLIST.append(i)
        self.LABELLISTTOT = LABELLIST
        self.LISTVARSUP = []
#----------------------------------------------------------------------------------------------------
        self.text1 = wx.StaticText(self, -1, u"Variables Actives (au moins 3)")
        self.text2 = wx.StaticText(self, -1, u"Variables Supplémentaires (au moins 1)")
        self.list_box_1 = wx.ListBox(self, -1, choices=LABELLIST, style=wx.LB_EXTENDED | wx.LB_HSCROLL)
        self.list_box_2 = wx.ListBox(self, -1, choices=LABELLIST, style=wx.LB_EXTENDED | wx.LB_HSCROLL)
        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        self.button_back = wx.Button(self, wx.ID_BACKWARD)
        self.button_forw = wx.Button(self, wx.ID_FORWARD)
        self.button_ok = wx.Button(self, wx.ID_OK)
        self.button_pref = wx.Button(self, wx.ID_PROPERTIES)
        self.button_selectall = wx.Button(self, wx.NewId(), u"Sélectionner tout")
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnPrec, self.button_back)
        self.Bind(wx.EVT_BUTTON, self.OnSuivant, self.button_forw)
        self.Bind(wx.EVT_BUTTON, self.OnValider, self.button_ok)
        self.Bind(wx.EVT_BUTTON, self.OnSelectAll, self.button_selectall)
        # end wxGlade
        self.parent = parent
        self.TEMPDIR = parent.TEMPDIR
        self.num = 0

    def __set_properties(self):
        # begin wxGlade: ConfChi2.__set_properties
        self.SetTitle(u"Sélection des variables")
        self.list_box_2.Enable(False)
        self.button_ok.Enable(False)        
        self.button_back.Enable(False)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: ConfChi2.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_5.Add(self.text1, 1, wx.CENTER | wx.ALL, 0)
        sizer_5.Add(self.text2, 1, wx.CENTER | wx.ALL, 0)
        sizer_3.Add(self.list_box_1, 0, wx.EXPAND, 0)
        sizer_3.Add(self.list_box_2, 0, wx.EXPAND, 0)
        sizer_6.Add(self.button_selectall, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 0) 
        sizer_7.Add(self.button_cancel, 0, wx.ALL, 0)
        sizer_7.Add(self.button_pref, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_7.Add(self.button_ok, 0, wx.wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_4.Add(self.button_back, 0, wx.ALL, 0)
        sizer_4.Add(self.button_forw, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_5, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_2.Add(sizer_6, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_4, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_7, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 4)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade
#--------------FIXME-----------------------
#NETTOYAGE des variables inutiles
    def OnSuivant(self, event): 
        LISTACTIVE = self.list_box_1.GetSelections()
        if len(LISTACTIVE) != len(self.LABELLISTTOT) and len(LISTACTIVE) >= 3: 
            self.button_ok.Enable(True)
        self.Box = 2
        self.LISTHEADERINDICE = []
        self.LISTNUMACTIVE = []
        COMPT = 0
        header = self.header[:]
        for i in range(0, len(header)):
            self.LISTHEADERINDICE.append(i)
        for i in LISTACTIVE :
            self.LISTNUMACTIVE.append(i)
            header.pop(i - COMPT)
            self.LISTHEADERINDICE.pop(i - COMPT)
            COMPT += 1
        self.LABELLIST = []
        for i in header:
            if len(i) > 60 :
                self.LABELLIST.append(i[0:60])
            else:
                self.LABELLIST.append(i)
        self.list_box_2.Clear()
        for i in self.LABELLIST :
            self.list_box_2.Append(i)
                    
        self.list_box_1.Enable(False)    
        self.list_box_2.Enable(True)
        self.button_forw.Enable(False)
        self.button_back.Enable(True)

    def OnValider(self, event):
        LISTVARSUPSEL = self.list_box_2.GetSelections()
        for i in LISTVARSUPSEL :
            self.LISTVARSUP.append(self.LISTHEADERINDICE[i])
        event.Skip()

    def OnPrec(self, event):
        self.list_box_1.Enable(True)
        self.list_box_2.Enable(False)
        self.button_forw.Enable(True)
        self.button_back.Enable(False)   
        self.button_ok.Enable(False)
        self.Box = 1
        event.Skip()

    def OnSelectAll(self, event):
        if self.Box == 1:
            for i in range(len(self.LABELLISTTOT)):
                self.list_box_1.Select(i)
        else:
            for i in range(len(self.LABELLIST)):
                self.list_box_2.Select(i)

class PrefDialog ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Settings").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.parent = parent
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Play a sound at the end of analysis").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )
        
        m_radioBox1Choices = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
        self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox1.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox1, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        msg = _(u"""Check for new 
releases at startup""").decode('utf8')
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )
        
        m_radioBox2Choices = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
        self.m_radioBox2 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox2Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox2.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox2, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        msg = _(u"Interface language").decode('utf8')
        self.m_staticText45 = wx.StaticText( self, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText45.Wrap( -1 )
        fgSizer1.Add( self.m_staticText45, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText46 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText46.Wrap( -1 )
        fgSizer1.Add( self.m_staticText46, 0, wx.ALL, 5 )
        
        self.listlangues = [ u"french", u"english", u"spanish", u"portuguese", u"italian" ]
        self.langues = wx.Choice( self, wx.ID_ANY, (200, -1), choices = self.listlangues)
        #self.langues.SetSelection( 0 )
        fgSizer1.Add( self.langues, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        msg = _(u"""Check installation 
of R packages""").decode('utf8')
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer1.Add( self.m_staticText6, 0, wx.ALL, 5 )
        
        self.m_button1 = wx.Button( self, wx.ID_ANY, _(u"Check").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.m_button1, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        bSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )
        if sys.platform == 'win32' :
            bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
            
            msg = _(u"""Maximum 
memory for R""").decode('utf8')
            self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText7.Wrap( -1 )
            bSizer2.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
            bSizer2.Add( self.m_checkBox1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.m_spinCtrl1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 32, 16000, 1535 )
            bSizer2.Add( self.m_spinCtrl1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
            bSizer2.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
            
            bSizer1.Add( bSizer2, 0, wx.EXPAND, 5 )
            self.m_checkBox1.Bind( wx.EVT_CHECKBOX, self.oncheckmem )

        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
        self.text8 = wx.StaticText( self, wx.ID_ANY, _(u"Use svdlibc").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.text8.Wrap( -1 )
        fgSizer1.Add( self.text8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.check_svdc = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.check_svdc, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        bSizer3.Add( bSizer4, 0, wx.EXPAND, 5 )
        self.fbb = filebrowse.FileBrowseButton(self, -1, size=(250, -1), fileMode = 2, fileMask = '*')
        bSizer3.Add( self.fbb, 0, wx.EXPAND, 5 )
        self.fbb.SetLabel(_(u"Path : ").decode('utf8'))
        fgSizer1.Add( wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 ),  wx.ID_ANY, wx.ALL, 5)
        fgSizer1.Add( bSizer3, 0,  wx.ALIGN_RIGHT|wx.ALL, 5 )

        Rpath_text =  wx.StaticText( self, wx.ID_ANY, _(u"R path").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        Rpath_text.Wrap( -1 )
        fgSizer1.Add( Rpath_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        fgSizer1.Add( wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 ),  wx.ID_ANY, wx.ALL, 5)
        self.Rpath_value = filebrowse.FileBrowseButton(self, -1, size=(350, -1), fileMode = 2, fileMask = '*')
        self.Rpath_value.SetLabel(_(u"Path : ").decode('utf8'))
        fgSizer1.Add( self.Rpath_value, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        mirror_text =  wx.StaticText( self, wx.ID_ANY, _(u"Default R mirror").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        mirror_text.Wrap( -1 )
        fgSizer1.Add( mirror_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        fgSizer1.Add( wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 ),  wx.ID_ANY, wx.ALL, 5)
        self.mirror_value = wx.TextCtrl( self, wx.ID_ANY, u'http://cran.univ-lyon1.fr', wx.DefaultPosition, wx.Size( 300,30 ), 0 ) 
        fgSizer1.Add( self.mirror_value, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )


        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize()
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.m_sdbSizer1OK.Bind( wx.EVT_BUTTON, self.OnValid )
        self.m_button1.Bind( wx.EVT_BUTTON, parent.OnVerif )
        self.check_svdc.Bind( wx.EVT_CHECKBOX, self.OnSVDC )
        self.__set_properties()

    def __set_properties(self):
        self.SetTitle(_(u"Settings").decode('utf8'))
        if self.parent.pref.getboolean('iramuteq', 'sound'): val1 = 0
        else : val1 = 1
        self.m_radioBox1.SetSelection(val1)
        if self.parent.pref.getboolean('iramuteq', 'checkupdate') : val2 = 0
        else : val2 = 1
        self.m_radioBox2.SetSelection(val2)
        self.langues.SetSelection(self.listlangues.index(self.parent.pref.get('iramuteq', 'guilanguage')))
        if sys.platform == 'win32' :
            if self.parent.pref.getboolean('iramuteq', 'R_mem') :
                self.m_checkBox1.SetValue(True)
                self.m_spinCtrl1.Enable(True)
                self.m_spinCtrl1.SetValue(self.parent.pref.getint('iramuteq', 'R_max_mem'))
            else :
                self.m_checkBox1.SetValue(False)
                self.m_spinCtrl1.Enable(False)
        if self.parent.pref.getboolean('iramuteq', 'libsvdc') : 
            self.check_svdc.SetValue(True)
            self.fbb.SetValue(self.parent.pref.get('iramuteq', 'libsvdc_path'))
        else :
            self.check_svdc.SetValue(False)
            self.fbb.SetValue(self.parent.pref.get('iramuteq', 'libsvdc_path'))
            self.fbb.Enable(False)
        self.Rpath_value.SetValue(self.parent.PathPath.get('PATHS', 'rpath'))
        self.mirror_value.SetValue(self.parent.pref.get('iramuteq', 'rmirror'))
        
    def oncheckmem(self, evt):
        if self.m_checkBox1.GetValue() :
            self.m_spinCtrl1.Enable(True)
        else :
            self.m_spinCtrl1.Enable(False)

    def OnSVDC(self, evt):
        if self.check_svdc.GetValue() :
            self.fbb.Enable(True)
        else :
            self.fbb.Enable(False)

    def OnValid(self, event):
        parent = self.parent
        if self.m_radioBox1.GetSelection() == 0 : valsound = 'true'
        else :  valsound = 'false'
        parent.pref.set('iramuteq', 'sound', valsound)
        if self.m_radioBox2.GetSelection() == 0 : valcheck = 'true'
        else :  valcheck = 'false'
        parent.pref.set('iramuteq', 'checkupdate', valcheck)
        parent.pref.set('iramuteq', 'guilanguage', self.listlangues[self.langues.GetSelection()])
        if sys.platform == 'win32' :
            if self.m_checkBox1.GetValue() :
                parent.pref.set('iramuteq', 'R_mem', 'true')
                parent.pref.set('iramuteq', 'R_max_mem', str(self.m_spinCtrl1.GetValue()))
            else :
                parent.pref.set('iramuteq', 'R_mem', 'false')
        if self.check_svdc.GetValue() :
            parent.pref.set('iramuteq', 'libsvdc', 'true')
        else :
            parent.pref.set('iramuteq', 'libsvdc', 'false')
        parent.pref.set('iramuteq', 'libsvdc_path', self.fbb.GetValue())
        self.parent.pref.set('iramuteq', 'rmirror', self.mirror_value.GetValue())
        file = open(parent.ConfigPath['preferences'], 'w')
        parent.pref.write(file)
        file.close()
        self.parent.PathPath.set('PATHS', 'rpath', self.Rpath_value.GetValue())
        with open(self.parent.ConfigPath['path'], 'w') as f:
            self.parent.PathPath.write(f)
        self.Close()

class PrefGraph(wx.Dialog):
    def __init__(self, parent, ID, paramgraph, title = '', size=wx.DefaultSize, pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        self.parent = parent
        self.paramgraph=paramgraph
        self.labeltype = wx.StaticText(self, -1, _(u"Graphic type").decode('utf8'))
        if self.paramgraph['clnb'] <= 3 :
            choix = [u'2D']#, 'web 2D']
        else :
            choix=[u'2D' ,u'3D']#, 'web 2D', 'web 3D']
        self.choicetype = wx.Choice(self, -1, (100,50), choices=choix)
        self.label_format = wx.StaticText(self, -1, _(u"Picture format").decode('utf8'))
        self.choix_format =  wx.Choice(self, -1, (100,50), choices = ['png', 'svg'])        
        self.label_1 = wx.StaticText(self, -1, _(u"width").decode('utf8'))
        self.spin1 = wx.SpinCtrl(self, -1, '',size = (100,30), min=100, max=5000)
        self.label_2 = wx.StaticText(self, -1, _(u"height").decode('utf8'))
        self.spin2 = wx.SpinCtrl(self, -1, '', size = (100,30), min=100, max=5000)
        self.label_what = wx.StaticText(self, -1, _(u"Representation").decode('utf8'))
        self.choice1 = wx.Choice(self, -1, (100,50), choices=[_(u"coordinates").decode('utf8'),_(u"correlations").decode('utf8')])
        self.label_qui = wx.StaticText(self, -1, u'Variables')
        self.choice2 = wx.Choice(self, -1, (100,50), choices=[_(u"actives").decode('utf8') ,_(u"supplementaries").decode('utf8'), _(u"stars").decode('utf8'), _(u"clusters").decode('utf8')])
        self.label_3 = wx.StaticText(self, -1, _(u"Text size").decode('utf8'))
        self.spin3 = wx.SpinCtrl(self, -1, '', size = (100,30), min=1, max=20)
        txt = _(u"Take the x first points").decode('utf8')
        self.label_4 = wx.StaticText(self, -1, txt)
        self.check1 = wx.CheckBox(self, -1)
        self.spin_nb = wx.SpinCtrl(self, -1, '', size = (100,30), min=2, max=1000)
        txt = _(u"Take the x first points by cluster").decode('utf8')
        self.label_chic = wx.StaticText(self, -1, txt)
        self.check_chic = wx.CheckBox(self, -1)
        self.spin_nbchic = wx.SpinCtrl(self, -1, '', size = (100,30), min=2, max=1000)        
        txt = _(u"Limit points by cluster chi2").decode('utf8')
        self.label_5 = wx.StaticText(self, -1, txt)
        self.check2 = wx.CheckBox(self, -1)
        self.spin_chi = wx.SpinCtrl(self, -1, '',size = (100,30),  min=2, max=1000)
        self.label_6 = wx.StaticText(self, -1, _(u"Avoid overlay").decode('utf8'))
        self.check3 = wx.CheckBox(self, -1)
        txt = _(u"Text size proportional to frequency").decode('utf8')
        self.label_7 = wx.StaticText(self, -1, txt)
        self.check4 = wx.CheckBox(self, -1)
        self.label_min = wx.StaticText(self, -1, 'min')
        self.spin_min = wx.SpinCtrl(self, -1, '',size = (100,30), min = 1, max = 100)
        self.label_max = wx.StaticText(self, -1, 'max')
        self.spin_max = wx.SpinCtrl(self, -1, '',size = (100,30), min = 1, max = 100)
        txt = _(u"Text size proportional to chi2").decode('utf8')
        self.label_tchi = wx.StaticText(self, -1, txt)
        self.check_tchi = wx.CheckBox(self, -1)
        self.label_min_tchi = wx.StaticText(self, -1, 'min')
        self.spin_min_tchi = wx.SpinCtrl(self, -1, '', size = (100,30), min = 1, max = 100)
        self.label_max_tchi = wx.StaticText(self, -1, 'max')
        self.spin_max_tchi = wx.SpinCtrl(self, -1, '', size = (100,30), min = 1, max = 100)
        self.label_8 = wx.StaticText(self, -1, _(u"Factor x : ").decode('utf8'))
        self.spin_f1 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=self.paramgraph['clnb']-1)
        self.label_9 = wx.StaticText(self, -1, _(u"Factor y : ").decode('utf8'))
        self.spin_f2 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=self.paramgraph['clnb']-1)
        self.label_f3 = wx.StaticText(self, -1, _(u"Factor z : ").decode('utf8'))
        self.spin_f3 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=self.paramgraph['clnb']-1)
        self.label_sphere = wx.StaticText(self, -1, _(u"Spheres transparency").decode('utf8'))
        self.slider_sphere = wx.Slider(self, -1, 10, 1, 100, size = (255,-1), style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)

        self.label_film = wx.StaticText(self, -1, _(u"Make a movie").decode('utf8'))
        self.film = wx.CheckBox(self, -1)
               
        self.btnsizer = wx.StdDialogButtonSizer()
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            self.btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_OK)
        btn.SetDefault()
        self.btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        self.btnsizer.AddButton(btn)
        self.btnsizer.Realize()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck1, self.check1)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck2, self.check2)
        self.Bind(wx.EVT_CHECKBOX, self.OnNorm, self.check4)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckTchi, self.check_tchi)
        self.Bind(wx.EVT_CHOICE, self.On3D, self.choicetype)
        self.Bind(wx.EVT_CHOICE, self.OnPass, self.choice2)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckChic, self.check_chic)
        self.__set_properties()
        self.OnNorm(wx.EVT_CHECKBOX)
        self.OnCheckTchi(wx.EVT_CHECKBOX)
        self.__do_layout()

    def __set_properties(self):
        self.choicetype.SetSelection(self.paramgraph['typegraph'])
        if self.paramgraph['typegraph'] == 0  or self.paramgraph['typegraph'] == 2:
            self.film.Enable(False)
            self.spin_f3.Enable(False)
            self.slider_sphere.Enable(False)
        self.choix_format.SetSelection(self.paramgraph['svg'])
        self.choice1.SetSelection(self.paramgraph['what'])
        self.choice2.SetSelection(self.paramgraph['qui'])
        self.spin_chi.SetValue(self.paramgraph['select_nb'])
        self.spin_nb.SetValue(self.paramgraph['select_chi'])
        self.spin1.SetValue(self.paramgraph['width'])
        self.spin2.SetValue(self.paramgraph['height'])
        self.spin3.SetValue(self.paramgraph['taillecar'])
        self.spin_nb.SetValue(self.paramgraph['select_nb'])
        self.spin_chi.SetValue(self.paramgraph['select_chi'])
        self.spin_nbchic.SetValue(self.paramgraph['nbchic'])
        self.check1.SetValue(self.paramgraph['do_select_nb'])
        self.check2.SetValue(self.paramgraph['do_select_chi'])
        self.check_chic.SetValue(self.paramgraph['do_select_chi_classe'])
        self.check3.SetValue(self.paramgraph['over'])
        if self.paramgraph['do_select_nb'] :
            self.spin_nb.Enable(True)
            self.spin_chi.Enable(False)
            self.spin_nbchic.Enable(False)
        elif self.paramgraph['do_select_chi_classe'] :
            self.spin_nb.Enable(False)
            self.spin_chi.Enable(False)
            self.spin_nbchic.Enable(True)
        elif self.paramgraph['do_select_chi'] :
            self.spin_nb.Enable(False)
            self.spin_chi.Enable(True)
            self.spin_nbchic.Enable(False)
        else :
            self.spin_nb.Enable(False)
            self.spin_chi.Enable(False)
            self.spin_nbchic.Enable(False)

            
        self.check4.SetValue(self.paramgraph['cex_txt'])
        self.spin_min.SetValue(self.paramgraph['txt_min'])
        self.spin_max.SetValue(self.paramgraph['txt_max'])
        self.check_tchi.SetValue(self.paramgraph['tchi'])
        self.spin_min_tchi.SetValue(self.paramgraph['tchi_min'])
        self.spin_max_tchi.SetValue(self.paramgraph['tchi_max'])

        self.spin_f1.SetValue(self.paramgraph['facteur'][0])
        self.spin_f2.SetValue(self.paramgraph['facteur'][1])
        self.spin_f3.SetValue(self.paramgraph['facteur'][2])
        self.slider_sphere.SetValue(self.paramgraph['alpha'])

    def __do_layout(self):
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        fsizer = wx.FlexGridSizer(0,2,0,5)
        grid_min = wx.FlexGridSizer(0, 2, 0, 0)
        grid_max = wx.FlexGridSizer(0, 2, 0, 0)
        grid_minmax = wx.FlexGridSizer(0, 2, 0, 0)
        grid_min_tchi = wx.FlexGridSizer(0, 2, 0, 0)
        grid_max_tchi = wx.FlexGridSizer(0, 2, 0, 0)
        grid_minmax_tchi = wx.FlexGridSizer(0, 2, 0, 0)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        
        fsizer.Add(self.labeltype, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(self.choicetype, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)

        fsizer.Add(self.label_format, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(self.choix_format, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)

        fsizer.Add(self.label_what, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(self.choice1, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        
        fsizer.Add(self.label_qui, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(self.choice2, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)              
        
        sizer_h1 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h1.Add(self.label_1, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_h1.Add(self.spin1, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(sizer_h1, 0, wx.ALL, 5)
        sizer_h2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_h2.Add(self.label_2, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_h2.Add(self.spin2, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(sizer_h2, 0, wx.ALL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        
        fsizer.Add(self.label_3, 0, wx.ALL | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(self.spin3, 0, wx.ALL | wx.LEFT | wx.ALIGN_CENTER_VERTICAL, 5)        
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        
        fsizer.Add(self.label_4, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_nb = wx.BoxSizer(wx.HORIZONTAL)
        sizer_nb.Add(self.check1, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_nb.Add(self.spin_nb, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(sizer_nb, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        
        fsizer.Add(self.label_chic, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_nbchic = wx.BoxSizer(wx.HORIZONTAL)
        sizer_nbchic.Add(self.check_chic, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_nbchic.Add(self.spin_nbchic, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(sizer_nbchic, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)

        fsizer.Add(self.label_5, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_chi = wx.BoxSizer(wx.HORIZONTAL)
        sizer_chi.Add(self.check2, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_chi.Add(self.spin_chi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(sizer_chi, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        
        fsizer.Add(self.label_6, 0,  wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL| wx.ADJUST_MINSIZE, 5)
        fsizer.Add(self.check3, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 5)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0) 
        
        sizer_2.Add(fsizer, 0, wx.EXPAND, 0)
        
        bsizer_1 = wx.FlexGridSizer(0,3,0,0)
        bsizer_1.Add(self.label_7, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        bsizer_1.Add(self.check4, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        grid_min.Add(self.label_min, 0,wx.ALL |  wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_min.Add(self.spin_min, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_max.Add(self.label_max, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_max.Add(self.spin_max, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_minmax.Add(grid_min, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_minmax.Add(grid_max, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)

        bsizer_1.Add(grid_minmax, 0, wx.ALL, 5)

        bsizer_1.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        bsizer_1.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0) 
        bsizer_1.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)        

        bsizer_1.Add(self.label_tchi, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        bsizer_1.Add(self.check_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5)
        grid_min_tchi.Add(self.label_min_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_min_tchi.Add(self.spin_min_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_max_tchi.Add(self.label_max_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_max_tchi.Add(self.spin_max_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_minmax_tchi.Add(grid_min_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        grid_minmax_tchi.Add(grid_max_tchi, 0, wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        bsizer_1.Add(grid_minmax_tchi, 0,  wx.ALL, 5)
        sizer_2.Add(bsizer_1, 0, wx.EXPAND, 5)
        
        sizer_2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0) 
        
        sizer_f = wx.BoxSizer(wx.HORIZONTAL)
        sizer_f.Add(self.label_8, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_f.Add(self.spin_f1, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        
        sizer_f.Add(self.label_9, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_f.Add(self.spin_f2, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

        sizer_f.Add(self.label_f3, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_f.Add(self.spin_f3, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(sizer_f, 0, wx.EXPAND, 5)
        
        sizer_2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 5)
        
        fsizer2 = wx.FlexGridSizer(0,2,0,0)
        fsizer2.Add(self.label_sphere, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer2.Add(self.slider_sphere, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)
        fsizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND, 0)

        fsizer2.Add(self.label_film, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer2.Add(self.film, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        sizer_2.Add(fsizer2, 0, wx.EXPAND, 5)
        sizer_2.Add(self.btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(sizer_2)
        sizer_2.Fit(self)
        self.Layout()
        
    def OnCheck1(self, event):
        if self.check1.GetValue() :
            self.check2.SetValue(False)
            self.check_chic.SetValue(False)
            self.spin_chi.Enable(False)
            self.spin_nb.Enable(True)
            self.spin_nbchic.Enable(False)
        else : 
            self.spin_nb.Enable(False)
            
    def OnCheck2(self, event):
        if self.check2.GetValue() :
            self.check1.SetValue(False)
            self.check_chic.SetValue(False)
            self.spin_chi.Enable(True)
            self.spin_nb.Enable(False)
            self.spin_nbchic.Enable(False)
        else :
            self.spin_chi.Enable(False) 

    def OnCheckChic(self, event) :
        if self.check_chic.GetValue() :
            self.check1.SetValue(False)
            self.check2.SetValue(False)
            self.spin_chi.Enable(False)
            self.spin_nb.Enable(False)
            self.spin_nbchic.Enable(True)
        else :
            self.spin_nbchic.Enable(False)

    def OnNorm(self, event):
        if not self.check4.GetValue() :
            self.spin_min.Disable()
            self.spin_max.Disable()
        else :
            self.spin_min.Enable(True)
            self.spin_max.Enable(True)
            self.check_tchi.SetValue(False)
            self.OnCheckTchi(wx.EVT_CHECKBOX)

    def OnCheckTchi(self, evt) :
        if not self.check_tchi.GetValue() :
            self.spin_min_tchi.Disable()
            self.spin_max_tchi.Disable()
        else :
            self.spin_min_tchi.Enable(True)
            self.spin_max_tchi.Enable(True)
            self.check4.SetValue(False)
            self.OnNorm(wx.EVT_CHECKBOX)

    def On3D(self, event) :
        if event.GetString() == u'3D' :
            self.film.Enable(True)
            self.spin_f3.Enable(True)
            self.slider_sphere.Enable(True)
        else :
            self.film.Enable(False)
            self.spin_f3.Enable(False)
            self.slider_sphere.Enable(False)
    
    def OnPass(self,evt) :
        if evt.GetString() == _(u"clusters").decode('utf8') :
            self.check4.SetValue(False)
            self.check4.Enable(False)
            self.OnNorm(wx.EVT_CHECKBOX)
        else :
            self.check4.Enable()
            

class SelectColDial ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 400,500 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        self.bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        #self.m_checkList2 = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ['r','t','y'], 0 ) 
        #bSizer2.Add( self.m_checkList2, 2, wx.ALL|wx.EXPAND, 5 )
        
        self.m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_CANCEL)
        self.butok = wx.Button( self, wx.ID_OK)
        #m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        #self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        #m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        #m_sdbSizer2.Realize();
        #self.bSizer2.Add( m_sdbSizer2, 0, wx.EXPAND, 5 )
        
        self.SetSizer( self.bSizer2 )
        self.Layout()
        
        self.Centre( wx.BOTH )
    
    def __del__( self ):
        pass

class PrefExport(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.OK|wx.DEFAULT_DIALOG_STYLE 
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileout = ""
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_lem = wx.StaticText(self, -1, _(u"Lemmatised corpus").decode('utf8'))
        box3.Add(self.label_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.radio_lem = wx.RadioBox(self, -1, u"", choices= [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        box3.Add(self.radio_lem, 0, wx.ALIGN_RIGHT, 5)
        sizer.Add(box3, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.label_txt = wx.StaticText(self, -1, _(u"Export for ...").decode('utf8'))
        box.Add(self.label_txt, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.radio_type = wx.RadioBox(self, -1, u"", choices=['IRaMuTeQ/ALCESTE', 'Lexico'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        box.Add(self.radio_type, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.txt2 = wx.StaticText(self, -1, _(u"Output file").decode('utf8'))
        box2.Add(self.txt2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.fbb = filebrowse.FileBrowseButton(self, -1, size=(450, -1), fileMode = 2)
        box2.Add(self.fbb, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.fbb.SetLabel("")
        sizer.Add(box2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5)
        self.Bind(wx.EVT_BUTTON, self.check_file, btn_ok)
        self.SetSizer(sizer)
        sizer.Fit(self)        

    def check_file(self, evt) :
        if evt.GetId() == wx.ID_OK :
            if os.path.exists(self.fbb.GetValue()):
                dlg = wx.MessageDialog(self, '\n'.join([u"%s" % self.fbb.GetValue(), _(u"This file already exists. Continue anyway ?").decode('utf8')]), _(u"Attention").decode('utf8'), wx.NO | wx.YES | wx.ICON_WARNING)
                dlg.CenterOnParent()
                if dlg.ShowModal() not in [wx.ID_NO, wx.ID_CANCEL]:
                    self.EndModal(wx.ID_OK)
            else :
                self.EndModal(wx.ID_OK)
        else :
            self.EndModal(wx.ID_CANCEL)

class PrefProfTypes(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.OK|wx.DEFAULT_DIALOG_STYLE 
        wx.Dialog.__init__(self, parent, *args, **kwds)
        self.fileout = ""
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        box = wx.BoxSizer(wx.HORIZONTAL)
        box3 = wx.BoxSizer(wx.HORIZONTAL)
        self.label_txt = wx.StaticText(self, -1, _(u"Settings").decode('utf8'))
        box.Add(self.label_txt, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.radio_type = wx.RadioBox(self, -1, u"", choices=[_(u"Like ALCESTE").decode('utf8'), _(u"Like Lexico").decode('utf8')], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        box.Add(self.radio_type, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.txt2 = wx.StaticText(self, -1, _(u"Output file").decode('utf8'))
        box2.Add(self.txt2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.fbb = filebrowse.FileBrowseButton(self, -1, size=(450, -1), fileMode = 2)
        box2.Add(self.fbb, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.fbb.SetLabel("")
        sizer.Add(box2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5)
        #self.Bind(wx.EVT_BUTTON, self.check_file, btn_ok)
        self.SetSizer(sizer)
        sizer.Fit(self)

class PrefSimpleFile(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.OK|wx.DEFAULT_DIALOG_STYLE 
        if 'mask' in kwds :
            self.mask = kwds['mask']
            del(kwds['mask'])
        else : self.mask = '*.*'
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileout = ""
        self.parent = parent
        sizer = wx.BoxSizer(wx.VERTICAL)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.txt2 = wx.StaticText(self, -1, _(u"Output file").decode('utf8'))
        box2.Add(self.txt2, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.fbb = filebrowse.FileBrowseButton(self, -1, size=(450, -1), fileMode = 2, fileMask = self.mask)
        box2.Add(self.fbb, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.fbb.SetLabel("")
        sizer.Add(box2, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.Realize()
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.ALIGN_RIGHT, 5)
        self.Bind(wx.EVT_BUTTON, self.check_file, btn_ok)
        self.SetSizer(sizer)
        sizer.Fit(self)        

    def check_file(self, evt) :
        if evt.GetId() == wx.ID_OK :
            if os.path.exists(self.fbb.GetValue()):
                dlg = wx.MessageDialog(self, '\n'.join([u"%s" % self.fbb.GetValue(), _(u"This file already exists. Continue anyway ?").decode('utf8')]), _(u"Attention").decode('utf8'), wx.NO | wx.YES | wx.ICON_WARNING)
                dlg.CenterOnParent()
                if dlg.ShowModal() not in [wx.ID_NO, wx.ID_CANCEL]:
                    self.EndModal(wx.ID_OK)
            else :
                self.EndModal(wx.ID_OK)
        else :
            self.EndModal(wx.ID_CANCEL)

class StatDialog ( wx.Dialog ):
    
    def __init__( self, parent, keys ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Settings").decode('utf8'), pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        self.fileout = ""
        self.parent = parent
        self.keys = keys
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        gSizer1 = wx.GridSizer( 0, 2, 0, 0 )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Lemmatization").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        gSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1 )
        
        radio_lemChoices = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
        self.radio_lem = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, radio_lemChoices, 1, wx.RA_SPECIFY_COLS )
        self.radio_lem.SetSelection( 0 )
        gSizer1.Add( self.radio_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 1 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"Keys properties").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        gSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1 )
        
        self.button_5 = wx.Button( self, wx.ID_PREFERENCES, _(u"properties").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        gSizer1.Add( self.button_5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 1 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"Dictionary").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        gSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1 )
        
        radio_dictchoiceChoices = [ _(u"indexation").decode('utf8'), _(u"other").decode('utf8') ]
        self.radio_dictchoice = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, radio_dictchoiceChoices, 1, wx.RA_SPECIFY_COLS )
        self.radio_dictchoice.SetSelection( 0 )
        gSizer1.Add( self.radio_dictchoice, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 1 )
        
        
        bSizer1.Add( gSizer1, 1, wx.EXPAND, 1 )
        
        self.dictpath = filebrowse.FileBrowseButton(self, -1, size=(350, -1),  labelText = _(u"Path").decode('utf8'), fileMode = 2, fileMask = '*')
        bSizer1.Add( self.dictpath, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1 )
        self.dictpath.Enable(False)

        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 0 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.button_5.Bind( wx.EVT_BUTTON, self.OnKeys )
        self.radio_dictchoice.Bind( wx.EVT_RADIOBOX, self.OnOther )
    
    def __del__( self ):
        pass
    
    
    # Virtual event handlers, overide them in your derived class
    def OnKeys( self, event ):
        dial = AlcOptFrame(self, self.parent)
        dial.CenterOnParent()
        dial.ShowModal()
        for i in range(0,len(dial.listlabel)):
            dial.keys[dial.listcle[i]] = dial.listspin[i].GetValue()
        DoConf().makeoptions(['KEY'], [dial.keys], outfile = self.parent.ConfigPath['key'])
        dial.Destroy()
    
    def OnOther( self, event ):
        if self.radio_dictchoice.GetSelection() :
            self.dictpath.Enable(True)
        else :
            self.dictpath.Enable(False)

# class StatDialog(wx.Dialog):
#     def __init__(self, parent, *args, **kwds):
#         kwds['style'] = wx.DEFAULT_DIALOG_STYLE 
#         wx.Dialog.__init__(self, *args, **kwds)
#         self.fileout = ""
#         self.parent = parent
#         self.label_lem = wx.StaticText(self, -1, _(u"Lemmatization").decode('utf8'))
#         self.radio_lem = wx.RadioBox(self, -1, u"", choices=[_(u'oui').decode('utf8'), _(u'non').decode('utf8')], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
#         #txt = u"""Fréquence minimum d'une forme
# #analysée (0 = non utilisé)"""
#         #self.label_8 = wx.StaticText(self, -1, txt)
#         #self.spin_ctrl_5 = wx.SpinCtrl(self, -1, "",size = (100,30), min=0, max=1000, initial=0)
#         #self.label_max_actives =  wx.StaticText(self, -1, u"Nombre maximum de formes analysées")
#         #self.spin_max_actives = wx.SpinCtrl(self, -1, "",size = (100,30), min=20, max=10000, initial=1500)
#         self.label_4 = wx.StaticText(self, -1, _(u"Keys settings").decode('utf8'))
#         self.button_5 = wx.Button(self, wx.ID_PREFERENCES, "")
#         self.labeldictchoice = wx.StaticText(self, -1, _(u"Dictionary").decode('utf8'))
#         self.radio_dictchoice = wx.RadioBox(self, -1, u"", choices=[_(u'indexation').decode('utf8'), _(u'other').decode('utf8')], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
#         #self.labeldictpath = wx.StaticText(self, -1, _(u"Path").decode('utf8'))
#         self.dictpath = filebrowse.FileBrowseButton(self, -1, size=(350, -1),  labelText = _(u"Path").decode('utf8'), fileMode = 2, fileMask = '*')
#         self.dictpath.Enable(False)
#         #self.Bind(wx.EVT_CHECKBOX, self.OnCheckUce, self.check_uce)
#         #self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.spin_ctrl_5)
#         self.Bind(wx.EVT_BUTTON, self.OnKeys, self.button_5)
#         self.Bind(wx.EVT_RADIOBOX, self.OnOther, self.radio_dictchoice)
#         self.__do_layout()
#         self.__set_properties()
# 
#     def __do_layout(self) :
#         first = wx.BoxSizer(wx.VERTICAL)
#         sizer = wx.FlexGridSizer(0,2,0,0)
#         sizer.Add(self.label_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(self.radio_lem, 0, wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.txt_exp, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.exp, 0, wx.ALIGN_RIGHT, 5)
#         #sizer.Add(self.label_uce, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.check_uce, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.label_occuce, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.spin_ctrl_4, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.label_8, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.spin_ctrl_5, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.label_max_actives, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.spin_max_actives, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(self.label_4, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(self.button_5, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         sizer.Add(self.labeldictchoice, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(self.radio_dictchoice, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         #sizer.Add(self.labeldictpath, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(self.dictpath, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
#         sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)      
#         #sizer.Add(box2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
#         first.Add(sizer, 0, wx.ALL, 5)
#         btnsizer = wx.StdDialogButtonSizer()
#         btn = wx.Button(self, wx.ID_CANCEL)
#         btnsizer.AddButton(btn)
#         btn_ok = wx.Button(self, wx.ID_OK)
#         btn_ok.SetDefault()
#         btnsizer.AddButton(btn_ok)
#         btnsizer.Realize()
#         first.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
#         self.SetSizer(first)
#         first.Fit(self)
# 
#     def __set_properties(self) :
#         self.SetTitle(_(u"Settings").decode('utf8'))
# 
#     def OnKeys(self, evt):
#         dial = AlcOptFrame(self, self.parent.parent)
#         dial.CenterOnParent()
#         dial.ShowModal()
#         for i in range(0,len(dial.listlabel)):
#             dial.keys[dial.listcle[i]] = dial.listspin[i].GetValue()
#         DoConf().makeoptions(['KEY'], [dial.keys], outfile = self.parent.parent.ConfigPath['key'])
#         dial.Destroy()
#     
#     def OnOther(self, evt):
#         if self.radio_dictchoice.GetSelection() :
#             self.dictpath.Enable(True)
#         else :
#             self.dictpath.Enable(False)

class PrefUCECarac(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE 
        kwds['title'] = _(u"Characteristic text segments").decode('utf8')
        wx.Dialog.__init__(self, *args, **kwds)
        self.parent = parent
        first = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.FlexGridSizer(0,2,0,0)
        self.label_type = wx.StaticText(self, -1, _(u"Ranking score").decode('utf8'))
        sizer.Add(self.label_type, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.radio_type = wx.RadioBox(self, -1, u"", choices=[_(u"absolute (sum of chi2 of marked forms in segment)").decode('utf8'), _(u"relative (mean of chi2 of marked forms in segment)").decode('utf8')], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        sizer.Add(self.radio_type, 0, wx.ALIGN_RIGHT, 5)
        self.txt_eff = wx.StaticText(self, -1, _(u"Maximum number of text segments").decode('utf8'))
        sizer.Add(self.txt_eff, 0, wx.ALIGN_CENTRE, 5)
        self.spin_eff = wx.SpinCtrl(self, -1, '', size = (100, 30), min = 1, max = 100000, initial = 50)
        self.spin_eff.SetValue(50)
        sizer.Add(self.spin_eff, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        first.Add(sizer, 0, wx.ALL, 5)
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.Realize()
        first.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        self.SetSizer(first)
        first.Fit(self)

class PrefSegProf(wx.Dialog) :
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Repeated segments profiles").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        txt = _(u"Be carefull : computation of repeated segments profiles can be very long on large corpus").decode('utf8')
        self.label = wx.StaticText( self, wx.ID_ANY, txt, wx.DefaultPosition, wx.DefaultSize, 0 ) 
        bSizer1.Add( self.label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5 )

        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Lemmatised corpus").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        box_lemChoices = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
        self.box_lem = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, box_lemChoices, 1, wx.RA_SPECIFY_COLS )
        self.box_lem.SetSelection( 1 )
        fgSizer1.Add( self.box_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        #self.box_lem.Enable(False)
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"Minimum size of segments").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_min = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (100,30), wx.SP_ARROW_KEYS, 2, 30, 2 )
        self.spin_min.SetValue(2)
        fgSizer1.Add( self.spin_min, 0, wx.ALL, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"Maxmum size of segments").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer1.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_max = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (100,30), wx.SP_ARROW_KEYS, 2, 30, 10 )
        self.spin_max.SetValue(10)
        fgSizer1.Add( self.spin_max, 0, wx.ALL, 5 )
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Minimum frequency of segments").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_eff = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (100,30), wx.SP_ARROW_KEYS, 4, 1000, 4 )
        self.spin_eff.SetValue(4)
        fgSizer1.Add( self.spin_eff, 0, wx.ALL, 5 )
        
        bSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn_ok = wx.Button(self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.Realize()
        bSizer1.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)

        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )

class PrefQuestAlc ( wx.Dialog ):
    
    def __init__( self, parent, tableau, sim = False):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Clustering").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        #---------------------------------------------------------------
        #self.content = parent.content[:]
        self.header = tableau.get_colnames()
        labels = [val for val in self.header]
        self.labels_tot = labels
        self.varsup = []
        self.sim = sim
        #---------------------------------------------------------------
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        if not self.sim :
            self.lab_format = wx.StaticText( self, wx.ID_ANY, _(u"Supplementary variables are marked with a *").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.lab_format.Wrap( -1 )
            fgSizer1.Add( self.lab_format, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
            m_radioBox1Choices = [ _(u"yes").decode('utf8'), _(u"no").decode('utf8') ]
            self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
            self.m_radioBox1.SetSelection( 0 )
            fgSizer1.Add( self.m_radioBox1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"Actives variables (almost 3)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"Supplementaries variables (almost 1)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )
        
        self.ListActive = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, labels,  wx.LB_EXTENDED )
        self.ListActive.SetMinSize( wx.Size( 300,250 ) )
        
        fgSizer1.Add( self.ListActive, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        self.ListSup = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, labels, wx.LB_EXTENDED )
        self.ListSup.SetMinSize( wx.Size( 300,250 ) )
        
        fgSizer1.Add( self.ListSup, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        self.but_suiv = wx.Button( self, wx.ID_ANY, _(u"Next").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.but_suiv, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.but_prec = wx.Button( self, wx.ID_ANY, _(u"Previous").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.but_prec, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        if not sim :
            self.lab_nbcl = wx.StaticText( self, wx.ID_ANY, _(u"Number of terminal clusters on phase 1").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.lab_nbcl.Wrap( -1 )
            fgSizer1.Add( self.lab_nbcl, 0, wx.ALL, 5 )
            
            self.spin_nbcl = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 2, 100, 10 )
            self.spin_nbcl.SetValue(10)
            self.spin_nbcl.SetMinSize( wx.Size( 100,30 ) )
            
            fgSizer1.Add( self.spin_nbcl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.lab_mincl = wx.StaticText( self, wx.ID_ANY, _(u"Minimum text segments frenquency in clusters (2= automatic)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.lab_mincl.Wrap( -1 )
            fgSizer1.Add( self.lab_mincl, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
            
            self.spin_mincl = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 2, 1000, 0 )
            self.spin_mincl.SetValue(2)
            self.spin_mincl.SetMinSize( wx.Size( 100,30 ) )
            
            fgSizer1.Add( self.spin_mincl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
        bSizer2.Add( fgSizer1, 1, wx.EXPAND, 5 )
        
        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        m_sdbSizer2.Realize();
        bSizer2.Add( m_sdbSizer2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        self.SetSizer( bSizer2 )
        self.Layout()
        bSizer2.Fit( self )
        
        self.Centre( wx.BOTH )
        
        if not self.sim :
            self.ListActive.Enable(False)
            self.ListSup.Enable(False)
            self.but_suiv.Enable(False)
            self.but_prec.Enable(False)
        else :
            self.ListSup.Enable(False)
            self.but_prec.Enable(False)
        
        # Connect Events
        if not self.sim :
            self.m_radioBox1.Bind( wx.EVT_RADIOBOX, self.onformat )
        self.but_suiv.Bind(wx.EVT_BUTTON, self.onsuivant)
        self.but_prec.Bind(wx.EVT_BUTTON, self.onprec)
        self.m_sdbSizer2OK.Bind(wx.EVT_BUTTON, self.onvalid)

    def __del__( self ):
        pass
    
    # Virtual event handlers, overide them in your derived class
    def onformat( self, event ):
        if self.m_radioBox1.GetSelection() == 0 :
            self.ListActive.Enable(False)
            self.ListSup.Enable(False)
            self.but_suiv.Enable(False)
            self.m_sdbSizer2OK.Enable(True)
        else :
            self.ListActive.Enable(True)
            self.but_suiv.Enable(True)
            self.m_sdbSizer2OK.Enable(False)
        
    def onsuivant(self, evt) :
        actives = list(self.ListActive.GetSelections())
        actives.sort()
        if len(actives)>=3 and len(actives) != len(self.header) :
            self.hindices = []
            self.nactives = []
            compt = 0
            header = self.header[:]
            for i in range(0, len(header)):
                self.hindices.append(i)
            for i in actives :
                self.nactives.append(i)
                header.pop(i - compt)
                self.hindices.pop(i - compt)
                compt += 1
            self.labels = [val for val in header]
            self.ListSup.Clear()
            for i in header :
                self.ListSup.Append(i)
                        
            self.ListActive.Enable(False)    
            self.ListSup.Enable(True)
            self.but_suiv.Enable(False)
            self.but_prec.Enable(True)
            if not self.sim :
                self.m_sdbSizer2OK.Enable(True)

    def onprec(self, evt) :
        self.ListActive.Enable(True)    
        self.ListSup.Enable(False)
        self.but_suiv.Enable(True)
        self.but_prec.Enable(False)
        if not self.sim :
            self.m_sdbSizer2OK.Enable(False)

    def onvalid(self, evt) :
        for i in self.ListSup.GetSelections() :
            self.varsup.append(self.hindices[i])
        if not self.sim :
            if len(self.varsup) >= 1 or self.m_radioBox1.GetSelection() == 0 :
                evt.Skip()
        else :
            if len(self.varsup) >= 1 :
                evt.Skip()

class FindInCluster(wx.Frame):
    def __init__(self, parent, id, result, style = wx.DEFAULT_FRAME_STYLE):
        # begin wxGlade: MyFrame.__init__
        wx.Frame.__init__(self, parent, id)
        self.spanel =  wx.ScrolledWindow(self, -1, style=wx.TAB_TRAVERSAL)
        self.sizer1 = wx.FlexGridSizer(0,4,0,0)
        self.parent = parent
        self.formes = {}
        txt =  [_(u"form").decode('utf8'),_(u"cluster").decode('utf8'),_(u"Chi2").decode('utf8'), _(u"see").decode('utf8')]
        for val in txt :
            self.sizer1.Add( wx.StaticText(self.spanel, -1, val), 0, wx.ALL, 5)
        for val in txt :
            self.sizer1.Add(wx.StaticLine(self.spanel, -1), 0, wx.ALL, 5)
        for i,val in enumerate(result) :
            forme = val[0]
            cl = val[1]
            chi = val[2]
            pan = wx.Panel(self.spanel, -1, style=wx.SIMPLE_BORDER)
            siz = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(pan, -1, forme)
            siz.Add(txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
            pan.SetSizer(siz)
            self.sizer1.Add(pan, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
            pan = wx.Panel(self.spanel, -1, style=wx.SIMPLE_BORDER)
            siz = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(pan, -1, str(cl))
            siz.Add(txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
            pan.SetSizer(siz)
            self.sizer1.Add(pan, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
            pan = wx.Panel(self.spanel, -1, style=wx.SIMPLE_BORDER)
            siz = wx.BoxSizer(wx.VERTICAL)
            txt = wx.StaticText(pan, -1, str(chi))
            siz.Add(txt, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
            pan.SetSizer(siz)
            self.sizer1.Add(pan, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5)
            idbut = wx.NewId()
            self.formes[idbut] = [forme, cl]
            but = wx.Button(self.spanel, idbut, u"voir")
            self.sizer1.Add(but, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5)
            self.Bind(wx.EVT_BUTTON, self.showitem, but)
        self.button_1 = wx.Button(self, -1, "Fermer")
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade
    
    def __set_properties(self):
        self.SetTitle(_(u"Results").decode('utf8'))
        self.spanel.EnableScrolling(True,True)
        #self.panel_1.SetSize((1000,1000))
        self.spanel.SetScrollRate(20, 20)
        h = 60 * len(self.formes)
        if h > 600 :
            h = 600
        if h < 150 :
            h = 150
        self.SetSize(wx.Size(400,h))

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        self.spanel.SetSizer(self.sizer1)
        sizer_1.Add(self.spanel, 4, wx.EXPAND, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        #sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        self.Layout()
        # end wxGlade

    def showitem(self, evt) :
        idb = evt.GetEventObject().GetId()
        nb = self.parent.nb
        profile = nb.GetPage(nb.GetSelection())
        cl = self.formes[idb][1] - 1
        forme = self.formes[idb][0]
        profile.ProfNB.SetSelection(cl)
        UnSelectList(profile.ProfNB.GetPage(cl))
        datas = dict([[profile.ProfNB.GetPage(cl).getColumnText(i,6),i] for i in range(profile.ProfNB.GetPage(cl).GetItemCount())])
        profile.ProfNB.GetPage(cl).SetItemState(datas[self.formes[idb][0]], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        profile.ProfNB.GetPage(cl).Focus(datas[forme])
        profile.ProfNB.GetPage(cl).SetFocus()

    def OnCloseMe(self, evt) :
        self.Close(True)

    def OnCloseWindow(self, evt):
        self.Destroy()

class SearchDial ( wx.Frame ):
    
    def __init__( self, parent, listctrl, col, shown):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP )
        self.parent = parent
        self.listctrl = listctrl
        self.col = col
        self.shown = shown
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.search = wx.SearchCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_PROCESS_ENTER )
        self.search.ShowSearchButton( True )
        self.search.ShowCancelButton( True )
        bSizer1.Add( self.search, 0, wx.ALL, 5 )
        sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.backward = wx.Button(self, wx.ID_BACKWARD, _(u"Previous").decode('utf8'))
        self.forward = wx.Button(self, wx.ID_FORWARD, _(u"Next").decode('utf8'))
        sizer2.Add(self.backward, 0, wx.ALL, 5)
        sizer2.Add(self.forward, 0, wx.ALL, 5)
        bSizer1.Add( sizer2, 0, wx.ALL, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.OnSearch, self.search)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.OnCancel, self.search)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnSearch, self.search)
        self.Bind(wx.EVT_BUTTON, self.onforward, self.forward)
        self.Bind(wx.EVT_BUTTON, self.onbackward, self.backward)
        self.search.SetFocus()
        self.forward.Enable(False)
        self.backward.Enable(False)

        self.Centre( wx.BOTH )
    
    def __del__( self ):
        pass

    def OnSearch(self, evt):
        UnSelectList(self.listctrl)
        search_word = self.search.GetValue()
        if search_word.strip() != '' :
            formes = [self.listctrl.getColumnText(i, self.col) for i in range(self.listctrl.GetItemCount())]
            if search_word.endswith(u'*') :
                search_word = search_word[0:-1]
                result = [j for j, forme in enumerate(formes) if forme.startswith(search_word)]
            else :
                result = [j for j, forme in enumerate(formes) if forme == search_word]
            if result == [] :
                self.noresult()
            elif self.shown == True :
                self.showitems(result)
            else :
                self.showresult(result)
        else :
            self.Destroy()

    
    def showitems(self, items) :
        if len(items) == 1 :
            self.listctrl.SetItemState(items[0], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            self.listctrl.Focus(items[0])
            self.listctrl.SetFocus()
            self.Destroy()
        else :
            for i in items :
                self.listctrl.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            self.listctrl.Focus(items[0])
            self.listctrl.SetFocus()
            self.forward.Enable(True)
            self.backward.Enable(False)
            self.items = items
            self.forwitem = 1
            self.backitem = -1
    
    def showresult(self, result) :
        toshow = [self.listctrl.itemDataMap[int(self.listctrl.getColumnText(i,0))] for i in result]
        proflist = [[[line[1], i+1, val] for i, val in enumerate(line[2:]) if val>=2] for line in toshow]
        #FIXME: intervenir en aval en virant les forme avec chi<2
        if proflist != [[]] :
            proflist = [val for line in proflist for val in line if line !=[]]
            nb = self.parent.parent.nb
            profile = nb.GetPage(nb.GetSelection())
            first_forme = proflist[0]
            cl = first_forme[1] - 1
            profile.ProfNB.SetSelection(cl)
            profile.ProfNB.GetPage(cl).SetFocus()
            UnSelectList(profile.ProfNB.GetPage(cl))
            datas = dict([[profile.ProfNB.GetPage(cl).getColumnText(i,6),i] for i in range(profile.ProfNB.GetPage(cl).GetItemCount())])
            profile.ProfNB.GetPage(cl).SetItemState(datas[first_forme[0]], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            profile.ProfNB.GetPage(cl).Focus(datas[first_forme[0]])
            profile.ProfNB.GetPage(cl).SetFocus()
            if len(proflist) == 1 :
                self.Destroy()
            else :
                SearchResult = FindInCluster(self.parent.parent, -1, proflist)
                SearchResult.Show()
                self.Destroy()
        else :
            self.noresult()

    def onforward(self, evt) :
        self.listctrl.Focus(self.items[self.forwitem])
        self.listctrl.SetFocus()
        self.forwitem += 1
        if self.forwitem == len(self.items) :
            self.forward.Enable(False)
            self.backward.Enable(True)
            self.backitem += 1
        else :
            self.backitem += 1
            self.backward.Enable(True)

    def onbackward(self, evt) :
        self.listctrl.Focus(self.items[self.backitem])
        self.listctrl.SetFocus()
        self.backitem -= 1
        if self.backitem == -1 :
            self.forwitem -= 1
            self.forward.Enable(True)
            self.backward.Enable(False)
        else :
            self.forwitem -= 1
            self.forward.Enable(True)

    def noresult(self) :
        msg = _(u"Absent form").decode('utf8')
        dial = wx.MessageDialog(self, _(u"Absent form").decode('utf8'),_(u"Absent form").decode('utf8'), wx.OK | wx.ICON_INFORMATION)
        dial.CenterOnParent()
        dial.ShowModal()
        dial.Destroy()

    def OnCancel(self, evt) :
        self.search.Clear()

def UnSelectList(liste) :
    if liste.GetFirstSelected() != -1 :
        last = liste.GetFirstSelected()
        liste.Select(liste.GetFirstSelected(), False)
        while liste.GetNextSelected(last) != -1 :
            last = liste.GetNextSelected(last)
            liste.Select(liste.GetFirstSelected(),False)


class OptLexi(wx.Dialog):
    def __init__(self, parent, force_chi = False):
        # begin wxGlade: MyDialog.__init__
        #kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, style = wx.DEFAULT_DIALOG_STYLE)
        self.listet = None
        self.variables = None
        self.force_chi = force_chi
        #self.labellem =  wx.StaticText(self, -1, u"Lemmatisation : ")
        #self.checklem = wx.CheckBox(self, -1)
        if not self.force_chi :
            self.label_typeformes =  wx.StaticText(self, -1, _(u"Used forms").decode('utf8'))
            typeformeschoiceChoices = [ _(u"actives and supplementaries").decode('utf8'), _(u"actives").decode('utf8'), _(u"supplementaries").decode('utf8')]
            self.typeformes = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, typeformeschoiceChoices, 0 )
            self.typeformes.SetSelection( 0 )

        self.label_var =  wx.StaticText(self, -1, _(u"Select by").decode('utf8'))
        self.choice = wx.Choice(self, -1, (100,50), choices = [_(u"variables").decode('utf8'), _(u"modalities").decode('utf8')])
        self.label1 =  wx.StaticText(self, -1, _(u"Choice").decode('utf8'))
        self.list_box_1 = wx.ListBox(self, -1, choices=[],  size = wx.Size( 150,200 ), style=wx.LB_EXTENDED | wx.LB_HSCROLL)
        self.button_2 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_1 = wx.Button(self, wx.ID_OK, "")
        if not self.force_chi :
            indices = [_(u"hypergeometrical law").decode('utf8'), _(u"chi2").decode('utf8')]
        else :
            indices = [_(u"chi2").decode('utf8')]
        self.label_indice =  wx.StaticText(self, -1, _(u"Score").decode('utf8'))
        self.choice_indice =  wx.Choice(self, -1, (100,50), choices = indices)
        if not self.force_chi :
            self.label = wx.StaticText(self, -1, _(u"Minimum frequency").decode('utf8'))
            self.spin = wx.SpinCtrl(self, -1, min = 1, max = 10000, initial = 10)
        self.Bind(wx.EVT_CHOICE, self.onselect, self.choice)
        self.Bind(wx.EVT_LISTBOX, self.onchoose, self.list_box_1)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle(_(u"Variables choice").decode('utf8'))
        if not self.force_chi :
            self.spin.SetValue(10)
        self.choice.SetSelection(0)
        self.choice_indice.SetSelection(0)
        self.button_1.Enable(False)
        #self.SetMinSize(wx.Size(300, 400))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.FlexGridSizer(0,2,0,0)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        #sizer_2.Add(self.labellem, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        #sizer_2.Add(self.checklem, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        if not self.force_chi :
            sizer_2.Add(self.label_typeformes, 0, wx.ALIGN_CENTER_VERTICAL, 3)
            sizer_2.Add(self.typeformes, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.label_var, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.choice, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.label1, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.list_box_1, 0, wx.ALIGN_RIGHT, 3)
        sizer_3.Add(self.button_2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_3.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.label_indice, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.choice_indice, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        if not self.force_chi :
            sizer_2.Add(self.label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
            sizer_2.Add(self.spin, 0, wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_1.Add(sizer_2, 0, wx.ALIGN_CENTER_HORIZONTAL, 3)
        sizer_1.Add(sizer_3, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_RIGHT, 3)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        self.Centre()

    def onselect(self, evt):
        self.list_box_1.Clear()
        if self.choice.GetSelection() == 0 :
            for var in self.variables :
                self.list_box_1.Append(var)
        else :
            for et in self.listet :
                self.list_box_1.Append(et)
    
    def onchoose(self, evt):
        if self.choice.GetSelection()== 0 :
            if len(self.list_box_1.GetSelections()) > 0 :
                self.button_1.Enable(True)
            else :
                self.button_1.Enable(False)
        elif self.choice.GetSelection() == 1 :
            if len(self.list_box_1.GetSelections()) > 1 :
                self.button_1.Enable(True)
            else :
                self.button_1.Enable(False)    

class PrefDendro ( wx.Dialog ):
    
    def __init__( self, parent, param ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Dendrogram").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.param = param
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Picture size").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"height").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer3.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_spinCtrl1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 50, 10000, 600 )
        bSizer3.Add( self.m_spinCtrl1, 0, wx.ALL, 5 )
        
        bSizer2.Add( bSizer3, 1, wx.EXPAND, 5 )
        
        bSizer31 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"width").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer31.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_spinCtrl2 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 50, 10000, 600 )
        bSizer31.Add( self.m_spinCtrl2, 0, wx.ALL, 5 )
        
        bSizer2.Add( bSizer31, 1, wx.EXPAND, 5 )
        
        fgSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
        
        self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"Dendrogram type").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer1.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        m_choice1Choices = [ u"phylogram", u"cladogram", u"fan", u"unrooted", u"radial" ]
        self.m_choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice1Choices, 0 )
        self.m_choice1.SetSelection( 0 )
        fgSizer1.Add( self.m_choice1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )
    
        self.text_format_image = wx.StaticText( self, wx.ID_ANY, _(u"Image format").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.text_format_image.Wrap( -1 )
        fgSizer1.Add( self.text_format_image, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.choice_format = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ['png', 'svg'], 0 )
        self.choice_format.SetSelection( 0 )
        fgSizer1.Add( self.choice_format, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        self.m_staticline31 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline31, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline41 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline41, 0, wx.EXPAND |wx.ALL, 5 )        
        
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Color or black and white").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        m_radioBox1Choices = [ _(u"color").decode('utf8'), _(u"black and white").decode('utf8') ]
        self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox1.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, _(u"Add cluster size").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        bSizer4.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox1.SetValue(True) 
        bSizer4.Add( self.m_checkBox1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )
        
        m_radioBox2Choices = [ _(u"circular diagram").decode('utf8'), _(u"bar").decode('utf8') ]
        self.m_radioBox2 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox2Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox2.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )
        
        
        fgSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        m_sdbSizer2.Realize();
        fgSizer1.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )
        
        self.__set_properties()
        self.SetSizer( fgSizer1 )
        self.Layout()
        fgSizer1.Fit( self )
        
        self.Centre( wx.BOTH )

    def __set_properties(self):
        self.m_spinCtrl2.SetValue(self.param['width'])
        self.m_spinCtrl1.SetValue(self.param['height'])
        self.m_choice1.SetSelection(self.param['type_dendro'])
        self.m_radioBox1.SetSelection(self.param['color_nb'])
        self.m_checkBox1.SetValue(self.param['taille_classe'])
        self.m_radioBox2.SetSelection(self.param['type_tclasse'])
        self.choice_format.SetSelection(self.param['svg'])
    
    def __del__( self ):
        pass


class PrefWordCloud ( wx.Dialog ):
    
    def __init__( self, parent, fromcluster = False ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Wordcloud settings").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        #self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Sélectionner les formes", wx.DefaultPosition, wx.DefaultSize, 0 )
        #self.m_staticText1.Wrap( -1 )
        #fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        #self.but_selectcol = wx.Button( self, wx.ID_ANY, u"Sélectionner", wx.DefaultPosition, wx.DefaultSize, 0 )
        #fgSizer1.Add( self.but_selectcol, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        #self.m_staticline1 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        #fgSizer1.Add( self.m_staticline1, 0, wx.EXPAND |wx.ALL, 5 )
        
        #self.m_staticline2 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        #fgSizer1.Add( self.m_staticline2, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer1 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"height").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.spin_H = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,30 ), wx.SP_ARROW_KEYS, 0, 10000, 600 )
        self.spin_H.SetValue( 800 )
        bSizer1.Add( self.spin_H, 0, wx.ALL, 5 )
        
        fgSizer1.Add( bSizer1, 1, wx.EXPAND, 5 )
        
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"width").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.spin_L = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,30 ), wx.SP_ARROW_KEYS, 0, 10000, 600 )
        self.spin_L.SetValue( 800 )
        bSizer3.Add( self.spin_L, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
        
        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, _(u"Picture format").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        fgSizer1.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        formatChoices = [ u"png", u"svg" ]
        self.format = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, formatChoices, 0 )
        self.format.SetSelection( 0 )
        fgSizer1.Add( self.format, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        if fromcluster :
            self.m_staticText111 = wx.StaticText( self, wx.ID_ANY, _(u"Word size proportional to ...").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText11.Wrap( -1 )
            fgSizer1.Add( self.m_staticText111, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
            IndiceChoices = [ _(u"chi2").decode('utf8'), _(u"frequency").decode('utf8') ]
            self.indice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, IndiceChoices, 0 )
            self.indice.SetSelection( 0 )
            fgSizer1.Add( self.indice, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )

        self.m_staticline13 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline13, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline14 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline14, 0, wx.EXPAND |wx.ALL, 5 )

        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Maximum number of forms").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.spin_maxword = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10000, 600 )
        self.spin_maxword.SetValue( 600 )
        fgSizer1.Add( self.spin_maxword, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.typeformes = wx.StaticText( self, wx.ID_ANY, _(u"Used forms").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.typeformes.Wrap( -1 )
        fgSizer1.Add( self.typeformes, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        typeformeschoiceChoices = [ _(u"actives").decode('utf8'), _(u"supplementaries").decode('utf8'), _(u"actives and supplementaries").decode('utf8') ]
        self.typeformeschoice = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, typeformeschoiceChoices, 0 )
        self.typeformeschoice.SetSelection( 0 )
        fgSizer1.Add( self.typeformeschoice, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticline11 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline11, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline12 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline12, 0, wx.EXPAND |wx.ALL, 5 )        
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, _(u"Text size").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer1.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        bSizer4 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        bSizer5.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_mincex = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 5 )
        self.spin_mincex.SetValue( 5 )
        bSizer5.Add( self.spin_mincex, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        bSizer4.Add( bSizer5, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )
        bSizer6.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_maxcex = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 50 )
        self.spin_maxcex.SetValue( 50 )
        bSizer6.Add( self.spin_maxcex, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        bSizer4.Add( bSizer6, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        fgSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )
        
        self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer61 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText81 = wx.StaticText( self, wx.ID_ANY, _(u"Text color").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText81.Wrap( -1 )
        bSizer61.Add( self.m_staticText81, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.color_text = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer61.Add( self.color_text, 0, wx.ALL, 5 )
        
        fgSizer1.Add( bSizer61, 1, wx.EXPAND, 5 )
        
        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, _(u"Background color").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        bSizer7.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.color_bg = wx.ColourPickerCtrl( self, wx.ID_ANY, (255,255,255), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer7.Add( self.color_bg, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( bSizer7, 1, wx.EXPAND, 5 )
        
        self.m_staticline9 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline9, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline10 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline10, 0, wx.EXPAND |wx.ALL, 5 )

        fgSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        fgSizer1.Add( m_sdbSizer1, 1, wx.EXPAND, 5 )
        
        self.SetSizer( fgSizer1 )
        self.Layout()
        fgSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
    
    def __del__( self ):
        pass
    
class PrefChi(sc.SizedDialog):
    def __init__(self, parent, ID, optionchi, title):

        sc.SizedDialog.__init__(self, None, -1, _(u"Settings").decode('utf8'), 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        pane.SetSizerProps(border=("all",5))
        self.parent = parent
        self.optionchi = optionchi
        

        self.label_obs = wx.StaticText(pane, -1, _(u"observed values").decode('utf8'))
        self.check1 = wx.CheckBox(pane, -1)
 
        self.label_theo = wx.StaticText(pane, -1, _(u"expected values").decode('utf8'))
        self.check2 = wx.CheckBox(pane, -1)

        self.label_resi = wx.StaticText(pane, -1, _(u"residuals").decode('utf8'))
        self.check3 = wx.CheckBox(pane, -1)

        self.label_contrib = wx.StaticText(pane, -1, _(u"standardized residuals").decode('utf8'))
        self.check4 = wx.CheckBox(pane, -1)
#        self.label_graph = wx.StaticText(pane, -1, u'graphique')
#        self.check8 = wx.CheckBox(pane, -1)
        self.label_pourcent = wx.StaticText(pane, -1, _(u"total percentage").decode('utf8'))
        self.check5 = wx.CheckBox(pane, -1)

        self.label_prl = wx.StaticText(pane, -1, _(u"row percentage").decode('utf8'))
        self.check6 = wx.CheckBox(pane, -1)

        self.label_prc = wx.StaticText(pane, -1, _(u"column percentage").decode('utf8'))
        self.check7 = wx.CheckBox(pane, -1)

        self.label_graph = wx.StaticText(pane, -1, _(u"graphical").decode('utf8'))
        self.check8 = wx.CheckBox(pane, -1)
        
        self.label_graphbw = wx.StaticText(pane, -1, _(u"black and white graphical").decode('utf8'))
        self.checkbw = wx.CheckBox(pane, -1)

        self.SetButtonSizer(self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL))

        self.__set_properties()
        self.Fit()
        self.SetMinSize(self.GetSize())

    def __set_properties(self):
        self.check1.SetValue(self.optionchi['valobs'])
        self.check2.SetValue(self.optionchi['valtheo'])
        self.check3.SetValue(self.optionchi['resi'])
        self.check4.SetValue(self.optionchi['contrib'])
        self.check5.SetValue(self.optionchi['pourcent'])
        self.check6.SetValue(self.optionchi['pourcentl'])
        self.check7.SetValue(self.optionchi['pourcentc'])
        self.check8.SetValue(self.optionchi['graph'])
        self.checkbw.SetValue(self.optionchi['bw'])

class ChiDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, optionchi, tableau, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)
        self.parent = parent 
        self.optionchi = optionchi
        self.chiopt = False
        self.tableau = tableau
        #self.Filename=parent.filename
        #self.content=parent.content[:]
        self.headers=self.tableau.get_colnames()
        LABELLIST=[]
        
        for i in self.headers:
            if len(i)>60 :
                LABELLIST.append(i[0:60])
            else:
                LABELLIST.append(i)
        
        self.ListOK=[]
        self.LabelListOK=LABELLIST
 
        self.list_box_1 = wx.ListBox(self, -1, choices=self.LabelListOK, style=wx.LB_EXTENDED|wx.LB_HSCROLL)
        self.list_box_2 = wx.ListBox(self, -1, choices=self.LabelListOK, style=wx.LB_EXTENDED|wx.LB_HSCROLL)
        self.button_1 = wx.Button(self, wx.ID_OK)
        self.button_cancel = wx.Button(self, wx.ID_CANCEL)
        self.button_pref = wx.Button(self, wx.ID_PREFERENCES)
        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_LISTBOX, self.selchange, self.list_box_1)
        self.Bind(wx.EVT_LISTBOX, self.selchange, self.list_box_2)
        self.Bind(wx.EVT_BUTTON, self.onparam, self.button_pref)
        self.button_1.Enable(False)
        # end wxGlade
#-------------------------------
    def __set_properties(self):
        # begin wxGlade: ConfChi2.__set_properties
        self.SetTitle(_(u"Variables selection").decode('utf8'))

    def __do_layout(self):
        # begin wxGlade: ConfChi2.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_4 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_3.Add(self.list_box_1, 0, wx.EXPAND, 0)
        sizer_3.Add(self.list_box_2, 0, wx.EXPAND|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_3, 1, wx.EXPAND, 0)
        sizer_4.Add(self.button_cancel, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_4.Add(self.button_pref, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_4.Add(self.button_1, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(sizer_4, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()
        # end wxGlade

    def selchange(self, event): # wxGlade: ConfChi2.<event_handler>
        if (len(self.list_box_1.GetSelections()) == 0) or (len(self.list_box_2.GetSelections()) == 0) :
            self.button_1.Enable(False)
        else :
            self.button_1.Enable(True)
    
    
    def onparam(self,event):
        self.dial = PrefChi(self.parent, -1, self.optionchi, '')
        self.dial.CenterOnParent()
        self.chiopt = self.dial.ShowModal()

class CorpusPref ( wx.Dialog ):
    
    def __init__( self, parent, parametres ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Settings").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE | wx.STAY_ON_TOP )
        self.parent = parent 
        langues_n = [u'français', u'english', u'german (expérimentale)', u'italian', u'swedish (expérimentale)', u'portuguese', u'spanish (expérimentale)', u'greek (expériementale)', u'galician (expérimentale)', u'autre...']
        self.langues = [u'french', u'english', u'german', u'italian', u'swedish', u'portuguese', u'spanish', u'greek', u'galician', u'other']
        self.encodages = [enc[0].lower() for enc in encodages]

        ucimark = [u'****', u'0000']
        ucemethod = [_(u"characters").decode('utf8'), _(u"occurrences").decode('utf8'), _(u"paragraphs").decode('utf8')]

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_panel1 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText7 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"corpus").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        fgSizer1.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.txtpath = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Path").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txtpath.Wrap( -1 )
        fgSizer1.Add( self.txtpath, 0, wx.ALL, 5 )

        self.m_staticText18 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Corpus' name").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText18.Wrap( -1 )
        fgSizer1.Add( self.m_staticText18, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.corpusname = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 200,-1 ), 0 )
        fgSizer1.Add( self.corpusname, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
             
        self.m_staticText1 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Characters set").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        encodage_choicesChoices = [' - '.join(encodage) for encodage in encodages]
        self.encodage_choices = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, encodage_choicesChoices, 0 )
        self.encodage_choices.SetSelection( 0 )
        fgSizer1.Add( self.encodage_choices, 0, wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Language").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        lang_choicesChoices = langues_n
        self.lang_choices = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, lang_choicesChoices, 0 )
        self.lang_choices.SetSelection( 0 )
        fgSizer1.Add( self.lang_choices, 0, wx.ALL, 5 )

        self.m_staticText19 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Dictionary").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )
        fgSizer1.Add( self.m_staticText19, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        
        fgSizer5 = wx.FlexGridSizer( 2, 2, 0, 0 )
        fgSizer5.SetFlexibleDirection( wx.BOTH )
        fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.radio_default_dict = wx.RadioButton( self.m_panel1, wx.ID_ANY, _(u"Default").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer5.Add( self.radio_default_dict, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.defaultdictpath = wx.TextCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 300,-1 ), wx.TE_READONLY )
        self.defaultdictpath.Enable( False )
        
        fgSizer5.Add( self.defaultdictpath, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.radio_other_dict = wx.RadioButton( self.m_panel1, wx.ID_ANY, _(u"Other").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer5.Add( self.radio_other_dict, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.otherdictpath = wx.FilePickerCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, _(u"Select a file").decode('utf8'), u"*.*", wx.DefaultPosition, wx.Size( 300,-1 ), wx.FLP_DEFAULT_STYLE )
        self.otherdictpath.SetMinSize(wx.Size(300, -1))
        fgSizer5.Add( self.otherdictpath, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.otherdictpath.Enable( False )
        
        
        bSizer2.Add( fgSizer5, 1, wx.EXPAND, 5 )
        
        
        fgSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )

        self.m_staticText3 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Output folder").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        
        fgSizer41 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer41.SetFlexibleDirection( wx.BOTH )
        fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.repout_choices = wx.TextCtrl( self.m_panel1, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.repout_choices.SetMinSize( wx.Size( 400,-1 ) )
        fgSizer41.Add( self.repout_choices, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_button1 = wx.Button( self.m_panel1, wx.ID_ANY, _(u"Change ...").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_button1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( fgSizer41, 1, wx.EXPAND, 5 )        

        self.m_staticText12 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Text mark").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )
        fgSizer1.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        ucimark_choicesChoices = ucimark
        self.ucimark_choices = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ucimark_choicesChoices, 0 )
        self.ucimark_choices.SetSelection( 0 )
        fgSizer1.Add( self.ucimark_choices, 0, wx.ALL, 5 )
        
        self.m_staticText6 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Use the expression dictionary").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer1.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_expressions = wx.CheckBox( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_expressions.SetValue(True) 
        fgSizer1.Add( self.check_expressions, 0, wx.ALL, 5 )
        
        self.m_staticText9 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Make text segments").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        fgSizer1.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_makeuce = wx.CheckBox( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_makeuce.SetValue(True) 
        fgSizer1.Add( self.check_makeuce, 0, wx.ALL, 5 )
        
        self.m_staticText10 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Text segments build process").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        fgSizer1.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        uce_modeChoices = ucemethod
        self.uce_mode = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, uce_modeChoices, 0 )
        self.uce_mode.SetSelection( 0 )
        fgSizer1.Add( self.uce_mode, 0, wx.ALL, 5 )
        
        self.m_staticText13 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Text segments size").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )
        fgSizer1.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.uce_size = wx.SpinCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000000, 40 )
        fgSizer1.Add( self.uce_size, 0, wx.ALL, 5 )
        
        
        self.m_panel1.SetSizer( fgSizer1 )
        self.m_panel1.Layout()
        fgSizer1.Fit( self.m_panel1 )
        self.m_notebook1.AddPage( self.m_panel1, _(u"General").decode('utf8'), True )
        self.m_panel2 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText4 = wx.StaticText( self.m_panel2, wx.ID_ANY, _(u"Put text in lowercase").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_lower = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_lower.SetValue(True) 
        fgSizer3.Add( self.check_lower, 0, wx.ALL, 5 )
        
        self.m_staticText5 = wx.StaticText( self.m_panel2, wx.ID_ANY, _(u"Delete characters not in this list").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer3.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.check_charact = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_charact.SetValue(True) 
        fgSizer4.Add( self.check_charact, 0, wx.ALL, 5 )
        
        self.txt_charact = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txt_charact.SetMinSize( wx.Size( 400,-1 ) )
        
        fgSizer4.Add( self.txt_charact, 0, wx.ALL|wx.EXPAND, 5 )
        
        
        fgSizer3.Add( fgSizer4, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        self.m_staticText14 = wx.StaticText( self.m_panel2, wx.ID_ANY, _(u"Replace apostrophe by space").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )
        fgSizer3.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_apos = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_apos.SetValue(True) 
        fgSizer3.Add( self.check_apos, 0, wx.ALL, 5 )
        
        self.m_staticText15 = wx.StaticText( self.m_panel2, wx.ID_ANY, _(u"Replace dash by space").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )
        fgSizer3.Add( self.m_staticText15, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_tirets = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_tirets.SetValue(True) 
        fgSizer3.Add( self.check_tirets, 0, wx.ALL, 5 )
        
        self.m_staticText17 = wx.StaticText( self.m_panel2, wx.ID_ANY, _(u"Keep punctuation").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        fgSizer3.Add( self.m_staticText17, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_ponct = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_ponct, 0, wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self.m_panel2, wx.ID_ANY, _(u"No space between two forms").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )
        fgSizer3.Add( self.m_staticText16, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_tolist = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_tolist, 0, wx.ALL, 5 )
        
        
        self.m_panel2.SetSizer( fgSizer3 )
        self.m_panel2.Layout()
        fgSizer3.Fit( self.m_panel2 )
        self.m_notebook1.AddPage( self.m_panel2, _(u"Cleaning").decode('utf8'), False )
        
        bSizer1.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
       

        # Connect Events
        self.Bind(wx.EVT_BUTTON, self.OnChangeDir, self.m_button1)
        self.lang_choices.Bind( wx.EVT_CHOICE, self.OnChangeLangage )
        self.radio_other_dict.Bind( wx.EVT_RADIOBUTTON, self.changedictchoice )
        self.radio_default_dict.Bind( wx.EVT_RADIOBUTTON, self.changedictchoice )
        self.otherdictpath.Bind( wx.EVT_FILEPICKER_CHANGED, self.selectdict) 

        self.setparametres(parametres) 
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )

    def OnChangeDir(self, evt) :
        dlg = wx.DirDialog(self.parent, _(u"Choose a folder").decode('utf8'), style = wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK :
            self.repout_choices.SetValue(dlg.GetPath())
    
    def __del__( self ):
        pass

    def setparametres(self, parametres) :
        if  locale.getpreferredencoding().lower() == 'mac-roman' :
            enc = self.encodages.index('macroman')
        else :
            try :
                enc = self.encodages.index(locale.getpreferredencoding().lower())
            except ValueError :
                enc = self.encodages.index('utf-8')
        self.encodage_choices.SetSelection(enc)
        self.lang_choices.SetSelection(0)
        self.repout_choices.SetValue(parametres['pathout'])
        self.corpusname.SetValue(parametres['corpus_name'])
        self.ucimark_choices.SetSelection(parametres['ucimark'])
        self.check_expressions.SetValue(parametres['expressions'])
        self.check_makeuce.SetValue(parametres['douce'])
        self.uce_mode.SetSelection(parametres['ucemethod'])
        self.uce_size.SetValue(parametres['ucesize'])
        self.check_lower.SetValue(parametres['lower'])
        #self.check_charact.SetValue(parametres['charact'])
        self.txt_charact.SetValue(parametres['keep_caract'])
        self.check_apos.SetValue(parametres['apos'])
        self.check_tirets.SetValue(parametres['tiret'])
        self.check_tolist.SetValue(parametres['tolist'])
        self.check_ponct.SetValue(parametres['keep_ponct'])
        self.defaultdictpath.SetValue(self.langues[0])

    def doparametres(self) :
        parametres = {}
        parametres['encoding'] = encodages[self.encodage_choices.GetSelection()][0]
        parametres['lang'] = self.langues[self.lang_choices.GetSelection()]
        parametres['pathout'] = self.repout_choices.GetValue()
        parametres['corpus_name'] = self.corpusname.GetValue()
        parametres['ucimark'] = self.ucimark_choices.GetSelection()
        parametres['expressions'] = self.check_expressions.GetValue()
        parametres['douce'] =  self.check_makeuce.GetValue()
        parametres['ucemethod'] = self.uce_mode.GetSelection()
        parametres['ucesize'] = self.uce_size.GetValue()
        parametres['lower'] = self.check_lower.GetValue()
        parametres['charact'] = self.check_charact.GetValue()
        parametres['keep_caract'] = self.txt_charact.GetValue()
        parametres['apos'] = self.check_apos.GetValue()
        parametres['tiret'] = self.check_tirets.GetValue()
        parametres['tolist'] = self.check_tolist.GetValue()
        parametres['keep_ponct'] = self.check_ponct.GetValue()
        if self.radio_other_dict.GetValue() :
            parametres['dictionary'] = self.otherdictpath.GetPath()
        for val in parametres :
            if isinstance(parametres[val], bool) :
                if parametres[val] :
                    parametres[val] = 1
                else :
                    parametres[val] = 0
        return parametres
    
    def OnChangeLangage(self, evt):
        self.defaultdictpath.SetValue(self.langues[self.lang_choices.GetSelection()])
    
    def changedictchoice(self, evt):
        if self.radio_default_dict.GetValue() :
            self.otherdictpath.Enable( False )
            self.m_sdbSizer1OK.Enable( True )
        else :
            self.otherdictpath.Enable( True )
            if self.otherdictpath.GetPath() == '' :
                self.m_sdbSizer1OK.Enable( False )
    
    def selectdict(self, evt):
        if self.otherdictpath.GetPath() != '' :
            self.m_sdbSizer1OK.Enable( True )
        


class ConcordList(wx.HtmlListBox):
    def __init__(self, parent, concord):
        self.concord = concord
        #self.script_status = dict()
        wx.HtmlListBox.__init__(self, parent, -1, size = (900, 600))
        self.SetItemCount(len(concord))
        #self.Bind(wx.EVT_LISTBOX, self.RefreshMe)
        #self.Bind(wx.EVT_LISTBOX_DCLICK, self.Download)
  
    def OnGetItem(self, index):
        return self.concord[index] #+ '<br>'

class message(wx.Frame):
    def __init__(self, parent, items, title, size, save = True, uceids = None):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = size, style = wx.CLOSE_BOX|wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT|wx.TAB_TRAVERSAL )
        self.save = save
        self.uceids = uceids
        self.ira = wx.GetApp().GetTopWindow()
        self.SetIcon(self.ira._icon)
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.items = items
        self.html = ""
        #self.HtmlPage=wx.html.HtmlWindow(self, -1)
        self.HtmlPage = ConcordList(self, items)
        #self.HtmlPage.SetMinSize( size )
        #if "gtk2" in wx.PlatformInfo:
        #    self.HtmlPage.SetStandardFonts()
        #self.HtmlPage.SetFonts('Courier','Courier')

        self.button_1 = wx.Button(self, wx.ID_CANCEL)

        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
        if self.save :
            self.button_2 = wx.Button(self, wx.ID_SAVE)
            self.Bind(wx.EVT_BUTTON, self.OnSavePage, self.button_2)
        if self.uceids is not None :
            self.butsub = wx.Button(self, -1, _(u"Build sub corpus").decode('utf8'))
            self.Bind(wx.EVT_BUTTON, self.OnSub, self.butsub)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)
        self.__do_layout()

    def __do_layout(self):
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        sizer_2.Add(self.HtmlPage, 1, wx.EXPAND|wx.ADJUST_MINSIZE, 0)
        #m_sdbSizer1 = wx.StdDialogButtonSizer()
        m_sdbSizer1 = wx.BoxSizer(wx.HORIZONTAL)
        m_sdbSizer1.Add(  self.button_1 , 0, wx.RIGHT | wx.EXPAND)
        if self.save :
            m_sdbSizer1.Add(  self.button_2 , 0, wx.RIGHT | wx.EXPAND)
        if self.uceids is not None :
            m_sdbSizer1.Add(  self.butsub , 0, wx.RIGHT | wx.EXPAND)
        #m_sdbSizer1.Realize()
        sizer_2.Add(m_sdbSizer1, 0, wx.RIGHT | wx.EXPAND, 5)
        self.SetSizer(sizer_2)
        self.Layout()
        sizer_2.Fit( self )

    def OnSavePage(self, evt) :
        dlg = wx.FileDialog(
            self, message=_(u"Save as ...").decode('utf8'), defaultDir=os.getcwd(),
            defaultFile="concordancier.html", wildcard="html|*.html", style=wx.SAVE | wx.OVERWRITE_PROMPT
            )
        dlg.SetFilterIndex(2)
        dlg.CenterOnParent()
        self.html = '<br>'.join([self.items[i] for i in range(0,len(self.items))])
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            with open(path, 'w') as f :
                f.write(self.html)

    def OnCloseMe(self, event):
        self.Close(True)

    def OnCloseWindow(self, event):
        self.Destroy()
    
    def OnSub(self ,evt):
        parametres = {'fromuceids' : True, 'uceids' : self.uceids, 'isempty' : True}
        self.ira.OnSubText(wx.MenuEvent(), None, parametres)


class ExtractDialog ( wx.Dialog ):
    
    def __init__( self, parent, option ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )

        self.option = option
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"corpus").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.corpusfile = wx.FilePickerCtrl( self, wx.ID_ANY, wx.EmptyString, _(u"Select a file").decode('utf8'), u"*.txt", wx.DefaultPosition, wx.Size( -1,-1 ), wx.FLP_DEFAULT_STYLE|wx.FLP_FILE_MUST_EXIST|wx.FLP_OPEN )
        self.corpusfile.SetMinSize( wx.Size( 500,-1 ) )
        
        fgSizer1.Add( self.corpusfile, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"Characters set").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        encodageChoices = [' - '.join(encodage) for encodage in encodages]
        self.encodage = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, encodageChoices, 0 )
        self.encodage.SetSelection( 0 )
        self.encodage.SetMinSize( wx.Size( 200,-1 ) )
        
        fgSizer1.Add( self.encodage, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        if option == 'splitvar' :
            self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"Variables (with the * but without the _)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText3.Wrap( -1 )
            fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.txtvar = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
            self.txtvar.SetMinSize( wx.Size( 200,-1 ) )
            
            fgSizer1.Add( self.txtvar, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        if option == 'mods' :
            self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"Modalities (one by line, with the *)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText4.Wrap( -1 )
            fgSizer1.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.txtmods = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
            self.txtmods.SetMinSize( wx.Size( 200,150 ) )
            
            fgSizer1.Add( self.txtmods, 0, wx.ALL|wx.EXPAND, 5 )
            
            self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Extraction type").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText5.Wrap( -1 )
            fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            extractformatChoices = [ _(u"Only one file").decode('utf8'), _(u"One file by modality").decode('utf8') ]
            self.extractformat = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, extractformatChoices, 1, wx.RA_SPECIFY_COLS )
            self.extractformat.SetSelection( 0 )
            fgSizer1.Add( self.extractformat, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        if option == 'them' :
            self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"thematics (one by line, with the -*)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText4.Wrap( -1 )
            fgSizer1.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.txtmods = wx.TextCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.TE_MULTILINE )
            self.txtmods.SetMinSize( wx.Size( 200,150 ) )
            
            fgSizer1.Add( self.txtmods, 0, wx.ALL|wx.EXPAND, 5 )
            
            #self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Extraction type").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            #self.m_staticText5.Wrap( -1 )
            #fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            #extractformatChoices = [ _(u"Only one file").decode('utf8'), _(u"One file by thematic").decode('utf8') ]
            #self.extractformat = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, extractformatChoices, 1, wx.RA_SPECIFY_COLS )
            #self.extractformat.SetSelection( 0 )
            #fgSizer1.Add( self.extractformat, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )        
            
        
        fgSizer1.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize()
        
        fgSizer1.Add( m_sdbSizer1, 1, wx.EXPAND, 5 )
        
        
        self.SetSizer( fgSizer1 )
        self.Layout()
        fgSizer1.Fit( self )
        
        self.Centre( wx.BOTH )

    def make_param(self) :
        parametres = {}
        le = [enc[0].lower() for enc in encodages]
        parametres['filein'] = self.corpusfile.GetPath()
        encodage = le[self.encodage.GetSelection()]
        parametres['encodein'] = encodage
        if self.option == 'splitvar' :
            parametres['var'] = self.txtvar.GetValue()
        if self.option == 'mods' :
            parametres['mods'] = self.txtmods.GetValue().splitlines()
            if self.extractformat.GetSelection() == 0 :
                parametres['onefile'] = True
            else :
                parametres['onefile'] = False
        if self.option == 'them' :
            parametres['them'] = self.txtmods.GetValue().splitlines()
        #    if self.extractformat.GetSelection() == 0 :
        #        parametres['onefile'] = True
        #    else :
        #        parametres['onefile'] = False        
        parametres['encodeout'] = le[self.encodage.GetSelection()]
        return parametres
    
    def __del__( self ):
        pass

class FreqDialog ( wx.Dialog ):
    
    def __init__( self, parent, listcol, title, size =  wx.Size( -1,-1 ), showNA = True):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        self.header = listcol
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        m_listBox1Choices = self.header
        self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_listBox1Choices, wx.LB_EXTENDED|wx.LB_HSCROLL )
        self.m_listBox1.SetMinSize( wx.Size( 500,-1 ) )
        bSizer1.Add( self.m_listBox1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        if showNA :
            fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
            fgSizer1.SetFlexibleDirection( wx.BOTH )
            fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
            self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Include empty cells (NA)").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText1.Wrap( -1 )
            fgSizer1.Add( self.m_staticText1, 0, wx.ALL, 5 )
        
            self.includeNA = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
            fgSizer1.Add( self.includeNA, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
            bSizer1.Add( fgSizer1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
        self.Bind(wx.EVT_LISTBOX, self.selchange, self.m_listBox1)
        self.m_sdbSizer1OK.Enable(False)
    
    def __del__( self ):
        pass
    
    def selchange(self, evt):
        if len(self.m_listBox1.GetSelections()) == 0 :
            self.m_sdbSizer1OK.Enable(False)
        else :
            self.m_sdbSizer1OK.Enable(True)

class ProtoDial ( wx.Dialog ):
    
    def __init__( self, parent, headers ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Settings").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.Size( -1,-1 ), wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Variables").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"Ranks").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        variablesChoices = headers
        self.variables = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, variablesChoices, wx.LB_HSCROLL|wx.LB_MULTIPLE )
        self.variables.SetMinSize( wx.Size( 350,-1 ) )
        
        fgSizer1.Add( self.variables, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        rangsChoices = headers
        self.rangs = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, rangsChoices, wx.LB_HSCROLL|wx.LB_MULTIPLE )
        self.rangs.SetMinSize( wx.Size( 350,-1 ) )
        
        fgSizer1.Add( self.rangs, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        
        bSizer1.Add( fgSizer1, 1, wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"Limit frequency").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer3.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        
        choix_freqChoices = [ _(u"automatic (mean)").decode('utf8'), _(u"manual").decode('utf8') ]
        self.choix_freq = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choix_freqChoices, 0 )
        self.choix_freq.SetSelection( 0 )
        bSizer2.Add( self.choix_freq, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.freqlim = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        self.freqlim.Enable( False )
        self.freqlim.SetMinSize( wx.Size( 100,-1 ) )
        
        bSizer2.Add( self.freqlim, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        
        fgSizer3.Add( bSizer2, 1, wx.EXPAND, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"Limit rank").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer21 = wx.BoxSizer( wx.HORIZONTAL )
        
        choix_rangChoices = [ _(u"automatic (mean)").decode('utf8'), _(u"manual").decode('utf8')]
        self.choix_rang = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choix_rangChoices, 0 )
        self.choix_rang.SetSelection( 0 )
        bSizer21.Add( self.choix_rang, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.ranglim = wx.TextCtrl( self, wx.ID_ANY, u"0", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        self.ranglim.Enable( False )
        self.ranglim.SetMinSize( wx.Size( 100,-1 ) )
        
        bSizer21.Add( self.ranglim, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        
        fgSizer3.Add( bSizer21, 1, wx.EXPAND, 5 )
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, _(u"Minimum frequency").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer3.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_textCtrl4 = wx.TextCtrl( self, wx.ID_ANY, u"2", wx.DefaultPosition, wx.DefaultSize, wx.TE_CENTRE )
        fgSizer3.Add( self.m_textCtrl4, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Type de représentation", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer3.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        m_choice3Choices = [ u"Classical - List", u"Classical - Cloud", u"Plan" ]
        self.typegraph = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, m_choice3Choices, 0 )
        self.typegraph.SetSelection( 0 )
        fgSizer3.Add( self.typegraph, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 5 )
        
        bSizer1.Add( fgSizer3, 0, wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.choix_freq.Bind( wx.EVT_CHOICE, self.UpdateText )
        self.choix_rang.Bind( wx.EVT_CHOICE, self.UpdateText )
        self.Bind(wx.EVT_LISTBOX, self.selchange, self.variables)
        self.Bind(wx.EVT_LISTBOX, self.selchange, self.rangs)
        
        self.m_sdbSizer1OK.Enable(False)
    
    def __del__( self ):
        pass
    
    def selchange(self, evt):
        if (len(self.variables.GetSelections()) == 0) or (len(self.rangs.GetSelections()) == 0) or (len(self.variables.GetSelections()) != len(self.rangs.GetSelections())) :
            self.m_sdbSizer1OK.Enable(False)
        else :
            self.m_sdbSizer1OK.Enable(True)
    
    
    # Virtual event handlers, overide them in your derived class
    def UpdateText( self, event ):
        event.Skip()

class SimpleDialog ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_panel1 = wx.Panel( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_staticText1 = wx.StaticText( self.m_panel1, wx.ID_ANY, _(u"Export finished. Open in a web browser :").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer2.Add( self.m_staticText1, 0, wx.ALL, 5 )
        
        self.link = wx.HyperlinkCtrl( self.m_panel1, wx.ID_ANY, u"wxFB Website", u"http://www.wxformbuilder.org", wx.DefaultPosition, wx.DefaultSize, wx.HL_DEFAULT_STYLE )
        bSizer2.Add( self.link, 0, wx.ALL, 5 )
        
        
        self.m_panel1.SetSizer( bSizer2 )
        self.m_panel1.Layout()
        bSizer2.Fit( self.m_panel1 )
        bSizer1.Add( self.m_panel1, 1, wx.EXPAND |wx.ALL, 5 )
        
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


class SubTextFromMetaDial ( wx.Dialog ):
    
    def __init__( self, parent, parametres ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Subcorpus").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Name").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.subcorpusname = wx.TextCtrl( self, wx.ID_ANY, parametres['corpus_name'], wx.DefaultPosition, wx.Size( 300,-1 ), 0 )
        fgSizer1.Add( self.subcorpusname, 0, wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"Select one or more metadata").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        m_listBox1Choices = parametres['meta']
        self.m_listBox1 = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.Size( -1,-1 ), m_listBox1Choices, wx.LB_HSCROLL|wx.LB_MULTIPLE )
        self.m_listBox1.SetMinSize( wx.Size( -1,200 ) )
        self.m_listBox1.SetMaxSize( wx.Size( -1,500 ) )
        
        fgSizer1.Add( self.m_listBox1, 0, wx.ALL|wx.EXPAND, 5 )
        
        
        bSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
        self.Bind(wx.EVT_LISTBOX, self.onchoose, self.m_listBox1)
        if not parametres.get('isempty', False) :
            self.m_sdbSizer1OK.Enable(False)
    
    def __del__( self ):
        pass
    
    def onchoose(self, evt):
        if len(self.m_listBox1.GetSelections()) > 0 :
            self.m_sdbSizer1OK.Enable(True)
        else :
            self.m_sdbSizer1OK.Enable(False)

class BarGraphDialog ( wx.Dialog ):
    
    def __init__( self, parent, width, height ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = _(u"Preferences").decode('utf8'), pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, _(u"Size").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        bSizer2.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        sizeradioChoices = [ _(u"automatic").decode('utf8'), _(u"manual").decode('utf8') ]
        self.sizeradio = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, sizeradioChoices, 1, wx.RA_SPECIFY_COLS )
        self.sizeradio.SetSelection( 0 )
        bSizer2.Add( self.sizeradio, 0, wx.ALIGN_TOP|wx.ALL, 5 )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, _(u"width").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.widthsp = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000000, 600 )
        fgSizer1.Add( self.widthsp, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, _(u"height").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.heightsp = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 10000000, 400 )
        fgSizer1.Add( self.heightsp, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        
        bSizer2.Add( fgSizer1, 1, wx.EXPAND, 5 )
        
        
        bSizer1.Add( bSizer2, 1, wx.EXPAND, 5 )
        
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, _(u"Image format").decode('utf8'), wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        formatChoices = [ u"png", u"svg" ]
        self.format = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, formatChoices, 0 )
        self.format.SetSelection( 0 )
        bSizer3.Add( self.format, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        
        bSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
        
        
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        self.sizeradio.Bind( wx.EVT_RADIOBOX, self.OnSizeRadio )
        
        self.widthsp.SetValue(width)
        self.heightsp.SetValue(height)
        self.widthsp.Enable(False)
        self.heightsp.Enable(False)
        self.m_sdbSizer1OK.SetFocus()
    
    def __del__( self ):
        pass
    
    
    # Virtual event handlers, overide them in your derived class
    def OnSizeRadio( self, event ):
        if self.sizeradio.GetSelection() == 0 :
            self.widthsp.Enable(False)
            self.heightsp.Enable(False)
        else :
            self.widthsp.Enable(True)
            self.heightsp.Enable(True)         
        event.Skip()

class MessageImage(wx.Frame):
    def __init__(self, parent, parametres, title, size):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = size, style = wx.CLOSE_BOX|wx.DEFAULT_FRAME_STYLE|wx.FRAME_FLOAT_ON_PARENT|wx.TAB_TRAVERSAL )
        self.ira = wx.GetApp().GetTopWindow()
        self.SetIcon(self.ira._icon)
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.parametres = parametres
        self.imageFile = self.parametres['tmpgraph']
        if parametres['svg'] == 'TRUE' :
            self.imagename = u"image.svg"
        else :
            self.imagename = u"image.png"
        self.HtmlPage = wx.html.HtmlWindow(self, -1)
        self.HtmlPage.SetMinSize(size)
        if "gtk2" in wx.PlatformInfo:
            self.HtmlPage.SetStandardFonts()
        self.HtmlPage.SetFonts('Courier', 'Courier')
        
        self.button_1 = wx.Button(self, wx.ID_CANCEL)
        self.button_2 = wx.Button(self, wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnSaveImage, self.button_2)
        self.do_layout()

    def do_layout(self):
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_1.Add(self.HtmlPage, 2, wx.EXPAND, 0)

        self.m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1.AddButton(  self.button_2 )
        self.m_sdbSizer1.AddButton(  self.button_1 )
        self.m_sdbSizer1.Realize()
        self.sizer_1.Add(self.m_sdbSizer1, 0, wx.EXPAND, 5)
        self.SetSizer(self.sizer_1)
        self.Layout()
        self.sizer_1.Fit( self )

    def OnCloseMe(self, event):
        self.Destroy()

    def OnSaveImage(self, event) :
        dlg = wx.FileDialog(
            self, message=_(u"Save as...").decode('utf8'), defaultDir=os.getcwd(),
            defaultFile= self.imagename, wildcard=self.parametres['wildcard'], style=wx.SAVE | wx.OVERWRITE_PROMPT
            )
        dlg.SetFilterIndex(2)
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            copyfile(self.imageFile, path)

class BarFrame :
    def __init__(self, ira, table, colnames, rownames, tree = False):
        if not tree :
            width = 100 + (10*len(rownames)) + (100 * len(colnames))
            height = len(rownames) * 15
            if height < 400 : 
                height = 400
        else :
            width = 500
            height = (35 * len(colnames)) + (15 * len(rownames))
        dial = BarGraphDialog(ira, width, height)
        val = dial.ShowModal()
        if val == wx.ID_OK :
            tmpgraph = tempfile.mktemp(dir=ira.TEMPDIR)        
            if dial.format.GetSelection() == 0 :
                svg = 'FALSE'
                wildcard = "png|*.png"
            else :
                svg = 'TRUE'
                wildcard = "svg|*.svg"
            parametres = {'width' : dial.widthsp.GetValue(),
                          'height': dial.heightsp.GetValue(),
                          'colnames' : colnames,
                          'rownames' : rownames,
                          'tmpgraph' : tmpgraph,
                          'rgraph' : ira.RscriptsPath['Rgraph'],
                          'svg' : svg,
                          'wildcard' : wildcard}
            if tree :
                parametres['tree'] = tree
            txt = barplot(table, parametres)
            tmpscript = tempfile.mktemp(dir=ira.TEMPDIR)
            with open(tmpscript,'w') as f :
                f.write(txt)
            exec_rcode(ira.RPath, tmpscript, wait = True)
            win = MessageImage(ira, parametres, _(u"Graphic").decode('utf8'), size=(700, 500))
            if svg == 'FALSE' :
                txt = "<img src='%s'>" % tmpgraph
            else :
                txt = """Copiez ce lien dans votre navigateur : <br>
                        <a href="%s">%s</a>""" % (tmpgraph, tmpgraph)
            win.HtmlPage.SetPage(txt)
            win.Show(True)
        dial.Destroy()           