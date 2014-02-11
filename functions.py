#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012 Pierre Ratinaud
#License: GNU/GPL

import wx
import re
from ConfigParser import ConfigParser
from subprocess import Popen, call, PIPE
import thread
import os
import ast
import sys
import csv
import platform
import traceback
import codecs
import locale
import datetime
from copy import copy
from shutil import copyfile
import shelve
#from dialog import BugDialog
import logging

log = logging.getLogger('iramuteq')


indices_simi = [u'cooccurrence' ,'pourcentage de cooccurrence',u'Russel',u'Jaccard', 'Kulczynski1', 'Kulczynski2', 'Mountford', 'Fager', 'simple matching', 'Hamman', 'Faith', 'Tanimoto', 'Dice', 'Phi', 'Stiles', 'Michael', 'Mozley', 'Yule', 'Yule2', 'Ochiai', 'Simpson', 'Braun-Blanquet','Chi-squared', 'Phi-squared', 'Tschuprow', 'Cramer', 'Pearson', 'binomial']


class History :
    def __init__(self, filein, syscoding = 'utf8') :
        self.filein = filein
        self.syscoding = syscoding
        self.corpora = {}
        self.openedcorpus = {}
        self.orph = []
        self.analyses = {}
        self.history = []
        self.opened = {}
        self.read()

    def read(self) :
        d = shelve.open(self.filein)
        self.history = d.get('history', [])
        self.matrix = d.get('matrix', [])
        self.ordercorpus = dict([[corpus['uuid'], i] for i, corpus in enumerate(self.history)])
        self.corpus = dict([[corpus['uuid'], corpus] for corpus in self.history])
        self.analyses = dict([[analyse['uuid'], analyse] for corpus in self.history for analyse in corpus.get('analyses', [])])
        self.matrixanalyse = dict([[mat['uuid'], mat] for mat in self.matrix])
        d.close()

    def write(self) :
        d = shelve.open(self.filein)
        d['history'] = self.history
        d['matrix'] = self.matrix
        d.close()
    
    def add(self, analyse) :
        log.info('add to history %s' % analyse.get('corpus_name', 'pas un corpus'))
        tosave = {'uuid' : analyse['uuid'], 'ira': analyse['ira'], 'type' : analyse['type']}
        if analyse.get('corpus', False) :
            if analyse['uuid'] in self.analyses :
                return
            tosave['corpus'] = analyse['corpus']
            tosave['name'] = analyse['name']
            acorpus_uuid =  analyse['corpus']
            if acorpus_uuid in self.corpus :
                if 'analyses' in self.history[self.ordercorpus[acorpus_uuid]] :
                    self.history[self.ordercorpus[acorpus_uuid]]['analyses'].append(tosave)
                else :
                    self.history[self.ordercorpus[acorpus_uuid]]['analyses'] = [tosave]
            else :
                self.orph.append(tosave)
        else :
            tosave['corpus_name'] = analyse['corpus_name']
            self.history.append(tosave)
        self.write()
        self.read()

    def addMatrix(self, analyse) :
        tosave = {'uuid' : analyse['uuid'], 'ira': analyse['ira'], 'type' : analyse['type']}
        tosave['name'] = analyse['name']
        self.matrix.append(tosave)
        self.write()
        self.read()

    def addmultiple(self, analyses) :
        log.info('add multiple')
        for analyse in analyses :
            tosave = {'uuid' : analyse['uuid'], 'ira': analyse['ira'], 'type' : analyse['type']}
            corpus = analyse['corpus']
            tosave['corpus'] = corpus
            tosave['name'] = analyse['name']
            if corpus in self.corpus :
                if 'analyses' in self.history[self.ordercorpus[corpus]] :
                    self.history[self.ordercorpus[corpus]]['analyses'].append(tosave)
                else :
                    self.history[self.ordercorpus[corpus]]['analyses'] = [tosave]
        self.write()
        self.read()

    def delete(self, analyse, corpus = False) :
        log.info('delete %s' % analyse.get('name', 'noname'))
        if corpus :
            self.history.pop(self.ordercorpus[analyse['uuid']])
            if analyse['uuid'] in self.openedcorpus :
                del self.openedcorpus[analyse['uuid']]
        elif analyse['uuid'] in self.analyses :
            todel = [i for i, ana in enumerate(self.corpus[analyse['corpus']]['analyses']) if ana['uuid'] == analyse['uuid']][0]
            self.history[self.ordercorpus[analyse['corpus']]]['analyses'].pop(todel)
        elif analyse['uuid'] in self.matrixanalyse :
            self.matrix = [mat for mat in self.matrix if mat['uuid'] != analyse['uuid']]
        self.write()
        self.read()

    def addtab(self, analyse) :
        self.opened[analyse['uuid']] = analyse

    def rmtab(self, analyse) :
        del self.opened[analyse['uuid']]

    def clean(self) :
        corpustodel = [corpus for corpus in self.history if not os.path.exists(corpus['ira'])]
        print corpustodel
        for corpus in corpustodel :
            print 'cleaning :', corpus['corpus_name']
            self.delete(corpus, corpus = True)
    
    def __str__(self) :
        return str(self.history)

