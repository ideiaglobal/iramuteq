#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL
import  wx
import  wx.lib.colourselect as  csel
import wx.lib.sized_controls as sc
import wx.lib.filebrowsebutton as filebrowse
import locale
import os
import sys
#from listlex import *
from KeyFrame import AlcOptFrame
#---------------------------------------------------------------------------
provider = wx.SimpleHelpProvider()
wx.HelpProvider_Set(provider)

#---------------------------------------------------------------------------


encodages = [[u'cp1252',u'Windows'], [u'utf-8',u'Linux'], [u'MacRoman',u'MacOs X'], [u'ascii', u'English'], [u'big5', u'Traditional Chinese'], [u'big5hkscs', u'Traditional Chinese'], [u'cp037', u'English'], [u'cp424', u'Hebrew'], [u'cp437', u'English'], [u'cp500', u'Western Europe'], [u'cp737', u'Greek'], [u'cp775', u'Baltic languages'], [u'cp850', u'Western Europe'], [u'cp852', u'Central and Eastern Europe'], [u'cp855', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'cp856', u'Hebrew'], [u'cp857', u'Turkish'], [u'cp860', u'Portuguese'], [u'cp861', u'Icelandic'], [u'cp862', u'Hebrew'], [u'cp863', u'Canadian'], [u'cp864', u'Arabic'], [u'cp865', u'Danish, Norwegian'], [u'cp866', u'Russian'], [u'cp869', u'Greek'], [u'cp874', u'Thai'], [u'cp875', u'Greek'], [u'cp932', u'Japanese'], [u'cp949', u'Korean'], [u'cp950', u'Traditional Chinese'], [u'cp1006', u'Urdu'], [u'cp1026', u'Turkish'], [u'cp1140', u'Western Europe'], [u'cp1250', u'Central and Eastern Europe'], [u'cp1251', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'cp1253', u'Greek'], [u'cp1254', u'Turkish'], [u'cp1255', u'Hebrew'], [u'cp1256', u'Arabic'], [u'cp1257', u'Baltic languages'], [u'cp1258', u'Vietnamese'], [u'euc_jp', u'Japanese'], [u'euc_jis_2004', u'Japanese'], [u'euc_jisx0213', u'Japanese'], [u'euc_kr', u'Korean'], [u'gb2312', u'Simplified Chinese'], [u'gbk', u'Unified Chinese'], [u'gb18030', u'Unified Chinese'], [u'hz', u'Simplified Chinese'], [u'iso2022_jp', u'Japanese'], [u'iso2022_jp_1', u'Japanese'], [u'iso2022_jp_2', u'Jp, K, S C, WE, G'], [u'iso2022_jp_2004', u'Japanese'], [u'iso2022_jp_3', u'Japanese'], [u'iso2022_jp_ext', u'Japanese'], [u'iso2022_kr', u'Korean'], [u'latin_1', u'West Europe'], [u'iso8859_2', u'Central and Eastern Europe'], [u'iso8859_3', u'Esperanto, Maltese'], [u'iso8859_4', u'Baltic languages'], [u'iso8859_5', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'iso8859_6', u'Arabic'], [u'iso8859_7', u'Greek'], [u'iso8859_8', u'Hebrew'], [u'iso8859_9', u'Turkish'], [u'iso8859_10', u'Nordic languages'], [u'iso8859_13', u'Baltic languages'], [u'iso8859_14', u'Celtic languages'], [u'iso8859_15', u'Western Europe'], [u'iso8859_16', u'South-Eastern Europe'], [u'johab', u'Korean'], [u'koi8_r', u'Russian'], [u'koi8_u', u'Ukrainian'], [u'mac_cyrillic', u'Bulg, Byelorus, Mace, Rus, Serb'], [u'mac_greek', u'Greek'], [u'mac_iceland', u'Icelandic'], [u'mac_latin2', u'Central and Eastern Europe'], [u'mac_turkish', u'Turkish'], [u'ptcp154', u'Kazakh'], [u'shift_jis', u'Japanese'], [u'shift_jis_2004', u'Japanese'], [u'shift_jisx0213', u'Japanese'], [u'utf_32', u'all languages'], [u'utf_32_be', u'all languages'], [u'utf_32_le', u'all languages'], [u'utf_16', u'all languages'], [u'utf_16_be', u'all languages (BMP only)'], [u'utf_16_le', u'all languages (BMP only)'], [u'utf_7', u'all languages'], [u'utf_8_sig', u'all languages']]

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
        grid_sizer = wx.FlexGridSizer(5, 2, 2, 2)
