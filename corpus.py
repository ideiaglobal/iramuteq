# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2010, Pierre Ratinaud
#Lisense: GNU/GPL

import codecs
import shelve
import csv
import re
import os
import sys
from colors import colors
from functions import decoupercharact, ReadDicoAsDico, sortedby
from ttparser import get_ucis_from_tt
#from ConfigParser import RawConfigParser
import json
from time import time
#import nltk

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

class Corpus :
    def __init__(self, parent) :
        self.parent = parent
        self.parametre = {'syscoding': sys.getdefaultencoding()}
        self.content = None
        self.ucis = None
        self.formes = {}
        self.lems = {}
        self.ucenb = None
        self.etoiles = None
        self.etintxt = {}
        self.ucis_paras_uces = None
        self.lc = None
        self.lc0 = None
        self.actives = None
        self.supp = None
        #self.supplementaires = []
        self.lenuc1 = None
        self.lenuc2 = None
        self.lexique = None

    def open_corpus(self) :
        with codecs.open(self.parametre['filename'], "r", self.parametre['encodage']) as f :
            self.content = f.read()
    
    def make_big(self) :
        import sqlite3
        ucifile = os.path.join(os.path.dirname(self.parametre['filename']), 'ucis.txt')
        uci = open(ucifile, 'w')
        #db = os.path.join(os.path.dirname(self.parametre['filename']), 'corpus.db')
        #conn = sqlite3.connect(db)
        #c = conn.cursor()
        #conn.text_factory = str
        #c = conn.cursor()
        #c.execute('''CREATE TABLE corpus (id integer, varet TEXT)''')
        #c = conn.cursor()
        ucinb = 0
        self.ucis = []
        txt = []
        with codecs.open(self.parametre['filename'], "r", self.parametre['encodage']) as open_corpus :
            for line in open_corpus :
                if line.startswith(u'****') :
                    print ucinb
                    uci.write(line.replace('/n', ' '))
                    #self.ucis.append([line.rstrip(), `ucinb`])
                    if ucinb != 0 :
                        for word in txt :
                            if word not in [' ','.', u'£', ';', '?', '!', ',', ':',''] :
                                id = len(self.formes)
                                self.feed_dict_big(word, ucinb)
                    txt = []
                    #c = conn.cursor()
                    #c.execute('INSERT INTO uci values (?,?)', (ucinb, line.rstrip()))
                    #conn.commit()
                    #print ucinb
                    ucinb += 1
                else :
                    line = line.lower().replace('-', ' ').replace(u'\'',' ').replace(u'’',' ').replace('...',u' £ ').replace('?',' ? ').replace('.',' . ').replace('!', ' ! ').replace(',',' , ').replace(';', ' ; ').replace(':',' : ').rstrip().split()
                    txt += line
        uci.close()
        print len(self.formes)
        print sum([self.formes[forme][0] for forme in self.formes])
        formes_out2 = os.path.join(os.path.dirname(self.parametre['filename']), 'formes_formes.csv')
        formes_uces = os.path.join(os.path.dirname(self.parametre['filename']), 'formes_uces.csv')
        with open(formes_out2, 'w') as f :
            f.write('\n'.join([';'.join([forme, `self.formes[forme][0]`, self.formes[forme][2]]) for forme in self.formes]))
        with open(formes_uces, 'w') as f:
            f.write('\n'.join([' '.join([' '.join([`uce`, `self.formes[forme][1][uce]`]) for uce in self.formes[forme][1]]) for forme in self.formes]))
        #uciout =  os.path.join(os.path.dirname(self.parametre['filename']), 'uciout.csv')
        #with open(uciout,'w') as f :
        #    f.write('\n'.join(['\t'.join(line) for line in self.ucis]))




    def read_corpus_out(self, corpus_out) :
        #print 'test encodage'
        #self.parametre['syscoding'] = 'cp1252'
        with codecs.open(corpus_out ,'r', self.parametre['syscoding']) as f:
            content = f.read()
            if sys.platform == 'win32' :
                sep = '\r\n\r\n'
            else :
                sep = '\n\n'
            self.ucis_paras_uces = [[[uce.split() for uce in para.splitlines()] for para in uci.split(u'$$$')] for uci in content.split(sep)]
            #print self.ucis_paras_uces

    def read_formes_out(self, forme_out) :
        print 'read formes'
        print 'test encodage'
        #t1 = time()
        if os.path.exists(forme_out) :
            with codecs.open(forme_out, 'r', self.parametre['syscoding']) as f :
                content = f.read()
                cc = [forme.split(u'$') for forme in content.splitlines()]
                self.formes = dict([[forme[0], [int(forme[1]), dict([[eval(uce.split(':')[0]), int(uce.split(':')[1])] for uce in forme[2].split(';')]), forme[3], int(forme[4])]] for forme in cc])
        else :
            formes_out2 = os.path.join(os.path.dirname(forme_out), 'formes_formes.csv')
            formes_uces = os.path.join(os.path.dirname(forme_out), 'formes_uces.csv')
            with codecs.open(formes_uces, 'r', self.parametre['syscoding']) as f:
                uces = f.read()
                uces = [list(chunks(line.split(),4)) for line in uces.splitlines()]
            with codecs.open(formes_out2, 'r', self.parametre['syscoding']) as f :
                self.formes = f.read()
                self.formes = [[line.split(';'), dict([[(int(uce[0]),int(uce[1]), int(uce[2])), int(uce[3])] for uce in uces[i]])] for i, line in enumerate(self.formes.splitlines())]
                self.formes = dict([[line[0][0], [int(line[0][1]), line[1], line[0][2], int(line[0][3])]] for line in self.formes])

    def read_corpus_from_shelves(self, db) :
        d = shelve.open(db)
        self.parametre = d['parametre']
        if not 'syscoding' in self.parametre :
            self.parametre['syscoding'] = sys.getdefaultencoding()
        self.lems = d['lems']
        if 'ucis_paras_uces' in d :
            self.ucis_paras_uces = d['ucis_paras_uces']
        else :
            corpus_out = os.path.join(os.path.dirname(db), 'corpus.txt')
            self.read_corpus_out(corpus_out)
        if 'formes' in d :
            self.formes = d['formes']
        else :
            formes_out =  os.path.join(os.path.dirname(db), 'formes.txt')
            self.read_formes_out(formes_out)
