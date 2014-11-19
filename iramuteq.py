#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012, Pierre Ratinaud
#License: GNU GPL

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
import wx.lib.agw.aui as aui
import wx.html
import wx.grid
import wx.lib.hyperlink as hl
#------------------------------------
from functions import BugReport, PlaySound, ReadLexique, History, DoConf, ReadDicoAsDico, progressbar
from checkversion import NewVersion
from guifunct import *
from tableau import Tableau
from dialog import PrefDialog, CorpusPref
from tabfrequence import Frequences, FreqMultiple
from tabchi2 import ChiSquare
#from tabstudent import MakeStudent
from tabchddist import ChdCluster
from tabafcm import DoAFCM
from tabchdalc import AnalyseQuest
from tabsimi import DoSimi
from tabrsimple import InputText
from tabverges import Prototypical
from tabsplitvar import SplitMatrixFromVar
#from textafcuci import AfcUci
from textdist import AnalysePam
from textstat import Stat
from textaslexico import Lexico
from textsimi import SimiTxt, SimiFromCluster
from textwordcloud import WordCloud, ClusterCloud
from textreinert import Reinert
#from profile_segment import ProfileSegment
#from textcheckcorpus import checkcorpus
from openanalyse import OpenAnalyse
from corpus import Builder, SubBuilder
#from sheet import MySheet
from checkinstall import CreateIraDirectory, CheckRPath, FindRPAthWin32, FindRPathNix, CheckRPackages, IsNew, UpgradeConf, CopyConf, RLibsAreInstalled
from chemins import RscriptsPath, ConstructConfigPath, ConstructDicoPath, ConstructGlobalPath, PathOut
from parse_factiva_xml import ImportFactiva
from tools import Extract

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
ID_CHDReinert = wx.NewId()
ID_TEXTAFCM = wx.NewId()
ID_TEXTSTAT = wx.NewId()
ID_ASLEX = wx.NewId()
ID_TEXTREINERT = wx.NewId()
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
ID_proto = wx.NewId()
ID_ImportTXM = wx.NewId()
ID_FreqMulti = wx.NewId()
##########################################################
#elements de configuration
##########################################################
#encodage
if sys.platform == 'darwin' :
    sys.setdefaultencoding('UTF-8')
    wx.SetDefaultPyEncoding('UTF-8')
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
DefaultConf = ConfigParser()
DefaultConf.read(DictConfigPath['preferences'])
#repertoire de l'utilisateur
if os.getenv('HOME') != None:
    user_home = os.getenv('HOME')
else:
    user_home = os.getenv('HOMEPATH')
UserConfigPath = os.path.abspath(os.path.join(user_home, '.iramuteq'))
#Si pas de fichiers de config utilisateur, on cree le repertoire
CreateIraDirectory(UserConfigPath, AppliPath)
#fichiers log pour windows (py2exe)
log = logging.getLogger('iramuteq')
fh = logging.FileHandler(os.path.join(UserConfigPath,'stdout.log'))
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)
if sys.platform != 'win32' and sys.platform != 'darwin':
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    log.addHandler(ch)
log.setLevel(logging.INFO)

class writer(object):
    def write(self, data):
        if data.strip() != '' :
            log.info('ERROR : %s' % data)

class printer(object) :
    def write(self, data) :
        if data.strip() != '' :
            log.info('Print : %s' % data)

sys.stderr = writer()
sys.stdout = printer()

ConfigPath = ConstructConfigPath(UserConfigPath)

langues = {'french' : wx.LANGUAGE_FRENCH,
            'english' : wx.LANGUAGE_ENGLISH,
            'portuguese' : wx.LANGUAGE_PORTUGUESE,
            'italian' : wx.LANGUAGE_ITALIAN,
            'spanish' : wx.LANGUAGE_SPANISH}

