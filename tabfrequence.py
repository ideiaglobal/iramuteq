#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008 Pierre Ratinaud
#Lisense: GNU/GPL

#from __future__ import division
import os
import sys
import wx
import wx.html
from chemins import ffr, FFF
import tempfile
from time import sleep
from functions import exec_rcode, check_Rresult

class FreqDialog(wx.Dialog):
    def __init__(
            self, parent, ID, title, size=wx.DefaultSize, pos=wx.DefaultPosition,
            style=wx.DEFAULT_DIALOG_STYLE | wx.CANCEL | wx.OK
            ):
        pre = wx.PreDialog()
        pre.SetExtraStyle(wx.DIALOG_EX_CONTEXTHELP)
        pre.Create(parent, ID, title, pos, size, style)
        self.PostCreate(pre)
        self.parent = parent 
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.content = parent.content
        self.header = parent.tableau.get_colnames()
        LABELLIST = []
        for i in self.header:
            forme = i
            if len(forme) > 60 :
                LABELLIST.append(i[0:60])
            else:
                LABELLIST.append(i)
        self.list_box_1 = wx.ListBox(self, -1, choices=LABELLIST, style=wx.LB_EXTENDED | wx.LB_HSCROLL)
        sizer.Add(self.list_box_1, 0, 5)
        
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        btn = wx.Button(self, wx.ID_CANCEL)
        btn.SetHelpText("Annuler")
        btnsizer.Add(btn)
        
        btn = wx.Button(self, wx.ID_OK)
        btn.SetHelpText("Valider")
        btn.SetDefault()
        btnsizer.Add(btn)
        
        sizer.Add(btnsizer, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(sizer)
        sizer.Fit(self)
        self.SetTitle(u"Sélection")
  
        # end wxGlade
        
class Frequences():
    def __init__(self, parent):
        #self.Filename = parent.filename
        self.fileforR = parent.tableau.parametre['csvfile']
        self.TEMPDIR = parent.TEMPDIR
        self.num = parent.FreqNum
        self.DICTFILE = {}
        self.RPath = parent.PathPath.get('PATHS', 'rpath')
        self.parent=parent
        dlg = FreqDialog(parent, -1, u"Fréquences", size=(350, 200),
                style=wx.DEFAULT_DIALOG_STYLE)
        dlg.CenterOnParent()
        val = dlg.ShowModal()
        if val == wx.ID_OK :
            ColSel = dlg.list_box_1.GetSelections()
            self.header=dlg.header
            dlg.Destroy()
            listfileout = self.ShowFreq(ColSel)
            parent.FreqNum += 1
            parent.DictTab[u"Fréquences_%s*" % parent.FreqNum] = listfileout
            parent.FileTabList.append(listfileout)
            parent.newtab = wx.html.HtmlWindow(parent.nb, -1)
            if "gtk2" in wx.PlatformInfo:
               parent.newtab.SetStandardFonts()
            parent.newtab.LoadPage(listfileout[len(listfileout) - 1])
            parent.nb.AddPage(parent.newtab, u"Fréquences_%s*" % parent.FreqNum)
            parent.nb.SetSelection(parent.nb.GetPageCount() - 1)
            parent.ShowAPane("Tab_content")
            parent.DisEnSaveTabAs(True) 
        else :
            dlg.Destroy()

    def ShowFreq(self, select):
        listfile = []
        listfile.append(False)
        self.ListFileForR = []
        self.ListTitre = []
        self.OutFrame = tempfile.mktemp(dir=self.TEMPDIR)
        if self.parent.g_id: rownames = '1'
        else: rownames = 'NULL'
        if self.parent.g_header : header = 'TRUE'
        else : header = 'FALSE'
        self.ListTitre = [self.header[i] for i in select]
        self.ListFileForR = [ffr(os.path.join(self.TEMPDIR, 'freq%s_%s.jpeg' % (str(self.num), i))) for i in range(len(select))]
        listfile = [os.path.join(self.TEMPDIR, 'freq%s_%s.jpeg' % (str(self.num), i)) for i in range(len(select))]
        sel = 'c(' + ','.join([str(val + 1) for val in select]) + ')'
        listfiles = 'c("' + '","'.join(self.ListFileForR) + '")'
        titles = 'c("' +  '","'.join(self.ListTitre) + '")'
        txt = """
        source("%s")
        """ % self.parent.RscriptsPath['Rfunct']

        txt += """
        datadm <- ReadData("%s", encoding="%s", header = TRUE, sep = ";",quote = "\\%s", na.strings = "%s",rownames=1)
        """ % (ffr(self.fileforR), self.parent.encode, self.parent.tableau.parametre['txtsep'], self.parent.nastrings)
        txt += """
        outframe<-data.frame(cbind('***','****'))
        colnames(outframe)<-c('effectif','pourcentage')
        select <- %s
        listfiles <- %s
        titles <- %s
        compteur <- 1
        """ % (sel, listfiles, titles)
        txt += """
        for (i in select) {
            datasum<-as.matrix(summary(datadm[,i]))
            if (rownames(datasum)[1]=='Min.' && rownames(datasum)[3]=='Median') {
                dtype<-'num'
            } else if (datasum[1] == "logical") {
                dtype <- 'char'
                datasum <- as.matrix(as.integer(datasum[2]))
                rownames(datasum) <- 'NA'
            } else {
                dtype<-'char'
            }
            datasum<-as.data.frame(datasum)
            if (dtype=='char') {
                datasum[,2]<-round((datasum[,1]/sum(datasum[,1]))*100,digits=2)
            } else {
                datasum[,2]<-datasum[,1]
            }
            colnames(datasum)<-c('effectif','pourcentage')
            graphout <- listfiles[compteur]  
            if (Sys.info()["sysname"]=='Darwin') {
                quartz(file=graphout,type='jpeg')
                par(cex=1)
            } else {
                jpeg(graphout,res=200)
                par(cex=0.3)
                }
            if (max(nchar(rownames(datasum))) > 15) {
                lab.bar <- 1:nrow(datasum)
            } else {
                lab.bar <- rownames(datasum)
            }
            barplot(datasum[,2],border=NA,beside=TRUE,names.arg=lab.bar)
            title(main=titles[compteur])
            dev.off()
            datasum<-rbind(datasum,total=colSums(datasum))
            outframe<-rbind(outframe,c('***','****'))
            datasum[,1]<-as.character(datasum[,1])
            datasum[,2]<-as.character(datasum[,2])
            outframe<-rbind(outframe,datasum)
            compteur <- compteur + 1
            }
        outframe<-rbind(outframe,c('***','****'))
        write.csv2(outframe,file="%s")
        """ % ffr(self.OutFrame)
        tmpfile = tempfile.mktemp(dir=self.TEMPDIR)
        tmpscript = open(tmpfile, 'w')
        tmpscript.write(txt)
        tmpscript.close()
        pid = exec_rcode(self.RPath, tmpfile, wait = False)
        while pid.poll() == None :
           sleep(0.2)
        check_Rresult(self.parent, pid)
        fileout = self.DoLayout()
        listfile.append(fileout)
        self.DICTFILE[self.num] = listfile
        return listfile


    def DoLayout(self):
        listtab = []
        tab = []
        filein = open(self.OutFrame, 'rU')
        content = filein.readlines()
        filein.close()
        content.pop(0)
        content.pop(0)
        texte = ''
        for ligne in content:
            ligne = ligne.replace('"', '').replace('\n', '')
            ligne = ligne.split(';')
            if ligne[1] == u'***' :
                if tab != []:
                    listtab.append(tab)
                tab = []
            else :
                tab.append(ligne)
        pretexte = u'''<html>
        <meta http-equiv="content-Type" content="text/html; charset=%s" />
        <body>\n<h1>Fréquences</h1>
        <a name="deb"></a><br>
        ''' % self.parent.SysEncoding
        for i in range(0, len(listtab)):
            pretexte += '<p><a href="#%s">%s</a></p>' % (str(i), self.ListTitre[i])
            texte += '<hr size="5" align="center" width="50%" color="green">\n'
            texte += '<p><a href="#deb">Retour</a></p>\n'
            texte += '<a name="%s"></a><h2>%s</h2>\n' % (str(i), self.ListTitre[i])
            texte += '<table>\n<tr><td>\n'
            texte += '<table border=1><tr><td></td><td>Effectifs</td><td>pourcentage</td></tr>'
            for line in listtab[i] :
                texte += '<tr>'
                texte += """
                <td>%s</td><td align=center>%s</td><td align=center>%s %%</td>
                """ % (line[0], line[1], line[2])
                texte += '</tr>'
            texte += '</table></td>'
            texte += """
            <td><img src="%s" alt="graph"/></td></tr></table>\n
            """ % os.path.basename(self.ListFileForR[i])
            texte += '</body>\n</html>'
        fileout = os.path.join(self.TEMPDIR, 'resultats%s-freq.html' % str(self.num))
        FILE = open(fileout, 'w')
        FILE.write(pretexte + texte)
        FILE.close()
        return fileout