#        print 'deb sql'
#        import sqlite3
#        db_out = os.path.join(os.path.dirname(db), 'formes.db')
#        conn = sqlite3.connect(db_out)
#        c = conn.cursor()
#        c.execute('''SELECT * FROM formes''')
#        self.formes = dict([[forme[0], [int(forme[1]), dict([[eval(uce.split(':')[0]), int(uce.split(':')[1])] for uce in forme[2].split(';')]), forme[3], int(forme[4])]] for forme in c])
#        print 'fin sql'
        self.etoiles = d['etoiles']
        self.actives = d['actives']
        self.ucis = d['ucis']
        self.lc = d['lc']
        self.lc0 = d['lc0']
        d.close()


    def save_corpus(self, db) :
        d= shelve.open(db)
        d['parametre'] = self.parametre
        #d['formes'] = self.formes
        d['lems'] = self.lems
        #d['ucis_paras_uces'] = self.ucis_paras_uces
        d['etoiles'] = self.etoiles
        d['actives'] = self.actives
        d['ucis'] = self.ucis
        d['lc'] = self.lc
        d['lc0'] = self.lc0
        d.close()
        corpus_out = os.path.join(os.path.dirname(db), 'corpus.txt')
        with open(corpus_out, 'w') as f :
            f.write('\n\n'.join([u'$$$'.join(['\n'.join([' '.join(uce) for uce in para]) for para in uci]) for uci in self.ucis_paras_uces]))
        #t1 = time()
        formes_out2 = os.path.join(os.path.dirname(db), 'formes_formes.csv')
        formes_uces = os.path.join(os.path.dirname(db), 'formes_uces.csv')

        with open(formes_out2, 'w') as f :
            f.write('\n'.join([';'.join([forme, `self.formes[forme][0]`, self.formes[forme][2], `self.formes[forme][3]`]) for forme in self.formes]))
        with open(formes_uces, 'w') as f:
            f.write('\n'.join([' '.join([' '.join([`uce[0]`,`uce[1]`, `uce[2]`, `self.formes[forme][1][uce]`]) for uce in self.formes[forme][1]]) for forme in self.formes]))
        #print time() - t1
        #t1 = time()
        #toprint = json.dumps(self.formes)
        #with open(os.path.join(os.path.dirname(db), 'json.db'), 'w') as f:
        #    f.write(toprint)
        #print time() - t2

#        import sqlite3
#        db_out = os.path.join(os.path.dirname(db), 'formes.db')
#        conn = sqlite3.connect(db_out)
#        c = conn.cursor()
#        conn.text_factory = str
#        c = conn.cursor()
#        c.execute('''CREATE TABLE formes (formes TEXT, freq integer, uces TEXT, type TEXT, identifiant integer)''')
#        c = conn.cursor()
#        for formes in self.formes :
#            c.execute('INSERT INTO formes values (?,?,?,?,?)', (formes, self.formes[formes][0], ';'.join([':'.join([str(uce), str(self.formes[formes][1][uce])]) for uce in self.formes[formes][1]]), self.formes[formes][2], self.formes[forme][3]))
#        conn.commit()
#        print 'fin sql'

    def make_len_uce(self, nbtotoc):
        if self.parametre['nbforme_uce'] == None or self.parametre['nbforme_uce'] == 0 :
            #FIXME
            if len(self.ucis) == 1:
                self.parametre['eff_min_uce'] = 30
            elif 200000 <= nbtotoc < 400000:
                self.parametre['eff_min_uce'] = (0.0016 * float(nbtotoc) / float(len(self.ucis))) + 20
            elif nbtotoc < 200000:
                self.parametre['eff_min_uce'] = (0.0016 * float(nbtotoc) / float(len(self.ucis))) + 30
            else:
                self.parametre['eff_min_uce'] = (float(nbtotoc) / float(len(self.ucis))) / float(15)
        else :
            self.parametre['eff_min_uce'] = self.parametre['nbforme_uce']
    #        print 'ATTENTION ASSIGNATION DE LA TAILLE DES UCE'
    #        self.lenuce = 44 

            
    def quick_clean1(self) :
        print 'quick clean'
        self.content = self.content.lower()
        keep_caract = u"a-zA-Z0-9àÀâÂäÄáÁéÉèÈêÊëËìÌîÎïÏòÒôÔöÖùÙûÛüÜçÇß’ñ.:,;!?\n*'_-"
        list_keep = u"[^" + keep_caract + "]+"
#        print 'NETTOYAGE CABLE PLUS SUB'
        #print ('#########ATTENTION CHINOIS plus keep_caract#################')
        #list_keep = u"[;]+"
        self.content = re.sub(list_keep, ' ', self.content)
        #self.content = re.sub(list_keep, ' ', self.content)

        #self.content = self.content.replace(u'[’]+', '\'')
        self.content = re.sub(u'[’]+', '\'', self.content)
        self.content = re.sub(u'[\r\n]+', '\n', self.content)
        self.content = self.content.replace(u'-*',u'#*')
    
    def find_expression(self,expressions) :
        print 'find expression'
        for expression in expressions:
            if expression in self.content :
                print expression, expressions[expression][0]
                #self.content = self.content.replace(' '+expression+' ', ' '+expressions[expression][0]+' ')
                self.content = self.content.replace(expression, expressions[expression][0])
    
    def quick_clean2(self):
        print 'quick clean 2'
        self.content = self.content.replace('\'',' ')
        self.content = re.sub(u'[-]+', ' ', self.content)
        self.content = re.sub(u'[ ]+', ' ', self.content)
        self.content = self.content.splitlines()
    
    def make_ucis(self) :
        print 'make_ucis'
        self.ucis = [[self.content[i].strip().split(),i] for i in range(0,len(self.content)) if self.content[i].startswith(u'****')]
        return [a[1] for a in self.ucis]
    
    def find_uci_with_digit(self, line) :
        if line[0:4].isdigit() and u'*' in line :
            return True
        else :
            return False
    
    def make_ucis_with_digit(self) :
        self.ucis = [[self.content[i].replace('\n',' ').strip().split(),i] for i in range(0,len(self.content)) if self.find_uci_with_digit(self.content[i])]
        return [a[1] for a in self.ucis]
    
    def make_lines(self, ucinb) :
        print 'make_lines'
        return [[ucinb[i]+1,ucinb[i+1]] for i in range(0,len(ucinb)-1)] + [[ucinb[len(ucinb)-1] + 1,len(self.content)]]
    
    def make_ucis_words(self, lines):
        print 'make ucis_words'
        return [' '.join(self.content[l[0]:l[1]]).lower().replace(u'\'','\' ').replace(u'’','\' ').replace('...',u' £ ').replace('?',' ? ').replace('.',' . ').replace('!', ' ! ').replace(',',' , ').replace(';', ' ; ').replace(':',' : ').strip().split() for l in lines]
    
    def make_ucis_txt(self, lines):
        print 'make ucis_txt'
        return [' '.join(self.content[l[0]:l[1]]).lower().replace(u'\'','\' ').replace(u'’','\' ').replace('...',u' £ ').replace('?',' ? ').replace('.',' . ').replace('!', ' ! ').replace(',',' , ').replace(';', ' ; ').replace(':', ' : ').strip() for l in lines]
    
    def make_ucis_lines(self, lines) :
        print 'make ucis lines'
        return [self.content[l[0]:l[1]] for l in lines]
        
    def make_para_coords(self, ucis_lines):
        print 'make para coords'
        return [[[uci[i].split()[0], i] for i in range(0,len(uci)) if uci[i].startswith(u'#*')] for uci in ucis_lines]
    
    def make_ucis_paras_txt(self, para_coords, ucis_lines, ucis_txt) :
        print 'make_ucis_paras_txt'
        if para_coords != [[] for val in para_coords] :
            paranb = [[para[1] for para in uci] for uci in para_coords]
            paras = []
            #print 'len paranb', len(paranb)
            #print len(self.ucis)
            for i, uci in enumerate(paranb) :
                uciline = ucis_lines[i]
                #print uci
                #print i
                #print uciline
                #print uci[i]
                para = [[uci[i]+1, uci[i+1]] for i in range(0,len(uci)-1)]
                para.append([uci[len(uci)-1]+1, len(uciline) ])
                paras.append(para)
            self.parametre['para'] = True
            return [[' '.join(ucis_lines[nb][l[0]:l[1]]).lower().replace(u'\'','\' ').replace(u'’','\' ').replace('...',u' £ ').replace('?',' ? ').replace('.',' . ').replace('!', ' ! ').replace(',',' , ').replace(';', ' ; ').replace(':',' : ').strip() for l in paras[nb]] for nb in range(0,len(paras))]
        else :
            print '############pas de para####################'
            self.parametre['para'] = False
            return [[val] for val in ucis_txt]

    def make_ucis_paras_txt_phrases(self, para_coords, ucis_lines, ucis_txt) :
        print 'make_ucis_paras_txt'
        if para_coords != [[] for val in para_coords] :
            paranb = [[para[1] for para in uci] for uci in para_coords]
            paras = []
            for i, uci in enumerate(paranb) :
                uciline = ucis_lines[i]
                para = [[uci[i]+1, uci[i+1]] for i in range(0,len(uci)-1)]
                para.append([uci[len(uci)-1]+1, len(uciline) ])
                paras.append(para)
            self.parametre['para'] = True
            return [[' '.join(ucis_lines[nb][l[0]:l[1]]).lower().replace(u'\'','\' ').replace(u'’','\' ').strip() for l in paras[nb]] for nb in range(0,len(paras))]
        else :
            print '############pas de para####################'
            self.parametre['para'] = False
            return [[val] for val in ucis_txt]

    def make_ucis_paras_uces_sentences(self, ucis_paras_txt, make_uce = True) :
        print 'make_ucis_paras_sentences'
        ponctuation_espace =  [' ','.', u'£', ';', '?', '!', ',', ':','']
        tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
        self.ucis_paras_uces = []
        for i, uci in enumerate(ucis_paras_txt) :
            self.ucis_paras_uces.append([])
            for j, para in enumerate(uci) :    
                    sentences = tokenizer.tokenize(para)
                    sentences = [[val.strip() for val in sent.strip().replace('...',u'£').replace('?',' ? ').replace('.',' . ').replace('!', ' ! ').replace(',',' , ').replace(';', ' ; ').replace(':',' : ').split() if val.strip() not in ponctuation_espace] for sent in sentences]
                    self.ucis_paras_uces[i].append(sentences)

    def get_tot_occ_from_ucis_txt(self, ucis_txt):
        print 'get_occ'
        ponctuation_espace =  [' ','.', u'£', ';', '?', '!', ',', ':','']
        return sum([len([val for val in uci.split() if val.strip() not in ponctuation_espace]) for uci in ucis_txt])

    def decouper_para(self, txt, listeSeparateurs, ls) :
        i = 0
        meilleur = ['', 0, 0]
        if len(txt) <= self.parametre['eff_min_uce'] :
            return False, txt, []
        else :
            while i <= self.parametre['eff_min_uce'] :
                rapport = abs(self.parametre['eff_min_uce'] - i) + 1
                forme = txt[i]
                if forme in ls and i != 0 :
                    poids = float(listeSeparateurs[ls.index(forme)][1]) / float(rapport)
                elif i!=0 :
                    poids = 0.1/float(rapport)
                else :
                    poids = 0
                if poids >= meilleur[1] :
                    meilleur[0] = forme
                    meilleur[1] = poids
                    meilleur[2] = i
                i += 1
            if meilleur[0] in ls :
                return True, txt[:meilleur[2]],txt[meilleur[2] + 1:]
            else :
                return True, txt[:meilleur[2]],txt[meilleur[2]:] 

    def make_ucis_paras_uces(self, ucis_paras_txt, make_uce = True) :
        print 'make_ucis_paras_uces'
        ponctuation_espace =  [' ','.', u'£', ';', '?', '!', ',', ':','']
        listeSeparateurs = [[u'.', 60.0], [u'?', 60.0], [u'!', 60.0], [u'£', 60], [u':', 50.0], [u';', 40.0], [u',', 10.0], [u' ', 0.1]]
        if make_uce :
            print 'decoupage uce'
            taille_uce = self.parametre['eff_min_uce']
