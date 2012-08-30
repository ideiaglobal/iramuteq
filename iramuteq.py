#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012, Pierre Ratinaud
#Lisense: GNU GPL

from optparse import OptionParser

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="open FILE", metavar="FILE", default=False)
(options, args) = parser.parse_args()

#print args
#print options

import sys
reload(sys)
import locale
import tempfile
import codecs
import os
import shutil
from random import randint
from ConfigParser import *
import webbrowser
import gettext
import logging
#------------------------------------
import wx
#import wx.aui
#import wx.lib.agw.aui as aui
import agw.aui as aui
import wx.html
import wx.grid
import wx.lib.hyperlink as hl
#from wx.lib.wordwrap import wordwrap
#------------------------------------
from functions import BugReport, PlaySound, ReadLexique, History, DoConf, ReadDicoAsDico, progressbar
from checkversion import NewVersion
from guifunct import *
from tableau import Tableau
from dialog import PrefDialog, EncodeDialog, CorpusPref
from tabfrequence import Frequences
from tabchi2 import ChiSquare
#from tabstudent import MakeStudent
from tabchddist import ChdCluster
from tabafcm import DoAFCM
from tabchdalc import AnalyseQuest
from tabsimi import DoSimi
from tabrsimple import InputText
from tabverges import Verges
#from textafcuci import AfcUci
#from textchdalc import AnalyseAlceste
from analysetxt import Alceste
from textdist import PamTxt
from textstat import Stat
from textaslexico import Lexico
from textsimi import SimiTxt
from textwordcloud import WordCloud
from profile_segment import ProfileSegment
from textcheckcorpus import checkcorpus
from openanalyse import OpenAnalyse
from corpusNG import BuildFromAlceste, Builder
from sheet import MySheet
from checkinstall import CreateIraDirectory, CheckRPath, FindRPAthWin32, FindRPathNix, CheckRapp, CheckRPackages, IsNew, UpgradeConf, CopyConf, RLibsAreInstalled
from chemins import ConstructRscriptsPath, ConstructConfigPath, ConstructDicoPath, ConstructGlobalPath, PathOut
from parse_factiva_xml import ImportFactiva
from tree import LeftTree
##########################################################
ID_OpenData = wx.NewId()
ID_Import = wx.NewId()
ID_OpenText = wx.NewId()
ID_OnOpenAnalyse = wx.NewId()
ID_Freq = wx.NewId()
ID_Chi2 = wx.NewId()
ID_Student = wx.NewId()
ID_CHDSIM = wx.NewId()
ID_CHDAlceste = wx.NewId()
ID_TEXTAFCM = wx.NewId()
ID_TEXTSTAT = wx.NewId()
ID_ASLEX = wx.NewId()
ID_TEXTALCESTE = wx.NewId()
ID_TEXTPAM = wx.NewId()
ID_CHECKCORPUS = wx.NewId()
ID_Tabcontent = wx.NewId()
ID_AFCM = wx.NewId()
ID_SIMI = wx.NewId()
ID_CloseTab = wx.NewId()
ID_SaveTab = wx.NewId()
ID_CreateText = wx.NewId()
ID_ACCEUIL = wx.NewId()
ID_RESULT = wx.NewId()
ID_VIEWDATA = wx.NewId()
ID_HTMLcontent = wx.NewId()
ID_SimiTxt = wx.NewId()
##########################################################
#elements de configuration
##########################################################
#encodage
if sys.platform == 'darwin' :
    sys.setdefaultencoding('utf-8')
    wx.SetDefaultPyEncoding('utf-8')
else :
    sys.setdefaultencoding(locale.getpreferredencoding())
#chemin de l'application

AppliPath = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])))
#chemin des images
ImagePath = os.path.join(AppliPath, 'images')
#configuration generale
DictConfigPath = ConstructGlobalPath(AppliPath)
ConfigGlob = ConfigParser()
ConfigGlob.read(DictConfigPath['global'])
#repertoire de l'utilisateur
if os.getenv('HOME') != None:
    user_home = os.getenv('HOME')
else:
    user_home = os.getenv('HOMEPATH')
UserConfigPath = os.path.abspath(os.path.join(user_home, '.iramuteq'))
#Si pas de fichiers de config utilisateur, on crée le repertoire
CreateIraDirectory(UserConfigPath, AppliPath)
#fichiers log pour windows (py2exe)
print 'PLUS DE LOG !!!!!!!!!!'
print 'LOGGING TEST'
log = logging.getLogger('iramuteq')
fh = logging.FileHandler(os.path.join(UserConfigPath,'stdout.log'))
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
log.addHandler(ch)
log.addHandler(fh)
log.setLevel(logging.INFO)
#debug = False
#if not debug :
#    if sys.platform == 'win32' or sys.platform == 'darwin':
#        sys.stdout = open(os.path.join(UserConfigPath,'stdout.log'), 'w')
#        sys.stderr = open(os.path.join(UserConfigPath,'stderr.log'), 'w')
#chemin des fichiers de configuration utilisateur
#print sys.argv[0]
ConfigPath = ConstructConfigPath(UserConfigPath)
#####################################################################

class IraFrame(wx.Frame):
    def __init__(self, parent, id= -1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE | 
                                            wx.SUNKEN_BORDER | 
                                            wx.CLIP_CHILDREN):
        log.info('Starting...')
        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        #configuration
        self.AppliPath = AppliPath
        self.images_path = os.path.join(AppliPath,'images')
        self.UserConfigPath = UserConfigPath
        self.RscriptsPath = ConstructRscriptsPath(AppliPath)
        self.DictPath = ConstructDicoPath(AppliPath)
        self.ConfigGlob = ConfigGlob
        self.ConfigPath = ConstructConfigPath(UserConfigPath)
        self.pref = RawConfigParser()
        #langues
        mylocale = wx.Locale(wx.LANGUAGE_FRENCH)
        mylocale.AddCatalogLookupPathPrefix(os.path.join(AppliPath,'locale'))
        mylocale.AddCatalog('iramuteq')
        presLan_en = gettext.translation("iramuteq", os.path.join(AppliPath,'locale'), languages=['en'])
        presLan_fr = gettext.translation("iramuteq", os.path.join(AppliPath,'locale'), languages=['fr_FR'])
        presLan_fr.install()


        # tell FrameManager to manage this frame        
        #self._mgr = wx.aui.AuiManager()
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.x = 0
        # create menu