code_langues = {'french' : 'fr_FR',
             'english' : 'en',
            'portuguese' : 'pt_PT',
            'italian' : 'it_IT',
            'spanish' : 'es_ES'
            }
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
        #self.RscriptsPath = ConstructRscriptsPath(AppliPath)
        self.RscriptsPath = PathOut(dirout=os.path.join(AppliPath, 'Rscripts'))
        self.RscriptsPath.basefiles(RscriptsPath)
        #self.DictPath = ConstructDicoPath(AppliPath)
        self.DictPath = ConstructDicoPath(UserConfigPath)
        self.ConfigGlob = ConfigGlob
        self.ConfigPath = ConstructConfigPath(UserConfigPath)
        self.pref = RawConfigParser()
        #workaround for import problem
        self.SimiFromCluster = SimiFromCluster
        #langues
        gettext.install('iramuteq',  os.path.join(AppliPath,'locale'), unicode=True)
        #langues = ['fr_FR', 'en', 'pt_PT']
        #for l in langues :
        #    pass
        self.preslangue = {}
        for langue in code_langues :
            self.preslangue[langue] = gettext.translation("iramuteq", os.path.join(AppliPath,'locale'), languages=[code_langues[langue]])
        self.setlangue()
        #self.presLan_fr = gettext.translation("iramuteq", os.path.join(AppliPath,'locale'), languages=['fr_FR'])
        #self.presLan_en = gettext.translation("iramuteq", os.path.join(AppliPath,'locale'), languages=['en'])
        # tell FrameManager to manage this frame        
        #self._mgr = wx.aui.AuiManager()
        self._mgr = aui.AuiManager()
        self._mgr.SetManagedWindow(self)
        self.x = 0
        # create menu