#            print 'plus de recomptage UCE'
            self.ucis_paras_uces = []
            for i, uci in enumerate(ucis_paras_txt) :
                self.ucis_paras_uces.append([])
                for j, para in enumerate(uci) :
                    #print '###########ATTENTION CHINOIS para to list################'
                    #para = ' '.join(list(para))
                    self.ucis_paras_uces[i].append([])
                    reste, texte_uce, suite = decouper(para+u'$', 250, 240, listeSeparateurs)
                    while reste :
                        uce = [val.strip() for val in texte_uce.strip().split() if val.strip() not in ponctuation_espace]
                        self.ucis_paras_uces[i][j].append(uce)
                        reste, texte_uce, suite = decouper(suite, 250, 240, listeSeparateurs)
                    newpara = []
                    nuce = []
                    for uce in self.ucis_paras_uces[i][j] :
                        nuce += uce
                        if len(nuce)>=taille_uce:
                            newpara.append(nuce)
                            nuce = []
                    if nuce != [] :
                        #FIXME ???
                        if len(nuce) >= 5 :
                            newpara.append(nuce)
                        else :
                            if newpara != [] :
                                newpara[-1] += nuce
                            else :
                                newpara.append(nuce)
                    self.ucis_paras_uces[i][j] = newpara
        else :
            self.ucis_paras_uces = [[[[val.strip() for val in para.strip().split() if val not in ponctuation_espace]] for para in uci] for uci in ucis_paras_txt]
                        