#--------------------------------------------------------------------------------
        self.mb = wx.MenuBar()

        file_menu = wx.Menu()
        item = wx.MenuItem(file_menu, ID_OpenData, _(u"Open a questionnaire"), _(u"Open a questionnaire"))
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)
        
        item = wx.MenuItem(file_menu, ID_OpenText, u"Ouvrir texte", u"Ouvrir un corpus texte")
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)
        
        item = wx.MenuItem(file_menu, ID_OnOpenAnalyse, u"Ouvrir une Analyse", "Ouvrir une Analyse")
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)

        item1 = wx.MenuItem(file_menu, ID_Import, u"Importer un corpus factiva...", "Importer un corpus factiva...")
        item1.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_TIP))
        file_menu.AppendItem(item1)
        #item1.Enable(True)
       
        item = wx.MenuItem(file_menu, ID_SaveTab, u"Enregistrer l\'onglet sous...", u"Enregistrer l\'onglet sous ...")
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE_AS))
        #item.Enable(False)
        file_menu.AppendItem(item)
        
        file_menu.Append(wx.ID_EXIT, u"Exit")
        
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_PREFERENCES, '', u'Préférences')
        
        view_menu = wx.Menu()
        view_menu.Append(ID_ACCEUIL, u"Page d'accueil")
        view_menu.Append(ID_VIEWDATA, u"Afficher les données")
        view_menu.Append(ID_RESULT, u'Afficher les résultats')
        #view_menu.AppendSeparator()

        analyse_menu = wx.Menu()
        analyse_menu.Append(ID_Freq, u"Fréquences")
        analyse_menu.Append(ID_Chi2, u"Chi2")
        #analyse_menu.Append(ID_Student, u"t de Student")
        menu_classif = wx.Menu()
        menu_classif.Append(ID_CHDAlceste, u"Méthode Alceste")
        menu_classif.Append(ID_CHDSIM, u"Par matrice des distances")
        analyse_menu.AppendMenu(-1, u"Classification", menu_classif)
        analyse_menu.Append(ID_AFCM, u"AFCM")
        analyse_menu.Append(ID_SIMI, u"Analyse de similitudes")
        ID_RCODE = wx.NewId()
        analyse_menu.Append(ID_RCODE, u"Code R...")

        text_menu = wx.Menu()
        text_menu.Append(ID_CHECKCORPUS, u"Vérifier le corpus")
        text_menu.Append(ID_TEXTSTAT, u"Statistiques textuelles")
        text_menu.Append(ID_ASLEX, u"Spécificités et AFC")
        #text_menu.Append(ID_TEXTAFCM, u"AFC sur UCI / Vocabulaire")
        menu_classiftxt = wx.Menu()
        menu_classiftxt.Append(ID_TEXTALCESTE, u"Méthode Alceste")
        menu_classiftxt.Append(ID_TEXTPAM, u"Par matrice des distances")
        text_menu.AppendMenu(-1, u"Classification", menu_classiftxt)
        text_menu.Append(ID_SimiTxt, u'Analyse de similitude') 
        ID_WC = wx.NewId()
        text_menu.Append(ID_WC, u'Nuage de mots')
        
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, u'À propos...')
        help_menu.Append(wx.ID_HELP, u'Aide en ligne')
        
        self.mb.Append(file_menu, _(u"File"))
        self.mb.Append(edit_menu, _(u"Edition"))
        self.mb.Append(view_menu, _(u"View"))
        self.mb.Append(analyse_menu, _("Spreadsheet analysis"))
        self.mb.Append(text_menu, _(u"Text analysis"))
        self.mb.Append(help_menu, _(u"Help"))
        
        self.SetMenuBar(self.mb)
#--------------------------------------------------------------------
        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -3])
        self.statusbar.SetStatusText(u"Prêt", 0)
        self.statusbar.SetStatusText(u"Bienvenue", 1)

        # min size for the frame itself isn't completely done.
        # see the end up FrameManager::Update() for the test
        # code. For now, just hard code a frame minimum size
        self.SetMinSize(wx.Size(400, 400))

        # create some toolbars
        tb1 = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER)
        tb1.SetToolBitmapSize(wx.Size(16, 16))
        tb1.AddLabelTool(ID_OpenData, "OpenData", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, wx.Size(16, 16)), shortHelp="Questionnaire", longHelp="Ouvrir un questionnaire")
        tb1.AddSeparator()
        tb1.AddLabelTool(ID_OpenText, "OpenText", wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, wx.Size(16, 16)), shortHelp="Texte", longHelp="Ouvrir un corpus texte")

        tb1.Realize()
        