#--------------------------------------------------------------------------------
        self.mb = wx.MenuBar()

        file_menu = wx.Menu()
        item = wx.MenuItem(file_menu, ID_OpenData, _(u"Open a matrix").decode('utf8'), _(u"Open a matrix").decode('utf8'))
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)
        
        item = wx.MenuItem(file_menu, ID_OpenText, _(u"Open a text corpus").decode('utf8'), _(u"Open a text corpus").decode('utf8'))
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)
        
        item = wx.MenuItem(file_menu, ID_OnOpenAnalyse, _(u"Open an analysis").decode('utf8'), _(u"Open an analysis").decode('utf8'))
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)

        
        menuFactiva = wx.Menu()
        fact_from_xml = wx.MenuItem(menuFactiva, wx.ID_ANY, _(u"from xml").decode('utf8'))
        fact_from_mail = wx.MenuItem(menuFactiva, wx.ID_ANY, _(u"from mail").decode('utf8'))
        fact_from_txt = wx.MenuItem(menuFactiva, wx.ID_ANY, _(u"from copy/paste").decode('utf8'))
        menuFactiva.AppendItem(fact_from_xml)
        menuFactiva.AppendItem(fact_from_mail)
        menuFactiva.AppendItem(fact_from_txt)
        file_menu.AppendMenu(-1, _(u"Import from factiva").decode('utf8'), menuFactiva)

        item = wx.MenuItem(file_menu, ID_ImportTXM, _(u"Import from TXM").decode('utf8'), _(u"Import from TXM").decode('utf8'))
        item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN))
        file_menu.AppendItem(item)

        menuTools = wx.Menu()
        splitvar = wx.MenuItem(menuTools, wx.ID_ANY, _(u"Split from variable").decode('utf8'))
        extractmod = wx.MenuItem(menuTools, wx.ID_ANY, _(u"Extract mods").decode('utf8'))
        extractthem = wx.MenuItem(menuTools, wx.ID_ANY, _(u"Extract thematics").decode('utf8'))
        menuTools.AppendItem(splitvar)
        menuTools.AppendItem(extractmod)
        menuTools.AppendItem(extractthem)
        self.ID_splitvar = splitvar.GetId()
        self.ID_extractmod = extractmod.GetId()
        self.ID_extractthem = extractthem.GetId()
        file_menu.AppendMenu(-1, _(u"Tools").decode('utf8'), menuTools)

               
        #item = wx.MenuItem(file_menu, ID_SaveTab, _(u"Save tab as...").decode('utf8'), _(u"Save tab as...").decode('utf8'))
        #item.SetBitmap(wx.ArtProvider_GetBitmap(wx.ART_FILE_SAVE_AS))
        #file_menu.AppendItem(item)
        
        file_menu.Append(wx.ID_EXIT, _(u"Exit").decode('utf8'))
        
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_PREFERENCES, '', _(u'Preferences').decode('utf8'))
        
        view_menu = wx.Menu()
        view_menu.Append(ID_ACCEUIL, _(u"Home page").decode('utf8'))
        view_menu.Append(ID_VIEWDATA, _(u"Show data").decode('utf8'))
        view_menu.Append(ID_RESULT, _(u'Show results').decode('utf8'))
        #view_menu.AppendSeparator()
        matrix_menu = wx.Menu()
        matrix_menu.Append(ID_Freq, _(u"Frequencies").decode('utf8'))
        matrix_menu.Append(ID_FreqMulti, _(u'Multiple frequencies').decode('utf8'))
        matrix_menu.Append(ID_Chi2, _(u"Chi2").decode('utf8'))
        #matrix_menu.Append(ID_Student, u"t de Student")
        menu_classif = wx.Menu()
        menu_classif.Append(ID_CHDReinert, _(u"Reinert's Method").decode('utf8'))
        #menu_classif.Append(ID_CHDSIM, u"Par matrice des distances")
        matrix_menu.AppendMenu(-1, _(u"Clustering").decode('utf8'), menu_classif)
        #matrix_menu.Append(ID_AFCM, u"AFCM")
        matrix_menu.Append(ID_SIMI, _(u"Similarities Analysis").decode('utf8'))
        matrix_menu.Append(ID_proto, _(u"Prototypical Analysis").decode('utf8'))
        ID_RCODE = wx.NewId()
        matrix_menu.Append(ID_RCODE, u"Code R...") 
        #menu_splittab = wx.Menu()
        #ID_SPLITVAR = wx.NewId()
        #splitvar = wx.MenuItem(menu_splittab, ID_SPLITVAR, _(u"Split from variable").decode('utf8'))
        #menu_splittab.AppendItem(splitvar)
        #matrix_menu.AppendMenu(-1, _(u"Split matrix").decode('utf8'), menu_splittab)
        self.matrix_menu = matrix_menu
        
        text_menu = wx.Menu()
        #text_menu.Append(ID_CHECKCORPUS, u"Vérifier le corpus")
        text_menu.Append(ID_TEXTSTAT, _(u"Statistics").decode('utf8'))
        text_menu.Append(ID_ASLEX, _(u"Specificities and CA").decode('utf8'))
        #text_menu.Append(ID_TEXTAFCM, u"AFC sur UCI / Vocabulaire")
        menu_classiftxt = wx.Menu()
        menu_classiftxt.Append(ID_TEXTREINERT, _(u"Reinert's Method").decode('utf8'))
        #menu_classiftxt.Append(ID_TEXTPAM, u"Par matrice des distances")
        text_menu.AppendMenu(-1, _(u"Clustering").decode('utf8'), menu_classiftxt)
        text_menu.Append(ID_SimiTxt, _(u"Similarities Analysis").decode('utf8')) 
        ID_WC = wx.NewId()
        text_menu.Append(ID_WC, _(u"WordCloud").decode('utf8'))
        self.text_menu = text_menu
        
        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, _(u"About...").decode('utf8'))
        help_menu.Append(wx.ID_HELP, _(u"Online help...").decode('utf8'))
        
        self.mb.Append(file_menu, _(u"File").decode('utf8'))
        self.mb.Append(edit_menu, _(u"Edition").decode('utf8'))
        self.mb.Append(view_menu, _(u"View").decode('utf8'))
        self.mb.Append(matrix_menu, _(u"Matrix analysis").decode('utf8'))
        self.mb.Append(text_menu, _(u"Text analysis").decode('utf8'))
        self.mb.Append(help_menu, _(u"Help").decode('utf8'))
        
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
        #if not os.path.exists(os.path.join(UserConfigPath, 'history.db')) :
        #    with open(os.path.join(UserConfigPath, 'history.db'), 'w') as f :
        #        f.write('')
        self.history = History(os.path.join(UserConfigPath, 'history.db'))
        self.tree = LeftTree(self)
        self._mgr.AddPane(self.tree, aui.AuiPaneInfo().Name("lefttree").Caption(_(u"Navigator").decode('utf8')).
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
        
        #self._mgr.AddPane(self.Sheet, wx.aui.AuiPaneInfo().Name("Data").CenterPane())
        #self._mgr.AddPane(self.Sheet, aui.AuiPaneInfo().Name("Data").CenterPane())
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
        self.Bind(wx.EVT_MENU, self.import_factiva_xml, fact_from_xml)
        self.Bind(wx.EVT_MENU, self.import_factiva_mail, fact_from_mail)
        self.Bind(wx.EVT_MENU, self.import_factiva_txt, fact_from_txt)
        self.Bind(wx.EVT_MENU, self.ExtractTools, splitvar)
        self.Bind(wx.EVT_MENU, self.ExtractTools, extractmod)
        self.Bind(wx.EVT_MENU, self.ExtractTools, extractthem)
        self.Bind(wx.EVT_MENU, self.OnFreq, id=ID_Freq)
        self.Bind(wx.EVT_MENU, self.OnFreqMulti, id=ID_FreqMulti)
        self.Bind(wx.EVT_MENU, self.OnChi2, id=ID_Chi2)
        self.Bind(wx.EVT_MENU, self.OnStudent, id=ID_Student)
        self.Bind(wx.EVT_MENU, self.OnCHDSIM, id=ID_CHDSIM)
        self.Bind(wx.EVT_MENU, self.OnCHDReinert, id=ID_CHDReinert)
        self.Bind(wx.EVT_MENU, self.OnAFCM, id=ID_AFCM)
        self.Bind(wx.EVT_MENU, self.OnProto, id=ID_proto)
        self.Bind(wx.EVT_MENU, self.OnRCode, id=ID_RCODE)
        #self.Bind(wx.EVT_MENU, self.OnSplitVar, id=ID_SPLITVAR)
        #self.Bind(wx.EVT_MENU, self.OnCheckcorpus, id = ID_CHECKCORPUS)
        self.Bind(wx.EVT_MENU, self.OnTextStat, id=ID_TEXTSTAT)
        self.Bind(wx.EVT_MENU, self.OnTextSpec, id=ID_ASLEX)
        self.Bind(wx.EVT_MENU, self.OnTextAfcm, id=ID_TEXTAFCM)
        self.Bind(wx.EVT_MENU, self.OnTextReinert, id=ID_TEXTREINERT)
        self.Bind(wx.EVT_MENU, self.OnPamSimple, id=ID_TEXTPAM)
        self.Bind(wx.EVT_MENU, self.OnSimiTxt, id=ID_SimiTxt)
        self.Bind(wx.EVT_MENU, self.OnWordCloud, id=ID_WC)
        self.Bind(wx.EVT_MENU, self.OnSimiTab, id=ID_SIMI)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        #self.Bind(wx.EVT_MENU, self.OnSaveTabAs, id=ID_SaveTab)
        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelp, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnPref, id=wx.ID_PREFERENCES)
        self.Bind(wx.EVT_MENU, self.OnImportTXM, id=ID_ImportTXM)
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

