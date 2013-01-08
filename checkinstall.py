#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008 Pierre Ratinaud
#Lisense: GNU/GPL

import os
import sys
import shutil
from chemins import ConstructConfigPath, ConstructDicoPath
from functions import exec_rcode, exec_RCMD
import wx
import tempfile
from ConfigParser import *
from time import sleep
import logging

log = logging.getLogger('iramuteq.checkinstall')

def IsNew(self):
    version_glob = self.ConfigGlob.get('DEFAULT', 'version_nb').split('.')
    try :
        version_user = self.pref.get('iramuteq','version_nb').split('.')
    except NoOptionError :
        return True
    if version_user :
        version_user[0] = int(version_user[0])
        version_user[1] = int(version_user[1])
        version_glob[0] = int(version_glob[0])
        version_glob[1] = int(version_glob[1])
        if len(version_user) == len(version_glob) :
            if version_glob > version_user :
                return True
            else :
                return False
        if len(version_glob) == 2 :
            if version_glob[:2] >= version_user[:2] :
                return True
            else :
                return False
        elif len(version_glob) == 3 :
            if version_glob[:2] <= version_user[:2] :
                return False
            else :
                return True

def UpgradeConf(self) :
    dictuser = self.ConfigPath
    dictappli = ConstructConfigPath(self.AppliPath, user = False)
    for item,filein in dictuser.iteritems():
        if not item == u'global' and not item == u'history':
            shutil.copyfile(dictappli[item], filein)

def CreateIraDirectory(UserConfigPath,AppliPath):
    if not os.path.exists(UserConfigPath):
        os.mkdir(UserConfigPath)
    if not os.path.exists(os.path.join(UserConfigPath, 'dictionnaires')) :
        os.mkdir(os.path.join(UserConfigPath, 'dictionnaires'))

def CopyConf(self) :
    DictUser = self.ConfigPath
    DictAppli = ConstructConfigPath(self.AppliPath,user=False)
    for item, filein in DictUser.iteritems():
        if not item == u'global' and not item == u'path' and not item == u'preferences' and not item == u'history' :
            shutil.copyfile(DictAppli[item],filein)
        if item == u'path':
            if not os.path.exists(filein):
                shutil.copyfile(DictAppli[item],filein)
        if item == u'preferences' :
            if not os.path.exists(filein) :
                shutil.copyfile(DictAppli[item],filein)
    dicoUser = self.DictPath
    dicoAppli = ConstructDicoPath(self.AppliPath)
    for fi in dicoUser :
        if not os.path.exists(dicoUser[fi]) and os.path.exists(dicoAppli[fi]):
            shutil.copyfile(dicoAppli[fi], dicoUser[fi])

def CheckRPath(PathPath):
    if not os.path.exists(PathPath.get('PATHS','rpath')):
        return False
    else :
        return True
        
def FindRPAthWin32():
    BestPath=False
    progpaths=[]
    if 'ProgramFiles' in os.environ :
        progpaths.append(os.environ['ProgramFiles'])
    if 'ProgramFiles(x86)' in os.environ :
        progpaths.append(os.environ['ProgramFiles(x86)'])
    if 'ProgramW6432' in os.environ :
        progpaths.append(os.environ['ProgramW6432'])
    progpaths = list(set(progpaths))
    if progpaths != [] :
        for progpath in progpaths :
            rpath = os.path.join(progpath, "R")
        if os.path.exists(rpath) :
            for i in range(7,20):
                for j in range(0,15):
                    path=os.path.join(rpath,"R-2."+str(i)+"."+str(j),'bin','R.exe')
                    if os.path.exists(path):
                        BestPath=path
    return BestPath

def FindRPathNix():
    BestPath=False
    if os.path.exists('/usr/bin/R'):
        BestPath='/usr/bin/R'
    elif os.path.exists('/usr/local/bin/R'):
        BestPath='/usr/local/bin/R'
    return BestPath

def RLibsAreInstalled(self) :
    rlibs = self.pref.get('iramuteq', 'rlibs')
    if rlibs == 'false' or rlibs == 'False' :
        return False
    else :
        return True

