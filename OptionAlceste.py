# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL

import wx
import shutil
from KeyFrame import AlcOptFrame
from chemins import ConstructConfigPath
from functions import DoConf



class OptionAlc(wx.Dialog):
    def __init__(self, parent, parametres, *args, **kwds):
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, parent, *args, **kwds)
        self.parent = parent
        self.parametres = parametres
        self.DictPath = parametres['pathout']
        self.AlcesteConf = parametres
        self.choose = False
        
        self.label_1 = wx.StaticText(self, -1, u"Lemmatisation")
        self.radio_1 = wx.RadioBox(self, -1, u"", choices=['oui', 'non'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)

        self.label_12 = wx.StaticText(self, -1, u"Classification")
        self.radio_box_2 = wx.RadioBox(self, -1, u"", choices=[u"double sur UC", u"simple sur UCE", u"simple sur UCI"], majorDimension=0, style=wx.RA_SPECIFY_ROWS) #, u"simple sur UCE (non implemente)"
        self.label_2 = wx.StaticText(self, -1, u"taille uc 1")
        self.spin_ctrl_1 = wx.SpinCtrl(self, -1, "formes actives",size = (100,30), min=0, max=100)
        self.label_3 = wx.StaticText(self, -1, u"taille uc 2")
        self.spin_ctrl_2 = wx.SpinCtrl(self, -1, "",size = (100,30), min=0, max=100)
        self.lab_nbcl = wx.StaticText(self, -1, u"nombre de classes terminales de la phase 1")
        self.spin_nbcl = wx.SpinCtrl(self, -1, "",size = (100,30), min=2, max=100)
        txt = """Nombre minimum d'uce par classe
(0 = automatique)"""
        self.label_7 = wx.StaticText(self, -1, txt)
        self.spin_ctrl_4 = wx.SpinCtrl(self, -1, "",size = (100,30), min=0, max=1000)       
        txt = u"""Fréquence minimum d'une forme
analysée (2 = automatique)"""
        self.label_8 = wx.StaticText(self, -1, txt)
        self.spin_ctrl_5 = wx.SpinCtrl(self, -1, "",size = (100,30), min=2, max=1000)
        self.label_max_actives =  wx.StaticText(self, -1, u"Nombre maximum de formes analysées")
        self.spin_max_actives = wx.SpinCtrl(self, -1, "",size = (100,30), min=20, max=10000)
        self.label_4 = wx.StaticText(self, -1, u"Configuration \ndes clés d'analyse")
        self.button_5 = wx.Button(self, wx.ID_PREFERENCES, "")
        self.button_1 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_2 = wx.Button(self, wx.ID_DEFAULT, u"Valeurs par défaut")
        self.button_4 = wx.Button(self, wx.ID_OK, "")
        self.static_line_1 = wx.StaticLine(self, -1)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnKeyPref, self.button_5)
        self.Bind(wx.EVT_BUTTON, self.OnDef, self.button_2)
        
    def __set_properties(self):
        self.SetTitle("Options")
        #lang = self.AlcesteConf.get('ALCESTE', 'lang')
        #self.choice_dict.SetSelection(self.langues.index(lang))
        DefaultLem = self.parametres['lem']
        if DefaultLem :
            self.radio_1.SetSelection(0)
        else:
            self.radio_1.SetSelection(1)
        self.radio_box_2.SetSelection(int(self.parametres['classif_mode']))
        self.spin_ctrl_1.SetValue(int(self.parametres['tailleuc1']))
        self.spin_ctrl_2.SetValue(int(self.parametres['tailleuc2']))
        self.spin_ctrl_4.SetValue(int(self.parametres['mincl']))
        self.spin_ctrl_5.SetValue(int(self.parametres['minforme']))
        self.spin_ctrl_5.Disable()
        self.spin_max_actives.SetValue(int(self.parametres['max_actives']))
        self.spin_nbcl.SetValue(int(self.parametres['nbcl_p1']))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer2 = wx.FlexGridSizer(0, 2, 0, 0)
        grid_button = wx.FlexGridSizer(1, 3, 0, 0)
        
        #grid_sizer2.Add(self.label_dict, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer2.Add(self.choice_dict, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)

        grid_sizer2.Add(self.label_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.radio_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_12, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.radio_box_2, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_ctrl_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_3, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_ctrl_2, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.lab_nbcl, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_nbcl, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_7, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_ctrl_4, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_8, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_ctrl_5, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_max_actives, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_max_actives, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
       
        grid_sizer2.Add(self.label_4, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.button_5, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
        
        grid_button.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_button.Add(self.button_2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_button.Add(self.button_4, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(grid_sizer2, 3, wx.EXPAND, 0)
        sizer_2.Add(grid_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def OnKeyPref(self, event): 
        self.choose = True
        dial = AlcOptFrame(self.parent, self)
        dial.CenterOnParent()
        val = dial.ShowModal()
    
    def OnDef(self, event):
        ConfOri = ConstructConfigPath(self.parent.AppliPath, user=False)
        ConfUser = ConstructConfigPath(self.parent.UserConfigPath)
        shutil.copyfile(ConfOri['alceste'], ConfUser['alceste'])
        corpus = self.parametres['corpus']
        pathout = self.parametres['pathout']
        self.parametres = DoConf(self.parent.ConfigPath['alceste']).getoptions('ALCESTE')
        self.parametres['corpus'] = corpus
        self.parametres['pathout'] = pathout
        self.__set_properties()
        
###################################################################################@

class OptionPam(wx.Dialog):
    def __init__(self, parent, *args, **kwds):
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.parent = parent
        self.DictPath = parent.DictPath
        self.pamconf = parent.pamconf
        self.type = parent.type
        self.choose = False
        
        self.label_1 = wx.StaticText(self, -1, u"Lemmatisation")
        self.radio_1 = wx.RadioBox(self, -1, u"", choices=['oui', 'non'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.label_exp = wx.StaticText(self, -1, u"Utiliser le dict. des expressions")
        self.radio_exp =  wx.RadioBox(self, -1, u"", choices=['oui', 'non'], majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        txt = u"""Methode de construction
de la matrice des distances"""
        self.label_12 = wx.StaticText(self, -1, txt)
        self.distance = [u"binary", u"euclidean", u"maximum", u'manhattan', u'canberra', u'minkowski']
        self.choice_1 =  wx.Choice(self, -1, (100,50), choices=self.distance)
        self.label_13 = wx.StaticText(self, -1, u'Analyse')
        self.cltype = [u'k-means (pam)', u'fuzzy (fanny)']
        self.radio_box_3 = wx.RadioBox(self, -1, u"", choices=self.cltype, majorDimension=0, style=wx.RA_SPECIFY_ROWS)
        self.label_classif = wx.StaticText(self, -1, u"Classification")
        self.radio_box_classif = wx.RadioBox(self, -1, u"", choices=[u"sur UCE", u"sur UCI"], majorDimension=0, style=wx.RA_SPECIFY_ROWS) 
        #self.label_2 = wx.StaticText(self, -1, "taille uc")
        #self.spin_ctrl_1 = wx.SpinCtrl(self, -1, "formes actives", min=0, max=100)
        self.label_max_actives =  wx.StaticText(self, -1, u"Nombre maximum de formes analysées")
        self.spin_max_actives = wx.SpinCtrl(self, -1, "",size = (100,30), min=20, max=10000)
        txt = """Nombre de formes par uce
(0 = automatique)"""
        self.label_6 = wx.StaticText(self, -1, txt)
        self.spin_ctrl_3 = wx.SpinCtrl(self, -1, "", size = (100,30), min=0, max=100000)
        txt = "Nombre de classes"
        self.label_7 = wx.StaticText(self, -1, txt)
        self.spin_ctrl_4 = wx.SpinCtrl(self, -1, "", size = (100,30), min=0, max=1000)        
        self.label_4 = wx.StaticText(self, -1, u"Configuration \ndes clés d'analyse")
        self.button_5 = wx.Button(self, wx.ID_PREFERENCES, "")
        self.button_1 = wx.Button(self, wx.ID_CANCEL, "")
        self.button_2 = wx.Button(self, wx.ID_DEFAULT, u"Valeurs par défaut")
        self.button_4 = wx.Button(self, wx.ID_OK, "")
        self.static_line_1 = wx.StaticLine(self, -1)

        self.__set_properties()
        self.__do_layout()

        self.Bind(wx.EVT_BUTTON, self.OnKeyPref, self.button_5)
        self.Bind(wx.EVT_BUTTON, self.OnDef, self.button_2)

    def __set_properties(self):
        self.SetTitle("Options")
        DefaultLem = self.pamconf.getboolean('pam', 'lem')
        if DefaultLem :
            self.radio_1.SetSelection(0)
        else:
            self.radio_1.SetSelection(1)
        expressions = self.pamconf.getboolean('pam', 'expressions')
        if expressions :
            self.radio_exp.SetSelection(0)
        else :
            self.radio_exp.SetSelection(1)
        self.choice_1.SetSelection(self.distance.index(self.pamconf.get('pam', 'method')))
        if self.pamconf.get('pam', 'cluster_type') == u'pam' :
            self.radio_box_3.SetSelection(0)
        else :
            self.radio_box_3.SetSelection(1)
        self.radio_box_classif.SetSelection(int(self.pamconf.get('pam','type')))
        self.spin_max_actives.SetValue(int(self.pamconf.get('pam','max_actives')))
        self.spin_ctrl_3.SetValue(int(self.pamconf.get('pam', 'nbforme_uce')))
        cle = 'nbcl'
        self.spin_ctrl_4.SetValue(int(self.pamconf.get('pam', cle)))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_2 = wx.BoxSizer(wx.VERTICAL)
        grid_sizer2 = wx.FlexGridSizer(11, 2, 2, 2)
        grid_button = wx.FlexGridSizer(1, 3, 1, 1)
        grid_sizer2.Add(self.label_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.radio_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
       
        grid_sizer2.Add(self.label_exp, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.radio_exp, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_12, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.choice_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_13, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.radio_box_3, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_classif, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.radio_box_classif, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
        
        #grid_sizer2.Add(self.label_2, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer2.Add(self.spin_ctrl_1, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        #grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        #grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
        
        grid_sizer2.Add(self.label_max_actives, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_max_actives, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)

        grid_sizer2.Add(self.label_6, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_ctrl_3, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0) 
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
        
        grid_sizer2.Add(self.label_7, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.spin_ctrl_4, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
        
        grid_sizer2.Add(self.label_4, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(self.button_5, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL, 0)
        grid_sizer2.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 1)
        grid_sizer2.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 1)
        
        grid_button.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_button.Add(self.button_2, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_button.Add(self.button_4, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer_2.Add(grid_sizer2, 3, wx.EXPAND, 0)
        sizer_2.Add(grid_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
        sizer_1.Add(sizer_2, 0, wx.EXPAND, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()

    def OnKeyPref(self, event):
        self.choose = True
        dial = AlcOptFrame(self.parent, self)
        dial.CenterOnParent()
        val = dial.ShowModal()
    
    def OnDef(self, event):
        ConfOri = ConstructConfigPath(self.parent.parent.AppliPath, user=False)
        ConfUser = ConstructConfigPath(self.parent.parent.UserConfigPath)
        shutil.copyfile(ConfOri['pam'], ConfUser['pam'])
        self.parent.pamconf.read(self.parent.ConfigPath['pam'])
        self.__set_properties()