##############################################################@
        self.DisEnSaveTabAs(False)
        self.ShowMenu('view', False)
        self.ShowMenu('matrix', False)
        self.ShowMenu('text', False)
   
        self._mgr.Update()

        self.DataPop = False
        self.DataTxt = False
        self.Text = ''

        self.lexique = None
        self.corpus = None

    def finish_init(self) :
        try :
            self.pref.read(self.ConfigPath['preferences'])
            if IsNew(self) :
                UpgradeConf(self)
                self.pref.read(self.ConfigPath['preferences'])
                New = True
            else :
                CopyConf(self)
                New = False
        except :
            UpgradeConf(self)
            self.pref.read(self.ConfigPath['preferences'])
            New = True
        self.sound = self.pref.getboolean('iramuteq', 'sound')
        self.check_update = self.pref.getboolean('iramuteq', 'checkupdate')
        self.version = ConfigGlob.get('DEFAULT', 'version')
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
(souvent C:\Program Files\R\R-2.x.x\R.exe sous windows ou /usr/bin/R sous linux ou Mac Os X)
vous devez signaler le chemin de l'éxecutable de R dans les préférences.""" 
            dlg = wx.MessageDialog(self, msg, u"Problème de configuration", wx.OK | wx.NO_DEFAULT | wx.ICON_WARNING)
            dlg.CenterOnParent()
            if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                pass
            dlg.Destroy()

    def setlangue(self) :
        self.pref.read(self.ConfigPath['preferences'])
        try :
            guilangue = self.pref.get('iramuteq', 'guilanguage')
        except :
            guilangue = DefaultConf.get('iramuteq', 'guilanguage')
        self.preslangue.get(guilangue, 'english').install()

    def OnVerif(self, evt) :
        pack = CheckRPackages(self)
        if pack :
            dlg = wx.MessageDialog(self, u"Installation OK", u"Installation", wx.OK | wx.ICON_INFORMATION)
            dlg.CenterOnParent()
            if dlg.ShowModal() in [wx.ID_NO, wx.ID_CANCEL]:
                evt.Veto()

    def DisEnSaveTabAs(self, DISEN):
    #Disable SaveTabAs
        file_menu = self.mb.GetMenu(0)
        items = file_menu.GetMenuItems()
        for item in items :
            if item.GetId() == ID_SaveTab :
                item.Enable(DISEN)
    
    def ShowMenu(self, menu, Show=True):
        if menu == 'text' :
            menu_pos = 4
        elif menu == 'matrix' :
            menu_pos = 3
        elif menu == 'view' :
            menu_pos = 2
        else :
            menu_pos = None
            
        #menu_pos = self.mb.FindMenu(menu)
        if not menu_pos is None :
            self.mb.EnableTop(menu_pos, Show)
            self.mb.UpdateMenus()


