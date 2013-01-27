# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2011 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, StatTxtPathOut
#from corpus import Corpus
from analysetxt import AnalyseText
import wx
import os
import sys
from listlex import *
from functions import exec_rcode, progressbar, check_Rresult, CreateIraFile, print_liste, treat_var_mod, write_tab, DoConf
from dialog import OptLexi, StatDialog #LexDialog
from openanalyse import OpenAnalyse
import tempfile
from ConfigParser import RawConfigParser
from guifunct import getPage, getCorpus
from time import sleep
import logging

log = logging.getLogger('iramuteq.spec')

class Lexico(AnalyseText) :
    def doanalyse(self) :
        pathout = self.pathout.dirout
        self.dictpathout = StatTxtPathOut(pathout)
        self.parametres['ira'] = self.dictpathout['ira']
        self.make_lexico()
        if self.dlg :
            try :
                self.dlg.Destroy()
            except :
                pass
   
    def DoR(self):
        nbligne = 5
        colonne = 1
        txt = """
        source("%s")
        source("%s")
        """ % (self.parent.RscriptsPath['chdfunct'], self.parent.RscriptsPath['Rgraph'])
        txt += """
        dmf<-read.csv2("%s",row.names=1)
        """ % self.dictpathout['tableafcm']
        txt += """
        dmt<-read.csv2("%s",row.names=1)
        """ % self.dictpathout['tabletypem']
        if self.parametres['indice'] == 'hypergeo' :
            txt += """
            outf <- make.spec.hypergeo(dmf)
            outt <- make.spec.hypergeo(dmt)
            """
        elif self.parametres['indice'] == 'chi2' :
            txt += """
            outf<-AsLexico2(dmf)
            outt<-AsLexico2(dmt)
            """

        txt += """
        specf<-outf[[1]]
        spect<-outt[[1]]
        write.csv2(specf,file="%s")
        """ % self.dictpathout['tablespecf']
        txt += """
        write.csv2(spect,file="%s")
        """ % self.dictpathout['tablespect']
        txt += """
        write.csv2(outf[[3]],file="%s")
        """ % self.dictpathout['eff_relatif_forme']
        txt += """
        write.csv2(outt[[3]],file="%s")
        """ % self.dictpathout['eff_relatif_type']
        if self.parametres['clnb'] > 2 :
            txt += """
            library(ca)
            nd <- ncol(specf) - 1
            if (nd > 6) nd <- 6
            slf <- rowSums(dmf)
            if (min(slf) == 0) {
                dmfp<-dmf[-which(slf==0),]
                specfp <- specf[-which(slf==0),]
            } else { 
                dmfp <- dmf
                specfp <- specf
                }
            afcf <- ca(dmfp, nd = nd)
            slt <- rowSums(dmt)
            if (min(slt) == 0) {
                dmtp<-dmt[-which(slt==0),]
                spectp <- spect[-which(slt==0),]
            } else { 
                dmtp <- dmt
                spectp <- spect
                }
            afct <- ca(dmtp, nd = nd)
            open_file_graph("%s", widt = 1000, height=1000)
            plot(afcf, what=c('all','none'), labels=c(1,1))
            open_file_graph("%s", widt = 1000, height=1000)
            plot(afcf, what=c('none','all'), labels=c(1,1))
            open_file_graph("%s", widt = 1000, height=1000)
            plot(afct, what=c('all','none'), labels=c(1,1))
            open_file_graph("%s", widt = 1000, height=1000)
            plot(afct, what=c('none','all'), labels=c(1,1))
            afcf <- AddCorrelationOk(afcf)
            afct <- AddCorrelationOk(afct)
            afcf <- summary.ca.dm(afcf)
            afct <- summary.ca.dm(afct)
            afcf_table <- create_afc_table(afcf)
            afct_table <- create_afc_table(afct)
            write.csv2(afcf_table$facteur, file = "%s")
            write.csv2(afcf_table$colonne, file = "%s")
            write.csv2(afcf_table$ligne, file = "%s")
            write.csv2(afct_table$facteur, file = "%s")
            write.csv2(afct_table$colonne, file = "%s")
            write.csv2(afct_table$ligne, file = "%s")
            debsup <- NULL
            debet <- NULL
            clnb <-  ncol(specf)
            """ % (self.dictpathout['afcf_row'], self.dictpathout['afcf_col'], self.dictpathout['afct_row'], self.dictpathout['afct_col'], self.dictpathout['afcf_facteur_csv'], self.dictpathout['afcf_col_csv'], self.dictpathout['afcf_row_csv'], self.dictpathout['afct_facteur_csv'], self.dictpathout['afct_col_csv'], self.dictpathout['afct_row_csv'])

        txt += """
        save.image("%s")
        """ % self.dictpathout['RData']
        tmpfile = tempfile.mktemp(dir=self.parent.TEMPDIR)
        tmpscript = open(tmpfile, 'w')
        tmpscript.write(txt)
        tmpscript.close()
        self.doR(tmpfile, dlg = self.dlg, message = 'R...')

    def preferences(self) :
        listet = self.corpus.make_etoiles()
        listet.sort()
        variables = treat_var_mod(listet)
        var = [v for v in variables]
        dial = OptLexi(self.parent)
        dial.listet = listet
        dial.variables = var
        for et in var :
            dial.list_box_1.Append(et)
        dial.CenterOnParent()
        self.dialok = dial.ShowModal()
        if self.dialok == wx.ID_OK :
            if dial.choice.GetSelection() == 1 :
                ListEt = [listet[i] for i in dial.list_box_1.GetSelections()]
            else :
                ListEt = variables[var[dial.list_box_1.GetSelections()[0]]]
            self.listet = ListEt
            self.parametres['mineff'] = dial.spin.GetValue()
            if dial.choice_indice.GetSelection() == 0 :
                self.parametres['indice'] = 'hypergeo'
            else :
                self.parametres['indice'] = 'chi2'
            self.parametres['clnb'] = len(ListEt)
            dial.Destroy()
            return self.parametres
        else :
            dial.Destroy()
            return None

    def make_lexico(self) :
        mineff = self.parametres['mineff']
        #dlg = progressbar(self, maxi = 3)
        tabout = self.corpus.make_lexitable(mineff, self.listet)
        #log.warning('Fmax a 200')
        #Fmax = [line for line in tabout[1:] if sum(line[1:]) > 199]
        #formesmax = [line[0] for line in Fmax]
        #Fmax = [line[1:] for line in Fmax]
        #summax = [sum(col) for col in zip(*Fmax)]
        #tabout.append(['Fmax'] + summax)
        #tabout = [line for line in tabout if line[0] not in formesmax]
        #log.warning('ATTENTION : hapax par etoile')
        #tabout.append(['hapax'] + self.corpus.gethapaxbyet(self.listet))
        write_tab(tabout, self.dictpathout['tableafcm'])
        
        #log.warning('ATTENTION : gethapaxuces')
        #self.corpus.gethapaxuces()

        tabout = self.corpus.make_efftype_from_etoiles(self.listet)
        write_tab(tabout, self.dictpathout['tabletypem'])
        if self.dlg :
            self.dlg.Update(2, u'R...')
        self.DoR()
        if self.dlg :
            self.dlg.Update(3, u'Chargement...')
        afcf_graph_list = [[os.path.basename(self.dictpathout['afcf_row']), u'lignes'],\
                            [os.path.basename(self.dictpathout['afcf_col']), u'colonnes']]
        afct_graph_list = [[os.path.basename(self.dictpathout['afct_row']), u'lignes'],\
                            [os.path.basename(self.dictpathout['afct_col']), u'colonnes']]
        print_liste(self.dictpathout['liste_graph_afcf'],afcf_graph_list)
        print_liste(self.dictpathout['liste_graph_afct'],afct_graph_list)
        DoConf().makeoptions(['spec'],[self.parametres], self.dictpathout['ira'])
