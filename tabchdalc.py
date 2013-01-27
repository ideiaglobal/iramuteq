#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, ChdTxtPathOut, ConstructAfcUciPath, ffr, PathOut
from functions import sortedby, CreateIraFile, print_liste, exec_rcode, check_Rresult
from PrintRScript import RchdQuest
from layout import OpenCHDS, PrintRapport
from dialog import PrefQuestAlc
from analysematrix import AnalyseMatrix
import os
import sys
import wx
import tempfile
import time


class AnalyseQuest():
    def __init__(self, parent):
        dlg = PrefQuestAlc(parent)
        dlg.CenterOnParent()
        self.val = dlg.ShowModal()
        parametres = parent.tableau.parametre
        if self.val == wx.ID_OK :
            parametres['nbcl_p1'] = dlg.spin_nbcl.GetValue()
            parametres['mincl'] = dlg.spin_mincl.GetValue()
            if dlg.m_radioBox1.GetSelection() == 1 :
                parametres['listact'] = dlg.nactives
                parametres['listsup'] = dlg.varsup
            else :
                parametres['formatted'] = 1
            DoQuestAlceste(parent, parametres)

class DoQuestAlceste(AnalyseMatrix):
    def __init__(self, parent, parametres):
        parametres['pathout'] = ConstructPathOut(parent.tableau.parametre['filename'], 'gnepaMatrix')
        self.parametres = parametres
        self.parametres['type'] = 'gnepamatrix'
        self.DictForme = {}
        self.DictFormeSup = {}
        self.Min = 10
        self.Linecontent = []
        self.parent = parent
        self.RPath = self.parent.PathPath.get('PATHS', 'rpath')
        #self.dictpathout = PathOut(dirout = self.pathout)
        #self.dictpathout = self.pathout
        #self.dictpathout.basefiles(ChdTxtPathOut)
        #self.pathout = self.dictpathout
        self.clnb = ''
        self.ListAct = parametres.get('listact', False)
        self.ucecla = ''
        dlg = wx.ProgressDialog("Traitements",
                               "Veuillez patienter...",
                               maximum=5,
                               parent=self.parent,
                               style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME
                                )

        AnalyseMatrix.__init__(self, parent, parent.tableau, self.parametres, dlg = dlg)
 


#-----------------------------------------------------------
    def doanalyse(self) :
#-------------------------------------------------------------------               
        self.dictpathout = self.pathout
        self.dictpathout.basefiles(ChdTxtPathOut)
        self.parent.tableau.dictpathout = self.dictpathout

        self.dlg.Center()
        count = 1
        keepGoing = self.dlg.Update(count)
#-------------------------------------------------------------------
        count += 1
        self.dlg.Update(count, u"passage en O/1")
        if 'formatted' in self.parametres:
            self.parent.tableau.make_01_alc_format(self.dictpathout['mat01'])
        else:
            self.parent.tableau.make_01_from_selection(self.parametres['listact'], self.parametres['listsup'])
        file = open(self.dictpathout['listeuce1'], 'w')
        file.write('num uce;num uc\n')
        for i in range(0, len(self.parent.tableau.linecontent)):
            file.write('%i;%i\n' % (i, i))
        file.close()
        self.nbind = len(self.parent.tableau.linecontent)
#------------------------------------------------------------
        RchdQuest(self.dictpathout, self.parent.RscriptsPath, self.parametres['nbcl_p1'], self.parametres['mincl'])
#------------------------------------------------------------
        count += 1
        self.dlg.Update(count, u"Analyse (patientez...)")
        
        pid = exec_rcode(self.RPath, self.dictpathout['Rchdquest'], wait = False)
        while pid.poll() == None :
            self.dlg.Pulse(u"Analyse (patientez...)")
            time.sleep(0.2)
        check_Rresult(self.parent, pid)
#------------------------------------------------------------
        count += 1
        self.dlg.Update(count, u"Ecriture des résultats")
        self.parent.tableau.buildprofil()
        self.clnb = self.parent.tableau.clnb
        self.parametres['clnb'] = self.clnb
        self.ucecla = self.parent.tableau.ucecla
        self.BuildProfile()
        temps = time.time() - self.t1
        PrintRapport(self, self, {}, istxt = False)
        self.parent.tableau.save_tableau(self.dictpathout['db'])
        #CreateIraFile(self.dictpathout, self.clnb, corpname = os.path.basename(self.parent.filename), section = 'questionnaire')
        afc_graph_list = [[os.path.basename(self.dictpathout['AFC2DL_OUT']), u'Variables actives - coordonnées - facteurs 1 / 2'],
                         [os.path.basename(self.dictpathout['AFC2DSL_OUT']), u'variables illustratives - coordonnées - facteurs 1 / 2'],
                         [os.path.basename(self.dictpathout['AFC2DCL_OUT']), u'Classes - Coordonnées - facteur 1 / 2'],]
        chd_graph_list = [[os.path.basename(self.dictpathout['dendro1']), u'dendrogramme à partir de chd1']]
        chd_graph_list.append([os.path.basename(self.dictpathout['arbre1']), u'chd1'])
        print_liste(self.dictpathout['liste_graph_afc'], afc_graph_list)
        print_liste(self.dictpathout['liste_graph_chd'], chd_graph_list)

        self.tableau = self.parent.tableau
        #OpenCHDS(self.parent, self, self.dictpathout['ira'], False)
#------------------------------------------------------------
        print 'fini', time.time() - self.t1
        count += 1
        self.dlg.Update(count, "Fini")
    
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
            xyminmax <- PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=1, fin=(debet-1), xlab = xlab, ylab = ylab)
            """ % (self.dictpathout['AFC2DL_OUT'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=debet, fin=fin, xlab = xlab, ylab = ylab, xmin = xyminmax$xminmax[1], xmax = xyminmax$xminmax[2], ymin = xyminmax$yminmax[1], ymax = xyminmax$yminmax[2])
            """ % (self.dictpathout['AFC2DSL_OUT'])
            txt += """
            PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col = TRUE, what='coord', xlab = xlab, ylab = ylab, xmin = xyminmax$xminmax[1], xmax = xyminmax$xminmax[2], ymin = xyminmax$yminmax[1], ymax = xyminmax$yminmax[2])
            """ % (self.dictpathout['AFC2DCL_OUT'])
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