#--------------------------------------------------------------------
    def OnClose(self, event):
        print 'onclose'
        with open(self.ConfigPath['path'], 'w') as f :
            self.PathPath.write(f)
        self._mgr.UnInit()
        del self._mgr
        self.Destroy()

    def OnOpenData(self, event):
        inputname, self.input_path = OnOpen(self, "Data")
        if inputname:
            #filename = self.input_path[0]
            self.tableau = Tableau(self,os.path.abspath(self.input_path[0]))
            val = get_table_param(self, self.input_path[0])
            if val == wx.ID_OK :
                self.tableau.make_content()
                OpenAnalyse(self, self.tableau.parametres)
                self.tree.OnItemAppend(self.tableau.parametres)
                #self.tableau.show_tab()

    def OnOpenAnalyse(self, event):
        self.AnalysePath = OnOpen(self, "Analyse")
        OpenAnalyse(self, self.AnalysePath[1][0], True)
        self.ShowMenu('view')

    def OnOpenText(self, event):
        inputname, self.input_path = OnOpen(self, "Texte")
        self.filename = self.input_path[0]
        if inputname:
            self.OpenText()
   
    def OnViewData(self, event):
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
    
    def OnSubText(self, corpus, parametres = None):
        if corpus is None :
            corpus = self.tree.getcorpus()
        builder = SubBuilder(self, corpus, parametres)
        if builder.res == wx.ID_OK :
            busy = wx.BusyInfo(_("Please wait...").decode('utf8'), self)
            wx.SafeYield()
            corpus = builder.doanalyse()
            self.history.add(corpus.parametres)
            self.tree.OnItemAppend(corpus.parametres)
            OpenAnalyse(self, corpus.parametres)
            del busy
            
    def OpenText(self):
        dlg = wx.ProgressDialog("Ouverture...",
                                   "Veuillez patienter...",
                                   maximum=2,
                                   parent=self,
                                   style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT
                                   )
        
        builder =  Builder(self, dlg)
        if builder.res == wx.ID_OK :
            try :
                corpus = builder.doanalyse()
                self.history.add(corpus.parametres)
                self.tree.OnItemAppend(corpus.parametres)
                OpenAnalyse(self, corpus.parametres)
            except :
                dlg.Destroy()
                BugReport(self)
            else :
                count = 1
                keepGoing = dlg.Update(count, u"Lecture du fichier")
                self.ShowMenu('view')
                self.ShowMenu('text')
                self.ShowMenu('matrix', False)
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
        dev = ConfigGlob.get('DEFAULT', 'dev').decode('utf8').split(';')
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
            if 'parametres' in dir(npage) :
                self.tree.GiveFocus(uuid=npage.parametres['uuid'])
                if npage.parametres.get('matrix', False) :
                    self.ShowMenu('text', False)
                    self.ShowMenu('matrix', True)
                elif npage.parametres.get('corpus', False) :
                    self.ShowMenu('text')
                    self.ShowMenu('matrix', False)

    def OnCloseTab(self, evt):
        #log.info('Closing tab %s' % str(evt.GetEventObject()))
        ctrl = evt.GetEventObject()
        if isinstance(ctrl.GetParent(), aui.AuiNotebook) or isinstance(ctrl.GetParent(), wx.Panel):
            notebook = True
        else :
            notebook = False
        page = self.nb.GetPage(self.nb.GetSelection())
        if 'parametres' in dir(page) and isinstance(ctrl.GetParent(), IraFrame) :
            self.history.rmtab(page.parametres)
            self.tree.CloseItem(uuid = page.parametres['uuid'])
        TabTitle = self.nb.GetPageText(self.nb.GetSelection())

        if self.nb.GetPageCount() == 1 and not notebook :
            self.LastTabClose()
    
    def LastTabClose(self) :
        if self.nb.GetPageCount() == 1 :
            #self.DisEnSaveTabAs(False)
            if self.DataTxt :
                self.ShowAPane("Text")
            elif self.DataPop :
                self.ShowAPane("Data")
            else :
                self.ShowAPane("Intro_Text")

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
    def analyse_matrix(self, analyse, analyse_type = '', matrix = None, parametres = None, dlgnb = 1):
        if matrix is None :
            matrix = self.tree.getmatrix()
        if parametres is not None :
            parametres['type'] = analyse_type
        else :
            parametres = {'type' : analyse_type}
        try :
        #print 'plus de bug@@@@@@@@@@@@@@@@@@@@@@'
            analyse(self, matrix, parametres = parametres, dlg = dlgnb)
        except:
            BugReport(self)           

    def OnFreq(self, event, matrix = None):
        self.analyse_matrix(Frequences, analyse_type = 'freq', matrix = matrix, dlgnb = 3)
    
    def OnFreqMulti(self, event, matrix = None):
        self.analyse_matrix(FreqMultiple, analyse_type = 'freqmulti', matrix = matrix, dlgnb = 3)

    def OnChi2(self, event, matrix = None):
        self.analyse_matrix(ChiSquare, matrix = matrix, analyse_type = 'chi2', dlgnb = 3) 

    def OnSimiTab(self, event, matrix = None):
        self.analyse_matrix(DoSimi, matrix = matrix, analyse_type = 'simimatrix', dlgnb = 5)

    def OnCHDReinert(self, event, matrix = None):
        #if matrix is None :
        #    matrix = self.tree.getmatrix()
        #AnalyseQuest(self, matrix, parametres = {'type' : 'reinertmatrix'}, dlg = 3)
        self.analyse_matrix(AnalyseQuest, matrix = matrix, analyse_type = 'reinertmatrix', dlgnb = 5)
            
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
 
