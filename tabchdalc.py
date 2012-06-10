#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, ChdTxtPathOut, ConstructAfcUciPath, ffr
from functions import sortedby, CreateIraFile, print_liste, exec_rcode, check_Rresult
from PrintRScript import RchdQuest
from layout import OpenCHDS, PrintRapport
from dialog import PrefQuestAlc
import os
import sys
import wx
from numpy import *
import tempfile
import time


class AnalyseQuest():
    def __init__(self, parent):
        dlg = PrefQuestAlc(parent)
        dlg.CenterOnParent()
        self.val = dlg.ShowModal()
        if self.val == wx.ID_OK :
            if dlg.m_radioBox1.GetSelection() == 1 :
                ListAct = dlg.nactives
                ListSup = dlg.varsup
                nbcl_p1 = dlg.spin_nbcl.GetValue()
                mincl = dlg.spin_mincl.GetValue()
                DoQuestAlceste(parent, ListAct, ListSup, nbcl = nbcl_p1, mincl = mincl)
            else:
                nbcl_p1 = dlg.spin_nbcl.GetValue()
                mincl = dlg.spin_mincl.GetValue()
                DoQuestAlceste(parent, nbcl = nbcl_p1, mincl = mincl) 

class DoQuestAlceste:
    def __init__(self, parent, ListAct=False, ListSup=False, nbcl = 10, mincl = 10):
        self.t1 = time.time()
#-------------------------------------------------------------------               
        dlg = wx.ProgressDialog("Traitements",
                               "Veuillez patienter...",
                               maximum=5,
                               parent=parent,
                               style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME
                                )
        dlg.Center()
        count = 1
        keepGoing = dlg.Update(count)
#-------------------------------------------------------------------
        self.pathout = ConstructPathOut(parent.tableau.parametre['filename'], 'AlcesteQuest')
        self.DictForme = {}
        self.DictFormeSup = {}
        self.Min = 10
        self.Linecontent = []
        self.parent = parent
        self.RPath = self.parent.PathPath.get('PATHS', 'rpath')
        self.dictpathout = ChdTxtPathOut(self.pathout)
        self.parent.tableau.dictpathout = self.dictpathout
        self.clnb = ''
        self.ListAct = ListAct
        self.ucecla = ''
        self.parent = parent
#-----------------------------------------------------------
        count += 1
        dlg.Update(count, u"passage en O/1")
        if not ListAct:
            self.parent.tableau.make_01_alc_format(self.dictpathout['Act01'])
        else:
            self.parent.tableau.make_01_from_selection(ListAct, ListSup)
        file = open(self.dictpathout['listeuce1'], 'w')
        file.write('num uce;num uc\n')
        for i in range(0, len(self.parent.tableau.linecontent)):
            file.write('%i;%i\n' % (i, i))
        file.close()
        self.nbind = len(self.parent.tableau.linecontent)
#------------------------------------------------------------
        RchdQuest(self.dictpathout, parent.RscriptsPath, nbcl, mincl)
#------------------------------------------------------------
        count += 1
        dlg.Update(count, u"Analyse (patientez...)")
        
        pid = exec_rcode(self.RPath, self.dictpathout['Rchdquest'], wait = False)
        while pid.poll() == None :
            dlg.Pulse(u"Analyse (patientez...)")
            time.sleep(0.2)
        check_Rresult(self.parent, pid)
#------------------------------------------------------------
        count += 1
        dlg.Update(count, u"Ecriture des résultats")
        self.parent.tableau.buildprofil()
        self.clnb = self.parent.tableau.clnb
        self.ucecla = self.parent.tableau.ucecla
        self.BuildProfile()
        temps = time.time() - self.t1
        PrintRapport(self, 'quest')
        self.parent.tableau.save_tableau(self.dictpathout['db'])
        CreateIraFile(self.dictpathout, self.clnb, corpname = os.path.basename(parent.filename), section = 'questionnaire')
        afc_graph_list = [[os.path.basename(self.dictpathout['AFC2DL_OUT']), u'Variables actives - coordonnées - facteurs 1 / 2'],
                         [os.path.basename(self.dictpathout['AFC2DSL_OUT']), u'variables illustratives - coordonnées - facteurs 1 / 2'],
                         [os.path.basename(self.dictpathout['AFC2DCL_OUT']), u'Classes - Coordonnées - facteur 1 / 2'],
                         [os.path.basename(self.dictpathout['AFC2DCoul']), u'Variables actives - Corrélation - facteur 1/2'],
                         [os.path.basename(self.dictpathout['AFC2DCoulSup']), u'Variables illustratives - Corrélation - facteur 1 / 2'],
                         [os.path.basename(self.dictpathout['AFC2DCoulCl']), u'Classes - Corrélations - facteurs 1 / 2'], ]
        chd_graph_list = [[os.path.basename(self.dictpathout['dendro1']), u'dendrogramme à partir de chd1']]
        chd_graph_list.append([os.path.basename(self.dictpathout['arbre1']), u'chd1'])
        print_liste(self.dictpathout['liste_graph_afc'], afc_graph_list)
        print_liste(self.dictpathout['liste_graph_chd'], chd_graph_list)

        self.tableau = self.parent.tableau
        OpenCHDS(self.parent, self, self.dictpathout['ira'], False)