#    def feed_dict(self, val, i, j, k, id) :
#        if val in self.formes :
#            self.formes[val][0] +=1
#            self.formes[val][1].append([i,j,k])
#        else :
#            if val in self.parent.lexique :
#                type_forme = self.parent.lexique[val][1]
#            else :
#                if val.isdigit():
#                    type_forme = 'num'
#                else :
#                    type_forme = 'nr'
#            self.formes[val] = [1, [[i,j,k]], type_forme, id]
    def feed_dict_big(self, val, ucinb) :
        if val in self.formes :
            self.formes[val][0] +=1
            if ucinb in self.formes[val][1] :
                self.formes[val][1][ucinb] += 1
            else :
                self.formes[val][1][ucinb] = 1
            #self.formes[val][1].append([i,j,k])
        else :
            if val in self.parent.lexique :
                type_forme = self.parent.lexique[val][1]
            else :
                if val.isdigit():
                    type_forme = 'num'
                else :
                    type_forme = 'nr'
            self.formes[val] = [1, {ucinb: 1}, type_forme]

    def feed_dict(self, val, i, j, k, id) :
        if val in self.formes :
            self.formes[val][0] +=1
            if (i,j,k) in self.formes[val][1] :
                self.formes[val][1][(i,j,k)] += 1
            else :
                self.formes[val][1][(i,j,k)] = 1
            #self.formes[val][1].append([i,j,k])
        else :
            if val in self.parent.lexique :
                type_forme = self.parent.lexique[val][1]
            else :
                if val.isdigit():
                    type_forme = 'num'
                else :
                    type_forme = 'nr'
            self.formes[val] = [1, {(i,j,k): 1}, type_forme, id]

    def check_uce_et(self) :
        return [[forme, self.formes[forme][1]] for forme in self.formes if forme.startswith('_') and forme.endswith('_')]

    def make_forms_and_uces(self) :
        print 'make forms and uces'
        uces = {}
        orderuces = {}
        compt = 0
        for i, uci in enumerate(self.ucis_paras_uces) :
            for j, para in enumerate(uci) :
                for k, uce in enumerate(para) :
                    ijk = (i,j,k)#'.'.join([`i`,`j`,`k`])
                    orderuces[ijk] = compt
                    compt += 1
                    if uce != [] :
                        for word in uce :
                            id = len(self.formes)
                            self.feed_dict(word, i, j, k, id)
                            #FIXME pas la bonne facon de compter la taille des uces
                            #passer par self.formes et self.lems
                            if ijk in uces and self.formes[word][2] in self.typeactive :
                                uces[ijk] += 1
                            elif ijk not in uces and self.formes[word][2] in self.typeactive :
                                uces[ijk] = 1
                            elif ijk not in uces :
                                uces[ijk] = 0
                    else :
                        uces[ijk] = 0
        self.etintxt = self.check_uce_et()
        for forme in self.etintxt :
            del(self.formes[forme[0]])
        return uces, orderuces

    def min_eff_formes(self) :
        if not self.parametre['lem'] :
            lformes = [self.formes[forme][0] for forme in self.formes if self.formes[forme][2] in self.typeactive]
            if len(lformes) <= self.parametre['max_actives'] :
                self.parametre['eff_min_forme'] = 3
            else :
                lformes.sort(reverse = True)
                self.parametre['eff_min_forme'] = lformes[self.parametre['max_actives']]
                print self.parametre['eff_min_forme']
        else :
            lems = self.make_lem_eff()
            llems = [lems[lem][0] for lem in lems if lems[lem][2] in self.typeactive]
            if len(llems) <= self.parametre['max_actives'] :
                self.parametre['eff_min_forme'] = 3
            else :
                llems.sort(reverse = True)
                self.parametre['eff_min_forme'] = llems[self.parametre['max_actives']]
                print self.parametre['eff_min_forme']
    
    def make_lems(self, lexique) :
        if self.parametre['lem'] :
            print 'lemmatsation'
            for word in self.formes :
                if word in lexique :
                    if lexique[word][0] in self.lems :
                        self.lems[lexique[word][0]].append(word)
                    else :
                        self.lems[lexique[word][0]] = [word]
                else :
                    if word in self.lems :
                        self.lems[word].append(word)
                    else :
                        self.lems[word] = [word]
        else :
            print 'pas de lemmatisation : lems = formes'
            for word in self.formes :
                self.lems[word] = [word]
            
    def make_lem_eff(self) :
        print 'make lem eff'
        lems = {}
        for lem in self.lems :
            lems[lem] = [sum([self.formes[word][0] for word in self.lems[lem]]), self.lems[lem], self.formes[self.lems[lem][0]][2]]
        return lems

    def make_lexique(self) :
        print 'make lexique'
        self.lexique = {}
        for lem in self.lems :
            for forme in self.lems[lem] :
                self.lexique[forme] = lem
    
#    def return_lem(self, word) :
#        if word in self.lexique :
#            return self.lexique[word]
#        else :
#            return word
    
    def make_ucis_paras_uces_lems(self):
        print 'make_ucis_paras_uces_lems'
        if self.lexique is None :
            self.make_lexique()
        return [[[[self.lexique.get(word, word) for word in uce] for uce in para] for para in uci] for uci in self.ucis_paras_uces]
    
    def make_var_actives(self) :
        print 'creation liste act'
        self.actives = [word for word in self.lems if self.formes[self.lems[word][0]][2] in self.typeactive and sum([self.formes[mot][0] for mot in self.lems[word]]) > self.parametre['eff_min_forme']]

    def make_var_supp(self) :
        print 'creation var supp'
        self.supp = [word for word in self.lems if self.formes[self.lems[word][0]][2] in self.supplementaires and sum([self.formes[mot][0] for mot in self.lems[word]]) > self.parametre['eff_min_forme']]

    def make_and_write_sparse_matrix_from_uci(self, fileout) :
        print 'make_and_write_sparse_martrix_from_uci'
        with open(fileout+'~', 'w') as f :
            for i, lem in enumerate(self.actives) :
                ucis = list(set([uce[0] for form in self.lems[lem] for uce in self.formes[form][1]]))
                ucis.sort()
                for uci in ucis :
                    f.write(''.join([' '.join([`uci+1`,`i+1`,`1`]),'\n']))
        with open(fileout+'~', 'r') as f :
            old = f.read()
            f.seek(0)
            for i, line in enumerate(f) :
                pass
            nrow = i + 1
        with open(fileout, 'w') as f :
            txt = "%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % ( len(self.ucis), len(self.actives), nrow)
            f.write(txt + old)
        os.remove(fileout+'~')


    def make_pondtable_with_uci(self, lformes, fileout) :
        table_uci = [[0 for val in lformes] for line in range(0,len(self.ucis))]
        for i, lem in enumerate(lformes) :
            for form in self.lems[lem] :
                ucit = [val for val in self.formes[form][1]]
                for uci in ucit :
                    table_uci[uci[0]][i] += self.formes[form][1][uci]
        table_uci = [[str(val) for val in line] for line in table_uci]
        table_uci.insert(0,lformes)
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in table_uci]))
        del table_uci

    def make_tableet_with_uci(self, fileout) :
        et = self.get_unique_etoiles()
        table_out = [[0 for val in et] for line in range(0,len(self.ucis))]
        for i, uci in enumerate(self.etoiles) :
            for valet in uci[0][0] :
                table_out[i][et.index(valet)] = 1
        table_out = [[str(val) for val in line] for line in table_out]
        table_out.insert(0,et)
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in table_out]))
        del table_out

    def make_table_with_uce(self, orderuces) :
        print 'make_table_with_uce'
        #print self.ucenb
        table_uce = [[0 for val in self.actives] for line in range(0, len(orderuces))]
        for i, lem in enumerate(self.actives) :
            for form in self.lems[lem] :
                for uce in self.formes[form][1] :
                    #ijk = '.'.join([str(val) for val in uce]) 
                    table_uce[orderuces[uce]][i] = 1
        return table_uce