#------------------------------------------------------------------------------------------------

        self.text_ctrl_txt = wx.TextCtrl(self, -1, "", wx.Point(0, 0), wx.Size(200, 200), wx.NO_BORDER | wx.TE_MULTILINE | wx.TE_RICH2 | wx.TE_READONLY)
                      
        #self._mgr.AddPane(self.text_ctrl_txt, wx.aui.AuiPaneInfo().
        #                  Name("Text").CenterPane())                      
        self._mgr.AddPane(self.text_ctrl_txt, aui.AuiPaneInfo().
                          Name("Text").CenterPane())
        #self._mgr.AddPane(IntroPanel(self), wx.aui.AuiPaneInfo().Name("Intro_Text").
        #                  CenterPane())
        self._mgr.AddPane(IntroPanel(self), aui.AuiPaneInfo().Name("Intro_Text").
                          CenterPane())
        if not os.path.exists(os.path.join(UserConfigPath, 'history.db')) :
            with open(os.path.join(UserConfigPath, 'history.db'), 'w') as f :
                f.write('')
        self.history = History(os.path.join(UserConfigPath, 'history.db'))
        self.tree = LeftTree(self)
        self._mgr.AddPane(self.tree, aui.AuiPaneInfo().Name("lefttree").Caption("Navigateur").
                          Left().MinSize(wx.Size(200,500)).Layer(1).Position(1).CloseButton(False).MaximizeButton(True).
                          MinimizeButton(True))
        
        #self.nb = wx.aui.AuiNotebook(self, -1, wx.DefaultPosition, wx.DefaultSize, wx.aui.AUI_NB_DEFAULT_STYLE | wx.aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.aui.AUI_NB_TAB_MOVE | wx.aui.AUI_NB_TAB_FLOAT| wx.NO_BORDER)
        self.nb = aui.AuiNotebook(self, -1, wx.DefaultPosition, wx.DefaultSize, aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_TAB_FLOAT| wx.NO_BORDER)
        notebook_flags =  aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_TAB_FLOAT| wx.NO_BORDER
        self.nb.SetAGWWindowStyleFlag(notebook_flags)
        self.nb.SetArtProvider(aui.ChromeTabArt())
        #self.nb.SetArtProvider(aui.VC8TabArt())
        #self.nb.parent = self
        #self._notebook_style = aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | wx.NO_BORDER
        #self._mgr.AddPane(self.nb, wx.aui.AuiPaneInfo().
        #                      Name("Tab_content").
        #                      CenterPane())
        self._mgr.AddPane(self.nb, aui.AuiPaneInfo().
                              Name("Tab_content").
                              CenterPane())        
        self.Sheet = MySheet(self)
        #self._mgr.AddPane(self.Sheet, wx.aui.AuiPaneInfo().Name("Data").CenterPane())
        self._mgr.AddPane(self.Sheet, aui.AuiPaneInfo().Name("Data").CenterPane())
        #self.nb.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
        self.nb.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
        self.nb.Bind(aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        # add the toolbars to the manager
                        
        #self._mgr.AddPane(tb1, wx.aui.AuiPaneInfo().
        #                  Name("tb1").Caption("Fichiers").
        #                  ToolbarPane().Top().
        #                  LeftDockable(False).RightDockable(False))
        self._mgr.AddPane(tb1, aui.AuiPaneInfo().
                          Name("tb1").Caption("Fichiers").
                          ToolbarPane().Top().
                          LeftDockable(True).RightDockable(False))        
        
        self.ShowAPane("Intro_Text")
        self._mgr.GetPane("lefttree").Show()
        self._mgr.GetPane("classif_tb").Hide()
        # "commit" all changes made to FrameManager   
        self._mgr.Update()

        # Show How To Use The Closing Panes Event
##################################################################        
        self.Bind(wx.EVT_MENU, self.OnAcceuil, id=ID_ACCEUIL)
        self.Bind(wx.EVT_MENU, self.OnViewData, id=ID_VIEWDATA)
        self.Bind(wx.EVT_MENU, self.ShowTab, id=ID_RESULT)
        self.Bind(wx.EVT_MENU, self.OnOpenData, id=ID_OpenData)
        self.Bind(wx.EVT_MENU, self.OnOpenText, id=ID_OpenText)
        self.Bind(wx.EVT_MENU, self.OnOpenAnalyse, id=ID_OnOpenAnalyse)
        self.Bind(wx.EVT_MENU, self.import_factiva, id= ID_Import)
        self.Bind(wx.EVT_MENU, self.OnFreq, id=ID_Freq)
        self.Bind(wx.EVT_MENU, self.OnChi2, id=ID_Chi2)
        self.Bind(wx.EVT_MENU, self.OnStudent, id=ID_Student)
        self.Bind(wx.EVT_MENU, self.OnCHDSIM, id=ID_CHDSIM)
        self.Bind(wx.EVT_MENU, self.OnCHDAlceste, id=ID_CHDAlceste)
        self.Bind(wx.EVT_MENU, self.OnAFCM, id=ID_AFCM)
        self.Bind(wx.EVT_MENU, self.OnRCode, id=ID_RCODE)
        self.Bind(wx.EVT_MENU, self.OnCheckcorpus, id = ID_CHECKCORPUS)
        self.Bind(wx.EVT_MENU, self.OnTextStat, id=ID_TEXTSTAT)
        self.Bind(wx.EVT_MENU, self.OnTextSpec, id=ID_ASLEX)
        self.Bind(wx.EVT_MENU, self.OnTextAfcm, id=ID_TEXTAFCM)
        self.Bind(wx.EVT_MENU, self.OnTextAlceste, id=ID_TEXTALCESTE)
        self.Bind(wx.EVT_MENU, self.OnPamSimple, id=ID_TEXTPAM)
        self.Bind(wx.EVT_MENU, self.OnSimiTxt, id=ID_SimiTxt)
        self.Bind(wx.EVT_MENU, self.OnWordCloud, id=ID_WC)
        self.Bind(wx.EVT_MENU, self.OnSimi, id=ID_SIMI)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnSaveTabAs, id=ID_SaveTab)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnPref, id=wx.ID_PREFERENCES)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
##################################################################
        flags = self._mgr.GetAGWFlags()
        #flags &= ~wx.aui.AUI_MGR_TRANSPARENT_HINT
        #flags &= ~wx.aui.AUI_MGR_VENETIAN_BLINDS_HINT
        #flags &= ~wx.aui.AUI_MGR_RECTANGLE_HINT
        flags &= ~(aui.AUI_MGR_RECTANGLE_HINT | aui.AUI_MGR_ALLOW_FLOATING)
        self._mgr.SetAGWFlags(self._mgr.GetAGWFlags() ^ (aui.AUI_MGR_RECTANGLE_HINT | aui.AUI_MGR_ALLOW_FLOATING))
        self._mgr.GetArtProvider().SetMetric(aui.AUI_DOCKART_GRADIENT_TYPE, aui.AUI_GRADIENT_HORIZONTAL)
        self.GetDockArt().SetColor(aui.AUI_DOCKART_ACTIVE_CAPTION_GRADIENT_COLOUR, "#00FFF9")
        self.DoUpdate()

        self._icon = wx.Icon(os.path.join(ImagePath, "iraicone.ico"), wx.BITMAP_TYPE_ICO)
        self.SetIcon(self._icon)