#------------------------------------------------------------
        print 'fini', time.time() - self.t1
        count += 1
        dlg.Update(count, "Fini")
    
    def BuildProfile(self):
        print 'build profile'
        txt = ''
        txt += """
        source("%s")
        """ % self.parent.RscriptsPath['chdfunct']
        txt += """
        load("%s")
        """ % self.dictpathout['RData']
        txt += """
        dataact<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
        """ % self.dictpathout['Contout']
        txt += """
        dataet<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
        """ % self.dictpathout['ContEtOut']
        txt += """
        clnb<-%i
        """ % self.clnb
        txt += """
        tablesqrpact<-BuildProf(as.matrix(dataact),n1,clnb)
        tablesqrpet<-BuildProf(as.matrix(dataet),n1,clnb)
        PrintProfile(n1,tablesqrpact[4],tablesqrpet[4],tablesqrpact[5],tablesqrpet[5],%i,"%s","%s")
        """ % (self.clnb, self.dictpathout['PROFILE_OUT'], self.dictpathout['ANTIPRO_OUT'])
        txt += """
        colnames(tablesqrpact[[2]])<-paste('classe',1:clnb,sep=' ')
        colnames(tablesqrpact[[1]])<-paste('classe',1:clnb,sep=' ')
        colnames(tablesqrpet[[2]])<-paste('classe',1:clnb,sep=' ')
        colnames(tablesqrpet[[1]])<-paste('classe',1:clnb,sep=' ')
        chistabletot<-rbind(as.data.frame(tablesqrpact[2]),as.data.frame(tablesqrpet[2]))
        ptabletot<-rbind(as.data.frame(tablesqrpact[1]),as.data.frame(tablesqrpet[1]))
        gbcluster<-n1
        write.csv2(chistabletot,file="%s")
        """ % self.dictpathout['chisqtable']
        txt += """
        write.csv2(ptabletot,file="%s")
        """ % self.dictpathout['ptable']
        txt += """
        write.csv2(gbcluster,file="%s")
        """ % self.dictpathout['SbyClasseOut']
        if self.clnb > 2 :
            txt += """
            library(ca)
            rowtot<-nrow(dataact)+nrow(dataet)
            afctable<-rbind(as.matrix(dataact),as.matrix(dataet))
            colnames(afctable)<-paste('classe',1:clnb,sep=' ')
            afc<-ca(afctable,suprow=((nrow(dataact)+1):rowtot),nd=(ncol(afctable)-1))
            debet<-nrow(dataact)+1
            debsup<-NULL
            fin<-rowtot
            afc<-AddCorrelationOk(afc)
            source("%s")
            """ % self.parent.RscriptsPath['Rgraph']
    
            txt += """
            afc <- summary.ca.dm(afc)
            afc_table <- create_afc_table(afc)
            write.csv2(afc_table$facteur, file = "%s")
            write.csv2(afc_table$colonne, file = "%s")
            write.csv2(afc_table$ligne, file = "%s")
            """ % (self.dictpathout['afc_facteur'], self.dictpathout['afc_col'], self.dictpathout['afc_row'])
            
            txt += """
            xlab <- paste('facteur 1 - ', round(afc$facteur[1,2],2), sep = '')
            ylab <- paste('facteur 2 - ', round(afc$facteur[2,2],2), sep = '')
            xlab <- paste(xlab, ' %', sep = '')
            ylab <- paste(ylab, ' %', sep = '')
            """
    
            txt += """
            PARCEX<-%s
            """ % "0.9"
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=1, fin=(debet-1), xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DL_OUT'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=debet, fin=fin, xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DSL_OUT'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col = TRUE, what='coord', xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DCL_OUT'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=1, fin=(debet-1), xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DCoul'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=debet, fin=fin, xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DCoulSup'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col = TRUE, what='crl', xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DCoulCl'])
        txt += """
        save.image(file="%s")
        """ % self.dictpathout['RData']
        tmpfile = tempfile.mktemp(dir=self.parent.TEMPDIR)
        tmpscript = open(tmpfile, 'w')
        tmpscript.write(txt)
        tmpscript.close()
        pid = exec_rcode(self.parent.RPath, tmpfile, wait = False)
        while pid.poll() == None :
            time.sleep(0.2)
        check_Rresult(self.parent, pid)
        temps = time.time() - self.t1
        self.minutes, self.seconds = divmod(temps, 60)
        self.hours, self.minutes = divmod(self.minutes, 60)        