def install_textometrieR(self) :
    dlg = wx.ProgressDialog("Installation de textometrieR",
    "Veuillez patientez...",
    maximum= 2,
    parent=self,
    style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT
    )
    dlg.Center()
    dlg.Update(1, 'Installation de textometrieR')
    path = os.path.join(self.AppliPath, 'Rlib', 'textometrieR')
    exec_RCMD(self.RPath, path)
    dlg.Update(2,'fini')
    dlg.Destroy()

def CheckRPackages(self):
    listdep = ['ca', 'gee', 'ape', 'igraph','proxy', 'wordcloud', 'textometrieR']
    nolib = []
    i=0
    dlg = wx.ProgressDialog("Test des librairies de R", "test en cours...", maximum = len(listdep), parent=self, style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT)
    for bib in listdep :
        dlg.Center()
        i+=1
        dlg.Update(i, "test de %s" % bib)
        txt = """library("%s")""" % bib
        tmpscript = tempfile.mktemp(dir=self.TEMPDIR)
        with open(tmpscript, 'w') as f :
            f.write(txt)
        test = exec_rcode(self.RPath, tmpscript, wait = True)
        if test :
            log.info('packages %s : NOT INSTALLED' % bib)
            nolib.append(bib)
        else :
            log.info('packages %s : OK' % bib)
    dlg.Update(len(listdep),'fini')
    dlg.Destroy()
    install_textoR = False
    if 'textometrieR' in nolib :
         nolib.pop(nolib.index('textometrieR'))
         install_textoR = True
    if nolib != [] :
        txt = '\n'.join(nolib)
        msg = u"""Les bibliothèques de R suivantes sont manquantes :
%s

Sans ces bibliothèques, IRamuteq ne fonctionnera pas.
    
- Vous pouvez installer ces bibliothèques manuellement :
        Cliquez sur Annuler
        Lancez R
        Tapez install.packages('nom de la bibiothèque')
        
- ou laisser IRamuteq les installer automatiquement en cliquant sur VALIDER .
        Les bibliothèques seront téléchargées depuis le site miroir de R %s.
        """ % (txt, self.pref.get('iramuteq','rmirror'))
        dial = wx.MessageDialog(self, msg, u"Installation incomplète", wx.OK | wx.CANCEL | wx.NO_DEFAULT | wx.ICON_WARNING)
        dial.CenterOnParent()
        val = dial.ShowModal()
        if val == wx.ID_OK :
            dlg = wx.ProgressDialog("Installation",
                                       "Veuillez patientez...",
                                       maximum=len(nolib) + 1,
                                       parent=self,
                                       style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT
                                       )
            dlg.Center()
            dlg.Update(1, u"installation...") 
            compt = 0

            for bib in nolib :
                compt += 1
                dlg.Update(compt, u"installation librairie %s" % bib)
                txt = """
                userdir <- unlist(strsplit(Sys.getenv("R_LIBS_USER"), .Platform$path.sep))[1]
                if (!file.exists(userdir)) {
                    if (!dir.create(userdir, recursive = TRUE)) 
                        print('pas possible')
                    lib <- userdir
                    .libPaths(c(userdir, .libPaths()))
                }
                print(userdir)
                .libPaths
                """
                txt += """
                install.packages("%s", repos = "%s")
                """ % (bib, self.pref.get('iramuteq','rmirror'))
                tmpscript = tempfile.mktemp(dir=self.TEMPDIR)
                with open(tmpscript, 'w') as f :
                    f.write(txt)
                test = exec_rcode(self.RPath, tmpscript, wait = False)
                while test.poll() == None :
                    dlg.Pulse(u"installation librairie %s" % bib)
                    sleep(0.2)
            dlg.Update(len(nolib) + 1, 'fin')
            dlg.Destroy()
        dial.Destroy()
    if install_textoR :
         install_textometrieR(self)
    if nolib == [] and not install_textoR :
        self.pref.set('iramuteq', 'rlibs', True)
        with open(self.ConfigPath['preferences'], 'w') as f :
            self.pref.write(f)
        return True