##########################
        self.ctrl = ""
        self.input_path = [False]
        self.TEMPDIR = tempfile.mkdtemp('iramuteq')
        self.FileTabList = []
        self.listbar=[]
        self.DictTab = {}
        self.FreqNum = 0
        self.colsep = ''
        self.txtsep = ''
        self.g_header = False
        self.g_id = False
        self.table = ''
        self.fileforR = ''
        self.filename = ''
        self.nastrings = ''
        self.encode = ''
        self.SysEncoding = sys.getdefaultencoding()
        self.syscoding = sys.getdefaultencoding()
        #print 'SysEncoding',self.SysEncoding
        if self.SysEncoding == 'mac-roman' : self.SysEncoding = 'MacRoman'
        self.type = ''

        try :
            self.pref.read(self.ConfigPath['preferences'])
            if IsNew(self) :
                UpgradeConf(self)
                New = True
            else :
                CopyConf(self)
                New = False
        except :
            UpgradeConf(self)
            self.pref.read(self.ConfigPath['preferences'])
            New = True
        #configuration des chemins de R
        self.PathPath = ConfigParser()
        self.PathPath.read(ConfigPath['path'])
        BestRPath = False
        if not CheckRPath(self.PathPath) :
            if sys.platform == 'win32':
                BestRPath = FindRPAthWin32()
            else:
                BestRPath = FindRPathNix()
            if BestRPath:
                self.PathPath.set('PATHS', 'rpath', BestRPath)
                with open(ConfigPath['path'], 'w') as f :
                    self.PathPath.write(f)
        else:
            BestRPath = True 
        if BestRPath :
            self.RPath = self.PathPath.get('PATHS', 'rpath')
            if New :
                CheckRPackages(self)
            if not RLibsAreInstalled(self) :
                CheckRPackages(self)
        else :
            msg = u"""
Le chemin de l'executable de R n'a pas été trouvé.
Si R n'est pas installé, vous devez l'installer (http://www.r-project.org/).
Si R n'est pas installé dans le répertoire par défaut
(C:\Program Files\R\R-2.x.x\R.exe sous windows ou /usr/bin/R sous linux ou Mac Os X)
vous devez signaler le chemin de l'éxecutable de R dans les préférences.""" 
            dlg = wx.MessageDialog(self, msg, u"Problème de configuration", wx.OK | wx.NO_DEFAULT | wx.ICON_WARNING)
            dlg.CenterOnParent()
            if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                 evt.Veto()
            else :
                print 'ok'
        if sys.platform == 'darwin':
            self.Rapp = self.PathPath.get('PATHS', 'rapp')
            RappOk = CheckRapp(self.Rapp)
        self.DataPop = False
        self.DataTxt = False
        self.Text = ''
        self.sound = self.pref.getboolean('iramuteq', 'sound')
        self.check_update = self.pref.getboolean('iramuteq', 'checkupdate')
        self.version = ConfigGlob.get('DEFAULT', 'version')
        self.lexique = None
        self.corpus = None
##############################################################@
        self.DisEnSaveTabAs(False)
        self.ShowMenu(_("View"), False)
        self.ShowMenu(_("Spreadsheet analysis"), False)
        self.ShowMenu(_("Text analysis"), False)
   
        self._mgr.Update()

    def OnVerif(self, evt) :
        pack = CheckRPackages(self)
        if pack :
            dlg = wx.MessageDialog(self, u"Installation OK", u"Installation", wx.OK | wx.NO_DEFAULT | wx.ICON_INFORMATION)
            dlg.CenterOnParent()
            if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                 evt.Veto()

    #FIXME  marche pas sous mac ?
    def DisEnSaveTabAs(self, DISEN):
    #Disable SaveTabAs
        file_menu = self.mb.GetMenu(0)
        items = file_menu.GetMenuItems()
        items[4].Enable(DISEN)
    
    def ShowMenu(self, menu, Show=True):
        menu_pos = self.mb.FindMenu(menu)
        self.mb.EnableTop(menu_pos, Show)
        self.mb.UpdateMenus()


