# -*- coding: utf-8 -*-
# Author: Pierre Ratinaud
# lisence : GNU GPL
# copyright : 2012-2013 (c) Pierre Ratinaud

import logging
from chemins import PathOut
from functions import exec_rcode, check_Rresult, DoConf, ReadDicoAsDico, progressbar
from shutil import copy
from time import time, sleep
from uuid import uuid4
import os
from openanalyse import OpenAnalyse
from dialog import StatDialog

log = logging.getLogger('iramuteq.analyse')

class AnalyseText :
    def __init__(self, ira, corpus, parametres=None, dlg=False, lemdial=True) :
        self.corpus = corpus
        self.ira = ira
        self.parent = ira
        self.dlg = dlg
        self.dialok = True
        self.parametres = parametres
        self.lemdial = lemdial
        self.val = False
        self.keys = DoConf(self.ira.ConfigPath['key']).getoptions()
        if not 'pathout' in self.parametres :
            self.pathout = PathOut(corpus.parametres['originalpath'], analyse_type=parametres['type'], dirout=corpus.parametres['pathout'])
        else :
            self.pathout = PathOut(filename=corpus.parametres['originalpath'], dirout=self.parametres['pathout'], analyse_type=self.parametres['type'])
        self.parametres = self.lemparam()
        if self.parametres is not None :
            self.parametres = self.make_config(parametres)
        log.info(self.pathout.dirout)
        if self.parametres is not None :
            self.keys = DoConf(self.ira.ConfigPath['key']).getoptions()
            gramact = [k for k in self.keys if self.keys[k] == 1]
            gramsup = [k for k in self.keys if self.keys[k] == 2]
            self.parametres['pathout'] = self.pathout.mkdirout()
            self.pathout = PathOut(dirout=self.parametres['pathout'])
            self.pathout.createdir(self.parametres['pathout'])
            self.parametres['corpus'] = self.corpus.parametres['uuid']
            self.parametres['uuid'] = str(uuid4())
            self.parametres['name'] = os.path.split(self.parametres['pathout'])[1]
            self.parametres['type'] = parametres['type']
            self.parametres['encoding'] = self.ira.syscoding
            self.t1 = time()
            if not self.parametres.get('dictionary', False) :
                self.corpus.make_lems(lem=self.parametres['lem'])
            else :
                print 'read new dico'
                dico = ReadDicoAsDico(self.parametres['dictionary'])
                self.corpus.make_lems_from_dict(dico, dolem=self.parametres['lem'])
                dictname = os.path.basename(self.parametres['dictionary'])
                dictpath = os.path.join(self.pathout.dirout, dictname)
                copy(self.parametres['dictionary'], dictpath)
                self.parametres['dictionary'] = dictpath
            self.corpus.parse_active(gramact, gramsup)
            if dlg :
                self.dlg = progressbar(self.ira, dlg)
            result_analyse = self.doanalyse()
            if result_analyse is None :
                self.time = time() - self.t1
                minutes, seconds = divmod(self.time, 60)
                hours, minutes = divmod(minutes, 60)            
                self.parametres['time'] = '%.0fh %.0fm %.0fs' % (hours, minutes, seconds)
                self.parametres['ira'] = self.pathout['Analyse.ira']
                DoConf().makeoptions([self.parametres['type']], [self.parametres], self.pathout['Analyse.ira'])
                self.ira.history.add(self.parametres)
                if dlg :
                    if not isinstance(dlg, int) :
                        dlg.Destroy()
                    self.dlg.Destroy()
                    OpenAnalyse(self.parent, self.parametres['ira'])
                    self.ira.tree.AddAnalyse(self.parametres)
                    self.val = 5100
            else :
                self.val = False
                if dlg :
                    try :
                        self.dlg.Destroy()
                    except :
                        pass
        else :
            #if isinstance(dlg, wx.ProgressDialog) :
            #    self.dlg.Destroy()
            self.val = False

    def doanalyse(self) :
        pass

    def lemparam(self) :
        if self.dlg and self.lemdial:
            dial = StatDialog(self.parent, self.keys)
            dial.CenterOnParent()
            val = dial.ShowModal()
            if val == 5100 :
                if dial.radio_lem.GetSelection() == 0 :
                    lem = 1
                else :
                    lem = 0            
                self.parametres['lem'] = lem
                if dial.radio_dictchoice.GetSelection() == 1 :
                    self.parametres['dictionary'] = dial.dictpath.GetValue() 
                dial.Destroy()
                return self.parametres
            else :
                dial.Destroy()
                return None        
        else :
            return self.parametres

    def make_config(self, config) :
        if config is not None :
            if not self.dlg : 
                return config
            else :
                return self.preferences()
        else :
            return None

    def readconfig(self, config) :
        return config

    def preferences(self) :
        return self.parametres

    def printRscript(self) :
        pass

    def doR(self, Rscript, wait=False, dlg=None, message='') :
        log.info('R code...')
        pid = exec_rcode(self.ira.RPath, Rscript, wait=wait)
        while pid.poll() is None :
            if dlg :
                self.dlg.Pulse(message)
                sleep(0.2)
            else :
                sleep(0.2)
        return check_Rresult(self.ira, pid)






# keys = {'art_def' : 2,
#        'pre' : 2,
#        'adj_dem' : 2,
#        'ono' : 2,
#        'pro_per' : 2,
#        'ver_sup' : 2,
#        'adv' : 1,
#        'ver' : 1,
#        'adj_ind' : 2,
#        'adj_pos' : 2,
#        'aux' : 2,
#        'adj_int' : 2,
#        'pro_ind' : 2,
#        'adj' : 1,
#        'pro_dem' : 2,
#        'nom' : 1,
#        'art_ind' : 2,
#        'pro_pos' : 2,
#        'nom_sup' : 2,
#        'adv_sup' : 2,
#        'adj_sup' : 2,
#        'adj_num' : 2,
#        'pro_rel' : 2,
#        'con' : 2,
#        'num' : 2,
#        'nr' : 1,
#        'sw' : 2,
# }
#
# gramact = [k for k in keys if keys[k] == 1]
# gramsup = [k for k in keys if keys[k] == 2]
