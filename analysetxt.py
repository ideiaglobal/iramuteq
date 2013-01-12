# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#lisence : GNU GPL
#copyright : 2012-2013 (c) Pierre Ratinaud

import logging
from chemins import PathOut, ChdTxtPathOut
from functions import exec_rcode, check_Rresult, DoConf, print_liste
from time import time, sleep
from uuid import uuid4
import os
from PrintRScript import RchdTxt, AlcesteTxtProf
from OptionAlceste import OptionAlc 
from layout import PrintRapport
from openanalyse import OpenAnalyse
from dialog import StatDialog
from time import time

log = logging.getLogger('iramuteq.analyse')

class AnalyseText :
    def __init__(self, ira, corpus, parametres = None, dlg = False) :
        self.corpus = corpus
        self.ira = ira
        self.parent = ira
        self.dlg = dlg
        self.dialok = True
        self.parametres = parametres
        self.val = False
        if not 'pathout' in self.parametres :
            self.pathout = PathOut(corpus.parametres['originalpath'], analyse_type = parametres['type'], dirout = corpus.parametres['pathout'])
        else :
            self.pathout = PathOut(filename = corpus.parametres['originalpath'], dirout = self.parametres['pathout'], analyse_type = self.parametres['name'])
        self.parametres = self.lemparam()
        if self.parametres is not None :
            self.parametres = self.make_config(parametres)
        log.info(self.pathout.dirout)
        if self.parametres is not None :
            self.keys = DoConf(self.ira.ConfigPath['key']).getoptions()
            gramact = [k for k in keys if keys[k] == 1]
            gramsup = [k for k in keys if keys[k] == 2]
            self.parametres['pathout'] = self.pathout.mkdirout()
            self.pathout = PathOut(dirout = self.parametres['pathout'])
            self.pathout.createdir(self.parametres['pathout'])
            self.parametres['corpus'] = self.corpus.parametres['uuid']
            self.parametres['uuid'] = str(uuid4())
            self.parametres['name'] = os.path.split(self.parametres['pathout'])[1]
            self.parametres['type'] = parametres['type']
            self.parametres['encoding'] = self.ira.syscoding
            self.t1 = time()
            self.corpus.make_lems(lem = self.parametres['lem'])
            corpus.parse_active(gramact, gramsup)
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
                     dlg.Destroy()
                     OpenAnalyse(self.parent, self.parametres['ira'])
                     self.ira.tree.AddAnalyse(self.parametres)
                     self.val = 5100
            else :
                 self.val = False
                 if dlg :
                     dlg.Destroy()
        else :
            if dlg :
                dlg.Destroy()
            self.val = False

    def doanalyse(self) :
        pass

    def lemparam(self) :
        if self.dlg :
            dial = StatDialog(self, self.parent)
            dial.CenterOnParent()
            val = dial.ShowModal()
            if val == 5100 :
                if dial.radio_lem.GetSelection() == 0 :
                    lem = 1
                else :
                    lem = 0            
                self.parametres['lem'] = lem
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

    def doR(self, Rscript, wait = False, dlg = None, message = '') :
        log.info('R code...')
        pid = exec_rcode(self.ira.RPath, Rscript, wait = wait)
        while pid.poll() is None :
            if dlg is not None :
                self.dlg.Pulse(message)
                sleep(0.2)
            else :
                sleep(0.2)
        return check_Rresult(self.ira, pid)