#    def make_sparse_matrix_with_uce(self, orderuces) :
#        print 'make_sparse_matrix_with_uce'
#        smat = []
#        for i, lem in enumerate(self.actives) :
#            for form in self.lems[lem] :
#                for uce in self.formes[form][1] :
#                    #ijk = '.'.join([str(val) for val in uce])
#                    smat.append((`orderuces[uce]+1`,`i+1`,`1`))
#        smat = list(set(smat))
#        smat.sort()
#        return smat
#
#    def write_sparse_matrix(self, fileout, smat, nrow, ncol) :
#        print 'write_sparse_matrix'
#        txt = "%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % ( nrow, ncol, len(smat))
#        with open(fileout, 'w') as f :
#            f.write(txt+'\n'.join([' '.join(line) for line in smat]))

    def make_and_write_sparse_matrix_from_uce(self, orderuces, fileout) :
        print 'make_and_write_sparse_martrix_from_uce'
        with open(fileout+'~', 'w') as f :
            for i, lem in enumerate(self.actives) :
                uces = list(set([uce for form in self.lems[lem] for uce in self.formes[form][1]]))
                for uce in uces :
                    f.write(''.join([' '.join([`orderuces[uce]+1`,`i+1`,`1`]),'\n']))

        with open(fileout+'~', 'r') as f :
            old = f.read()
            f.seek(0)
            for i, line in enumerate(f) :
                pass
            nrow = i + 1
        with open(fileout, 'w') as f :
            txt = "%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % ( len(orderuces), len(self.actives), nrow)
            f.write(txt + old)
        os.remove(fileout+'~')

    def make_and_write_sparse_matrix_from_uce_list(self, listin, fileout) :
        print 'make_and_write_sparse_martrix_from_uce'
        orderuces = [(i,j,k) for i, uci in enumerate(self.ucis_paras_uces) for j, para in enumerate(uci) for k, uce in enumerate(para)]
        orderuces = dict([[uce,i] for i, uce in enumerate(orderuces)])
        with open(fileout+'~', 'w') as f :
            for i, forme in enumerate(listin) :
                uces = [uce for uce in self.formes[forme][1]]
                for uce in uces :
                    f.write(''.join([' '.join([`orderuces[uce]+1`,`i+1`,`1`]),'\n']))

        with open(fileout+'~', 'r') as f :
            old = f.read()
            f.seek(0)
            for i, line in enumerate(f) :
                pass
            nrow = i + 1
        with open(fileout, 'w') as f :
            txt = "%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % ( len(orderuces), len(listin), nrow)
            f.write(txt + old)
        os.remove(fileout+'~')


    def make_table_with_classe(self, uces, list_act) :
        table_uce = [[0 for val in list_act] for line in range(0,len(uces))]
        uces = dict([[uce, i] for i, uce in enumerate(uces)])
        for i, lem in enumerate(list_act) :
            for form in self.lems[lem] :
                for uce in self.formes[form][1] :
                    if uce in uces :
                        table_uce[uces[uce]][i] = 1
        table_uce.insert(0, list_act)
        return table_uce
    
    def make_and_write_sparse_matrix_from_classe(self, uces, list_act, fileout) :
        print 'make_and_write_sparse_martrix_from_classe'
        duces = dict([[uce, i] for i, uce in enumerate(uces)])
        with open(fileout+'~', 'w') as f :
            for i, lem in enumerate(list_act) :
                uces_ok = list(set([uce for form in self.lems[lem] for uce in self.formes[form][1]]).intersection(uces))
                for uce in uces_ok :
                    f.write(''.join([' '.join([`duces[uce]+1`,`i+1`,`1`]),'\n']))

        with open(fileout+'~', 'r') as f :
            old = f.read()
            f.seek(0)
            for i, line in enumerate(f) :
                pass
            nrow = i + 1
        with open(fileout, 'w') as f :
            txt = "%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % ( len(uces), len(list_act), nrow)
            f.write(txt + old)
        os.remove(fileout+'~')
    
    def make_uc(self, uces, orderuce, min_word_by_uc):
        print 'start make uc'
        ucenb= [uces[val] for val in orderuce]
        uc = []
        uces_uc = {}
        for i, uci in enumerate(self.ucis_paras_uces) :
            for j, para in enumerate(uci) :
                uc.append(0)
                for k, uce in enumerate(para) :
                    uce_id = (i,j,k)
                    if uc[-1] >= min_word_by_uc :
                        uc.append(uces[uce_id])
                    else :
                        uc[-1] += uces[uce_id]
                    uces_uc[uce_id] = len(uc)-1
        lenuc = len(uc)
        del uc
        return lenuc, uces_uc
    
    def make_and_write_sparse_matrix_from_uc(self, uces_uc, fileout) :
        print 'make_and_write_sparse_martrix_from_uc'
        deja_la = {}
        with open(fileout+'~', 'w') as f :
            for i, lem in enumerate(self.actives) :
                uces = list(set([uce for form in self.lems[lem] for uce in self.formes[form][1]]))
                for uce in uces :
                    if (uces_uc[uce],i) not in deja_la :
                        f.write(''.join([' '.join([`uces_uc[uce]+1`,`i+1`,`1`]),'\n']))   
                        deja_la[(uces_uc[uce],i)]=''
        del(deja_la)
        with open(fileout+'~', 'r') as f :
            old = f.read()
            f.seek(0)
            for i, line in enumerate(f) :
                pass
            nrow = i + 1
        with open(fileout, 'w') as f :
            txt = "%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % (max(uces_uc.values()) + 1, len(self.actives), nrow)
            f.write(txt + old)
        os.remove(fileout+'~')
                   