class DoConf :
    def __init__(self, configfile=None, diff = None, parametres = None) :
        self.configfile = configfile
        self.conf = ConfigParser()
        if configfile is not None :
            self.conf.readfp(codecs.open(configfile, 'r', 'utf8'))
        self.parametres = {}
        if parametres is not None :
            self.doparametres(parametres)

    def doparametres(self, parametres) :
        return parametres

    def getsections(self) :
        return self.conf.sections()

    def getoptions(self, section = None, diff = None):
        parametres = {}
        if section is None :
            section = self.conf.sections()[0]
        for option in self.conf.options(section) :
            if self.conf.get(section, option).isdigit() :
                parametres[option] = int(self.conf.get(section, option))
            elif self.conf.get(section, option) == 'False' :
                parametres[option] = False
            elif self.conf.get(section, option) == 'True' :
                parametres[option] = True
            elif self.conf.get(section, option).startswith('(') and self.conf.get(section, option).endswith(')') :
                parametres[option] = ast.literal_eval(self.conf.get(section, option))
            elif self.conf.get(section, option).startswith('[') and self.conf.get(section, option).endswith(']') :
                parametres[option] = ast.literal_eval(self.conf.get(section, option))
            else :
                parametres[option] = self.conf.get(section, option)
        if 'type' not in parametres :
            parametres['type'] = section
        return parametres
            
    def makeoptions(self, sections, parametres, outfile = None) :
        txt = ''
        for i, section in enumerate(sections) :
            txt += '[%s]\n' % section
            if not self.conf.has_section(section) :
                self.conf.add_section(section)
            for option in parametres[i] :
                if isinstance(parametres[i][option], int) :
                    self.conf.set(section, option, `parametres[i][option]`)
                    txt += '%s = %i\n' % (option, parametres[i][option])
                elif isinstance(parametres[i][option], basestring) :
                    self.conf.set(section, option, parametres[i][option].encode('utf8'))
                    txt += '%s = %s\n' % (option, parametres[i][option])
                elif isinstance(parametres[i][option], wx.Colour) :
                    self.conf.set(section, option, str(parametres[i][option]))
                    txt += '%s = %s\n' % (option, str(parametres[i][option]))
                elif option == 'analyses' :
                    pass
                else :
                    self.conf.set(section, option, `parametres[i][option]`)
                    txt += '%s = %s\n' % (option, `parametres[i][option]`)
        if outfile is None :
            outfile = self.configfile
        with codecs.open(outfile, 'w', 'utf8') as f :
            f.write(txt)
            #self.conf.write(f)

    def totext(self, parametres) :
        #txt = ['Corpus']
        txt = []
        for val in parametres :
            if isinstance(parametres[val], int) :
                txt.append(' \t\t: '.join([val, `parametres[val]`]))
            elif isinstance(parametres[val], basestring) :
                txt.append(' \t\t: '.join([val, parametres[val]]))
            elif val in ['listet', 'stars'] :
                pass
            else :
                txt.append(' \t\t: '.join([val, `parametres[val]`]))
        return '\n'.join(txt)