class Alceste(AnalyseText) :
    def doanalyse(self) :
        self.parametres['type'] = 'alceste'
        self.pathout.basefiles(ChdTxtPathOut)
        self.actives, lim = self.corpus.make_actives_nb(self.parametres['max_actives'], 1)
        self.parametres['eff_min_forme'] = lim
        self.parametres['nbactives'] = len(self.actives)
        if self.parametres['classif_mode'] == 0 :
            lenuc1, lenuc2 = self.corpus.make_and_write_sparse_matrix_from_uc(self.actives, self.parametres['tailleuc1'], self.parametres['tailleuc2'], self.pathout['TableUc1'], self.pathout['TableUc2'], self.pathout['listeuce1'], self.pathout['listeuce2'])
            self.parametres['lenuc1'] = lenuc1
            self.parametres['lenuc2'] = lenuc2
        elif self.parametres['classif_mode'] == 1 :
            self.corpus.make_and_write_sparse_matrix_from_uces(self.actives, self.pathout['TableUc1'], self.pathout['listeuce1'])
        elif self.parametres['classif_mode'] == 2 :
            self.corpus.make_and_write_sparse_matrix_from_uci(self.actives, self.pathout['TableUc1'], self.pathout['listeuce1'])
        Rscript = self.printRscript()
        self.doR(Rscript, dlg = self.dlg, message = 'CHD...')
        self.corpus.make_ucecl_from_R(self.pathout['uce'])
        self.corpus.make_and_write_profile(self.actives, self.corpus.lc, self.pathout['Contout'])
        self.sup, lim = self.corpus.make_actives_nb(self.parametres['max_actives'], 2)
        self.corpus.make_and_write_profile(self.sup, self.corpus.lc, self.pathout['ContSupOut'])
        self.corpus.make_and_write_profile_et(self.corpus.lc, self.pathout['ContEtOut'])
        self.clnb = len(self.corpus.lc)
        self.parametres['clnb'] = self.clnb
        Rscript = self.printRscript2()
        self.doR(Rscript, dlg = self.dlg, message = 'profils et A.F.C. ...')
        self.time = time() - self.t1
        minutes, seconds = divmod(self.time, 60)
        hours, minutes = divmod(minutes, 60)            
        self.parametres['time'] = '%.0fh %.0fm %.0fs' % (hours, minutes, seconds)
        self.print_graph_files()

    def preferences(self) :
        parametres = DoConf(self.parent.ConfigPath['alceste']).getoptions('ALCESTE')
        parametres['corpus'] = self.corpus
        parametres['pathout'] = self.pathout
        self.dial = OptionAlc(self.parent, parametres)
        self.dial.CenterOnParent()
        self.dialok = self.dial.ShowModal()
        if self.dialok == 5100 :
            if self.dial.radio_1.GetSelection() == 0 :
                lem = 1
            else :
                lem = 0
            parametres['lem'] = lem
            parametres['classif_mode'] = self.dial.radio_box_2.GetSelection()
            parametres['tailleuc1'] = self.dial.spin_ctrl_1.GetValue()
            parametres['tailleuc2'] = self.dial.spin_ctrl_2.GetValue()
            parametres['mincl'] = self.dial.spin_ctrl_4.GetValue()
            parametres['minforme'] = self.dial.spin_ctrl_5.GetValue()
            parametres['nbcl_p1'] = self.dial.spin_nbcl.GetValue()
            parametres['max_actives'] = self.dial.spin_max_actives.GetValue()
            parametres['corpus'] = ''
            parametres['pathout'] = self.pathout.dirout
            DoConf(self.parent.ConfigPath['alceste']).makeoptions(['ALCESTE'], [parametres])
            self.dial.Destroy()
            return parametres
        else :
            self.dial.Destroy()
            return None

    def printRscript(self) :
        RchdTxt(self.pathout, self.parent.RscriptsPath, self.parametres['mincl'], self.parametres['classif_mode'], nbt = self.parametres['nbcl_p1'] - 1, libsvdc = self.parent.pref.getboolean('iramuteq','libsvdc'), libsvdc_path = self.parent.pref.get('iramuteq','libsvdc_path'), R_max_mem = False)
        return self.pathout['Rchdtxt']

    def printRscript2(self) :
        AlcesteTxtProf(self.pathout, self.parent.RscriptsPath, self.clnb, 0.9)
        return self.pathout['RTxtProfGraph']

    def print_graph_files(self) :
        mess_afc = u"La position des points n'est peut être pas exacte"
        afc_graph_list = [[os.path.basename(self.pathout['AFC2DL_OUT']), u'Variables actives - coordonnées - 30 points par classes - facteurs 1 / 2 - %s' % mess_afc],
                      [os.path.basename(self.pathout['AFC2DSL_OUT']), u'variables supplémentaires - coordonnées - 30 points par classes - facteurs 1 / 2 - %s' % mess_afc],
                      [os.path.basename(self.pathout['AFC2DEL_OUT']), u'Variables illustratives - Coordonnées - 30 points par classes - facteur 1 / 2 - %s' % mess_afc],
                      [os.path.basename(self.pathout['AFC2DCL_OUT']), u'Classes - Coordonnées - facteur 1 / 2']]
        chd_graph_list = [[os.path.basename(self.pathout['dendro1']), u'dendrogramme à partir de chd1']]
        if self.parametres['classif_mode'] == 0 :
            chd_graph_list.append([os.path.basename(self.pathout['dendro2']), u'dendrogramme à partir de chd2'])
        chd_graph_list.append([os.path.basename(self.pathout['arbre1']), u'chd1'])
        if self.parametres['classif_mode'] == 0 :
            chd_graph_list.append([os.path.basename(self.pathout['arbre2']), u'chd2'])       
        print_liste(self.pathout['liste_graph_afc'],afc_graph_list)
        print_liste(self.pathout['liste_graph_chd'],chd_graph_list)
        PrintRapport(self, self.corpus, self.parametres)


keys = {'art_def' : 2,
        'pre' : 2,
        'adj_dem' : 2,
        'ono' : 2,
        'pro_per' : 2,
        'ver_sup' : 2,
        'adv' : 1,
        'ver' : 1,
        'adj_ind' : 2,
        'adj_pos' : 2,
        'aux' : 2,
        'adj_int' : 2,
        'pro_ind' : 2,
        'adj' : 1,
        'pro_dem' : 2,
        'nom' : 1,
        'art_ind' : 2,
        'pro_pos' : 2,
        'nom_sup' : 2,
        'adv_sup' : 2,
        'adj_sup' : 2,
        'adj_num' : 2,
        'pro_rel' : 2,
        'con' : 2,
        'num' : 2,
        'nr' : 1,
        'sw' : 2,
}

gramact = [k for k in keys if keys[k] == 1]
gramsup = [k for k in keys if keys[k] == 2]