#--------------------------------------------------------------------
    def OnClose(self, event):
        print 'onclose'
        with open(self.ConfigPath['path'], 'w') as f :
            self.PathPath.write(f)
        if self.DictTab != {} :
            savestates = [self.DictTab[item][0] for item in self.DictTab]
            if False in savestates :
                notsave = [item for item in self.DictTab if self.DictTab[item][0] == False] 
                msg = u"""
 Certains résultats ne sont pas enregistrés.
 Voulez-vous fermer quand même ?"""
                dlg = wx.MessageDialog(self, msg, "Sauvegarde",
                       wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
                dlg.CenterOnParent()
                if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                    event.Veto()
                    dlg.Destroy()
                else:
                    dlg.Destroy()
                    for item in notsave :
                        for tmpfile in self.DictTab[item][1:] :
                            os.remove(tmpfile)
                            print 'remove : ' + tmpfile
                    self._mgr.UnInit()
                    del self._mgr
                    self.Destroy()
            else :
                self._mgr.UnInit()
                del self._mgr
                self.Destroy()
        else :
            self._mgr.UnInit()
            del self._mgr
            self.Destroy()
            ##FIXME
            #if sys.platform == 'win32' :
            #    os.system("taskkill /im iramuteq.exe /f")
            #    print 'meurtre de process'

    def OnOpenData(self, event):
        inputname, self.input_path = OnOpen(self, "Data")
        if inputname:
            self.filename = self.input_path[0]
            self.tableau = Tableau(self,os.path.abspath(self.input_path[0]))
            get_table_param(self, self.input_path[0])
            self.tableau.make_content()
            self.tableau.show_tab()

    def OnOpenAnalyse(self, event):
        self.AnalysePath = OnOpen(self, "Analyse")
        OpenAnalyse(self, self.AnalysePath[1][0], True)
        self.ShowMenu(_("View"))

    def OnOpenText(self, event):
        inputname, self.input_path = OnOpen(self, "Texte")
        self.filename = self.input_path[0]
        if inputname:
             self.OpenText()
   
    def OnViewData(self, event):
        print self.type
        print self.DataTxt
        if self.type == "Data":
            if not self.DataPop :
                self.Sheet.Populate(self.content)
                self.DataPop = True
                self.DataTxt = False
            self.ShowAPane(u"Data")
        elif self.type == "Texte" or self.type == 'Analyse' :
            if not self.DataTxt :
                self.text_ctrl_txt.Clear()
                self.text_ctrl_txt.write(self.content)
                self.text_ctrl_txt.ShowPosition(0)
                self.DataTxt = True
                self.DataPop = False
            self.ShowAPane(u"Text")
        self._mgr.Update()
        
    def OpenText(self):
        #dial = EncodeDialog(self)
        dlg = wx.ProgressDialog("Ouverture...",
                                   "Veuillez patienter...",
                                   maximum=2,
                                   parent=self,
                                   style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT
                                   )
        
        builder =  Builder(self, dlg)
        if builder.res == wx.ID_OK :
            corpus = builder.doanalyse()
            self.history.add(corpus.parametres)
            self.tree.OnItemAppend(corpus.parametres)
            OpenAnalyse(self, corpus.parametres)
        #self.content = DoConf().totext(corpus.parametres)
#        parametres = DoConf(os.path.join(UserConfigPath,'corpus.cfg')).getoptions('corpus')
#        parametres['originalpath'] = self.filename
#        
#        parametres['pathout'] = PathOut(self.filename, 'corpus').dirout
#        dial = CorpusPref(self, parametres)
#        dial.CenterOnParent()
#        dial.txtpath.SetLabel(self.filename)
#        res = dial.ShowModal()
#        parametres = dial.doparametres()
#        print parametres
#        ReadLexique(self, lang = parametres['lang'])
#        self.expressions = ReadDicoAsDico(self.DictPath.get(parametres['lang'], 'french_exp'))
#        corpus = BuildFromAlceste(self.filename, parametres, self.lexique, self.expressions).corpus
        #self.corpus_encodage =  dial.encodages[dial.list_encodages.GetSelection()][0]
        #self.corpus_lang = dial.langues[dial.choice_dict.GetSelection()]
            count = 1
            keepGoing = dlg.Update(count, u"Lecture du fichier")
#        try :
#            with codecs.open(self.filename, 'rU', self.corpus_encodage) as f:
#                self.content = f.read()
#            #self.content = self.content.replace('\r','\n')
#        except UnicodeDecodeError :
#            msg = u"Ce fichier ne semble pas être encodé en %s" % self.corpus_encodage
#            dial = wx.MessageDialog(self, msg, u"Problème d'encodage", wx.OK | wx.NO_DEFAULT | wx.ICON_WARNING)
#            dial.CenterOnParent()
#            res = dial.ShowModal()
#            dial.Destroy()
#            self.OpenText()
            self.ShowMenu(_("View"))
            self.ShowMenu(_("Text analysis"))
            self.ShowMenu(_(u"Spreadsheet analysis"), False)
            self.type = "Texte"
            self.DataTxt = False
            self.Text = ''
            count += 1
            keepGoing = dlg.Update(count, u"Chargement du dictionnaire")
        dlg.Destroy()
        #self.OnViewData(wx.EVT_BUTTON)
        
    def OnExit(self, event):
        self.Close()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = ConfigGlob.get('DEFAULT', 'name')
        info.Version = ConfigGlob.get('DEFAULT', 'version')
        info.Copyright = ConfigGlob.get('DEFAULT', 'copyright')
        info.Description = u"""
Interface de R pour les Analyses Multidimensionnelles 
de Textes et de Questionnaires

Un logiciel libre
construit avec des logiciels libres.

Laboratoire LERASS

REPERE
"""
        info.WebSite = ("http://www.iramuteq.org", u"Site web IRaMuTeQ")
        dev = ConfigGlob.get('DEFAULT', 'dev').split(';')
        info.Developers = dev
        info.License = u"""Iramuteq est un logiciel libre ; vous pouvez le diffuser et/ou le modifier 
suivant les termes de la Licence Publique Générale GNU telle que publiée 
par la Free Software Foundation ; soit la version 2 de cette licence, 
soit (à votre convenance) une version ultérieure.

Iramuteq est diffusé dans l'espoir qu'il sera utile, 
mais SANS AUCUNE GARANTIE ; sans même une garantie implicite 
de COMMERCIALISATION ou d'ADÉQUATION À UN USAGE PARTICULIER. 
Voyez la Licence Publique Générale GNU pour plus de détails.

Vous devriez avoir reçu une copie de la Licence Publique Générale GNU
avec Iramuteq ; sinon, veuillez écrire à la Free Software Foundation,
Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, États-Unis."""
        wx.AboutBox(info)

    def GetDockArt(self):
        return self._mgr.GetArtProvider()

    def DoUpdate(self):
        self._mgr.Update()

    def OnPageChanged(self, event) :
        new = event.GetSelection()
        nobject = event.GetEventObject()
        parent = nobject.GetParent()
        if isinstance(parent, IraFrame) :
            npage = self.nb.GetPage(new)
            self.tree.GiveFocus(uuid=npage.parametres['uuid'])

    def OnCloseTab(self, evt):
        log.info('Closing tab %s' % str(evt.GetEventObject()))
        ctrl = evt.GetEventObject()
        if isinstance(ctrl.GetParent(), aui.AuiNotebook) or isinstance(ctrl.GetParent(), wx.Panel):
            notebook = True
        else :
            notebook = False
        page = self.nb.GetPage(self.nb.GetSelection())
        if 'parametres' in dir(page) :
            self.history.rmtab(page.parametres)
            self.tree.CloseItem(uuid = page.parametres['uuid'])
        TabTitle = self.nb.GetPageText(self.nb.GetSelection())
        if self.DictTab != {} :
            if TabTitle in self.DictTab :
                ListFile=self.DictTab[TabTitle]
                if False in ListFile:
                    msg = u"""
Certains résultats ne sont pas enregistrer.
Voulez-vous fermer quand même ?"""
                    dlg = wx.MessageDialog(self, msg, "Sauvegarde",wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)

                    dlg.CenterOnParent()
                    if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                        remove = False
                        evt.Veto()
                        dlg.Destroy()
                    else :
                        for f in ListFile[1:] :
                            print 'remove', f
                            os.remove(f)
                            remove = True
                        dlg.Destroy()
                elif True in ListFile :
                    remove = True
                if remove:
                   del self.DictTab[TabTitle]
            else : 
                self.LastTabClose()
        else :
            remove = True
        if self.nb.GetPageCount() == 1 and remove and not notebook :
            self.LastTabClose()

    
    def LastTabClose(self) :
        if self.nb.GetPageCount() == 1 :
            self.DisEnSaveTabAs(False)
            if self.DataTxt :
                self.ShowAPane("Text")
            elif self.DataPop :
                self.ShowAPane("Data")
            else :
                self.ShowAPane("Intro_Text")

    def OnSaveTabAs(self, event):
        SelectTab = self.nb.GetSelection()
        TabTitle = self.nb.GetPageText(SelectTab)
        FileToSave = self.DictTab[TabTitle]
        NewListFile = []
        dlg = wx.FileDialog(
            self, message="Enregistrer sous...", defaultDir=os.getcwd(),
            defaultFile="resultat.html", wildcard="Tous les fichiers|*", style=wx.SAVE | wx.OVERWRITE_PROMPT
            )
        dlg.SetFilterIndex(2)
        dlg.CenterOnParent()
        
        if dlg.ShowModal() == wx.ID_OK:
            Path = dlg.GetPath()
            Dirname = os.path.dirname(Path)
            Filename = dlg.GetFilename()
        else :
            Path = False
        dlg.Destroy()
        if Path:
            shutil.copyfile(FileToSave[-1], Path)
            os.remove(FileToSave[len(FileToSave) - 1])
            NewListFile.append(True)
            NewListFile.append(Path)
            for f in FileToSave[1:-1] :
                Fileout = os.path.join(Dirname, os.path.basename(f))
                shutil.copyfile(f, Fileout)
                NewListFile.append(Fileout)
                os.remove(f)
            TabText = Filename
            self.DictTab[TabText] = NewListFile
            del self.DictTab[TabTitle]
            self.nb.SetPageText(SelectTab, TabText)

    def GetStartPosition(self):

        self.x = self.x + 20
        x = self.x
        pt = self.ClientToScreen(wx.Point(0, 0))
        
        return wx.Point(pt.x + x, pt.y + x)
    
    def ShowAPane(self, panel):
        for pane in self._mgr.GetAllPanes() :
            if not pane.IsToolbar() and pane.name != 'lefttree': 
                pane.Hide()
        self._mgr.GetPane(panel).Show()
        self._mgr.Update()
        
    def OnAcceuil(self, event):
        self.ShowAPane(u"Intro_Text")
        event.Skip()
    #???
#    def OnCreateTab(self, event):
#        if not self._mgr.GetPane("Tab_content").name == "Tab_content":
#            self._mgr.AddPane(self.CreateTabCtrl(), aui.AuiPaneInfo().
#                              Name("Tab_content").
#                              CenterPane())
#            self._mgr.GetPane("Intro_Text").Hide()
#            self._mgr.GetPane("Tab_content").Show()
#            self.ctrl.Bind(aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnCloseTab)
#        else :
#            page = wx.TextCtrl(self, -1, str(text), style=wx.TE_MULTILINE)
#            self.ctrl.AddPage(page, "qsdqsd")
#            self.ctrl.SetSelection(self.ctrl.GetPageCount() - 1)
#        self._mgr.Update()
    
    
    def CreateHTMLCtrl(self):
        ctrl = wx.html.HtmlWindow(self, -1, wx.DefaultPosition, wx.Size(400, 300))
        if "gtk2" in wx.PlatformInfo:
            ctrl.SetStandardFonts()
        ctrl.SetPage(u"text")        
        return ctrl

    def ShowTab(self, evt):
        self.ShowAPane("Tab_content")

################################################################
#debut des analyses
################################################################

    def OnFreq(self, event):
        try:
            Frequences(self) 
        except:
            BugReport(self)
            
    def OnChi2(self, event):
        try:
        #    print('PAS DE DEBUG SUR CHI2')
            chi = ChiSquare(self)
        except:
            BugReport(self)
    
    def OnStudent(self, event):
        try:
            MakeStudent(self) 
        except:
            BugReport(self)

    def OnRCode(self, event):
        try:
            InputText(self)
        except:
            BugReport(self)

    def OnCHDSIM(self, event):
        try:
        #    print 'ATTENTION!!!!'
            chdsim = ChdCluster(self)
            if chdsim.val == wx.ID_OK:
                PlaySound(self)
        except:
            BugReport(self)
 
    def OnCHDAlceste(self, event):
        try:
         #   print('PLUS DE BUG SUR ALCESTE QUESTIONNAIRE')
            self.quest = AnalyseQuest(self)
            if self.quest.val == wx.ID_OK:
                PlaySound(self)
        except:
            BugReport(self)

    def OnSimiTxt(self, evt, corpus = None) :
            print 'PLUS DE BUG SUR SIMITXT'
        #try :
            #self.Text = SimiTxt(self)
            self.Text = SimiTxt(self, corpus, parametres = {'type': 'simitxt'}, dlg = progressbar(self, 3))
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        #except :
        #    BugReport(self)
    
    def OnWordCloud(self, evt) :
        #    print 'PLUS DE BUG SUR WORDCLOUD'
        try :
            self.Text = WordCloud(self)
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        except :
            BugReport(self)


    def OnAFCM(self, event):
        try:
            DoAFCM(self)
        except:
            BugReport(self)

    def OnCheckcorpus(self, evt):
        try :
            checkcorpus(self)
        except :
            BugReport(self)

    def OnTextStat(self, event, corpus = None):
            print 'PAS DE BUG SUR TEXT STAT'
        #try:
            self.Text = Stat(self, corpus, parametres = {'type': 'stat'}, dlg = progressbar(self, 7))
            
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        #except:
        #    BugReport(self)
        
    def OnTextSpec(self, event, corpus = None):  
        #try:
            #self.Text = AsLexico(self)
            print('ATTENTION : PLUS DE BUG SUR LEXICO')
            self.Text = Lexico(self, corpus, parametres = {'type' : 'spec'}, dlg = progressbar(self, 3))
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        #except:
        #    BugReport(self)
    
    def OnTextAfcm(self, event):
        try:
            AfcUci(self)
            PlaySound(self)
        except:
            BugReport(self)

    def import_factiva(self,event):
        try :
            ImportFactiva(self)
        except :
            BugReport(self)

    def OnTextAlceste(self, event, corpus = None):
        #try:
            print('ATTENTION : PLUS DE BUG SUR ALCESTE')
            #RunAnalyse(self, corpus, Alceste, OptAlceste)
            self.Text = Alceste(self, corpus, parametres = {'type': 'alceste'}, dlg = progressbar(self,6))
            #self.history.addtab(self.Text.parametres)
            #OpenAnalyse(self, self.Text.parametres['ira'])
            if self.Text.val == wx.ID_OK:
                PlaySound(self)
        #except:
        #    BugReport(self)

    def OnPamSimple(self, event):
        try:
            self.Text = PamTxt(self)
            if self.Text.val == wx.ID_OK:
                PlaySound(self)
        except:
            BugReport(self)
    
    def OnSimi(self,evt):
        try :
            #print 'ATTENTION !!!! VERGES'
            self.res = DoSimi(self, param = None)
            #self.res = Verges(self)
            if self.res.val == wx.ID_OK :
                 PlaySound(self)
        except :
            BugReport(self)
#################################################################

    def OnHelp(self, event):
        webbrowser.open('http://www.iramuteq.org/documentation')
    
    def OnPref(self, event):
        dlg = PrefDialog(self)
        dlg.CenterOnParent()
        self.val = dlg.ShowModal()

    def Upgrade(self) :
        if self.check_update:
            NewVersion(self)
        else:
            print 'pas de verif'    
        #IsNew(self)
        #CheckRPackages(self)

    def OnOpenFromCmdl(self):
        truepath = True
        if options.filename :
            if os.path.exists(options.filename):
                self.filename = os.path.abspath(options.filename)
            else:
                truepath = False
        elif args :
            if os.path.exists(os.path.realpath(args[0])):
                self.filename = os.path.abspath(os.path.realpath(args[0]))
            else:
                truepath = False
        else:
            pass
        if truepath :
            if os.path.splitext(self.filename)[1] in ['.csv', '.xls', '.ods']:
                self.tableau = Tableau(self, self.filename)
                get_table_param(self, self.filename)
                self.tableau.make_content()
                self.tableau.show_tab()
                #open_data(self, self.filename)
            elif os.path.splitext(self.filename)[1] == '.txt':
                self.OpenText()
            elif os.path.splitext(self.filename)[1] == '.ira' :
                #self.corpus = Corpus(self)
                #self.Text = OpenAnalyse(self, self.filename)
                OpenAnalyse(self, self.filename)
        if not truepath:
            print 'ce fichier n\'existe pas'
            
        

class IntroPanel(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        #col = randint(0, 100)
        col = 0
        bckgrdcolor = wx.Colour(col, col, col)
        self.SetBackgroundColour(bckgrdcolor)
        txtcolour = wx.Colour(250, 250, 250)
        linkcolor = wx.Colour(255, 0, 0)
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        sizer3 = wx.BoxSizer(wx.HORIZONTAL)
        sizer4 = wx.BoxSizer(wx.VERTICAL)
        sizer5 = wx.BoxSizer(wx.HORIZONTAL)
        grid_sizer_1 = wx.FlexGridSizer(1, 4, 0, 0)
        grid_sizer_3 = wx.FlexGridSizer(1, 4, 0, 0)
        grid_sizer_2 = wx.FlexGridSizer(1, 3, 0, 0)
        PanelPres = wx.Panel(self)
        PanelPres.SetBackgroundColour(bckgrdcolor)
        label_1 = wx.StaticText(self, -1, u"IRaMuTeQ", size=(-1, -1))
        label_1.SetFont(wx.Font(46, wx.TELETYPE, wx.NORMAL, wx.BOLD, 0, "Purisa"))
        label_1.SetForegroundColour(wx.RED)
        label2 = wx.StaticText(PanelPres, -1 , u'\nVersion ' + ConfigGlob.get('DEFAULT', 'version') + '\n')
        label2.SetForegroundColour(txtcolour)
        label2.SetBackgroundColour(bckgrdcolor)
        #label3 = wx.StaticText(PanelPres, -1 , u'Equipe ')
        #label3.SetForegroundColour(txtcolour)
        #label3.SetBackgroundColour(bckgrdcolor)
        self.hyper2 = hl.HyperLinkCtrl(PanelPres, wx.ID_ANY, u"REPERE", URL="http://repere.no-ip.org/")
        self.hyper2.SetColours(linkcolor, linkcolor, "RED")
        self.hyper2.SetBackgroundColour(bckgrdcolor)
        self.hyper2.EnableRollover(True)
        self.hyper2.SetUnderlines(False, False, True)
        self.hyper2.SetBold(True)
        self.hyper2.UpdateLink()
        label_lerass = wx.StaticText(PanelPres, -1, u'Laboratoire ')
        label_lerass.SetForegroundColour(txtcolour)
        label_lerass.SetBackgroundColour(bckgrdcolor)
        self.hyper_lerass = hl.HyperLinkCtrl(PanelPres, -1, u'LERASS', URL="http://www.lerass.com")
        self.hyper_lerass.SetColours(linkcolor, linkcolor, "RED")
        self.hyper_lerass.SetBackgroundColour(bckgrdcolor)
        self.hyper_lerass.EnableRollover(True)
        self.hyper_lerass.SetUnderlines(False, False, True)
        self.hyper_lerass.SetBold(True)
        self.hyper_lerass.UpdateLink()
        blank = wx.StaticText(PanelPres, -1, u'\n')
        blank1 = wx.StaticText(PanelPres, -1, u'\n')
        labellicence = wx.StaticText(PanelPres, -1, u'Licence GNU GPL')
        labellicence.SetForegroundColour(txtcolour)
        labellicence.SetBackgroundColour(bckgrdcolor)
        labelcopy = wx.StaticText(PanelPres, -1, ConfigGlob.get('DEFAULT', 'copyright'))
        labelcopy.SetForegroundColour(txtcolour)
        labelcopy.SetBackgroundColour(bckgrdcolor)
        python_img = wx.Image(os.path.join(ImagePath,'python-logo.jpg'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        r_img = wx.Image(os.path.join(ImagePath,'Rlogo.jpg'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        lexique_img = wx.Image(os.path.join(ImagePath,'LexTexte4.jpg'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        but_python = wx.BitmapButton(self, -1, python_img)
        but_lexique = wx.BitmapButton(self, -1, lexique_img)
        but_r = wx.BitmapButton(self, -1, r_img)
        self.Bind(wx.EVT_BUTTON, self.OnPython, but_python)
        self.Bind(wx.EVT_BUTTON, self.OnLexique, but_lexique)
        self.Bind(wx.EVT_BUTTON, self.OnR, but_r)
        
        
        #grid_sizer_1.Add(label3, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_1.Add(self.hyper2, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_3.Add(label_lerass, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        grid_sizer_3.Add(self.hyper_lerass, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer4.Add(label_1, 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(label2, 0, wx.ALIGN_CENTER, 5)
        #sizer2.Add(wx.StaticText(PanelPres, -1, u''), 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(wx.StaticText(PanelPres, -1, u''), 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(wx.StaticText(PanelPres, -1, u''), 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(grid_sizer_3, 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(wx.StaticText(PanelPres, -1, u' '), 0, wx.ALIGN_CENTER, 5)
        #sizer2.Add(wx.StaticText(PanelPres, -1, u''), 0, wx.ALIGN_CENTER, 5)
        #sizer2.Add(wx.StaticText(PanelPres, -1, u''), 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(grid_sizer_1, 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(labellicence, 0, wx.ALIGN_CENTER, 5)
        sizer2.Add(labelcopy, 0, wx.ALIGN_CENTER, 5)
        sizer1.Add(sizer4, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        PanelPres.SetSizer(sizer2)
        sizer5.Add(blank, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 2)
        sizer5.Add(PanelPres, 1, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 0)
        sizer5.Add(blank1, 1, wx.ALIGN_CENTER_HORIZONTAL,2)
        grid_sizer_2.Add(but_python, 1, wx.ALIGN_CENTER_HORIZONTAL| wx.ALIGN_CENTER_VERTICAL)
        grid_sizer_2.Add(but_lexique, 1,wx.ALIGN_CENTER_HORIZONTAL| wx.ALIGN_CENTER_VERTICAL)
        grid_sizer_2.Add(but_r, 1, wx.ALIGN_CENTER_HORIZONTAL| wx.ALIGN_CENTER_VERTICAL)
        
        sizer1.Add(sizer5, 3, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL, 1)
        sizer1.Add(grid_sizer_2, 1, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer1)
        sizer1.Fit(self)
    
    def OnPython(self,evt):
        webbrowser.open('http://www.python.org')
    
    def OnLexique(self,evt):
        webbrowser.open('http://www.lexique.org')
        
    def OnR(self,evt):
        webbrowser.open('http://www.r-project.org')

class MySplashScreen(wx.SplashScreen):
    def __init__(self):
        bmp = wx.Image(os.path.join(ImagePath, 'splash.png')).ConvertToBitmap()
        wx.SplashScreen.__init__(self, bmp,
                                 wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT,
                                 3000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fc = wx.FutureCall(1500, self.ShowMain)

    def OnClose(self, evt):
        evt.Skip()
        self.Hide()
        
        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()

    def ShowMain(self):
        frame = IraFrame(None, -1, "IRaMuTeQ " + ConfigGlob.get('DEFAULT', 'version'), size=(950, 650))
        frame.Show()
        frame.Upgrade()
        frame.OnOpenFromCmdl()
#        if self.fc.IsRunning():
#            self.Raise()
        #wx.CallAfter(frame.ShowTip)
        
class MyApp(wx.App):
    def OnInit(self):
        """
        Create and show the splash screen.  It will then create and show
        the main frame when it is time to do so.
        """

        wx.SystemOptions.SetOptionInt("mac.window-plain-transition", 1)
        self.SetAppName("Iramuteq")       
        splash = MySplashScreen()
        splash.Show()
        return True

def main():
    app = MyApp(False)
    app.MainLoop()

if __name__ == '__main__':
    __name__ = 'Main'
    main()