#    def make_tab_uc(self, uces_uc, uc) :
#        print 'make_tab_uc'
#        tabuc = [[0 for val in self.actives] for line in uc]
#        for i, word in enumerate(self.actives) :
#            for forme in self.lems[word] :
#                valforme = self.formes[forme]
#                for j, uce in enumerate(valforme[1]):
#                    #uce = '.'.join([str(val) for val in uci])
#                    ligne = uces_uc[uce]
#                    tabuc[ligne][i] = 1
#        return tabuc

    def write_tab(self, tab, fileout) :
        print 'commence ecrire'
        #print len(tab)
        #print len(tab[0])
        writer = csv.writer(open(fileout, 'wb'), delimiter=';', quoting = csv.QUOTE_NONNUMERIC)
        writer.writerows(tab)

    def make_concord(self, words, txt, color) :
        txt = ' '+ txt +' '
        for word in words :
            for forme in self.lems[word] :
                txt = txt.replace(' '+forme+' ', ' <font color=%s>' % color +forme+'</font> ')
        return txt.strip()

    def make_colored_corpus(self) :
        #colors = ['black', 'red', 'blue', 'green', 'orange', 'yellow', 'brown', 'pink', 'grey']
        ucecl = {}
        for i, lc in enumerate(self.lc) :
            for uce in lc :
                ucecl[uce] = i + 1
        for uce in self.lc0 :
            ucecl[uce] = 0
        color = ['black'] + colors[len(self.lc) - 1]
        txt = '''<html>
        <meta http-equiv="content-Type" content="text/html; charset=%s" />
        <body>
''' % sys.getdefaultencoding()
        res = [[' '.join(self.ucis[i][0]), '<br><hr>'.join(['<font color="%s">' % color[ucecl[(i,j, k)]] +  ' '.join(uce) + '</font>' for j, paras in enumerate(uci) for k, uce in enumerate(paras) ])] for i, uci in enumerate(self.ucis_paras_uces)]
        txt += '<br>'.join(['<br>'.join(uci) for uci in res])
        txt += '</body></html>'
        return txt
        #with open(filename,'w') as f :
        #    f.write(txt)

    def export_corpus_classes(self, filename, alc = False, lem = False) :
        if lem :
            ucis_paras_uces = self.make_ucis_paras_uces_lems()
        else :
            ucis_paras_uces = self.ucis_paras_uces
        ucecl = {}
        for i, lc in enumerate(self.lc) :
            for uce in lc :
                ucecl[uce] = i + 1
        for uce in self.lc0 :
            ucecl[uce] = 0
        ucecltri = ucecl.keys()
        #ucecltri = [[int(val) for val in uce] for uce in ucecltri]
        ucecltri.sort()
        if alc :
            #for i, uce in enumerate(ucecltri) :
            #    print i, uce
            #    print self.etoiles[uce[0]][uce[1]][uce[2]]
            #    print ' '.join(ucis_paras_uces[uce[0]][uce[1]][uce[2]])
            res = [[u'**** *classe_%i ' % ucecl[uce] + ' '.join(self.etoiles[uce[0]][uce[1]][uce[2]]), ' '.join(ucis_paras_uces[uce[0]][uce[1]][uce[2]])] for uce in ucecltri]
        else :
            vd = [self.etoiles[uce[0]][uce[1]][uce[2]] for uce in ucecltri]
            vd = [['<' + '='.join(et.split('_')) + '>' for et in l] for l in vd]
            res = [['<classe=%i>' % ucecl[uce], ' '.join(ucis_paras_uces[uce[0]][uce[1]][uce[2]])] for uce in ucecltri]
            res = [[' '.join([res[i][0],' '.join(vd[i])]), res[i][1]] for i, d in enumerate(res)]
        with open(filename,'w') as f :
            f.write('\n'.join(['\n'.join(uce) for uce in res]))
    
    def get_concord(self, duce, word, uces, color):
        print 'get concord'
        lformes = self.lems[word]
        for forme_ori in lformes :
            forme = self.formes[forme_ori]
            for ucenb in forme[1] :
                ijk = ucenb 
                if ijk in uces :
                    ucinb, paranb, ucenb = ucenb
                    if ijk in duce :
                        nuce = ' ' + duce[ijk] + ' '
                        nuce = nuce.replace(' '+forme_ori+' ', ' <font color=%s>' % color +forme_ori+'</font> ')
                        duce[ijk] = nuce.strip()
                    else :
                        nuce = ' ' + ' '.join(self.ucis_paras_uces[ucinb][paranb][ucenb]) + ' '
                        nuce = nuce.replace(' '+forme_ori+' ', ' <font color = %s>' % color +forme_ori+'</font> ')
                        duce[ijk] = nuce.strip()
        return duce 
    
    def count_from_list(self, l, d) :
        for val in l :
            if val in d :
                d[val] += 1
            else :
                d[val] = 1
        return d

    def count_from_list_cl(self, l, d, a, clnb) :
        for val in l :
            if val in d :
                d[val][a] += 1
            else :
                d[val] = [0] * clnb
                d[val][a] = 1
        return d
    
    def find_segments(self, taille_segment, taille_limite) :
        print 'find_segments'
        d = {}
        for para in self.ucis_paras_uces :
            for uces in para :
                for uce in uces :
                    d = self.count_from_list([' '.join(uce[i:i+taille_segment]) for i in range(len(uce)-(taille_segment - 1))], d)
        l = [[d[val], val] for val in d if d[val] >= 3]
        del(d)
        l.sort()
        if len(l) > taille_limite :
            l = l[-taille_limite:]
        return l

    def find_segments_doublon(self, taille_segment, taille_limite) :
        print 'find_segments'
        d = {}
        for para in self.ucis_paras_uces :
            for uces in para :
                for uce in uces :
                    d = self.count_from_list([' '.join(uce[i:i+taille_segment]) for i in range(len(uce)-(taille_segment - 1))], d)
        l = [[d[val], val] for val in d if d[val] > 1]
        del(d)
        l.sort()
        if len(l) > taille_limite :
            l = l[-taille_limite:]
        return l

    def find_segments_in_classe(self, list_uce, taille_segment, taille_limite):
        d={}
        ucel = [self.ucis_paras_uces[uce[0]][uce[1]][uce[2]] for uce in list_uce]
        for uce in ucel :
            d =self.count_from_list([' '.join(uce[i:i+taille_segment]) for i in range(len(uce)-(taille_segment - 1))], d)
        l = [[d[val], val, taille_segment] for val in d if d[val] >= 3]
        del(d)
        l.sort()
        if len(l) > taille_limite :
            l = l[-taille_limite:]
        return l

    def make_segments_profile(self, fileout, lenmin = 3, lenmax = 10, effmin = 50, lem = False) :
        if lem :
            ucis_paras_uces = self.make_ucis_paras_uces_lems()
        else :
            ucis_paras_uces = self.ucis_paras_uces
        d={}
        cl_uces = [[ucis_paras_uces[uce[0]][uce[1]][uce[2]] for uce in list_uce] for list_uce in self.lc]
        for b, classe in enumerate(cl_uces) :
            for uce in classe :
                for taille_segment in range(lenmin,lenmax) :
                    d =self.count_from_list_cl([' '.join(uce[i:i+taille_segment]) for i in range(len(uce)-(taille_segment - 1))], d, b, len(self.lc))
        result = [[seg] + [str(val) for val in d[seg]] for seg in d if sum(d[seg]) >= effmin]
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in result]))

    def read_uce_from_R(self, filein) :
        with open(filein, 'rU') as f :
            c = f.readlines()
        c.pop(0)
        ucecl = []
        for line in c :
            line = line.replace('\n', '').replace('"', '').split(';')
            ucecl.append([int(line[0]) - 1, int(line[1])])
        return ucecl

    def make_lc(self, uces, classes, clnb) :    
        self.lc = [[] for classe in range(0,clnb)]
        for i in range(0,clnb):
            self.lc[i] = [uce for j, uce in enumerate(uces) if i+1 == classes[j]]
        self.lc0 = [uce for j, uce in enumerate(uces) if 0 == classes[j]]

    def build_profile(self, clnb, classes, lformes, fileout) :
        print 'build_profile'
        tabout = [[[] for val in range(0,clnb)] for line in lformes]
        for j, forme in enumerate(lformes) :
            for word in self.lems[forme] :
                for i in range(0,clnb) :
                    tabout[j][i] += list(set([uce for uce in self.formes[word][1]]).intersection(set(self.lc[i])))
        tabout = [[len(set(val)) for val in line] for line in tabout]
        tabout = [[lformes[i]] + [str(val) for val in tabout[i]] for i, line in enumerate(tabout) if sum(line) > 3]
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in tabout]))
        del tabout

    def make_etoiles(self, para_coords) :
        if self.parametre['para'] :
            self.etoiles = [[[uci[0][1:]+[para_coords[j][i][0]] for uce in self.ucis_paras_uces[j][i]] for i, para in enumerate(para_coords[j])] for j, uci in enumerate(self.ucis)]
        else :
            self.etoiles = [[[uci[0][1:] for uce in self.ucis_paras_uces[j][i]] for i, para in enumerate(self.ucis_paras_uces[j])] for j, uci in enumerate(self.ucis)]
            print '#####_etoile_######'
        for forme in self.etintxt :
            ucel = [tuple(val) for val in forme[1]]
            for uce in set(ucel) :
                self.etoiles[uce[0]][uce[1]][uce[2]].append(forme[0])

    def build_profile_et(self, clnb, classes, uces, fileout) :
        print 'build_profile_et'
        unique_et = list(set([uce[i] for uci in self.etoiles for para in uci for uce in para for i in range(0,len(uce))])) 
        tabout = [[0 for val in range(0,clnb)] for line in unique_et]
        for i, et in enumerate(unique_et) :
            for j in range(0,clnb) :
                for uce in self.lc[j] :
                    #coord = uce.split('.')
                    coord = uce
                    #coord = [int(val) for val in coord]
                    if et in self.etoiles[coord[0]][coord[1]][coord[2]] :
                        tabout[i][j] += 1
        tabout = [[unique_et[i]] + [str(val) for val in tabout[i]] for i,line in enumerate(tabout) if sum(line) >= 1]
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in tabout]))       
        del tabout

    def make_lem_type_list(self) :
        self.lem_type_list = [[word, self.formes[self.lems[word][0]][2]] for word in self.lems]

    def extractnr(self) :
        with open('/home/pierre/fac/identite/nr.csv', 'w') as f :
            f.write('\n'.join([';'.join(line) for line in self.lem_type_list if line[1] == 'nr']))

    def get_actives_nb(self) :
        return len([lem for lem in self.lems if self.formes[self.lems[lem][0]][2] not in self.supplementaires])

    def get_supp_nb(self) :
        return len([lem for lem in self.lems if self.formes[self.lems[lem][0]][2] in self.supplementaires])

    def get_tot_occurrences(self) :
        return sum([self.formes[forme][0] for forme in self.formes])

    def get_unique_etoiles(self):
        return list(set([uce[i] for uci in self.etoiles for para in uci for uce in para for i in range(0,len(uce))]))

    def get_hapax(self) :
        return [forme for forme in self.formes if self.formes[forme][0] == 1]

