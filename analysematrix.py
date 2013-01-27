#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2013 Pierre Ratinaud
#Lisense: GNU GPL



import logging
import os
from time import time
from uuid import uuid4


from chemins import PathOut
from functions import exec_rcode, check_Rresult, DoConf
from time import time, sleep
from openanalyse import OpenAnalyse

class AnalyseMatrix :
    def __init__(self, ira, tableau, parametres = None, dlg = False) :
        self.tableau = tableau
        self.ira = ira
        self.parent = ira
        self.dlg = dlg
        self.parametres = parametres
        self.val = False
        if not 'pathout' in self.parametres :
            self.pathout = PathOut(tableau.parametres['filename'], analyse_type = parametres['type'], dirout = parametres['pathout'])
        else :
            self.pathout = PathOut(filename = tableau.parametres['filename'], dirout = self.parametres['pathout'], analyse_type = self.parametres['type'])

        self.parametres['pathout'] = self.pathout.dirout
        self.parametres['uuid'] = str(uuid4())
        self.parametres['name'] = os.path.split(self.parametres['pathout'])[1]
        self.parametres['encoding'] = self.ira.syscoding

        self.t1 = time()
        result_analyse = self.doanalyse()
        if result_analyse is None :
            self.time = time() - self.t1
            minutes, seconds = divmod(self.time, 60)
            hours, minutes = divmod(minutes, 60)            
            self.parametres['time'] = '%.0fh %.0fm %.0fs' % (hours, minutes, seconds)
            self.parametres['ira'] = self.pathout['Analyse.ira']
            DoConf().makeoptions([self.parametres['type']], [self.parametres], self.pathout['Analyse.ira'])
            self.ira.history.addMatrix(self.parametres)
            if dlg :
                dlg.Destroy()
                OpenAnalyse(self.parent, self.parametres['ira'])
                #self.ira.tree.AddAnalyse(self.parametres)
                self.val = 5100
        else :
            self.val = False
            if dlg :
                dlg.Destroy()
 
    def doanalyse(self) :
        pass
    
    def doR(self, Rscript, wait = False, dlg = None, message = '') :
        log.info('R code...')
        pid = exec_rcode(self.ira.RPath, Rscript, wait = wait)
        while pid.poll() is None :
            if dlg :
                self.dlg.Pulse(message)
                sleep(0.2)
            else :
                sleep(0.2)
        return check_Rresult(self.ira, pid)
    