#     def OnCHDReinert(self, event):
#         try:
#          #   print('PLUS DE BUG SUR ALCESTE QUESTIONNAIRE')
#             self.quest = AnalyseQuest(self)
#             if self.quest.val == wx.ID_OK:
#                 PlaySound(self)
#         except:
#             BugReport(self)
    
    def OnProto(self, evt, matrix = None) :
        self.analyse_matrix(Prototypical, matrix = matrix, analyse_type = 'proto', dlgnb = 3) 
        #Prototypical(self, {'type' : 'proto'})
    
    def OnSplitVar(self, evt, matrix = None):
        self.analyse_matrix(SplitMatrixFromVar, matrix = matrix, analyse_type = 'splitvar', parametres = {'pathout': matrix.pathout.dirout}, dlgnb = 3)
        matrix = self.tree.getmatrix()
        

    def OnSimiTxt(self, evt, corpus = None) :
        #    print 'PLUS DE BUG SUR SIMITXT'
        try :
            #self.Text = SimiTxt(self)
            if corpus is None :
                corpus = self.tree.getcorpus()            
            self.Text = SimiTxt(self, corpus, parametres = {'type': 'simitxt'}, dlg = 3)
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        except :
            BugReport(self)
    
    def OnWordCloud(self, evt, corpus = None) :
        #    print 'PLUS DE BUG SUR WORDCLOUD'
        try :
            if corpus is None :
                corpus = self.tree.getcorpus()            
            self.Text = WordCloud(self, corpus, parametres = {'type' : 'wordcloud'}, dlg = 3)
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        except :
            BugReport(self)

    def OnClusterCloud(self, corpus, parametres = None) :
        self.Text = ClusterCloud(self, corpus, parametres = parametres, dlg = 3)

    def OnAFCM(self, event):
        try:
            DoAFCM(self)
        except:
            BugReport(self)

    def OnTextStat(self, event, corpus = None):
            #print 'PAS DE BUG SUR TEXT STAT'
        try:
            if corpus is None :
                corpus = self.tree.getcorpus()
            self.Text = Stat(self, corpus, parametres = {'type': 'stat'}, dlg = 7)
            
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        except:
            BugReport(self)
        
    def OnTextSpec(self, event, corpus = None):  
        try:
            #self.Text = AsLexico(self)
            #print('ATTENTION : PLUS DE BUG SUR LEXICO')
            if corpus is None :
                corpus = self.tree.getcorpus()
            self.Text = Lexico(self, corpus, parametres = {'type' : 'spec'}, dlg = 3)
            if self.Text.val == wx.ID_OK :
                PlaySound(self)
        except:
            BugReport(self)
    
    def OnTextAfcm(self, event):
        try:
            AfcUci(self)
            PlaySound(self)
        except:
            BugReport(self)

    def import_factiva_xml(self,event):
        try :
            ImportFactiva(self, 'xml')
        except :
            BugReport(self)

    def import_factiva_mail(self, evt) :
        try :
            ImportFactiva(self, 'mail')
        except :
            BugReport(self)

    def import_factiva_txt(self, evt) :
        try :
            ImportFactiva(self, 'txt')
        except :
            BugReport(self)

    def OnImportTXM(self, evt) :
        try :
            ImportFactiva(self, 'txm')
        except :
            BugReport(self)

    def ExtractTools(self, evt) :
        ID = evt.GetId()
        if ID == self.ID_splitvar :
            Extract(self, 'splitvar')
        elif ID == self.ID_extractmod :
            Extract(self, 'mods')
        elif ID == self.ID_extractthem :
            Extract(self, 'them')

    def OnTextReinert(self, event, corpus = None):
        try:
            #print('ATTENTION : PLUS DE BUG SUR ALCESTE')
            #RunAnalyse(self, corpus, Alceste, OptAlceste)
            if corpus is None :
                corpus = self.tree.getcorpus()            
            self.Text = Reinert(self, corpus, parametres = {'type': 'alceste'}, dlg = 6)
            if self.Text.val == wx.ID_OK:
                PlaySound(self)
        except:
            BugReport(self)

    def OnPamSimple(self, event, corpus = None):
        try:
            if corpus is None :
                corpus = self.tree.getcorpus()
            self.Text = AnalysePam(self, corpus, parametres = {'type' : 'pamtxt'}, dlg = 6)
            if self.Text.val == wx.ID_OK:
                PlaySound(self)
        except:
            BugReport(self)

    def SimiCluster(self, parametres = {}, fromprof = False, pathout = '', listactives = [], actives = [], tableau = None) :
        DoSimi(self, param = parametres, fromprof =  fromprof, listactives = listactives, actives = actives, tableau = tableau)
    