#    def get_hapax_by_cluster(self):
#        print 'get_hapax_by_cluster'
#        hapax = self.get_hapax()
#        res = dict([[i+1, 0] for i in range(len(self.lc))])
#        sets = [dict(zip(cl,cl)) for cl in self.lc] 
#        #classement = [self.lc0] + self.lc
#        #print classement
#        for hx in hapax :
#            uce = self.formes[hx][1].keys()[0]
#            for i, cl in enumerate(self.lc) :
#                if '.'.join([str(val) for val in uce]) in sets[i] :
#                    res[i+1] += 1
#        toprint = '\n'.join([';'.join([`i`, `res[i]`]) for i in res])
#        outf = os.path.join(os.path.dirname(self.dictpathout['ira']), 'hapax_par_classe.csv')
#        with open(outf, 'w') as f :
#            f.write(toprint)

    def get_stat_by_cluster(self, outf) :
        print 'get_occurrence_by_cluster'
        t1 = time()
        #def douce(uce) :
        #    return tuple([int(val) for val in uce.split('.')])
        res = dict([[i+1, 0] for i in range(len(self.lc))])
        res2 = dict([[i+1, 0] for i in range(len(self.lc))])
        res3 = dict([[i+1, 0] for i in range(len(self.lc))])
        res4 = dict([[i+1,len(cl)] for i, cl in enumerate(self.lc)])
        sets = [set(cl) for cl in self.lc]
        dicts = [dict(zip(cl,cl)) for cl in self.lc]
        for forme in self.formes :
            for i, cl in enumerate(self.lc) :
                concern = sets[i].intersection(self.formes[forme][1].keys())
                for uce in concern :
                    res[i+1] += self.formes[forme][1][uce]
                if len(concern) != 0 :
                    res2[i+1] += 1
        hapax = self.get_hapax()
        for hx in hapax :
            uce = self.formes[hx][1].keys()[0]
            for i, cl in enumerate(self.lc) :
                if uce in dicts[i] :
                    res3[i+1] += 1
        toprint = '\n'.join([';'.join([`i`, `res[i]`, `res2[i]`, `res3[i]`, `res4[i]`, `float(res3[i])/float(res2[i])`]) for i in res])
        toprint = '\n'.join([';'.join([u'classe', u'occurrences', 'nb formes', u'hapax', u'uce', 'hapax/nb formes']), toprint])
        #outf = os.path.join(os.path.dirname(self.dictpathout['ira']), 'stat_par_classe.csv')
        with open(outf, 'w') as f :
            f.write(toprint)
        print time() - t1
