#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2010, Pierre Ratinaud
#Lisense: GNU/GPL

import tempfile
from ProfList import *
import agw.aui as aui
from functions import exec_rcode, check_Rresult, ReadProfileAsDico, ReadList
from listlex import *
from dialog import PrefSegProf, PrefProfTypes
from time import sleep

class ProfileSegment() :
    def __init__(self, parent, pathout, parametres, corpus) :
        self.parent = parent
        self.corpus = corpus
        self.dictpathout = pathout
        self.parametres = parametres
        dial = PrefSegProf(self.parent)
        dial.CenterOnParent()
        if dial.ShowModal() == wx.ID_OK :
           if dial.box_lem.GetSelection() == 0 :
               self.lem = True
           else :
               self.lem = False
           self.mini = dial.spin_min.GetValue()
           self.maxi = dial.spin_max.GetValue()
           self.eff = dial.spin_eff.GetValue()
           dial.Destroy()
           self.dlg = progressbar(self, maxi = 4)
           self.dlg.Update(1, u'Recherche des segments')
           self.make_table()
           self.make_prof()
           self.dlg.Update(3, u'ouverture des profils')
           self.do_layout()
           self.dlg.Update(4, 'fini')
           self.dlg.Destroy()
    
    def make_table(self) :
        self.corpus.make_segments_profile(self.dictpathout['segments_classes'], lenmin = self.mini, lenmax = self.maxi, effmin = self.eff, lem = self.lem)

    def make_prof(self) :
        txt = """
        load("%s")
        source("%s")
        """ % (self.dictpathout['RData'], self.parent.RscriptsPath['chdfunct'])

        txt += """
        dt <- read.csv2("%s", row.names = 1)
        to <- build.pond.prof(dt)
        PrintProfile(n1,to[4],NULL,to[5],NULL,clnb,"%s","%s")
        """ % (self.corpus.dictpathout['segments_classes'], self.dictpathout['prof_seg'], self.dictpathout['antiprof_seg'])
        fo = tempfile.mktemp(dir=self.parent.TEMPDIR)
        with open(fo, 'w') as f :
            f.write(txt)
        pid = exec_rcode(self.parent.RPath, fo, wait = False)
        while pid.poll() == None :
            self.dlg.Pulse(u'Construction des profils...')
            sleep(0.2)
        check_Rresult(self.parent, pid)

    def do_layout(self) :
        SelectTab = self.parent.nb.GetSelection()
        page = self.parent.nb.GetPage(SelectTab).TabChdSim
        prof_seg = ReadProfileAsDico(self, self.dictpathout['prof_seg'], True, self.parent.syscoding)
        prof_seg_nb = aui.AuiNotebook(self.parent, -1, wx.DefaultPosition)
        for i in range(0,len(self.corpus.lc)) :
            ntab = ProfListctrlPanel(self.parent, self, prof_seg[str(i + 1)], False, i + 1)
            prof_seg_nb.AddPage(ntab, 'classe %i' % (i + 1))
        page.AddPage(prof_seg_nb, u'Profils des segements répétés')
        page.SetSelection(page.GetPageCount() - 1)

class ProfilType() :
    def __init__(self, parent, corpus, parametres) :
        self.parent = parent
        self.corpus = corpus
        self.parametres = parametres
        self.outprof = self.corpus.dictpathout['prof_type']
        dial = PrefProfTypes(self.parent)
        dial.fbb.SetValue(self.outprof)
        dial.CenterOnParent()
        res = dial.ShowModal()
        if res == wx.ID_OK :
            if dial.radio_type.GetSelection() == 0 :
                alceste = True
            else :
                alceste = False
            #if 'outprof' in self.corpus.parametre :
            #    self.corpus.parametre['outprof'][self.outprof] = alceste
            #else :
            #    self.corpus.parametre['outprof'] = {self.outprof: alceste}
            self.dlg = progressbar(self, maxi = 4)
            self.dlg.Update(1, u'Recherche des types')
            self.make_table()
            self.dlg.Update(1, u'Construction des profils')
            self.make_prof(alceste = alceste)
            self.dlg.Update(3, u'Ouverture des profils')
            self.do_layout(alceste = alceste)
            self.dlg.Update(4, 'fini')
            self.dlg.Destroy()
    
    def make_table(self) :
        self.corpus.make_proftype(self.corpus.dictpathout['type_cl'])

    def make_prof(self, alceste = True) :
        txt = """
        load("%s")
        source("%s")
        """ % (self.corpus.dictpathout['RData'], self.parent.RscriptsPath['chdfunct'])

        txt += """
        dt <- read.csv2("%s", row.names = 1)
        """ % self.corpus.dictpathout['type_cl']
        if alceste :
            txt += """
            to <- build.pond.prof(dt)
            PrintProfile(n1,to[4],NULL,to[5],NULL,clnb,"%s","%s")
            """ % (self.outprof, self.corpus.dictpathout['antiprof_type'])
        else :
            txt += """
            to <- AsLexico2(dt)
            write.csv2(to[[1]], file = "%s")
            """ % (self.outprof)
            #write.csv2(to[[3]], file = "%s")
            # % (self.outprof)
        fo = tempfile.mktemp(dir=self.parent.TEMPDIR)
        with open(fo, 'w') as f :
            f.write(txt)
        pid = exec_rcode(self.parent.RPath, fo, wait = False)
        while pid.poll() == None :
            self.dlg.Pulse(u'Construction des profils...')
            sleep(0.2)
        check_Rresult(self.parent, pid)

    def do_layout(self, alceste = True) :
        SelectTab = self.parent.nb.GetSelection()
        page = self.parent.nb.GetPage(SelectTab).TabChdSim
        prof_seg_nb = aui.AuiNotebook(self.parent, -1, wx.DefaultPosition)
        if alceste :
            prof_seg = ReadProfileAsDico(self, self.outprof, True)
            for i in range(0,len(self.corpus.lc)) :
                ntab = ProfListctrlPanel(self.parent, self, prof_seg[str(i + 1)], False, i + 1)
                prof_seg_nb.AddPage(ntab, 'classe %i' % (i + 1))
        else :
            self.DictSpec, first = ReadList(self.outprof)
            self.ListPan = ListForSpec(self.parent, self, self.DictSpec, first)
            prof_seg_nb.AddPage(self.ListPan, u'Spécificités')

        page.AddPage(prof_seg_nb, u'Profils des types')
        page.SetSelection(page.GetPageCount() - 1)