def write_tab(tab, fileout) :
        writer = csv.writer(open(fileout, 'wb'), delimiter=';', quoting = csv.QUOTE_NONNUMERIC)
        writer.writerows(tab)

class BugDialog(wx.Dialog):
    def __init__(self, *args, **kwds):
        # begin wxGlade: MyDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        kwds["size"] = wx.Size(500, 200)
        wx.Dialog.__init__(self, *args, **kwds)
        self.SetTitle(kwds['title'])
        self.text_ctrl_1 = wx.TextCtrl(self, -1, "", style=wx.TE_MULTILINE)
        self.text_ctrl_1.SetBackgroundColour('#DDE8EB')
        self.button_1 = wx.Button(self, wx.ID_OK, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MyDialog.__set_properties
        self.SetMinSize(wx.Size(500, 200))
        self.text_ctrl_1.SetMinSize(wx.Size(500, 200))
        
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyDialog.__do_layout
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add(self.text_ctrl_1, 1, wx.EXPAND, 0)
        sizer_1.Add(self.button_1, 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        self.Layout()


def CreateIraFile(DictPathOut, clusternb, corpname='corpus_name', section = 'analyse'):
    AnalyseConf = ConfigParser()
    AnalyseConf.read(DictPathOut['ira'])
    AnalyseConf.add_section(section)
    date = datetime.datetime.now().ctime()
    AnalyseConf.set(section, 'date', str(date))
    AnalyseConf.set(section, 'clusternb', clusternb)
    AnalyseConf.set(section, 'corpus_name', corpname)

    fileout = open(DictPathOut['ira'], 'w')
    AnalyseConf.write(fileout)
    fileout.close()

def sortedby(list, direct, *indices):

    """
        sortedby: sort a list of lists (e.g. a table) by one or more indices
                  (columns of the table) and return the sorted list

        e.g.
         for list = [[2,3],[1,2],[3,1]]:
         sortedby(list,1) will return [[3, 1], [1, 2], [2, 3]],
         sortedby(list,0) will return [[1, 2], [2, 3], [3, 1]]
    """

    nlist = map(lambda x, indices=indices: 
                 map(lambda i, x=x: x[i], indices) + [x],
                 list)
    if direct == 1:
        nlist.sort()
    elif direct == 2:
        nlist.sort(reverse=True)
    return map(lambda l: l[-1], nlist)

def add_type(line, dictlem):
    if line[4] in dictlem:
        line.append(dictlem[line[4]])
    else :
        line.append('')
    return line

def treat_line_alceste(i, line) :
    if line[0] == '*' or line[0] == '*****' :
        return line + ['']
    if line[5] == 'NA':
        print 'NA', line[5]
        pass
    elif float(line[5].replace(',', '.')) < 0.0001:
        line[5] = '< 0,0001'
    elif float(line[5].replace(',', '.')) > 0.05:
        line[5] = 'NS (%s)' % str(float(line[5].replace(',', '.')))[0:7]
    else:
        line[5] = str(float(line[5].replace(',', '.')))[0:7]
    return [i, int(line[0]), int(line[1]), float(line[2]), float(line[3]), line[6], line[4], line[5]]

def ReadProfileAsDico(File, Alceste=False, encoding = sys.getdefaultencoding()):
    #print 'lecture des profils : ReadProfileAsDico'
    #if Alceste :
    #    print 'lecture du dictionnaire de type'
    #    dictlem = {}
    #    for line in parent.corpus.lem_type_list :
    #        dictlem[line[0]] = line[1]
    dictlem = {}
    print 'lecture des profiles'
    #encoding = sys.getdefaultencoding()
    FileReader = codecs.open(File, 'r', encoding)
    Filecontent = FileReader.readlines()
    FileReader.close()
    DictProfile = {}
    count = 0
    #rows = [row.replace('\n', '').replace("'", '').replace('\"', '').replace(',', '.').replace('\r','').split(';') for row in Filecontent]
    rows = [row.replace('\n', '').replace("'", '').replace('\"', '').replace('\r','').split(';') for row in Filecontent]
    rows.pop(0)
    ClusterNb = rows[0][2]
    rows.pop(0)
    clusters = [row[2] for row in rows if row[0] == u'**']
    valclusters = [row[1:4] for row in rows if row[0] == u'****']
    lp = [i for i, line in enumerate(rows) if line[0] == u'****']
    prof = [rows[lp[i] + 1:lp[i+1] - 1] for i in range(0, len(lp)-1)] + [rows[lp[-1] + 1:len(rows)]] 
    if Alceste :
        prof = [[add_type(row, dictlem) for row in pr] for pr in prof]
        prof = [[treat_line_alceste(i,line) for i, line in enumerate(pr)] for pr in prof] 
    else :
        prof = [[line + [''] for line in pr] for pr in prof]
        prof = [[treat_line_alceste(i,line) for i, line in enumerate(pr)] for pr in prof]
    for i, cluster in enumerate(clusters):
        DictProfile[cluster] = [valclusters[i]] + prof[i]
    return DictProfile

def GetTxtProfile(dictprofile, cluster_size) :
    proflist = []
    for classe in range(0, len(dictprofile)) :
        prof = dictprofile[str(classe + 1)]
        clinfo = cluster_size[classe]
        proflist.append('\n'.join([' '.join(['classe %i' % (classe + 1), '-', '%s uce sur %s - %s%%' % (clinfo[0], clinfo[1], clinfo[2])]), '\n'.join(['%5s|%5s|%6s|%6s|%8s|%8s|%20s\t%10s' % tuple([str(val) for val in line]) for line in prof if len(line)==8])]))
    return '\n\n'.join(proflist)

def formatExceptionInfo(maxTBlevel=5):
         cla, exc, trbk = sys.exc_info()
         try :
            excName = cla.__name__
         except :
            excName = 'None'
         try:
             excArgs = exc.args[0]
         except :
             excArgs = "<no args>"
         excTb = traceback.format_tb(trbk, maxTBlevel)
         return (excName, excArgs, excTb)


#fonction des etudiants de l'iut
def decoupercharact(chaine, longueur, longueurOptimale, separateurs = None) :
    """
        on part du dernier caractère, et on recule jusqu'au début de la chaîne.
        Si on trouve un '$', c'est fini.
        Sinon, on cherche le meilleur candidat. C'est-à-dire le rapport poids/distance le plus important.
    """
    separateurs = [[u'.', 60.0], [u'?', 60.0], [u'!', 60.0], [u'£$£', 60], [u':', 50.0], [u';', 40.0], [u',', 10.0], [u' ', 0.1]]
    trouve = False                 # si on a trouvé un bon séparateur
    iDecoupe = 0                # indice du caractere ou il faut decouper
    
    # on découpe la chaine pour avoir au maximum 240 caractères
    longueur = min(longueur, len(chaine) - 1)
    chaineTravail = chaine[:longueur + 1]
    nbCar = longueur
    meilleur = ['', 0, 0]        # type, poids et position du meilleur separateur
    
    # on vérifie si on ne trouve pas un '$'
    indice = chaineTravail.find(u'$')
    if indice > -1:
        trouve = True
        iDecoupe = indice

    # si on ne trouve rien, on cherche le meilleur séparateur
    if not trouve:
        while nbCar >= 0:
            caractere = chaineTravail[nbCar]
            distance = abs(longueurOptimale - nbCar) + 1
            meilleureDistance = abs(longueurOptimale - meilleur[2]) + 1

            # on vérifie si le caractére courant est une marque de ponctuation
            for s in separateurs:
                if caractere == s[0]:
                    # si c'est une ponctuation 
                    
                    if s[1] / distance > float(meilleur[1]) / meilleureDistance:
                        # print nbCar, s[0]
                        meilleur[0] = s[0]
                        meilleur[1] = s[1]
                        meilleur[2] = nbCar
                        trouve = True
                        iDecoupe = nbCar
                        
                    # et on termine la recherche
                    break

            # on passe au caractère précédant
            nbCar = nbCar - 1
    
    # si on a trouvé
    if trouve:
        fin = chaine[iDecoupe + 1:]
        retour = chaineTravail[:iDecoupe]
        return len(retour) > 0, retour.split(), fin
    # si on a rien trouvé
    return False, chaine.split(), ''


exceptions = {'paragrapheOT' : u"Un problème de formatage (présence d'un marqueur de paragraphe (-*) en dehors d'un texte) est survenu à la ligne ",
              'EmptyText' : u"Texte vide (probablement un problème de formatage du corpus). Le problème est apparu à la ligne ",
              'CorpusEncoding' : u"Problème d'encodage.",
              'TextBeforeTextMark' : u"Problème de formatage : du texte avant le premier marqueur de texte (****). Le problème est survenu à la ligne ",
}

def BugReport(parent, error = None):
    for ch in parent.GetChildren():
        if "<class 'wx._windows.ProgressDialog'>" == str(type(ch)):
            ch.Destroy()   
    excName, exc, excTb = formatExceptionInfo()
    if excName == 'Exception' :
        print exc
        if len(exc.split()) == 2 :
            mss, linenb = exc.split()
            if mss in exceptions :
                txt = exceptions[mss] + linenb
            else :
                txt = exc
        else :
            if exc in exceptions :
                txt = exceptions[exc]
            else :
                txt = exc
        title = "Information"
    else :
        txt = u'            !== BUG ==!       \n'
        txt += u'*************************************\n'
        txt += '\n'.join(excTb).replace('    ', ' ')
        txt += excName + '\n'
        txt += exc
        title = "Bug"

    dial = BugDialog(parent, **{'title' : title})
    if 'Rerror' in dir(parent) :
        txt += parent.Rerror
        parent.Rerror = ''
    log.info(txt)
    dial.text_ctrl_1.write(txt)
    dial.CenterOnParent()
    dial.ShowModal()
    dial.Destroy()
    
def PlaySound(parent):
    if parent.pref.getboolean('iramuteq', 'sound') :
        try:
            if "gtk2" in wx.PlatformInfo:
                error = Popen(['aplay','-q',os.path.join(parent.AppliPath,'son_fin.wav')])
            else :    
                sound = wx.Sound(os.path.join(parent.AppliPath, 'son_fin.wav'))
                sound.Play(wx.SOUND_SYNC)
        except :
            print 'pas de son'

def ReadDicoAsDico(dicopath):
    with codecs.open(dicopath, 'r', 'UTF8') as f:
        content = f.readlines()
    dico = {}
    for line in content :
        if line[0] != u'':
            line = line.rstrip('\n\r').replace(u'\n', '').replace('"', '').split('\t')
            dico[line[0]] = line[1:]
    return dico

def ReadLexique(parent, lang = 'french', filein = None):
    if lang != 'other' :
        if filein is None :
            parent.lexique = ReadDicoAsDico(parent.DictPath.get(lang, 'french'))
        else :
            parent.lexique = ReadDicoAsDico(filein)
    else :
        parent.lexique = {}

def ReadList(filein, encoding = sys.getdefaultencoding()):
    #file = open(filein)
    file = codecs.open(filein, 'r', encoding)
    content = file.readlines()
    file.close()
    first = content.pop(0)
    first = first.replace('\n', '').replace('\r','').replace('\"', '').split(';')
    dict = {}
    i = 0
    for line in content:
        line = line.replace('\n', '').replace('\r','').replace('\"', '').replace(',', '.')
        line = line.split(';')
        nline = [line[0]]
        for val in line[1:]:
            if val == u'NA' :
                don = ''
            else: 
                try:
                    don = int(val)
                except:
                    don = float('%.5f' % float(val))
            nline.append(don)
        dict[i] = nline
        i += 1
    return dict, first

def exec_RCMD(rpath, command) :
    log.info('R CMD INSTALL %s' % command)
    rpath = rpath.replace('\\','\\\\')
    error = call(["%s" % rpath, 'CMD', 'INSTALL', "%s" % command])
    return error

def exec_rcode(rpath, rcode, wait = True, graph = False):
    log.info("R Script : %s" % rcode)
    needX11 = False
    if sys.platform == 'darwin' :
        try :
            macversion = platform.mac_ver()[0].split('.')
            if int(macversion[1]) < 5 :
                needX11 = True
            else :
                needX11 = False
        except :
            needX11 = False

    rpath = rpath.replace('\\','\\\\')
    env = os.environ.copy()
    if sys.platform == 'darwin' and 'LC_ALL' not in env:
        env['LC_ALL'] = 'en_US.UTF-8'
    if not graph :
        if wait :
            if sys.platform == 'win32':
                error = call(["%s" % rpath, "--vanilla","--slave","-f", "%s" % rcode])
            else :
                error = call([rpath, '--slave', "--vanilla", "-f %s" % rcode, "--encoding=UTF-8"], env = env)
            return error
        else :
            if sys.platform == 'win32':
                pid = Popen(["%s" % rpath, '--vanilla','--slave','-f', "%s" % rcode])
            else :
                pid = Popen([rpath, '--slave', "--vanilla", "-f %s" % rcode, "--encoding=UTF-8"], stderr = PIPE, env = env)
            return pid
    else :
        if wait :
            if sys.platform == 'win32':
                error = call(["%s" % rpath, '--vanilla','--slave','-f', "%s" % rcode])
            elif sys.platform == 'darwin' and needX11:
                os.environ['DISPLAY'] = ':0.0'
                error = call([rpath, '--vanilla','--slave',"-f %s" % rcode, "--encoding=UTF-8"], env = env)
            else :
                error = call([rpath, '--vanilla','--slave',"-f %s" % rcode, "--encoding=UTF-8"], env = env)
            return error
        else :
            if sys.platform == 'win32':
                pid = Popen(["%s" % rpath, '--vanilla','--slave','-f', "%s" % rcode])
            elif sys.platform == 'darwin' and needX11:
                os.environ['DISPLAY'] = ':0.0'
                pid = Popen([rpath, '--vanilla','--slave',"-f %s" % rcode, "--encoding=UTF-8"], stderr = PIPE, env = env)
            else :
                pid = Popen([rpath, '--vanilla','--slave',"-f %s" % rcode, "--encoding=UTF-8"], stderr = PIPE, env = env)
            return pid

def check_Rresult(parent, pid) :
    if isinstance(pid, Popen) :
        if pid.returncode != 0 :
            error = pid.communicate()
            error = [str(error[0]), error[1]]
            if error[1] is None :
                error[1] = 'None'
            parent.Rerror = '\n'.join([str(pid.returncode), '\n'.join(error)])
            try :
                raise Exception('\n'.join([u'Erreur R', '\n'.join(error[1:])]))
            except :
                BugReport(parent)
            return False
        else :
            return True
    else :
        if pid != 0 :
            try :
                raise Exception(u'Erreur R')
            except :
                BugReport(parent)
            return False
        else :
            return True

def print_liste(filename,liste):
    with open(filename,'w') as f :
        for graph in liste :
            f.write(';'.join(graph)+'\n')

def read_list_file(filename, encoding = sys.getdefaultencoding()):
    with codecs.open(filename,'rU', encoding) as f :
        content=f.readlines()
        ncontent=[line.replace('\n','').split(';') for line in content if line.strip() != '']
    return ncontent
        
class MessageImage(wx.Frame):
    def __init__(self, parent,title, size):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = title, pos = wx.DefaultPosition, size = size, style = wx.DEFAULT_FRAME_STYLE )
        self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
        self.imageFile = False
        self.imagename = u"chi_classe.png"
        self.HtmlPage = wx.html.HtmlWindow(self, -1)
        self.HtmlPage.SetMinSize(size)
        if "gtk2" in wx.PlatformInfo:
            self.HtmlPage.SetStandardFonts()
        self.HtmlPage.SetFonts('Courier', 'Courier')
        
        self.button_1 = wx.Button(self, wx.ID_CANCEL)
        self.button_2 = wx.Button(self, wx.ID_SAVE)
        self.Bind(wx.EVT_BUTTON, self.OnCloseMe, self.button_1)
        self.Bind(wx.EVT_BUTTON, self.OnSaveImage, self.button_2)
        self.do_layout()

    def do_layout(self):
        self.sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_1.Add(self.HtmlPage, 2, wx.EXPAND, 0)

        self.m_sdbSizer1 = wx.StdDialogButtonSizer()
        self.m_sdbSizer1.AddButton(  self.button_2 )
        self.m_sdbSizer1.AddButton(  self.button_1 )
        self.m_sdbSizer1.Realize()
        self.sizer_1.Add(self.m_sdbSizer1, 0, wx.EXPAND, 5)
        self.SetSizer(self.sizer_1)
        self.Layout()
        self.sizer_1.Fit( self )

    def addsaveimage(self, imageFile) :
        self.imageFile = imageFile
        
    def OnCloseMe(self, event):
        self.Destroy()

    def OnSaveImage(self, event) :
        dlg = wx.FileDialog(
            self, message="Enregistrer sous...", defaultDir=os.getcwd(),
            defaultFile= self.imagename, wildcard="png|*.png", style=wx.SAVE | wx.OVERWRITE_PROMPT
            )
        dlg.SetFilterIndex(2)
        dlg.CenterOnParent()
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            copyfile(self.imageFile, path)
            

def progressbar(self, maxi) :
    if 'parent' in dir(self) :
        parent = self.parent
    else :
        parent = self
    return wx.ProgressDialog("Traitements",
                             "Veuillez patienter...",
                             maximum=maxi,
                             parent=parent,
                             style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT
                             )


def treat_var_mod(variables) :
    var_mod = {}
    variables = list(set(variables))
    varmod = [variable.split('_') for variable in variables]
    vars = list(set([var[0] for var in varmod if len(var) >=2]))
    for var in vars :
        mods = ['_'.join(v) for v in varmod if v[0] == var]
        var_mod[var] = mods
    
#     for variable in variables :
#         if u'_' in variable :
#             forme = variable.split(u'_')
#             var = forme[0]
#             mod = forme[1]
#             if not var in var_mod :
#                 var_mod[var] = [variable]
#             else :
#                 if not mod in var_mod[var] :
#                     var_mod[var].append(variable)
    return var_mod

def doconcorde(corpus, uces, mots, uci = False) :
    if not uci :
        ucestxt1 = [row for row in corpus.getconcorde(uces)]
    else :
        ucestxt1 = [row for row in corpus.getuciconcorde(uces)]
    ucestxt1 = dict(ucestxt1)
    ucestxt = []
    ucis_txt = []
    listmot = [corpus.getlems()[lem].formes for lem in mots]
    listmot = [corpus.getforme(fid).forme for lem in listmot for fid in lem]
    mothtml = ['<font color=red><b>'+mot+'</b></font>' for mot in listmot]
    dmots = dict(zip(listmot, mothtml))
    for uce in uces :
        ucetxt = ucestxt1[uce].split()
        ucetxt = ' '.join([dmots.get(mot, mot) for mot in ucetxt])
        if not uci :
            ucis_txt.append('<p><b>' + ' '.join(corpus.ucis[corpus.getucefromid(uce).uci].etoiles) + '</b></p>')
        else :
            ucis_txt.append('<p><b>' + ' '.join(corpus.ucis[uce].etoiles) + '</b></p>')
        ucestxt.append(ucetxt)        
    return ucis_txt, ucestxt
 

def getallstcarac(corpus, analyse) :
   pathout = PathOut(analyse['ira'])
   profils =  ReadProfileAsDico(pathout['PROFILE_OUT'], Alceste, self.encoding)
   print profils