#    def get_formenb_by_cluster(self) :
#        print 'get_formenb_by_cluster'
#        t1 = time()
#        res = dict([[i+1, 0] for i in range(len(self.lc))])
#        sets = [set(cl) for cl in self.lc]
#        for forme in self.formes :
#            uces = ['.'.join([str(val) for val in uce]) for uce in self.formes[forme][1]]
#            for i, cl in enumerate(sets) :
#                if len(cl.intersection(uces)) != 0 :
#                    res[i+1] += 1 
#        toprint = '\n'.join([';'.join([`i`, `res[i]`]) for i in res])
#        outf = os.path.join(os.path.dirname(self.dictpathout['ira']), 'nbformes_par_classe.csv')
#        with open(outf, 'w') as f :
#            f.write(toprint)

    def make_eff_from_etoiles(self, let, mineff) :
        forme_ok = [forme for forme in self.lems if sum([self.formes[word][0] for word in self.lems[forme]]) > mineff]
        forme_ok.sort()
        #forme_ok = [forme for forme in self.formes if self.formes[forme][0] >= mineff]
        tabout = [[0 for et in let] for forme in forme_ok]
        for i, forme in enumerate(forme_ok) :
            for word in self.lems[forme] :
                for coord in self.formes[word][1] :
                    for j, et in enumerate(let) :
                        if et in self.etoiles[coord[0]][coord[1]][coord[2]]: 
                            #tabout[i][j] += 1
                            tabout[i][j] += self.formes[word][1][coord]
        tabout = [[forme] + tabout[i] for i, forme in enumerate(forme_ok) if sum(tabout[i]) >= mineff]
        tabout.insert(0, [''] + let)
        return tabout
            
    def make_efftype_from_etoiles(self, let) :
        dtypes = {}
        for forme in self.formes :
            if self.formes[forme][2] in dtypes :
                dtypes[self.formes[forme][2]][0] += self.formes[forme][0]
                #dtypes[self.formes[forme][2]][1] += self.formes[forme][1][:]
                dtypes[self.formes[forme][2]][1] += [uce for uce in self.formes[forme][1]]
            else :
                #dtypes[self.formes[forme][2]] = [self.formes[forme][0], self.formes[forme][1][:]]
                dtypes[self.formes[forme][2]] = [self.formes[forme][0], [uce for uce in self.formes[forme][1]]]
        ltypes = [typ for typ in dtypes]
        tabout = [[0 for et in let] for typ in dtypes]
        for i, typ in enumerate(ltypes) :
            for coord in dtypes[typ][1] :
                for j, et in enumerate(let) :
                    if et in self.etoiles[coord[0]][coord[1]][coord[2]]: 
                        tabout[i][j] += 1
        tabout = [[typ] + tabout[i] for i, typ in enumerate(ltypes)]
        tabout.insert(0, [''] + let)
        return tabout

    def make_etline(self, listet) :
        orderuces = [(i,j,k) for i, uci in enumerate(self.ucis_paras_uces) for j, para in enumerate(uci) for k, uce in enumerate(para)]
        orderuces = dict([[uce,i] for i, uce in enumerate(orderuces)])
        linenb = []
        for et in listet :
            linenb.append([`orderuces[(i,j,k)] + 1` for i, uci in enumerate(self.ucis_paras_uces) for j,para in enumerate(uci) for k, uce in enumerate(para) if et in self.ucis[i][0]])
            linenb[-1].insert(0,et)
        return linenb

    def write_etoiles(self, fileout) :
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(self.ucis[i][0][1:]) for i,uci in enumerate(self.ucis) for para in self.ucis_paras_uces[i] for uce in para]))

    def start_analyse(self, parent, dlg = None, cmd = False, fromtt = False) :
        if not cmd :
            dlg.Update(1, u'Nettoyage 1')
        if not fromtt :
            self.quick_clean1()
        if self.parametre['expressions'] and not fromtt:
            if not cmd :
                dlg.Update(2, u'Expressions...')
            lang = self.parametre['lang']
            dico_path = parent.DictPath.get(lang + '_exp', 'french_exp')
            expressions = ReadDicoAsDico(dico_path)
            self.find_expression(expressions)
        
        if not cmd :
            dlg.Update(3, u'Nettoyage 2')
        if not fromtt :
            self.quick_clean2()
        if not cmd :
            dlg.Update(4, u'Construction des tableaux')
        if not fromtt :
            ucisnb = self.make_ucis()
        if not fromtt :
            if self.ucis == [] :
                ucisnb  = self.make_ucis_with_digit()
            lines = self.make_lines(ucisnb)
            del ucisnb
        #ucis_mots = make_ucis_words(lines)
        if not fromtt :
            ucis_txt = self.make_ucis_txt(lines)
            #print 'ATTENTION : CHECK DOUBLON'
            #self.check_double(ucis_txt)
            ucis_lines = self.make_ucis_lines(lines)
            self.para_coords = self.make_para_coords(ucis_lines)
            ucis_paras_txt = self.make_ucis_paras_txt(self.para_coords, ucis_lines, ucis_txt)
            del ucis_lines
        else :
            ucis_txt = get_ucis_from_tt(self)
            print ucis_txt[0]
            ucis_paras_txt = [[uci] for uci in ucis_txt]
            self.para_coords = [[] for val in ucis_paras_txt]
        #print('ATTENTION PHRASE')
        #ucis_paras_txt = self.corpus.make_ucis_paras_txt_phrases(para_coords, ucis_lines, ucis_txt)
        return ucis_txt, ucis_paras_txt

    def check_double(self, ucis_txt):
        ducis = {}
        uci_ok = []
        for i, uci in enumerate(ucis_txt) :
            if uci in ducis :
                ducis[uci][0] += 1
                ducis[uci][1].append(i)
            else :
                ducis[uci] = [1, [i]]
                uci_ok.append(i)
        print len(uci_ok)
        list_uci_ok = [uci for uci in ducis]
        print 'len(list_uci_ok)', len(list_uci_ok)
        print 'len set list uci', len(set(list_uci_ok))
        toprint = [[' '.join(self.ucis[i][0]), ucis_txt[i]] for i in uci_ok]
        print 'len toprint', len(toprint)
        with open('/media/cledemoi/voile_2003_2004_ssdoublons.txt', 'w') as f:
            f.write('\n'.join(['\n'.join(val) for val in toprint]))
        lucis = [ducis[uci] for uci in ducis]
        #lucis = sortedby(lucis, 2, 0)
        lucis = [val for val in lucis if val[0] > 1]
        print 'len lucis', len(lucis)
        #print lucis
        #ducis = {}
        #for val in lucis :
        #    if val[0] in ducis :
        #        ducis[val[0]] += 1
        #    else :
        #        ducis[val[0]] = 1
        #print ducis
        uci_pas_ok = [[ducis[uci][0], uci.replace(';', ' '), ';'.join([str(val) for val in ducis[uci][1]])] for uci in ducis if ducis[uci][0] > 1]
        #uci_pas_ok = sortedby(uci_pas_ok, 0, 2)
        uci_pas_ok = [[str(val[0]), val[1], val[2]] for val in uci_pas_ok]
        with open('/media/cledemoi/doublons.txt', 'w') as f:
            f.write('\n'.join([';'.join(val) for val in uci_pas_ok]))
        etpasok = [[' '.join(self.ucis[i][0]) for i in ducis[uci][1]] for uci in ducis if ducis[uci][0] > 1]
        with open('/media/cledemoi/etdoublons.txt', 'w') as f:
            f.write('\n'.join([';'.join(line) for line in etpasok]))

    def make_et_table(self) :
        fileout = os.path.join(os.path.dirname(self.dictpathout['ira']), 'tableau_et.csv') 
        #fileout = '/home/pierre/tableau_et.csv'
        with open(fileout,'w') as f :
            f.write('\n'.join([';'.join(line[0]) for line in self.ucis]))

    def make_uci_stat(self) :
        lc = []
        for i, classe in enumerate(self.lc) :
            classe = [val.split('.') + [str(i)] for val in classe]
            lc += classe
        fileout = os.path.join(os.path.dirname(self.dictpathout['ira']), 'uci_stat.csv')
        with open(fileout,'w') as f :
            f.write('\n'.join([';'.join(line) for line in lc]))

    def make_size_uci(self) :
        sizes = [[i, sum([len(uce) for para in uci for uce in para])] for i, uci in enumerate(self.ucis_paras_uces)]
        outf =  os.path.join(os.path.dirname(self.dictpathout['ira']), 'taille_uci.csv')
        for i, size in sizes :
            if size == 0 :
                print self.ucis_paras_uces[i]
                print self.etoiles[i]
        with open(outf, 'w') as f :
            f.write('\n'.join([';'.join([str(val) for val in line]) for line in sizes]))

    def prof_type(self) :
        print 'prof_type'
        t1 = time()
        res = dict([[i+1, {}] for i in range(len(self.lc))])
        sets = [set(cl) for cl in self.lc]
        dicts = [dict(zip(cl,cl)) for cl in self.lc]
        for forme in self.formes :
            ftype = self.formes[forme][2]
            #if not (forme.startswith(u'_') and forme.endswith(u'_')) :
            #    for uce in self.formes[forme][1] :
            #        ucet = '.'.join([str(val) for val in uce])
            for i, cl in enumerate(self.lc) :
                concern = sets[i].intersection(self.formes[forme][1].keys())
                for uce in concern :
                    if ftype in res[i+1] :
                        res[i+1][ftype] += self.formes[forme][1][uce]
                    else :
                        res[i+1][ftype] = self.formes[forme][1][uce]
        types = list(set([typ for typ in res[i] for i in res]))
        types.sort()
        colnames = ['type'] + ['classe ' + `i+1` for i in range(len(self.lc))]
        toprint = [[typ] + [`res[i+1].get(typ, 0)` for i in range(len(self.lc))] for typ in types]
        toprint.insert(0, colnames)
        fileout = self.dictpathout['type_cl']
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in toprint]))
        print time() - t1

    def make_type_tot(self):
        tt = {}
        for lem in self.lems :
            for forme in self.lems[lem] :
                if self.formes[forme][2] in tt :
                    tt[self.formes[forme][2]][0] += self.formes[forme][0]
                    tt[self.formes[forme][2]][1].append(forme)
                else :
                    tt[self.formes[forme][2]] = [self.formes[forme][0], [forme]]
        res = [';'.join([typ,str(len(tt[typ][1])),str(tt[typ][0])]) for typ in tt]
        res2 = ['\n'.join([';'.join([forme, str(self.formes[forme][0])]) for forme in tt[typ][1]]) for typ in tt]
        res = ['\n'.join([res[i], res2[i]]) for i, val in enumerate(res)]
        fileout = os.path.join(os.path.dirname(self.dictpathout['ira']), 'type_stat.csv')
        with open(fileout, 'w') as f:
            f.write('\n'.join(res))


    def count_uci_from_list(self, list_in):
        #liste_in = '/home/pierre/fac/lerass/bouquin_indentite/liste_mot_chercher_uci.txt'
        with codecs.open(list_in,'r', 'utf8') as f :
            content = f.read()
        content = content.splitlines()
        ucis = []
        for forme in content :
            if forme in self.formes :
                ucis.append(self.formes[forme][1])
            else :
                print forme
        #ucis = [self.formes[forme][1] for forme in content]
        ucis = [uc[0] for val in ucis for uc in val]
        print len(list(set(ucis)))