##############################

        label = wx.StaticText(self, -1, u"La première ligne contient les noms de colonne")
        label.SetHelpText(u"La première ligne contient les noms de colonne")
        grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        on = ["oui", "non"]
        self.radio_box_1 = wx.RadioBox(self, -1, u"", choices=on, majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.radio_box_1.SetHelpText(u"La première ligne contient les noms de colonne")
        grid_sizer.Add(self.radio_box_1, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

##############################

        label = wx.StaticText(self, -1, u"La première colonne contient un identifiant")
        label.SetHelpText(u"La première colonne contient un identifiant")
        grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        on = ["oui", "non"]
        self.radio_box_2 = wx.RadioBox(self, -1, u"", choices=on, majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.radio_box_2.SetHelpText(u"La première colonne contient un identifiant")
        grid_sizer.Add(self.radio_box_2, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)

##############################
        if sep:
            label = wx.StaticText(self, -1, u"Séparateur de colonne")
            label.SetHelpText(u"Quel charactère sépare les colonnes ?")
            grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.colsep = [";", "tabulation", ","]
            self.choice3 = wx.Choice(self, -1, (100, 50), choices=self.colsep)
            self.choice3.SetHelpText(u"Quel charactère sépare les colonnes ?")
            grid_sizer.Add(self.choice3, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
    
    ##############################
    
            label = wx.StaticText(self, -1, u"Séparateur de texte")
            label.SetHelpText(u"Quel caractère encadre les champs texte ?")
            grid_sizer.Add(label, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.txtsep = ["\"", "'"]
            self.choice4 = wx.Choice(self, -1, (100, 50), choices=self.txtsep)
            self.choice4.SetHelpText(u"Quel caractère encadre les champs texte ?")
            grid_sizer.Add(self.choice4, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.choice3.SetSelection(0)
            self.choice4.SetSelection(0)
            self.text = wx.StaticText(self, -1, u"Encodage du corpus : ")
            grid_sizer.Add(self.text, 1, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
            self.le = [enc[0].lower() for enc in encodages] 
            self.list_encodages = wx.Choice(self, -1, (25, 30), choices=[' - '.join(encodage) for encodage in encodages])
            if locale.getpreferredencoding().lower() == 'mac-roman' :
                enc = self.le.index('macroman')
            else :
                enc = self.le.index(locale.getpreferredencoding().lower())
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
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cnacels the dialog. (Cool, huh?)")
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
        print str(LIST_CLASSE_OK)
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
        btn.SetHelpText("The OK button completes the dialog")
        btn.SetDefault()
        btnsizer.AddButton(btn)

        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("The Cancel button cnacels the dialog. (Cool, huh?)")
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

class EncodeDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        kwds["size"] = wx.Size(100, 60)
        kwds["title"] = u'Encodage'
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_dict = wx.StaticText(self, -1, u"Langue")
        langues_n = [u'français', u'english', u'german (expérimentale)', u'italian (expérimentale)', u'swedish (exp.)', u'portuguese (exp.)']
        self.langues = [u'french', u'english', u'german', 'italian', 'swedish', 'portuguese']
        self.choice_dict = wx.Choice(self, -1, choices = langues_n)
        self.encodages = encodages
        self.text = wx.StaticText(self, -1, u"Encodage du corpus : ")
        self.le = [enc[0].lower() for enc in self.encodages] 
        self.list_encodages = wx.Choice(self, -1, (25, 50), choices=[' - '.join(encodage) for encodage in self.encodages])#style=wx.LB_SINGLE | wx.LB_HSCROLL)
        self.button_1 = wx.Button(self, wx.ID_OK, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle(u"Encodage du corpus")
        self.SetMinSize(wx.Size(300, 100))
        if  locale.getpreferredencoding().lower() == 'mac-roman' :
            enc = self.le.index('macroman')
        else :
            enc = self.le.index(locale.getpreferredencoding().lower())
        self.list_encodages.SetSelection(enc)
        self.choice_dict.SetSelection(0)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(self.list_encodages, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(self.label_dict, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(self.choice_dict, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

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
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Préférences", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.parent = parent
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 4, 3, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Jouer un son à la fin des analyses", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )
        
        m_radioBox1Choices = [ u"oui", u"non" ]
        self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox1.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox1, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        msg = u"""Vérifier au démarrage si une
nouvelle version est disponible"""
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer1.Add( self.m_staticText4, 0, wx.ALL, 5 )
        
        m_radioBox2Choices = [ u"oui", u"non" ]
        self.m_radioBox2 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox2Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox2.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox2, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        msg = u"""Vérifier l'installation des
bibliothèques de R"""
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, msg, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer1.Add( self.m_staticText6, 0, wx.ALL, 5 )
        
        self.m_button1 = wx.Button( self, wx.ID_ANY, u"Vérifier", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.m_button1, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        bSizer1.Add( fgSizer1, 1, wx.EXPAND, 5 )
        if sys.platform == 'win32' :
            bSizer2 = wx.BoxSizer( wx.HORIZONTAL )
            
            msg = u"""Mémoire maximum allouée
    à R (en Mo)"""
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
        self.text8 = wx.StaticText( self, wx.ID_ANY, u"Utiliser svdlibc", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.text8.Wrap( -1 )
        fgSizer1.Add( self.text8, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        self.check_svdc = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer4.Add( self.check_svdc, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        bSizer3.Add( bSizer4, 0, wx.EXPAND, 5 )
        self.fbb = filebrowse.FileBrowseButton(self, -1, size=(250, -1), fileMode = 2, fileMask = '*')
        bSizer3.Add( self.fbb, 0, wx.EXPAND, 5 )
        self.fbb.SetLabel(u"Chemin : ")
        fgSizer1.Add( wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 ),  wx.ID_ANY, wx.ALL, 5)
        fgSizer1.Add( bSizer3, 0,  wx.ALIGN_RIGHT|wx.ALL, 5 )

        Rpath_text =  wx.StaticText( self, wx.ID_ANY, u"Chemin de R", wx.DefaultPosition, wx.DefaultSize, 0 )
        Rpath_text.Wrap( -1 )
        fgSizer1.Add( Rpath_text, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        fgSizer1.Add( wx.StaticText(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 ),  wx.ID_ANY, wx.ALL, 5)
        self.Rpath_value = filebrowse.FileBrowseButton(self, -1, size=(350, -1), fileMode = 2, fileMask = '*')
        self.Rpath_value.SetLabel(u'Chemin : ')
        fgSizer1.Add( self.Rpath_value, 0, wx.ALIGN_RIGHT|wx.ALL, 5 )

        mirror_text =  wx.StaticText( self, wx.ID_ANY, u"Miroir de R par défaut", wx.DefaultPosition, wx.DefaultSize, 0 )
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
        m_sdbSizer1.Realize();
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
        self.SetTitle(u"Préférences")
        if self.parent.pref.getboolean('iramuteq', 'sound'): val1 = 0
        else : val1 = 1
        self.m_radioBox1.SetSelection(val1)
        if self.parent.pref.getboolean('iramuteq', 'checkupdate') : val2 = 0
        else : val2 = 1
        self.m_radioBox2.SetSelection(val2)
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
        self.labeltype = wx.StaticText(self, -1, u'Type de graph')
        if self.paramgraph['clnb'] <= 3 :
            choix = [u'2D']
        else :
            choix=[u'2D' ,u'3D']
        self.choicetype = wx.Choice(self, -1, (100,50), choices=choix)
        self.label_1 = wx.StaticText(self, -1, u'Largeur')
        self.spin1 = wx.SpinCtrl(self, -1, '',size = (100,30), min=100, max=5000)
        self.label_2 = wx.StaticText(self, -1, u'Hauteur')
        self.spin2 = wx.SpinCtrl(self, -1, '', size = (100,30), min=100, max=5000)
        self.label_what = wx.StaticText(self, -1, u'Représentation')
        self.choice1 = wx.Choice(self, -1, (100,50), choices=[u'coordonnées' ,u'corrélation'])
        self.label_qui = wx.StaticText(self, -1, u'Variables')
        self.choice2 = wx.Choice(self, -1, (100,50), choices=[u'actives' ,u'supplémentaires', u'étoilées', 'classes'])
        self.label_3 = wx.StaticText(self, -1, u'Taille du texte')
        self.spin3 = wx.SpinCtrl(self, -1, '', size = (100,30), min=1, max=20)
        txt = u"""Prendre les x premiers points"""
        self.label_4 = wx.StaticText(self, -1, txt)
        self.check1 = wx.CheckBox(self, -1)
        self.spin_nb = wx.SpinCtrl(self, -1, '', size = (100,30), min=2, max=1000)
        txt = u"""Limiter le nombre de points 
par le chi2 de liaison aux classes"""
        self.label_5 = wx.StaticText(self, -1, txt)
        self.check2 = wx.CheckBox(self, -1)
        self.spin_chi = wx.SpinCtrl(self, -1, '',size = (100,30),  min=2, max=1000)
        self.label_6 = wx.StaticText(self, -1, u'Eliminer les recouvrements')
        self.check3 = wx.CheckBox(self, -1)
        txt = u"""Taille du texte proportionnel
à la masse de la forme"""
        self.label_7 = wx.StaticText(self, -1, txt)
        self.check4 = wx.CheckBox(self, -1)
        self.label_min = wx.StaticText(self, -1, 'min')
        self.spin_min = wx.SpinCtrl(self, -1, '',size = (100,30), min = 1, max = 100)
        self.label_max = wx.StaticText(self, -1, 'max')
        self.spin_max = wx.SpinCtrl(self, -1, '',size = (100,30), min = 1, max = 100)
        txt = u"""Taille du texte proportionnel
au chi2 d'association de la forme"""
        self.label_tchi = wx.StaticText(self, -1, txt)
        self.check_tchi = wx.CheckBox(self, -1)
        self.label_min_tchi = wx.StaticText(self, -1, 'min')
        self.spin_min_tchi = wx.SpinCtrl(self, -1, '', size = (100,30), min = 1, max = 100)
        self.label_max_tchi = wx.StaticText(self, -1, 'max')
        self.spin_max_tchi = wx.SpinCtrl(self, -1, '', size = (100,30), min = 1, max = 100)
        self.label_8 = wx.StaticText(self, -1, 'Facteur x :')
        self.spin_f1 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=self.paramgraph['clnb']-1)
        self.label_9 = wx.StaticText(self, -1, 'Facteur y :')
        self.spin_f2 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=self.paramgraph['clnb']-1)
        self.label_f3 = wx.StaticText(self, -1, 'Facteur z :')
        self.spin_f3 = wx.SpinCtrl(self, -1, '',size = (100,30), min=1, max=self.paramgraph['clnb']-1)
        self.label_sphere = wx.StaticText(self, -1, u"Transparence des sphères")
        self.slider_sphere = wx.Slider(self, -1, 10, 1, 100, size = (255,-1), style = wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS)

        self.label_film = wx.StaticText(self, -1, 'Faire un film')
        self.film = wx.CheckBox(self, -1)
               
        self.btnsizer = wx.StdDialogButtonSizer()
        if wx.Platform != "__WXMSW__":
            btn = wx.ContextHelpButton(self)
            self.btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("Ok")
        btn.SetDefault()
        self.btnsizer.AddButton(btn)
        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("Annuler")
        self.btnsizer.AddButton(btn)
        self.btnsizer.Realize()
        
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck1, self.check1)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck2, self.check2)
        self.Bind(wx.EVT_CHECKBOX, self.OnNorm, self.check4)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheckTchi, self.check_tchi)
        self.Bind(wx.EVT_CHOICE, self.On3D, self.choicetype)
        self.Bind(wx.EVT_CHOICE, self.OnPass, self.choice2)
        self.__set_properties()
        self.OnNorm(wx.EVT_CHECKBOX)
        self.OnCheckTchi(wx.EVT_CHECKBOX)
        self.__do_layout()

    def __set_properties(self):
        self.choicetype.SetSelection(self.paramgraph['typegraph'])
        if self.paramgraph['typegraph'] == 0 :
            self.film.Enable(False)
            self.spin_f3.Enable(False)
            self.slider_sphere.Enable(False)
        self.choice1.SetSelection(self.paramgraph['what'])
        self.choice2.SetSelection(self.paramgraph['qui'])
        self.spin_chi.SetValue(self.paramgraph['select_nb'])
        self.spin_nb.SetValue(self.paramgraph['select_chi'])
        self.spin1.SetValue(self.paramgraph['width'])
        self.spin2.SetValue(self.paramgraph['height'])
        self.spin3.SetValue(self.paramgraph['taillecar'])
        self.spin_nb.SetValue(self.paramgraph['select_nb'])
        self.spin_chi.SetValue(self.paramgraph['select_chi'])
        self.check1.SetValue(self.paramgraph['do_select_nb'])
        self.check2.SetValue(self.paramgraph['do_select_chi'])
        self.check3.SetValue(self.paramgraph['over'])
        if self.paramgraph['do_select_nb'] :
            self.spin_nb.Enable(True)
            self.spin_chi.Enable(False)
        else :
            self.spin_nb.Enable(False)
        self.check4.SetValue(self.paramgraph['cex_txt'])
        self.spin_min.SetValue(self.paramgraph['txt_min'])
        self.spin_max.SetValue(self.paramgraph['txt_max'])
        self.check_tchi.SetValue(self.paramgraph['tchi'])
        self.spin_min_tchi.SetValue(self.paramgraph['tchi_min'])
        self.spin_max_tchi.SetValue(self.paramgraph['tchi_max'])

        if self.paramgraph['do_select_chi'] :
            self.spin_nb.Enable(False)
            self.spin_chi.Enable(True)    
        else :
            self.spin_chi.Enable(False)            
        self.spin_f1.SetValue(self.paramgraph['facteur'][0])
        self.spin_f2.SetValue(self.paramgraph['facteur'][1])
        self.spin_f3.SetValue(self.paramgraph['facteur'][2])
        self.slider_sphere.SetValue(self.paramgraph['alpha'])

    def __do_layout(self):
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        fsizer = wx.FlexGridSizer(12,2,0,5)
        grid_min = wx.FlexGridSizer(1, 2, 0, 0)
        grid_max = wx.FlexGridSizer(1, 2, 0, 0)
        grid_minmax = wx.FlexGridSizer(1, 2, 0, 0)
        grid_min_tchi = wx.FlexGridSizer(1, 2, 0, 0)
        grid_max_tchi = wx.FlexGridSizer(1, 2, 0, 0)
        grid_minmax_tchi = wx.FlexGridSizer(1, 2, 0, 0)

        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        
        fsizer.Add(self.labeltype, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
        fsizer.Add(self.choicetype, 0, wx.ALL | wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 5)
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
        
        bsizer_1 = wx.FlexGridSizer(3,3,0,0)
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
        
        fsizer2 = wx.FlexGridSizer(2,2,0,0)
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
        
    def OnCheck1(self,event):
        if self.check1.GetValue() :
            self.check2.SetValue(False)
            self.spin_chi.Enable(False)
            self.spin_nb.Enable(True)
        else : 
            self.spin_nb.Enable(False)
            
    def OnCheck2(self,event):
        if self.check2.GetValue() :
           self.check1.SetValue(False)
           self.spin_nb.Enable(False)
           self.spin_chi.Enable(True)
        else :
           self.spin_chi.Enable(False) 

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
        if evt.GetString() != u'actives' :
            self.check4.SetValue(False)
            self.check4.Enable(False)
            self.OnNorm(wx.EVT_CHECKBOX)
        else :
            self.check4.Enable()
            
class PrefSimi ( wx.Dialog ):
    
    def __init__( self, parent, ID, paramsimi, indices ):
        wx.Dialog.__init__ ( self, None, id = wx.ID_ANY, title = u"Paramètres", pos = wx.DefaultPosition, size = wx.Size( -1,-1 ), style = wx.DEFAULT_DIALOG_STYLE )
        self.parent = parent
        self.paramsimi=paramsimi
        self.indices = indices

        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        fgSizer5 = wx.FlexGridSizer( 0, 3, 0, 0 )
        fgSizer5.SetFlexibleDirection( wx.BOTH )
        fgSizer5.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Sélectionner les colonnes", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer3.Add( self.m_staticText1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.check_colch = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_colch, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticline29 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline29, 0, wx.EXPAND, 5 )
        
        self.m_staticline291 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline291, 0, wx.EXPAND, 5 )
        if not self.paramsimi['first'] :
 
            self.m_staticText271 = wx.StaticText( self, wx.ID_ANY, u"Utiliser les coordonnées\nprécédentes", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText271.Wrap( -1 )
            fgSizer3.Add( self.m_staticText271, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
            self.check_coord = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
            fgSizer3.Add( self.check_coord, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
            self.m_staticline36 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
            fgSizer3.Add( self.m_staticline36, 0, wx.EXPAND, 5 )
        
            self.m_staticline37 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
            fgSizer3.Add( self.m_staticline37, 0, wx.EXPAND, 5 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Indice", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer3.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        choice1Choices = []
        self.choice1 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.indices, 0 )
        self.choice1.SetSelection( 0 )
        fgSizer3.Add( self.choice1, 0, wx.ALL, 5 )
        
        self.m_staticline293 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline293, 0, wx.EXPAND, 5 )
        
        self.m_staticline292 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline292, 0, wx.EXPAND, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Layout", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        choice2Choices = [u"random", u"cercle", u"fruchterman reingold", u"kamada kawai", u"graphopt"]
        self.choice2 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice2Choices, 0 )
        self.choice2.SetSelection( 0 )
        fgSizer3.Add( self.choice2, 0, wx.ALL, 5 )
        
        self.m_staticline294 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline294, 0, wx.EXPAND, 5 )
        
        self.m_staticline295 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline295, 0, wx.EXPAND, 5 )
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Type de graph", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer3.Add( self.m_staticText5, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        choice3Choices = [u"dynamique", u"statique", u"3D"]
        self.choice3 = wx.Choice( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, choice3Choices, 0 )
        self.choice3.SetSelection( 0 )
        fgSizer3.Add( self.choice3, 0, wx.ALL, 5 )
        
        self.m_staticline296 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline296, 0, wx.EXPAND, 5 )
        
        self.m_staticline297 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline297, 0, wx.EXPAND, 5 )
        
        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Arbre maximum", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )
        fgSizer3.Add( self.m_staticText8, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.check1 = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check1, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticline298 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline298, 0, wx.EXPAND, 5 )
        
        self.m_staticline299 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline299, 0, wx.EXPAND, 5 )
        
        self.m_staticText91 = wx.StaticText( self, wx.ID_ANY, u"Graph à seuil", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText91.Wrap( -1 )
        fgSizer3.Add( self.m_staticText91, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        bSizer21 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.check_seuil = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer21.Add( self.check_seuil, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.spin_seuil = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 10000, 1 )
        bSizer21.Add( self.spin_seuil, 0, wx.ALL, 5 )
        
        fgSizer3.Add( bSizer21, 1, wx.EXPAND, 5 )
        
        self.m_staticline2910 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2910, 0, wx.EXPAND, 5 )
        
        self.m_staticline2911 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2911, 0, wx.EXPAND, 5 )
        
        self.m_staticText19 = wx.StaticText( self, wx.ID_ANY, u"Texte sur les sommets", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText19.Wrap( -1 )
        fgSizer3.Add( self.m_staticText19, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.check_vlab = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_vlab, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticline2912 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2912, 0, wx.EXPAND, 5 )
        
        self.m_staticline2913 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2913, 0, wx.EXPAND, 5 )
        
        self.m_staticText20 = wx.StaticText( self, wx.ID_ANY, u"Indices sur les arêtes", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText20.Wrap( -1 )
        fgSizer3.Add( self.m_staticText20, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.check_elab = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_elab, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticline2914 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2914, 0, wx.EXPAND, 5 )
        
        self.m_staticline2915 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2915, 0, wx.EXPAND, 5 )
        
        self.m_staticText27 = wx.StaticText( self, wx.ID_ANY, u"Taille du texte", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText27.Wrap( -1 )
        fgSizer3.Add( self.m_staticText27, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.spin_cex = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 10 )
        fgSizer3.Add( self.spin_cex, 0, wx.ALL, 5 )
        
        self.m_staticline2916 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2916, 0, wx.EXPAND, 5 )
        
        self.m_staticline2917 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer3.Add( self.m_staticline2917, 0, wx.EXPAND, 5 )
        
        if 'bystar' in self.paramsimi :
            self.m_staticText40 = wx.StaticText( self, wx.ID_ANY, u"Sélectionner une variable", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.m_staticText40.Wrap( -1 )
            fgSizer3.Add( self.m_staticText40, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
            
            self.check_bystar = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
            fgSizer3.Add( self.check_bystar, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
            
            self.m_staticline3200 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
            fgSizer3.Add( self.m_staticline3200, 0, wx.EXPAND, 5 )
            self.m_staticline3201 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
            fgSizer3.Add( self.m_staticline3201, 0, wx.EXPAND, 5 )

        fgSizer5.Add( fgSizer3, 1, wx.EXPAND, 5 )
        
        self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_VERTICAL )
        self.m_staticline5.SetForegroundColour( wx.Colour( 0, 0, 0 ) )
        
        fgSizer5.Add( self.m_staticline5, 0, wx.EXPAND|wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5 )
        
        fgSizer51 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer51.SetFlexibleDirection( wx.BOTH )
        fgSizer51.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Taille du graphique", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer51.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer31 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer31.SetFlexibleDirection( wx.BOTH )
        fgSizer31.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"hauteur", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        fgSizer31.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_height = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 10, 100000, 800 )
        fgSizer31.Add( self.spin_height, 0, wx.ALL, 5 )
        
        self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"largeur", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        fgSizer31.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_width = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 10, 100000, 800 )
        fgSizer31.Add( self.spin_width, 0, wx.ALL, 5 )
        
        fgSizer51.Add( fgSizer31, 1, wx.EXPAND, 5 )
        
        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline3, 0, wx.EXPAND, 5 )
        
        self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline4, 0, wx.EXPAND, 5 )
        
        self.m_staticText101 = wx.StaticText( self, wx.ID_ANY, u"Taille des sommets \nproportionnelle à l'effectif\n(les scores sont normalisés)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText101.Wrap( -1 )
        fgSizer51.Add( self.m_staticText101, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
        
        bSizer9 = wx.BoxSizer( wx.VERTICAL )
        
        self.check2 = wx.CheckBox( self, wx.ID_ANY, u"eff.", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer9.Add( self.check2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        if 'sfromchi' in self.paramsimi :
            self.checki = wx.CheckBox( self, wx.ID_ANY, u"chi2", wx.DefaultPosition, wx.DefaultSize, 0 )
            bSizer9.Add( self.checki, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer7.Add( bSizer9, 0, wx.ALIGN_CENTER_VERTICAL, 5 )
        
        fgSizer7 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer7.SetFlexibleDirection( wx.BOTH )
        fgSizer7.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText11 = wx.StaticText( self, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText11.Wrap( -1 )
        fgSizer7.Add( self.m_staticText11, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_tvmin = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
        fgSizer7.Add( self.spin_tvmin, 0, wx.ALL, 5 )
        
        self.m_staticText12 = wx.StaticText( self, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )
        fgSizer7.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_tvmax = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
        fgSizer7.Add( self.spin_tvmax, 0, wx.ALL, 5 )
        
        bSizer7.Add( fgSizer7, 1, wx.EXPAND, 5 )
        
        fgSizer51.Add( bSizer7, 1, wx.EXPAND, 5 )
        
        self.m_staticline31 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline31, 0, wx.EXPAND, 5 )
        
        self.m_staticline32 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline32, 0, wx.EXPAND, 5 )
        
        self.m_staticText1011 = wx.StaticText( self, wx.ID_ANY, u"Taille du texte des sommets \nproportionnelle à l'effectif\n(les scores sont normalisés)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1011.Wrap( -1 )
        fgSizer51.Add( self.m_staticText1011, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        bSizer71 = wx.BoxSizer( wx.HORIZONTAL )
        
        bSizer8 = wx.BoxSizer( wx.VERTICAL )
        
        self.check_vcex = wx.CheckBox( self, wx.ID_ANY, u"eff.", wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer8.Add( self.check_vcex, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        if 'cexfromchi' in self.paramsimi :
        
            self.checkit = wx.CheckBox( self, wx.ID_ANY, u"chi2", wx.DefaultPosition, wx.DefaultSize, 0 )
            bSizer8.Add( self.checkit, 0, wx.ALL, 5 )
        
        bSizer71.Add( bSizer8, 0, wx.ALIGN_CENTER_VERTICAL, 5 )
        
        fgSizer71 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer71.SetFlexibleDirection( wx.BOTH )
        fgSizer71.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText111 = wx.StaticText( self, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText111.Wrap( -1 )
        fgSizer71.Add( self.m_staticText111, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_vcexmin = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
        fgSizer71.Add( self.spin_vcexmin, 0, wx.ALL, 5 )
        
        self.m_staticText121 = wx.StaticText( self, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText121.Wrap( -1 )
        fgSizer71.Add( self.m_staticText121, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_vcexmax = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
        fgSizer71.Add( self.spin_vcexmax, 0, wx.ALL, 5 )
        
        bSizer71.Add( fgSizer71, 1, wx.EXPAND, 5 )
        
        fgSizer51.Add( bSizer71, 1, wx.EXPAND, 5 )
        
        self.m_staticline321 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline321, 0, wx.EXPAND, 5 )
        
        self.m_staticline322 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline322, 0, wx.EXPAND, 5 )
        
        self.m_staticText10111 = wx.StaticText( self, wx.ID_ANY, u"Largeur des arêtes\nproportionnelle à l'indice", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10111.Wrap( -1 )
        fgSizer51.Add( self.m_staticText10111, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        bSizer711 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.check3 = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer711.Add( self.check3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer711 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer711.SetFlexibleDirection( wx.BOTH )
        fgSizer711.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1111 = wx.StaticText( self, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1111.Wrap( -1 )
        fgSizer711.Add( self.m_staticText1111, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_temin = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
        fgSizer711.Add( self.spin_temin, 0, wx.ALL, 5 )
        
        self.m_staticText1211 = wx.StaticText( self, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1211.Wrap( -1 )
        fgSizer711.Add( self.m_staticText1211, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_temax = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 0 )
        fgSizer711.Add( self.spin_temax, 0, wx.ALL, 5 )
        
        bSizer711.Add( fgSizer711, 1, wx.EXPAND, 5 )
        
        fgSizer51.Add( bSizer711, 1, wx.EXPAND, 5 )
        
        self.m_staticline33 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline33, 0, wx.EXPAND, 5 )
        
        self.m_staticline34 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline34, 0, wx.EXPAND, 5 )
        
        self.m_staticText28 = wx.StaticText( self, wx.ID_ANY, u"Gradiant de gris sur les textes en fonction \nde l'effectif (du chi2) (0=noir; 1=blanc)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText28.Wrap( -1 )
        fgSizer51.Add( self.m_staticText28, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer10 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_checkBox14 = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer10.Add( self.m_checkBox14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer11 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer12 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText31 = wx.StaticText( self, wx.ID_ANY, u"min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText31.Wrap( -1 )
        bSizer12.Add( self.m_staticText31, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_spinCtrl14 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10, 0 )
        bSizer12.Add( self.m_spinCtrl14, 0, wx.ALL, 5 )
        
        bSizer11.Add( bSizer12, 1, wx.EXPAND, 5 )
        
        bSizer13 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText32 = wx.StaticText( self, wx.ID_ANY, u"max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText32.Wrap( -1 )
        bSizer13.Add( self.m_staticText32, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_spinCtrl15 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10, 10 )
        bSizer13.Add( self.m_spinCtrl15, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer11.Add( bSizer13, 1, wx.EXPAND, 5 )
        
        bSizer10.Add( bSizer11, 1, wx.EXPAND, 5 )
        
        fgSizer51.Add( bSizer10, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        self.m_staticline3311 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline3311, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline33111 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline33111, 0, wx.EXPAND |wx.ALL, 5 )
        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText21 = wx.StaticText( self, wx.ID_ANY, u"Couleur des sommets", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText21.Wrap( -1 )
        bSizer5.Add( self.m_staticText21, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.cols = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.Colour( 255, 0, 0 ), wx.DefaultPosition, wx.Size( 10,10 ), wx.CLRP_DEFAULT_STYLE )
        bSizer5.Add( self.cols, 0, wx.ALL, 5 )
        
        fgSizer51.Add( bSizer5, 1, wx.EXPAND, 5 )
        
        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText22 = wx.StaticText( self, wx.ID_ANY, u"Couleur des arêtes", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText22.Wrap( -1 )
        bSizer6.Add( self.m_staticText22, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.cola = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.Colour( 208, 208, 208 ), wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer6.Add( self.cola, 0, wx.ALL, 5 )
        
        fgSizer51.Add( bSizer6, 1, wx.EXPAND, 5 )
        
        self.m_staticline331 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline331, 0, wx.EXPAND, 5 )
        
        self.m_staticline332 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline332, 0, wx.EXPAND, 5 )
        
        self.m_staticText23 = wx.StaticText( self, wx.ID_ANY, u"Taille des sommets unique", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText23.Wrap( -1 )
        fgSizer51.Add( self.m_staticText23, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        bSizer72 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.check_s_size = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        bSizer72.Add( self.check_s_size, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.spin_tv = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 100, 10 )
        bSizer72.Add( self.spin_tv, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        fgSizer51.Add( bSizer72, 1, wx.EXPAND, 5 )
        
        self.m_staticline333 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline333, 0, wx.EXPAND, 5 )
        
        self.m_staticline334 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline334, 0, wx.EXPAND, 5 )
        
        self.m_staticText24 = wx.StaticText( self, wx.ID_ANY, u"Transparence des sphères", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText24.Wrap( -1 )
        fgSizer51.Add( self.m_staticText24, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.slider_sphere = wx.Slider( self, wx.ID_ANY, 10, 0, 100, wx.DefaultPosition, wx.DefaultSize, wx.SL_HORIZONTAL|wx.SL_LABELS )
        fgSizer51.Add( self.slider_sphere, 0, wx.ALL|wx.EXPAND|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticline335 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline335, 0, wx.EXPAND, 5 )
        
        self.m_staticline336 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline336, 0, wx.EXPAND, 5 )
        
        self.m_staticText25 = wx.StaticText( self, wx.ID_ANY, u"Faire un film", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText25.Wrap( -1 )
        fgSizer51.Add( self.m_staticText25, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.film = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer51.Add( self.film, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL, 5 )
        
        self.m_staticline2918 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline2918, 0, wx.EXPAND, 5 )
        
        self.m_staticline2919 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer51.Add( self.m_staticline2919, 0, wx.EXPAND, 5 )
        
        
        fgSizer51.AddSpacer( ( 0, 0), 1, wx.EXPAND, 5 )
        
        m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer2.AddButton( self.m_sdbSizer2OK )
        self.m_sdbSizer2Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer2.AddButton( self.m_sdbSizer2Cancel )
        m_sdbSizer2.Realize();
        fgSizer51.Add( m_sdbSizer2, 1, wx.EXPAND, 5 )
        
        fgSizer5.Add( fgSizer51, 1, wx.EXPAND, 5 )
        
        self.SetSizer( fgSizer5 )
        self.__set_properties()

        self.Layout()
        fgSizer5.Fit( self )
        
        self.Centre( wx.BOTH )
        
        # Connect Events
        if not self.paramsimi['first'] :
            self.check_coord.Bind( wx.EVT_CHECKBOX, self.OnKeepCoords )
        self.choice3.Bind( wx.EVT_CHOICE, self.OnChangeType )
        self.check2.Bind( wx.EVT_CHECKBOX, self.OnCheck2 )
        if 'cexfromchi' in self.paramsimi :
            self.checkit.Bind( wx.EVT_CHECKBOX, self.OnCheckit )
        if 'sfromchi' in self.paramsimi :
            self.checki.Bind( wx.EVT_CHECKBOX, self.OnChecki )
        self.check_vcex.Bind( wx.EVT_CHECKBOX, self.OnCheck_vcex )
        self.check_s_size.Bind( wx.EVT_CHECKBOX, self.OnCheck_s_size )

    def __set_properties(self):
        self.choice1.SetSelection(self.paramsimi['coeff'])
        self.choice2.SetSelection(self.paramsimi['layout'])
        self.choice3.SetSelection(self.paramsimi['type_graph'])
        if self.paramsimi['type'] != 2 :
            self.film.Enable(False)
            self.slider_sphere.Enable(False)
        else :
            self.film.Enable(True)
            self.slider_sphere.Enable(True)
        self.check1.SetValue(self.paramsimi['arbremax'])
        self.check_vlab.SetValue(self.paramsimi['label_v'])
        self.check_elab.SetValue(self.paramsimi['label_e'])
        self.check2.SetValue(self.paramsimi['tvprop'])
        self.spin_tv.SetValue(self.paramsimi['coeff_tv_nb'])
        self.check_s_size.SetValue(self.paramsimi['coeff_tv'])
        self.spin_tvmin.SetValue(self.paramsimi['tvmin'])
        self.spin_tvmax.SetValue(self.paramsimi['tvmax'])
        self.check3.SetValue(self.paramsimi['coeff_te'])
        self.spin_temin.SetValue(self.paramsimi['coeff_temin'])
        self.spin_temax.SetValue(self.paramsimi['coeff_temax'])
        self.check_vcex.SetValue(self.paramsimi['vcex'])
        self.spin_vcexmin.SetValue(self.paramsimi['vcexmin'])
        self.spin_vcexmax.SetValue(self.paramsimi['vcexmax'])
        self.spin_cex.SetValue(self.paramsimi['cex'])
        self.check_seuil.SetValue(self.paramsimi['seuil_ok'])
        self.spin_seuil.SetValue(self.paramsimi['seuil'])
        self.cols.SetColour(self.paramsimi['cols'])
        self.cola.SetColour(self.paramsimi['cola'])
        self.spin_width.SetValue(self.paramsimi['width'])
        self.spin_height.SetValue(self.paramsimi['height'])
        if 'cexfromchi' in self.paramsimi :
            self.checkit.SetValue(self.paramsimi['cexfromchi'])
        if 'sfromchi' in self.paramsimi :
            self.checki.SetValue(self.paramsimi['sfromchi'])
        if not self.paramsimi['first'] :
            self.check_coord.SetValue(self.paramsimi['keep_coord'])
            self.OnKeepCoords(wx.EVT_CHECKBOX)
        if self.paramsimi.get('bystar', False) :
            self.check_bystar.SetValue(True)
            self.stars = self.paramsimi['stars']
        self.slider_sphere.SetValue(self.paramsimi['alpha'])
        self.film.SetValue(self.paramsimi['film'])

    def OnCheck_s_size(self, evt):
        if self.check_s_size.GetValue() :
            if 'cexfromchi' in self.paramsimi :
                self.checki.SetValue(False)
            self.check2.SetValue(False)
            self.spin_tvmin.Enable(False)
            self.spin_tvmax.Enable(False)
            self.spin_tv.Enable(True)
        else :
            self.check2.SetValue(True)
            self.spin_tvmin.Enable(True)
            self.spin_tvmax.Enable(True)
            self.spin_tv.Enable(False)

    def OnCheck2(self, evt):
        if self.check2.GetValue():
            self.check_s_size.SetValue(False)
            if 'cexfromchi' in self.paramsimi :
                self.checki.SetValue(False)
            self.spin_tvmin.Enable(True)
            self.spin_tvmax.Enable(True)
            self.spin_tv.Enable(False)
        else :
            self.check_s_size.SetValue(True)
            self.spin_tvmin.Enable(False)
            self.spin_tvmax.Enable(False)
            self.spin_tv.Enable(True)

    def OnChecki(self, evt):
        if 'sfromchi' in self.paramsimi :
            if self.checki.GetValue() :
                self.check_s_size.SetValue(False)
                self.check2.SetValue(False)
                self.spin_tvmin.Enable(True)
                self.spin_tvmax.Enable(True)
                self.spin_tv.Enable(False)
            else :
                self.check_s_size.SetValue(True)
                #self.check2.SetValue(True)
                self.spin_tvmin.Enable(False)
                self.spin_tvmax.Enable(False)
                self.spin_tv.Enable(True)

    def OnCheckit(self,evt) :
        if 'cexfromchi' in self.paramsimi :
            if self.checkit.GetValue() :
                if self.check_vcex.GetValue() :
                    self.check_vcex.SetValue(False)

    def OnCheck_vcex(self, evt):
        if self.check_vcex.GetValue() :
            if 'checkit' in dir(self) :
                if self.checkit.GetValue() :
                    self.checkit.SetValue(False)
    
    def OnChangeType(self, event) :
        if event.GetInt() != 1 :
            self.spin_width.Enable(False)
            self.spin_height.Enable(False)
        else :
            self.spin_width.Enable(True)
            self.spin_height.Enable(True)
        if event.GetInt() != 2 :
            self.film.Enable(False)
            self.slider_sphere.Enable(False)
        else :
            self.film.Enable(True)
            self.slider_sphere.Enable(True)

    def OnKeepCoords(self, event):
        if self.check_coord.GetValue() :
            self.choice1.SetSelection(self.paramsimi['coeff'])
            self.choice2.SetSelection(self.paramsimi['layout'])
            self.check_seuil.SetValue(self.paramsimi['seuil_ok'])
            self.spin_seuil.SetValue(self.paramsimi['seuil'])
            self.choice1.Disable()
            self.choice2.Disable()
            self.check_seuil.Disable()
            self.spin_seuil.Disable()
            self.check_colch.SetValue(False)
            self.check_colch.Disable()
        else :
            self.choice1.Enable(True)
            self.choice2.Enable(True)
            self.check_seuil.Enable(True)
            self.spin_seuil.Enable(True)
            self.check_colch.Enable(True)

class SelectColDial ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 200,300 ), style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        self.bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        #self.m_checkList2 = wx.CheckListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ['r','t','y'], 0 ) 
        #bSizer2.Add( self.m_checkList2, 2, wx.ALL|wx.EXPAND, 5 )
        
        self.m_sdbSizer2 = wx.StdDialogButtonSizer()
        self.m_sdbSizer2OK = wx.Button( self, wx.ID_OK )
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
        self.label_lem = wx.StaticText(self, -1, u"Corpus Lemmatisé")
        box3.Add(self.label_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.radio_lem = wx.RadioBox(self, -1, u"", choices=['oui', 'non'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        box3.Add(self.radio_lem, 0, wx.ALIGN_RIGHT, 5)
        sizer.Add(box3, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        self.label_txt = wx.StaticText(self, -1, u"Exporter pour...")
        box.Add(self.label_txt, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.radio_type = wx.RadioBox(self, -1, u"", choices=['IRaMuTeQ/ALCESTE', 'Lexico'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        box.Add(self.radio_type, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.txt2 = wx.StaticText(self, -1, u"Fichier en sortie")
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
                dlg = wx.MessageDialog(self, u"%s\nCe fichier existe, continuer quand même ?" % self.fbb.GetValue(), 'ATTENTION', wx.NO | wx.YES | wx.ICON_WARNING)
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
        self.label_txt = wx.StaticText(self, -1, u"Préférences")
        box.Add(self.label_txt, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.radio_type = wx.RadioBox(self, -1, u"", choices=['comme ALCESTE', 'comme Lexico'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        box.Add(self.radio_type, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)
        box2 = wx.BoxSizer(wx.HORIZONTAL)
        self.txt2 = wx.StaticText(self, -1, u"Fichier en sortie")
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
        self.txt2 = wx.StaticText(self, -1, u"Fichier en sortie")
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
                dlg = wx.MessageDialog(self, u"%s\nCe fichier existe, continuer quand même ?" % self.fbb.GetValue(), 'ATTENTION', wx.NO | wx.YES | wx.ICON_WARNING)
                dlg.CenterOnParent()
                if dlg.ShowModal() not in [wx.ID_NO, wx.ID_CANCEL]:
                    self.EndModal(wx.ID_OK)
            else :
                 self.EndModal(wx.ID_OK)
        else :
            self.EndModal(wx.ID_CANCEL)


class StatDialog(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE 
        wx.Dialog.__init__(self, *args, **kwds)
        self.fileout = ""
        self.parent = parent
        #box = wx.BoxSizer(wx.HORIZONTAL)
        self.label_lem = wx.StaticText(self, -1, u"Lemmatisation")
        self.radio_lem = wx.RadioBox(self, -1, u"", choices=['oui', 'non'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        #sizer.Add(box, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        #box2 = wx.BoxSizer(wx.HORIZONTAL)
        #self.txt_exp = wx.StaticText(self, -1, u"Utiliser le Dict. des expressions")
        #self.exp = wx.RadioBox(self, -1, u"", choices=['oui', 'non'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        #self.label_uce =  wx.StaticText(self, -1, u"Construire des UCE")
        #self.check_uce = wx.CheckBox(self, -1)
        #txt = """Nombre d'occurrences par uce"""
        #self.label_occuce = wx.StaticText(self, -1, txt)
        #self.spin_ctrl_4 = wx.SpinCtrl(self, -1, "",size = (100,30), min=10, max=1000, initial = 35)
        #txt = u"""Fréquence minimum d'une forme
#analysée (0 = non utilisé)"""
        #self.label_8 = wx.StaticText(self, -1, txt)
        #self.spin_ctrl_5 = wx.SpinCtrl(self, -1, "",size = (100,30), min=0, max=1000, initial=0)
        #self.label_max_actives =  wx.StaticText(self, -1, u"Nombre maximum de formes analysées")
        #self.spin_max_actives = wx.SpinCtrl(self, -1, "",size = (100,30), min=20, max=10000, initial=1500)
        self.label_4 = wx.StaticText(self, -1, u"Configuration des clés d'analyse")
        self.button_5 = wx.Button(self, wx.ID_PREFERENCES, "")

        #self.Bind(wx.EVT_CHECKBOX, self.OnCheckUce, self.check_uce)
        #self.Bind(wx.EVT_SPINCTRL, self.OnSpin, self.spin_ctrl_5)
        self.Bind(wx.EVT_BUTTON, self.OnKeys, self.button_5)
        self.__do_layout()
        self.__set_properties()

    def __do_layout(self) :
        first = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.FlexGridSizer(4,2,0,0)
        sizer.Add(self.label_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        sizer.Add(self.radio_lem, 0, wx.ALIGN_LEFT, 5)
        sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
        sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
        #sizer.Add(self.txt_exp, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.exp, 0, wx.ALIGN_RIGHT, 5)
        #sizer.Add(self.label_uce, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.check_uce, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.label_occuce, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.spin_ctrl_4, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.label_8, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.spin_ctrl_5, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.label_max_actives, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        #sizer.Add(self.spin_max_actives, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        sizer.Add(self.label_4, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        sizer.Add(self.button_5, 0,  wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
        sizer.Add(wx.StaticLine(self),0, wx.ALIGN_LEFT, 5)
        #sizer.Add(box2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
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

    def __set_properties(self) :
        self.SetTitle(u'Préférences')
        #self.spin_ctrl_4.Enable(False)
        #self.spin_ctrl_5.Enable(False)
        #self.spin_max_actives.Enable(False)

#    def OnCheckUce(self, evt) :
#        if self.check_uce.GetValue() :
#            self.spin_ctrl_4.Enable(True)
#            self.spin_ctrl_5.Enable(True)
#            if self.spin_ctrl_5.GetValue() > 0 :
#                self.spin_max_actives.Enable(False)
#            else :
#                self.spin_max_actives.Enable(True)
#        else :
#            self.spin_ctrl_4.Enable(False)
#            self.spin_ctrl_5.Enable(False)
#            self.spin_max_actives.Enable(False)

#    def OnSpin(self, evt) :
#        if self.spin_ctrl_5.GetValue() > 0 :
#            self.spin_max_actives.Enable(False)
#        else :
#            self.spin_max_actives.Enable(True)

    def OnKeys(self, evt):
        dial = AlcOptFrame(self.parent, self)
        dial.CenterOnParent()
        val = dial.ShowModal()

class LexDialog( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer2 = wx.FlexGridSizer( 2, 2, 0, 0 )
        fgSizer2.SetFlexibleDirection( wx.BOTH )
        fgSizer2.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Lemmatisation", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        fgSizer2.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3 )
        
        m_radioBox2Choices = [ u"oui", u"non" ]
        self.m_radioBox2 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox2Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox2.SetSelection( 0 )
        fgSizer2.Add( self.m_radioBox2, 0, wx.ALIGN_RIGHT|wx.ALL, 3 )
        
#        self.m_staticText10 = wx.StaticText( self, wx.ID_ANY, u"Utiliser le Dict. des expressions", wx.DefaultPosition, wx.DefaultSize, 0 )
#        self.m_staticText10.Wrap( -1 )
#        fgSizer2.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 3 )
#        
#        m_radioBox21Choices = [ u"oui", u"non" ]
#        self.m_radioBox21 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox21Choices, 1, wx.RA_SPECIFY_COLS )
#        self.m_radioBox21.SetSelection( 0 )
#        fgSizer2.Add( self.m_radioBox21, 0, wx.ALIGN_RIGHT|wx.ALL, 3 )
#        bSizer2.Add( fgSizer2, 1, wx.EXPAND, 5 )
        
        btnsizer = wx.StdDialogButtonSizer()
        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btn_ok = wx.Button( self, wx.ID_OK)
        btn_ok.SetDefault()
        btnsizer.AddButton(btn_ok)
        btnsizer.Realize()

        bSizer2.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, 5)
        self.SetSizer( bSizer2 )
        self.Layout()
        bSizer2.Fit( self )
        self.Centre( wx.BOTH )

class PrefUCECarac(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE 
        kwds['title'] = u"UCE caractéristiques"
        wx.Dialog.__init__(self, *args, **kwds)
        self.parent = parent
        first = wx.BoxSizer(wx.VERTICAL)
        sizer = wx.FlexGridSizer(2,2,0,0)
        self.label_type = wx.StaticText(self, -1, u"Score de classement")
        sizer.Add(self.label_type, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, 5)
        self.radio_type = wx.RadioBox(self, -1, u"", choices=[u'absolu (somme des chi2 des formes marquées de l\'UCE)', u'relatif (moyenne des chi2 des formes marquées de l\'UCE)'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        sizer.Add(self.radio_type, 0, wx.ALIGN_RIGHT, 5)
        self.txt_eff = wx.StaticText(self, -1, u"Nombre d\'UCE maximum")
        sizer.Add(self.txt_eff, 0, wx.ALIGN_CENTRE, 5)
        self.spin_eff = wx.SpinCtrl(self, -1, '', size = (100, 30), min = 1, max = 100000, initial = 50)
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
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Profils des segments répétés", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        txt = u"ATTENTION : le calcul des profils des segments répétés\npeut être très long sur les corpus importants"
        self.label = wx.StaticText( self, wx.ID_ANY, txt, wx.DefaultPosition, wx.DefaultSize, 0 ) 
        bSizer1.Add( self.label, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5 )

        fgSizer1 = wx.FlexGridSizer( 2, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Corpus lemmatisé", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        box_lemChoices = [ u"oui", u"non" ]
        self.box_lem = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, box_lemChoices, 1, wx.RA_SPECIFY_COLS )
        self.box_lem.SetSelection( 1 )
        fgSizer1.Add( self.box_lem, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        #self.box_lem.Enable(False)
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Taille minimum des segments", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_min = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (100,30), wx.SP_ARROW_KEYS, 2, 30, 2 )
        self.spin_min.SetValue(2)
        fgSizer1.Add( self.spin_min, 0, wx.ALL, 5 )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Taille maximum des segments", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer1.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_max = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, (100,30), wx.SP_ARROW_KEYS, 2, 30, 10 )
        self.spin_max.SetValue(10)
        fgSizer1.Add( self.spin_max, 0, wx.ALL, 5 )
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Effectif minimum d'un segment retenu", wx.DefaultPosition, wx.DefaultSize, 0 )
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
    
    def __init__( self, parent, sim = False):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u'Classification', pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        #---------------------------------------------------------------
        #self.content = parent.content[:]
        self.header = parent.tableau.get_colnames()
        labels = [val for val in self.header]
        self.labels_tot = labels
        self.varsup = []
        self.sim = sim
        #---------------------------------------------------------------
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        fgSizer1 = wx.FlexGridSizer( 2, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        if not self.sim :
            self.lab_format = wx.StaticText( self, wx.ID_ANY, u"Le corpus est formaté", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.lab_format.Wrap( -1 )
            fgSizer1.Add( self.lab_format, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
            m_radioBox1Choices = [ u"oui", u"non" ]
            self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
            self.m_radioBox1.SetSelection( 0 )
            fgSizer1.Add( self.m_radioBox1, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Variables actives (min = 3) :", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Variables illustratives (min = 1):", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALL, 5 )
        
        self.ListActive = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, labels,  wx.LB_EXTENDED )
        self.ListActive.SetMinSize( wx.Size( 300,250 ) )
        
        fgSizer1.Add( self.ListActive, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        self.ListSup = wx.ListBox( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, labels, wx.LB_EXTENDED )
        self.ListSup.SetMinSize( wx.Size( 300,250 ) )
        
        fgSizer1.Add( self.ListSup, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL|wx.EXPAND, 5 )
        
        self.but_suiv = wx.Button( self, wx.ID_ANY, u"Suivant", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.but_suiv, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.but_prec = wx.Button( self, wx.ID_ANY, u"Précédent", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer1.Add( self.but_prec, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        if not sim :
            self.lab_nbcl = wx.StaticText( self, wx.ID_ANY, u"Nombre de classes terminales de la phase 1", wx.DefaultPosition, wx.DefaultSize, 0 )
            self.lab_nbcl.Wrap( -1 )
            fgSizer1.Add( self.lab_nbcl, 0, wx.ALL, 5 )
            
            self.spin_nbcl = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 2, 100, 10 )
            self.spin_nbcl.SetValue(10)
            self.spin_nbcl.SetMinSize( wx.Size( 100,30 ) )
            
            fgSizer1.Add( self.spin_nbcl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
            
            self.lab_mincl = wx.StaticText( self, wx.ID_ANY, u"Effectif minimum d'une classe (2 = automatique)", wx.DefaultPosition, wx.DefaultSize, 0 )
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
        self.sizer1 = wx.FlexGridSizer(len(result)+1,4,0,0)
        self.parent = parent
        self.formes = {}
        txt =  [u'forme',u'classe',u'chi2',u'voir']
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
        self.SetTitle(u'Résultats')
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
        UnSelectList(profile.ProfNB.GetPage(cl).list)
        datas = dict([[profile.ProfNB.GetPage(cl).getColumnText(i,6),i] for i in range(profile.ProfNB.GetPage(cl).list.GetItemCount())])
        profile.ProfNB.GetPage(cl).list.SetItemState(datas[self.formes[idb][0]], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
        profile.ProfNB.GetPage(cl).list.Focus(datas[forme])
        profile.ProfNB.GetPage(cl).list.SetFocus()

    def OnCloseMe(self, evt) :
        self.Close(True)

    def OnCloseWindow(self, evt):
        self.Destroy()

class SearchDial ( wx.Dialog ):
    
    def __init__( self, parent, listctrl, col, shown):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
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
        self.backward = wx.Button(self, wx.ID_BACKWARD, u"Précédent")
        self.forward = wx.Button(self, wx.ID_FORWARD, u"Suivant")
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
        UnSelectList(self.listctrl.list)
        search_word = self.search.GetValue()
        if search_word.strip() != '' :
            formes = [self.listctrl.getColumnText(i, self.col) for i in range(self.listctrl.list.GetItemCount())]
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
            self.listctrl.list.SetItemState(items[0], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            self.listctrl.list.Focus(items[0])
            self.listctrl.list.SetFocus()
            self.Destroy()
        else :
            for i in items :
                self.listctrl.list.SetItemState(i, wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            self.listctrl.list.Focus(items[0])
            self.listctrl.list.SetFocus()
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
            profile.ProfNB.GetPage(cl).list.SetFocus()
            UnSelectList(profile.ProfNB.GetPage(cl).list)
            datas = dict([[profile.ProfNB.GetPage(cl).getColumnText(i,6),i] for i in range(profile.ProfNB.GetPage(cl).list.GetItemCount())])
            profile.ProfNB.GetPage(cl).list.SetItemState(datas[first_forme[0]], wx.LIST_STATE_SELECTED, wx.LIST_STATE_SELECTED)
            profile.ProfNB.GetPage(cl).list.Focus(datas[first_forme[0]])
            profile.ProfNB.GetPage(cl).list.SetFocus()
            if len(proflist) == 1 :
                self.Destroy()
            else :
                SearchResult = FindInCluster(self.parent.parent, -1, proflist)
                SearchResult.Show()
                self.Destroy()
        else :
            self.noresult()

    def onforward(self, evt) :
        self.listctrl.list.Focus(self.items[self.forwitem])
        self.listctrl.list.SetFocus()
        self.forwitem += 1
        if self.forwitem == len(self.items) :
            self.forward.Enable(False)
            self.backward.Enable(True)
            self.backitem += 1
        else :
            self.backitem += 1
            self.backward.Enable(True)

    def onbackward(self, evt) :
        self.listctrl.list.Focus(self.items[self.backitem])
        self.listctrl.list.SetFocus()
        self.backitem -= 1
        if self.backitem == -1 :
            self.forwitem -= 1
            self.forward.Enable(True)
            self.backward.Enable(False)
        else :
            self.forwitem -= 1
            self.forward.Enable(True)

    def noresult(self) :
        msg = u"Forme absente"
        dial = wx.MessageDialog(self, 'Forme absente','Forme absente', wx.OK | wx.ICON_INFORMATION)
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
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.listet = None
        self.variables = None
        self.labellem =  wx.StaticText(self, -1, u"Lemmatisation : ")
        self.checklem = wx.CheckBox(self, -1)
        self.label_var =  wx.StaticText(self, -1, u"Sélection par :")
        self.choice = wx.Choice(self, -1, (100,50), choices = [u'variables', u'modalités'])
        self.label1 =  wx.StaticText(self, -1, u"Choix")
        self.list_box_1 = wx.ListBox(self, -1, choices=[],  size = wx.Size( 150,200 ), style=wx.LB_EXTENDED | wx.LB_HSCROLL)
        self.button_2 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_1 = wx.Button(self, wx.ID_OK, "")
        self.label_indice =  wx.StaticText(self, -1, u"indice")
        self.choice_indice =  wx.Choice(self, -1, (100,50), choices = [u'loi hypergéométique', u'chi2'])
        self.label = wx.StaticText(self, -1, u"effectif minimum")
        self.spin = wx.SpinCtrl(self, -1, min = 1, max = 10000)
        self.Bind(wx.EVT_CHOICE, self.onselect, self.choice)
        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetTitle("Choix des variables")
        self.spin.SetValue(10)
        self.choice.SetSelection(0)
        #self.SetMinSize(wx.Size(300, 400))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.FlexGridSizer(2,2,0,0)
        sizer_3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add(self.labellem, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.checklem, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.label_var, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.choice, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.label1, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.list_box_1, 0, wx.ALIGN_RIGHT, 3)
        sizer_3.Add(self.button_2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_3.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.label_indice, 0, wx.ALIGN_CENTER_VERTICAL, 3)
        sizer_2.Add(self.choice_indice, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 3)
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


class PrefDendro ( wx.Dialog ):
    
    def __init__( self, parent, param ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Dendrogramme", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.param = param
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText1 = wx.StaticText( self, wx.ID_ANY, u"Taille de l'image", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        bSizer2 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText2 = wx.StaticText( self, wx.ID_ANY, u"Hauteur", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        bSizer3.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_spinCtrl1 = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 50, 10000, 600 )
        bSizer3.Add( self.m_spinCtrl1, 0, wx.ALL, 5 )
        
        bSizer2.Add( bSizer3, 1, wx.EXPAND, 5 )
        
        bSizer31 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Largeur", wx.DefaultPosition, wx.DefaultSize, 0 )
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
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Type de dendrogramme", wx.DefaultPosition, wx.DefaultSize, 0 )
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
        
        self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Couleur ou noir et blanc", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        m_radioBox1Choices = [ u"couleur", u"noir et blanc" ]
        self.m_radioBox1 = wx.RadioBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, m_radioBox1Choices, 1, wx.RA_SPECIFY_COLS )
        self.m_radioBox1.SetSelection( 0 )
        fgSizer1.Add( self.m_radioBox1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer4 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Ajouter la taille des classes", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        bSizer4.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_checkBox1 = wx.CheckBox( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_checkBox1.SetValue(True) 
        bSizer4.Add( self.m_checkBox1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )
        
        m_radioBox2Choices = [ u"camemberts", u"barres" ]
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
    
    def __del__( self ):
        pass


class PrefWordCloud ( wx.Dialog ):
    
    def __init__( self, parent ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Préférences wordcloud", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        
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
        
        self.m_staticText3 = wx.StaticText( self, wx.ID_ANY, u"Hauteur", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        bSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.spin_H = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,30 ), wx.SP_ARROW_KEYS, 0, 10000, 600 )
        bSizer1.Add( self.spin_H, 0, wx.ALL, 5 )
        
        fgSizer1.Add( bSizer1, 1, wx.EXPAND, 5 )
        
        bSizer3 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText4 = wx.StaticText( self, wx.ID_ANY, u"Largeur", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        bSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.spin_L = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size( 100,30 ), wx.SP_ARROW_KEYS, 0, 10000, 600 )
        bSizer3.Add( self.spin_L, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( bSizer3, 1, wx.EXPAND, 5 )
        
        self.m_staticline3 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline3, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline4 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline4, 0, wx.EXPAND |wx.ALL, 5 )
        
        #self.m_staticText5 = wx.StaticText( self, wx.ID_ANY, u"Nombre maximum de formes", wx.DefaultPosition, wx.DefaultSize, 0 )
        #self.m_staticText5.Wrap( -1 )
        #fgSizer1.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        #self.spin_maxword = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 10000, 600 )
        #fgSizer1.Add( self.spin_maxword, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        #self.m_staticline5 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        #fgSizer1.Add( self.m_staticline5, 0, wx.EXPAND |wx.ALL, 5 )
        
        #self.m_staticline6 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        #fgSizer1.Add( self.m_staticline6, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticText6 = wx.StaticText( self, wx.ID_ANY, u"Taille du texte", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer1.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        bSizer4 = wx.BoxSizer( wx.VERTICAL )
        
        bSizer5 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText7 = wx.StaticText( self, wx.ID_ANY, u"Min", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        bSizer5.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_mincex = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 5 )
        bSizer5.Add( self.spin_mincex, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT|wx.ALL, 5 )
        
        bSizer4.Add( bSizer5, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        bSizer6 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText8 = wx.StaticText( self, wx.ID_ANY, u"Max", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText8.Wrap( -1 )
        bSizer6.Add( self.m_staticText8, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.spin_maxcex = wx.SpinCtrl( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 0, 1000, 50 )
        bSizer6.Add( self.spin_maxcex, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        bSizer4.Add( bSizer6, 1, wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        fgSizer1.Add( bSizer4, 1, wx.EXPAND, 5 )
        
        self.m_staticline7 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline7, 0, wx.EXPAND |wx.ALL, 5 )
        
        self.m_staticline8 = wx.StaticLine( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL )
        fgSizer1.Add( self.m_staticline8, 0, wx.EXPAND |wx.ALL, 5 )
        
        bSizer61 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText81 = wx.StaticText( self, wx.ID_ANY, u"Couleur du texte", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText81.Wrap( -1 )
        bSizer61.Add( self.m_staticText81, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.color_text = wx.ColourPickerCtrl( self, wx.ID_ANY, wx.BLACK, wx.DefaultPosition, wx.DefaultSize, wx.CLRP_DEFAULT_STYLE )
        bSizer61.Add( self.color_text, 0, wx.ALL, 5 )
        
        fgSizer1.Add( bSizer61, 1, wx.EXPAND, 5 )
        
        bSizer7 = wx.BoxSizer( wx.HORIZONTAL )
        
        self.m_staticText9 = wx.StaticText( self, wx.ID_ANY, u"Couleur du fond", wx.DefaultPosition, wx.DefaultSize, 0 )
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

        sc.SizedDialog.__init__(self, None, -1, u"Paramètres", 
                        style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        pane = self.GetContentsPane()
        pane.SetSizerType("form")
        pane.SetSizerProps(border=("all",5))
        self.parent = parent
        self.optionchi = optionchi
        

        self.label_obs = wx.StaticText(pane, -1, u'valeurs observée')
        self.check1 = wx.CheckBox(pane, -1)
 
        self.label_theo = wx.StaticText(pane, -1, u'valeurs théoriques')
        self.check2 = wx.CheckBox(pane, -1)

        self.label_resi = wx.StaticText(pane, -1, u'residuals')
        self.check3 = wx.CheckBox(pane, -1)

        self.label_contrib = wx.StaticText(pane, -1, u'contributions a posteriori')
        self.check4 = wx.CheckBox(pane, -1)
#        self.label_graph = wx.StaticText(pane, -1, u'graphique')
#        self.check8 = wx.CheckBox(pane, -1)
        self.label_pourcent = wx.StaticText(pane, -1, u'pourcentage total')
        self.check5 = wx.CheckBox(pane, -1)

        self.label_prl = wx.StaticText(pane, -1, u'pourcentages en ligne')
        self.check6 = wx.CheckBox(pane, -1)

        self.label_prc = wx.StaticText(pane, -1, u'pourcentages en colonne')
        self.check7 = wx.CheckBox(pane, -1)

        self.label_graph = wx.StaticText(pane, -1, u'graphique')
        self.check8 = wx.CheckBox(pane, -1)
        
        self.label_graphbw = wx.StaticText(pane, -1, u'graphique en noir et blanc')
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
            self, parent, ID, title, optionchi, size=wx.DefaultSize, pos=wx.DefaultPosition, 
            style=wx.DEFAULT_DIALOG_STYLE
            ):

        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)

        self.PostCreate(pre)
        self.parent = parent 
        self.optionchi = optionchi
        self.chiopt = False
        #self.Filename=parent.filename
        #self.content=parent.content[:]
        self.headers=parent.tableau.get_colnames()
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

        self.Bind(wx.EVT_LISTBOX, self.Select1, self.list_box_1)
        self.Bind(wx.EVT_BUTTON, self.onparam, self.button_pref)
        # end wxGlade
#-------------------------------
    def __set_properties(self):
        # begin wxGlade: ConfChi2.__set_properties
        self.SetTitle(u"Sélection des variables")

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

    def Select1(self, event): # wxGlade: ConfChi2.<event_handler>
        event.Skip()
    
    
    def onparam(self,event):
        self.dial = PrefChi(self.parent, -1, self.optionchi, '')
        self.dial.CenterOnParent()
        self.chiopt = self.dial.ShowModal()

class CorpusPref ( wx.Dialog ):
    
    def __init__( self, parent, parametres ):
        wx.Dialog.__init__ ( self, parent, id = wx.ID_ANY, title = u"Préférences", pos = wx.DefaultPosition, size = wx.DefaultSize, style = wx.DEFAULT_DIALOG_STYLE )
        self.parent = parent 
        langues_n = [u'français', u'english', u'german (expérimentale)', u'italian (expérimentale)', u'swedish (exp.)', u'portuguese (exp.)']
        self.langues = [u'french', u'english', u'german', 'italian', 'swedish', u'portuguese']
        self.encodages = encodages
        ucimark = [u'****', u'0000']
        ucemethod = [u'charactères', u'occurrences', u'paragraphe']

        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        
        bSizer1 = wx.BoxSizer( wx.VERTICAL )
        
        self.m_notebook1 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_panel1 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer1 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer1.SetFlexibleDirection( wx.BOTH )
        fgSizer1.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText7 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Corpus", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText7.Wrap( -1 )
        fgSizer1.Add( self.m_staticText7, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.txtpath = wx.StaticText( self.m_panel1, wx.ID_ANY, u"path", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txtpath.Wrap( -1 )
        fgSizer1.Add( self.txtpath, 0, wx.ALL, 5 )
        
        self.m_staticText1 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Encodage", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText1.Wrap( -1 )
        fgSizer1.Add( self.m_staticText1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        encodage_choicesChoices = [' - '.join(encodage) for encodage in self.encodages]
        self.encodage_choices = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, encodage_choicesChoices, 0 )
        self.encodage_choices.SetSelection( 0 )
        fgSizer1.Add( self.encodage_choices, 0, wx.ALL, 5 )
        
        self.m_staticText2 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Langue", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText2.Wrap( -1 )
        fgSizer1.Add( self.m_staticText2, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        lang_choicesChoices = langues_n
        self.lang_choices = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, lang_choicesChoices, 0 )
        self.lang_choices.SetSelection( 0 )
        fgSizer1.Add( self.lang_choices, 0, wx.ALL, 5 )

        self.m_staticText3 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Répertoire en sortie", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText3.Wrap( -1 )
        fgSizer1.Add( self.m_staticText3, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        
        fgSizer41 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer41.SetFlexibleDirection( wx.BOTH )
        fgSizer41.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.repout_choices = wx.TextCtrl( self.m_panel1, wx.ID_ANY, u"MyLabel", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.repout_choices.SetMinSize( wx.Size( 400,-1 ) )
        fgSizer41.Add( self.repout_choices, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        self.m_button1 = wx.Button( self.m_panel1, wx.ID_ANY, u"Modifier...", wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer41.Add( self.m_button1, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5 )
        
        fgSizer1.Add( fgSizer41, 1, wx.EXPAND, 5 )        

        self.m_staticText12 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Marqueur d'UCI", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText12.Wrap( -1 )
        fgSizer1.Add( self.m_staticText12, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        ucimark_choicesChoices = ucimark
        self.ucimark_choices = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, ucimark_choicesChoices, 0 )
        self.ucimark_choices.SetSelection( 0 )
        fgSizer1.Add( self.ucimark_choices, 0, wx.ALL, 5 )
        
        self.m_staticText6 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Utiliser le dictionnaire des expressions", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText6.Wrap( -1 )
        fgSizer1.Add( self.m_staticText6, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_expressions = wx.CheckBox( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_expressions.SetValue(True) 
        fgSizer1.Add( self.check_expressions, 0, wx.ALL, 5 )
        
        self.m_staticText9 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Construire des UCE", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText9.Wrap( -1 )
        fgSizer1.Add( self.m_staticText9, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_makeuce = wx.CheckBox( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_makeuce.SetValue(True) 
        fgSizer1.Add( self.check_makeuce, 0, wx.ALL, 5 )
        
        self.m_staticText10 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Mode de construction des UCE", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText10.Wrap( -1 )
        fgSizer1.Add( self.m_staticText10, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        uce_modeChoices = ucemethod
        self.uce_mode = wx.Choice( self.m_panel1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, uce_modeChoices, 0 )
        self.uce_mode.SetSelection( 0 )
        fgSizer1.Add( self.uce_mode, 0, wx.ALL, 5 )
        
        self.m_staticText13 = wx.StaticText( self.m_panel1, wx.ID_ANY, u"Taille des UCE", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText13.Wrap( -1 )
        fgSizer1.Add( self.m_staticText13, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.uce_size = wx.SpinCtrl( self.m_panel1, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, wx.SP_ARROW_KEYS, 1, 1000000, 40 )
        fgSizer1.Add( self.uce_size, 0, wx.ALL, 5 )
        
        
        self.m_panel1.SetSizer( fgSizer1 )
        self.m_panel1.Layout()
        fgSizer1.Fit( self.m_panel1 )
        self.m_notebook1.AddPage( self.m_panel1, u"Générale", True )
        self.m_panel2 = wx.Panel( self.m_notebook1, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
        fgSizer3 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer3.SetFlexibleDirection( wx.BOTH )
        fgSizer3.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.m_staticText4 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Passer le corpus en minuscule", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText4.Wrap( -1 )
        fgSizer3.Add( self.m_staticText4, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_lower = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_lower.SetValue(True) 
        fgSizer3.Add( self.check_lower, 0, wx.ALL, 5 )
        
        self.m_staticText5 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Retirez les caractères en dehors cette liste", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText5.Wrap( -1 )
        fgSizer3.Add( self.m_staticText5, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        fgSizer4 = wx.FlexGridSizer( 0, 2, 0, 0 )
        fgSizer4.SetFlexibleDirection( wx.BOTH )
        fgSizer4.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )
        
        self.check_charact = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_charact.SetValue(True) 
        fgSizer4.Add( self.check_charact, 0, wx.ALL, 5 )
        
        self.txt_charact = wx.TextCtrl( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.txt_charact.SetMinSize( wx.Size( 200,-1 ) )
        
        fgSizer4.Add( self.txt_charact, 0, wx.ALL|wx.EXPAND, 5 )
        
        
        fgSizer3.Add( fgSizer4, 1, wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, 5 )
        
        self.m_staticText14 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Remplacer les apostrophes par des espaces", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText14.Wrap( -1 )
        fgSizer3.Add( self.m_staticText14, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_apos = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_apos.SetValue(True) 
        fgSizer3.Add( self.check_apos, 0, wx.ALL, 5 )
        
        self.m_staticText15 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Remplacer les tirets par des espaces", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText15.Wrap( -1 )
        fgSizer3.Add( self.m_staticText15, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_tirets = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.check_tirets.SetValue(True) 
        fgSizer3.Add( self.check_tirets, 0, wx.ALL, 5 )
        
        self.m_staticText17 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Conserver la ponctuation", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText17.Wrap( -1 )
        fgSizer3.Add( self.m_staticText17, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_ponct = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_ponct, 0, wx.ALL, 5 )

        self.m_staticText16 = wx.StaticText( self.m_panel2, wx.ID_ANY, u"Pas d'espace entre deux formes (pour le chinois par exemple)", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.m_staticText16.Wrap( -1 )
        fgSizer3.Add( self.m_staticText16, 0, wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT|wx.ALL, 5 )
        
        self.check_tolist = wx.CheckBox( self.m_panel2, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        fgSizer3.Add( self.check_tolist, 0, wx.ALL, 5 )
        
        
        self.m_panel2.SetSizer( fgSizer3 )
        self.m_panel2.Layout()
        fgSizer3.Fit( self.m_panel2 )
        self.m_notebook1.AddPage( self.m_panel2, u"Nettoyage", False )
        
        bSizer1.Add( self.m_notebook1, 1, wx.EXPAND |wx.ALL, 5 )
        
        m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1OK = wx.Button( self, wx.ID_OK )
        m_sdbSizer1.AddButton( self.m_sdbSizer1OK )
        self.m_sdbSizer1Cancel = wx.Button( self, wx.ID_CANCEL )
        m_sdbSizer1.AddButton( self.m_sdbSizer1Cancel )
        m_sdbSizer1.Realize();
        
        bSizer1.Add( m_sdbSizer1, 0, wx.EXPAND, 5 )
       

        self.Bind(wx.EVT_BUTTON, self.OnChangeDir, self.m_button1)
        self.setparametres(parametres) 
        self.SetSizer( bSizer1 )
        self.Layout()
        bSizer1.Fit( self )
        
        self.Centre( wx.BOTH )

    def OnChangeDir(self, evt) :
        dlg = wx.DirDialog(self.parent, u"Choisissez un répertoire", style = wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK :
            self.repout_choices.SetValue(dlg.GetPath())
    
    def __del__( self ):
        pass

    def setparametres(self, parametres) :
        self.encodage_choices.SetSelection(0)
        self.lang_choices.SetSelection(0)
        self.repout_choices.SetValue(parametres['pathout'])
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

    def doparametres(self) :
        parametres = {}
        parametres['encoding'] = self.encodages[self.encodage_choices.GetSelection()][0]
        parametres['lang'] = self.langues[self.lang_choices.GetSelection()]
        parametres['pathout'] = self.repout_choices.GetValue()
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
        for val in parametres :
            if isinstance(parametres[val], bool) :
                if parametres[val] :
                    parametres[val] = 1
                else :
                    parametres[val] = 0
        return parametres