#    def OnSimi(self,evt):
#        try :
            #print 'ATTENTION !!!! VERGES'
            #print 'PLUS DE BUG SUR SIMI'
#            self.res = DoSimi(self, param = None)
            #self.res = Verges(self)
#            if self.res.val == wx.ID_OK :
#                PlaySound(self)
#        except :
#            BugReport(self)
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
                val = get_table_param(self, self.filename)
                if val == wx.ID_OK :
                    self.tableau.make_content()
                    OpenAnalyse(self, self.tableau.parametres)
                    self.tree.OnItemAppend(self.tableau.parametres)
                #get_table_param(self, self.filename)
                #self.tableau.make_content()
                #self.tableau.show_tab()
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
        col = randint(0, 255)
        col1 = randint(0,255)
        col2 = randint(0,255)
        col = 57
        bckgrdcolor = wx.Colour(col, col1, col2)
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
        labellicence = wx.StaticText(PanelPres, -1, _(u"License GNU GPL").decode('utf8'))
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
                                 2000, None, -1)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.fc = wx.FutureCall(1, self.ShowMain)

    def OnClose(self, evt):
        evt.Skip()
        self.Hide()
        
        if self.fc.IsRunning():
            self.fc.Stop()
            self.ShowMain()

    def ShowMain(self):
        displaySize = wx.DisplaySize()
        w = displaySize[0]/1.2
        h = displaySize[1]/1.2
        frame = IraFrame(None, -1, "IRaMuTeQ " + ConfigGlob.get('DEFAULT', 'version'), size=(w, h))
        frame.Show()
        frame.finish_init()
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
