# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud

import codecs
import os
import sys
from time import time
from functions import decoupercharact, ReadDicoAsDico, DoConf
import re
import sqlite3
import numpy
import itertools
import logging
from operator import itemgetter
from uuid import uuid4
from chemins import PathOut
from dialog import CorpusPref
from functions import ReadLexique, ReadDicoAsDico
import datetime


log = logging.getLogger('iramuteq.corpus')


def copycorpus(corpus) :
    log.info('copy corpus')
    copy_corpus = Corpus(corpus.parent, parametres = corpus.parametres)
    copy_corpus.ucis = corpus.ucis
    copy_corpus.formes = corpus.formes
    copy_corpus.pathout = corpus.pathout
    copy_corpus.conn_all()
    return copy_corpus



class Corpus :
    """Corpus class
    list of uci

    """
    def __init__(self, parent, parametres = {}, read = False) :
        self.parent = parent
        self.parametres = parametres
        self.cformes = None         
        self.connformes = None
        self.connuces = None
        self.conncorpus = None
        self.islem = False
        self.cuces = None
        self.ucis = []
        self.formes = {}
        self.flems = {}
        self.lems = None
        self.idformesuces = {}
        self.iduces = None
        self.idformes = None
        if read :
            self.pathout = PathOut(dirout = parametres['pathout'])
            self.read_corpus()

    def add_word(self, word) :
        if word in self.formes :
            self.formes[word].freq += 1
            if self.formes[word].ident in self.idformesuces :
                if self.ucis[-1].uces[-1].ident in self.idformesuces[self.formes[word].ident] :
                    self.idformesuces[self.formes[word].ident][self.ucis[-1].uces[-1].ident] += 1
                else :
                    self.idformesuces[self.formes[word].ident][self.ucis[-1].uces[-1].ident] = 1
            else :
                self.idformesuces[self.formes[word].ident] = {self.ucis[-1].uces[-1].ident: 1}
        else :
            if word in self.parent.lexique :
                gramtype = self.parent.lexique[word][1]
                lem = self.parent.lexique[word][0]
            elif word.isdigit() :
                gramtype = 'num'
                lem = word
            else :
                gramtype = 'nr'
                lem = word
            self.formes[word] =  Word(word, gramtype, len(self.formes), lem)
            self.idformesuces[self.formes[word].ident] = {self.ucis[-1].uces[-1].ident : 1}

    def conn_all(self): 
        """connect corpus to db"""
        if self.connformes is None :
            log.info('connexion corpus')
            self.connuces = sqlite3.connect(self.pathout['uces.db'])
            self.cuces = self.connuces.cursor()
            self.connformes = sqlite3.connect(self.pathout['formes.db'])
            self.cformes = self.connformes.cursor()
            self.conncorpus = sqlite3.connect(self.pathout['corpus.db'])
            self.ccorpus = self.conncorpus.cursor()
            self.cformes.execute('PRAGMA temp_store=MEMORY;')
            self.cformes.execute('PRAGMA journal_mode=MEMORY;')
            self.cformes.execute('PRAGMA  synchronous = OFF;')
            self.cuces.execute('PRAGMA temp_store=MEMORY;')
            self.cuces.execute('PRAGMA journal_mode=MEMORY;')
            self.cuces.execute('PRAGMA  synchronous = OFF;')
            self.ccorpus.execute('PRAGMA temp_store=MEMORY;')
            self.ccorpus.execute('PRAGMA journal_mode=MEMORY;')
            self.ccorpus.execute('PRAGMA  synchronous = OFF;')

    def read_corpus(self) :
        log.info('read corpus')
        self.parametres['syscoding'] = sys.getdefaultencoding()
        if self.conncorpus is None :
            self.conn_all()
        res = self.ccorpus.execute('SELECT * FROM etoiles;')
        for row in res :
            self.ucis.append(Uci(row[0], row[1], row[2]))
            uces = self.conncorpus.cursor().execute('SELECT * FROM luces where uci=?;',(`self.ucis[-1].ident`,))
            for uce in uces:
                self.ucis[-1].uces.append(Uce(uce[2], uce[1], uce[0]))
        res = self.ccorpus.execute('SELECT * FROM formes;')
        self.formes = dict([[forme[1], Word(forme[1], forme[3], forme[0], lem = forme[2], freq = forme[4])] for forme in res])
        self.ccorpus.close()
    
    def getworduces(self, wordid) :
        if isinstance(wordid, basestring) :
            wordid = self.formes[wordid].ident
        res = self.cformes.execute('SELECT uces FROM uces where id=? ORDER BY id;', (`wordid`,))
        return list(itertools.chain(*[[int(val) for val in row[0].split()] if not isinstance(row[0], int) else [row[0]] for row in res]))

    def getlemuces(self, lem) :
        formesid = ', '.join([`val` for val in self.lems[lem].formes])
        query = 'SELECT uces FROM uces where id IN (%s) ORDER BY id' % formesid
        res = self.cformes.execute(query)
        return list(set(list(itertools.chain(*[[int(val) for val in row[0].split()] if not isinstance(row[0], int) else [row[0]] for row in res]))))

    def getlemucis(self, lem) :
        uces = self.getlemuces(lem)
        return list(set([self.getucefromid(val).uci for val in uces]))

    def getlemuceseff(self, lem) :
        formesid = ', '.join([`val` for val in self.lems[lem].formes])
        query = 'SELECT uces FROM uces where id IN (%s) ORDER BY id' % formesid
        res = self.cformes.execute(query)
        uces = list(itertools.chain(*[[int(val) for val in row[0].split()] if not isinstance(row[0], int) else [row[0]] for row in res]))
        query = 'SELECT eff FROM eff where id IN (%s) ORDER BY id' % formesid
        res = self.cformes.execute(query)
        eff = list(itertools.chain(*[[int(val) for val in row[0].split()] if not isinstance(row[0], int) else [row[0]] for row in res]))
        lemuceeff = {}
        for i, uce in enumerate(uces) :
            lemuceeff[uce] = lemuceeff.get(uce, 0) + eff[i]
        return lemuceeff    

    def getlemeff(self, lem) :
        return self.lems[lem].freq

    def getlems(self) :
        return self.lems

    def getforme(self, formeid) :
        if self.idformes is None : self.make_idformes()
        return self.idformes[formeid]

    def gettotocc(self) :
        return sum([self.formes[forme].freq for forme in self.formes])

    def getucemean(self) :
        return float(self.gettotocc())/self.getucenb()

    def getucenb(self) :
        return self.ucis[-1].uces[-1].ident + 1

    def getucinb(self) :
        return self.ucis[-1].ident + 1

    def getucisize(self) :
        ucesize = self.getucesize()
        return [sum(ucesize[uci.uces[0].ident:(uci.uces[-1].ident + 1)]) for uci in self.ucis]
    
    def getucesize(self) :
        res = self.getalluces()
        return [len(uce[1].split()) for uce in res]

#    def getlemseff(self) :
#        if self.idformes is None :
#            self.make_idformes()
#        return dict([[lem, sum([self.idformes[forme].freq for forme in self.lems[lem]])] for lem in self.lems])

#    def getlemsefftype(self) :
#        if self.idformes is None :
#            self.make_idformes()
#        if self.lems is None :
#            self.make_lems()
#        return dict([[lem, [sum([self.idformes[forme].freq for forme in self.lems[lem]]), '', self.idformes[self.lems[lem].keys()[0]].gram]] for lem in self.lems])

    def getconcorde(self, uces) :
        return self.cuces.execute('select * from uces where id IN (%s);' % ', '.join([`i` for i in uces])) 

    def getwordconcorde(self, word) :
        return self.getconcorde(self.getworduces(word))

    def getlemconcorde(self, lem) :
        return self.getconcorde(self.getlemuces(lem))

    def getalluces(self) :
        return self.cuces.execute('SELECT * FROM uces')

    def getucesfrometoile(self, etoile) :
        return [uce.ident for uci in self.ucis for uce in uci.uces if etoile in uci.etoiles]

    def getucefromid(self, uceid) :
        if self.iduces is None : self.make_iduces()
        return self.iduces[uceid]

    def gethapaxnb(self) :
        return len([None for forme in self.formes if self.formes[forme].freq == 1])

    def getactivesnb(self, key) :
        return len([lem for lem in self.lems if self.lems[lem].act == key])
#    def make_lems(self, lem = True) :
#        log.info('make lems')
#        self.lems = {}
#        for forme in self.formes :
#            if self.formes[forme].lem in self.lems :
#                if self.formes[forme].ident not in self.lems[self.formes[forme].lem] :
#                    self.lems[self.formes[forme].lem][self.formes[forme].ident] = 0
#            else :
#                    self.lems[self.formes[forme].lem] = {self.formes[forme].ident : 0}

    def make_lems(self, lem = True) :
        log.info('make lems')
        self.lems = {}
        if lem :
            for forme in self.formes :
                if self.formes[forme].lem in self.lems :
                    if self.formes[forme].ident not in self.lems[self.formes[forme].lem].formes :
                        self.lems[self.formes[forme].lem].add_forme(self.formes[forme])
                else :
                    self.lems[self.formes[forme].lem] = Lem(self, self.formes[forme])
        else :
            self.lems = dict([[forme, Lem(self, self.formes[forme])] for forme in self.formes])
                
    def make_idformes(self) :
        self.idformes = dict([[self.formes[forme].ident, self.formes[forme]] for forme in self.formes])

    def make_iduces(self) :
        if self.iduces is None :
            self.iduces = dict([[uce.ident, uce] for uci in self.ucis for uce in uci.uces])

    def make_lexitable(self, mineff, etoiles) :
        tokeep = [lem for lem in self.lems if self.lems[lem].freq > mineff]
        etuces = [[] for et in etoiles]
        for uci in self.ucis :
            get = list(set(uci.etoiles).intersection(etoiles))
            if len(get) > 1 :
                return '2 variables sur la meme ligne'
            elif get != [] :
                etuces[etoiles.index(get[0])] += [uce.ident for uce in uci.uces]
        etuces = [set(val) for val in etuces]
        tab = []
        for lem in tokeep :
            deff = self.getlemuceseff(lem)
            ucesk = deff.keys()
            tab.append([lem] + [sum([deff[uce] for uce in et.intersection(ucesk)]) for et in etuces])
        tab.insert(0, [''] + etoiles)
        return tab
    
    def make_efftype_from_etoiles(self, etoiles) :
        dtype = {}
        etuces = [[] for et in etoiles]
        for uci in self.ucis :
            get = list(set(uci.etoiles).intersection(etoiles))
            if len(get) > 1 :
                return '2 variables sur la meme ligne'
            elif get != [] :
                etuces[etoiles.index(get[0])] += [uce.ident for uce in uci.uces]
        etuces = [set(val) for val in etuces]
        for lem in self.lems :
            deff = self.getlemuceseff(lem)
            ucesk = deff.keys()
            gram = self.lems[lem].gram
            if gram in dtype :
                dtype[gram] = [i + j for i, j in zip(dtype[gram], [sum([deff[uce] for uce in et.intersection(ucesk)]) for et in etuces])]
            else :
                dtype[gram] = [sum([deff[uce] for uce in et.intersection(ucesk)]) for et in etuces]
        tabout = [[gram] + dtype[gram] for gram in dtype]
        tabout.insert(0, [''] + etoiles)
        return tabout

    def make_uceactsize(self, actives) :
        res = self.getalluces()
        ucesize = {}
        for lem in actives: 
            deff = self.getlemuceseff(lem)
            for uce in deff :
                ucesize[uce] = ucesize.get(uce, 0) + 1
        return ucesize

    def make_uc(self, actives, lim1, lim2) :
        uceactsize = self.make_uceactsize(actives)
        last1 = 0
        last2 = 0
        uc1 = [[]]
        uc2 = [[]]
        lastpara = 0
        for uce in [uce for uci in self.ucis for uce in uci.uces] :
            if uce.para == lastpara :
                if last1 <= lim1 :
                    last1 += uceactsize.get(uce.ident,0)
                    uc1[-1].append(uce.ident)
                else :
                    uc1.append([uce.ident])
                    last1 = 0
                if last2 <= lim2 :
                    last2 += uceactsize.get(uce.ident, 0)
                    uc2[-1].append(uce.ident)
                else :
                    uc2.append([uce.ident])
                    last2 = 0
            else :
                last1 = uceactsize.get(uce.ident, 0)
                last2 = uceactsize.get(uce.ident, 0)
                lastpara = uce.para
                uc1.append([uce.ident])
                uc2.append([uce.ident])
        return uc1, uc2

    def make_and_write_sparse_matrix_from_uc(self, actives, sizeuc1, sizeuc2, uc1out, uc2out, listuce1out, listuce2out) :
        uc1, uc2 = self.make_uc(actives, sizeuc1, sizeuc2)
        log.info('taille uc1 : %i - taille uc2 : %i' % (len(uc1), len(uc2)))
        self.write_ucmatrix(uc1, actives, uc1out)
        self.write_ucmatrix(uc2, actives, uc2out)
        listuce1 = [['uce', 'uc']] + [[`uce`, `i`] for i, ucl in enumerate(uc1) for uce in ucl]
        listuce2 = [['uce', 'uc']] + [[`uce`, `i`] for i, ucl in enumerate(uc2) for uce in ucl]
        with open(listuce1out, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in listuce1]))
        with open(listuce2out, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in listuce2]))
        return len(uc1), len(uc2)

    def write_ucmatrix(self, uc, actives, fileout) :
        log.info('write uc matrix %s' % fileout)
        uces_uc = dict([[uce, i] for i, ucl in enumerate(uc) for uce in ucl])
        deja_la = {}
        nbl = 0
        with open(fileout + '~', 'w+') as f :
            for i, lem in enumerate(actives) :
                for uce in self.getlemuces(lem):
                    if (uces_uc[uce], i) not in deja_la :
                        nbl += 1
                        f.write(''.join([' '.join([`uces_uc[uce]+1`,`i+1`,`1`]),'\n']))
                        deja_la[(uces_uc[uce], i)] = 0
            f.seek(0)
            with open(fileout, 'w') as ffin :        
                ffin.write("%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % (len(uc), len(actives), nbl))
                for line in f :
                    ffin.write(line)
        os.remove(fileout + '~')
        del(deja_la)

    def export_corpus(self, outf) :
        #outf = 'export_corpus.txt'
        self.make_iduces()
        res = self.getalluces()
        self.make_iduces()
        actuci = ''
        actpara = False
        with open(outf,'w') as f :
            for uce in res :
                if self.iduces[uce[0]].uci == actuci and self.iduces[uce[0]].para == actpara :
                    f.write(uce[1].encode(self.parametres['syscoding']) + '\n')
                elif self.iduces[uce[0]].uci != actuci :
                    actuci = self.iduces[uce[0]].uci
                    if self.ucis[self.iduces[uce[0]].uci].paras == [] :
                        actpara = self.iduces[uce[0]].para
                        f.write('\n' + ' '.join(self.ucis[self.iduces[uce[0]].uci].etoiles).encode(self.parametres['syscoding']) + '\n' + uce[1].encode(self.parametres['syscoding']) + '\n')
                    else :
                        ident = 0
                        actpara = self.iduces[uce[0]].para
                        f.write('\n'.join([' '.join(self.ucis[self.iduces[uce[0]].uci].etoiles).encode(self.parametres['syscoding']), self.ucis[self.iduces[uce[0]].uci].paras[ident].encode(self.parametres['syscoding']), uce[1].encode(self.parametres['syscoding'])]) + '\n')
                elif self.iduces[uce[0]].para != actpara :
                    actpara = self.iduces[uce[0]].para
                    ident += 1
                    f.write('\n'.join([self.ucis[self.iduces[uce[0]].uci].paras[ident].encode(self.parametres['syscoding']), uce[1].encode(self.parametres['syscoding'])]) + '\n')

    def make_and_write_sparse_matrix_from_uces(self, actives, outfile, listuce = False) :
        log.info('make_and_write_sparse_matrix_from_uces %s' % outfile)
        nbl = 0
        with open(outfile + '~', 'w+') as f :
            for i, lem in enumerate(actives) :
                for uce in sorted(self.getlemuces(lem)) :
                    nbl += 1
                    f.write(''.join([' '.join([`uce+1`, `i+1`,`1`]),'\n']))
            f.seek(0)
            with open(outfile, 'w') as ffin :        
                ffin.write("%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % (self.getucenb(), len(actives), nbl))
                for line in f :
                    ffin.write(line)
        os.remove(outfile + '~')
        if listuce :
            with open(listuce, 'w') as f :
                f.write('\n'.join(['uce;uc'] + [';'.join([`i`,`i`]) for i in range(0, self.getucenb())]))

    def make_and_write_sparse_matrix_from_uci(self, actives, outfile, listuci = False) :
        log.info('make_and_write_sparse_matrix_from_ucis %s' % outfile)
        nbl = 0
        with open(outfile + '~', 'w+') as f :
            for i, lem in enumerate(actives) :
                for uci in sorted(self.getlemucis(lem)) :
                    nbl += 1
                    f.write(''.join([' '.join([`uci+1`, `i+1`,`1`]),'\n']))
            f.seek(0)
            with open(outfile, 'w') as ffin :        
                ffin.write("%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % (self.getucinb(), len(actives), nbl))
                for line in f :
                    ffin.write(line)
        os.remove(outfile + '~')
        if listuci :
            with open(listuci, 'w') as f :
                f.write('\n'.join(['uci;uc'] + [';'.join([`i`,`i`]) for i in range(0, self.getucinb())]))
                    
    def make_and_write_sparse_matrix_from_classe(self, actives, uces, outfile) :
        log.info('make_and_write_sparse_matrix_from_classe %s' % outfile)
        nbl = 0
        duces = dict([[uce, i] for i, uce in enumerate(uces)])
        with open(outfile + '~', 'w+') as f :
            for i, lem in enumerate(actives) :
                uces_ok = list(set(self.getlemuces(lem)).intersection(uces))
                for uce in uces_ok :
                    f.write(''.join([' '.join([`duces[uce]+1`,`i+1`,`1`]),'\n']))
            f.seek(0)
            with open(outfile, 'w') as ffin :        
                ffin.write("%%%%MatrixMarket matrix coordinate integer general\n%i %i %i\n" % (self.getucenb(), len(actives), nbl))
                for line in f :
                    ffin.write(line)
        os.remove(outfile + '~')

    def parse_active(self, gramact, gramsup = None) :
        log.info('parse actives')
        for lem in self.lems :
            if self.lems[lem].gram in gramact :
                self.lems[lem].act = 1
            elif gramsup is not None :
                if self.lems[lem].gram in gramsup :
                    self.lems[lem].act = 2
                else :
                    self.lems[lem].act =  0
            else :
                self.lems[lem].act = 2

    def make_actives_limit(self, limit) :
        if self.idformes is None :
            self.make_idformes()
        return [lem for lem in self.lems if self.getlemeff(lem) >= limit]
    
    def make_actives_nb(self, nbmax, key) :
        log.info('make_actives_nb : %i - %i' % (nbmax,key))
        if self.idformes is None :
            self.make_idformes()
        allactives = [[self.lems[lem].freq, lem] for lem in self.lems if self.lems[lem].act == key and self.lems[lem].freq >= 3]
        self.activenb = len(allactives)
        allactives = sorted(allactives, reverse = True)
        if len(allactives) <= nbmax :
            log.info('nb = %i - eff min = %i ' % (len(allactives), allactives[-1][0]))
            return [val[1] for val in allactives], allactives[-1][0]
        else :
            effs = [val[0] for val in allactives]
            if effs.count(effs[nbmax - 1]) > 1 :
                lim = effs[nbmax - 1] + 1
                nok = True
                while nok :
                    try :
                        stop = effs.index(lim)
                        nok = False
                    except ValueError:
                        lim -= 1
            else :
                stop = nbmax - 1
        log.info('nb actives = %i - eff min = %i ' % (stop, lim))
        return [val[1] for val in allactives[0:stop + 1]], lim

    def make_and_write_profile(self, actives, ucecl, fileout) :
        log.info('formes/classes')
        tab = [[lem] + [len(set(self.getlemuces(lem)).intersection(classe)) for classe in ucecl] for lem in actives]
        tab = [[line[0]] + [`val` for val in line[1:]] for line in tab if sum(line[1:]) >= 3]
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join(line) for line in tab]).encode(self.parametres['syscoding']))

    def make_etoiles(self) :
        etoiles = set([])
        for uci in self.ucis :
            etoiles.update(uci.etoiles[1:] + uci.paras)
        return list(etoiles)

    def make_and_write_profile_et(self, ucecl, fileout) :
        log.info('etoiles/classes')
        etoiles = self.make_etoiles()
        with open(fileout, 'w') as f :
            f.write('\n'.join([';'.join([etoile] + [`len(set(self.getucesfrometoile(etoile)).intersection(classe))` for classe in ucecl]) for etoile in etoiles]).encode(self.parametres['syscoding']))

    def count_from_list(self, l, d) :
        for val in l :
            if val in d :
                d[val] += 1
            else :
                d[val] = 1
        return d

    def find_segments(self, taille_segment, taille_limite) :
        d = {}
        for uce in self.getalluces() :
            uce = uce[1].split()
            d = self.count_from_list([' '.join(uce[i:i+taille_segment]) for i in range(len(uce)-(taille_segment - 1))], d)
        l = [[d[val], val] for val in d if d[val] >= 3]
        del(d)
        l.sort()
        if len(l) > taille_limite :
            l = l[-taille_limite:]
        return l
         
    def make_ucecl_from_R(self, filein) :
        with open(filein, 'rU') as f :
            c = f.readlines()
        c.pop(0)
        self.lc = []
        for line in c :
            line = line.replace('\n', '').replace('"', '').split(';')
            self.lc.append([int(line[0]) - 1, int(line[1])])
        classesl = [val[1] for val in self.lc]
        clnb = max(classesl)
        self.lc = sorted(self.lc, key=itemgetter(1))
        self.lc = [[uce[0] for uce in self.lc if uce[1] == i] for i in range(clnb+1)]
        self.lc0 = self.lc.pop(0)
        #return ucecl

class Uci :
    def __init__(self, iduci, line, paraset = None) :
        self.ident = iduci
        self.etoiles = line.split()
        self.uces = []
        if paraset is not None :
            self.paras = paraset.split()
        else :
            self.paras = []

class Uce :
    def __init__(self, iduce, idpara, iduci) :
        self.ident = iduce
        self.para = idpara
        self.uci = iduci

class Word :
    def __init__(self, word, gramtype, idword, lem = None, freq = None) :
        self.forme = word
        self.lem = lem
        self.gram = gramtype
        self.ident = idword
        self.act = 1
        if freq is not None :
            self.freq = freq
        else :
            self.freq = 1

class Lem :
    def __init__(self, parent, forme) :
        self.formes = {forme.ident : forme.freq}
        self.gram = forme.gram
        self.freq = forme.freq
        self.act = forme.act

    def add_forme(self, forme) :
        self.formes[forme.ident] = forme.freq
        self.freq += forme.freq

def decouperlist(chaine, longueur, longueurOptimale) :
    """
        on part du dernier caractère, et on recule jusqu'au début de la chaîne.
        Si on trouve un '$', c'est fini.
        Sinon, on cherche le meilleur candidat. C'est-à-dire le rapport poids/distance le plus important.
    """
    separateurs = [[u'.', 6.0], [u'?', 6.0], [u'!', 6.0], [u'£', 6.0], [u':', 5.0], [u';', 4.0], [u',', 1.0], [u' ', 0.01]]
    dsep = dict([[val[0],val[1]] for val in separateurs])
    trouve = False                 # si on a trouvé un bon séparateur
    iDecoupe = 0                # indice du caractere ou il faut decouper
    
    longueur = min(longueur, len(chaine) - 1)
    chaineTravail = chaine[:longueur + 1]
    nbCar = longueur
    meilleur = ['', 0, 0]        # type, poids et position du meilleur separateur
    
    try :
        indice = chaineTravail.index(u'$')
        trouve = True
        iDecoupe = indice
    except ValueError :
        pass
    if not trouve:
        while nbCar >= 0:
            caractere = chaineTravail[nbCar]
            distance = abs(longueurOptimale - nbCar) + 1
            meilleureDistance = abs(longueurOptimale - meilleur[2]) + 1
            if caractere in dsep :
                if (float(dsep[caractere]) / distance) > (float(meilleur[1]) / meilleureDistance) :
                    meilleur[0] = caractere
                    meilleur[1] = dsep[caractere]
                    meilleur[2] = nbCar
                    trouve = True
                    iDecoupe = nbCar
            else :
                if (float(dsep[' ']) / distance) > (float(meilleur[1]) / meilleureDistance) :
                    meilleur[0] = caractere
                    meilleur[1] = dsep[' ']
                    meilleur[2] = nbCar
                    trouve = True
                    iDecoupe = nbCar
            nbCar = nbCar - 1
    # si on a trouvé
    if trouve:
        fin = chaine[iDecoupe + 1:]
        retour = chaineTravail[:iDecoupe]
        return len(retour) > 0, retour, fin
    # si on a rien trouvé
    return False, chaine, ''

def testetoile(line) :
    return line.startswith(u'****')

def testint(line) :
    return line[0:4].isdigit() and u'*' in line

def prep_txtlist(txt) :
    return txt.split() + [u'$']

def prep_txtcharact(txt) :
    return txt + u'$'

class BuildCorpus :
    """
    Class for building a corpora
    """
    def __init__(self, infile, parametres_corpus, lexique = None, expressions = None, dlg = None) :
        log.info('begin building corpus...')
        self.lexique = lexique
        self.expressions = expressions
        self.dlg = dlg
        self.corpus = Corpus(self, parametres_corpus)
        self.infile = infile
        self.last = 0
        self.lim = parametres_corpus.get('lim', 1000000)
        self.encoding = parametres_corpus['encoding']
        self.corpus.pathout = PathOut(filename = parametres_corpus['originalpath'], dirout = parametres_corpus['pathout'])
        self.corpus.pathout.createdir(parametres_corpus['pathout'])
        self.corpus.parametres['uuid'] = str(uuid4())
        self.corpus.parametres['corpus_name'] = os.path.split(self.corpus.parametres['pathout'])[1]
        self.corpus.parametres['type'] = 'corpus'
        if self.corpus.parametres['keep_ponct'] :
            self.ponctuation_espace = [' ', '']
        else :
            self.ponctuation_espace =  [' ','.', u'£', ';', '?', '!', ',', ':','']
        self.cleans = []
        self.tolist = self.corpus.parametres.get('tolist', 0)
        self.buildcleans()
        self.prep_makeuce()
        #create database
        self.connect()
        self.dobuild()

    def prep_makeuce(self) :
        method = self.corpus.parametres.get('ucemethod', 0)
        if method == 1 :
            self.decouper = decouperlist
            self.prep_txt = prep_txtlist
            self.ucesize = self.corpus.parametres.get('ucesize', 40)
        elif method == 0 :
            self.decouper = decoupercharact
            self.prep_txt = prep_txtcharact
            self.ucesize = self.corpus.parametres.get('ucesize', 240)
        log.info('method uce : %s' % method)

    def dobuild(self) :    
        t1 = time()
        self.read_corpus(self.infile)
        self.indexdb()
        self.corpus.parametres['ira'] = self.corpus.pathout['Corpus.cira']
        self.time = time() - t1
        self.dofinish()
        DoConf().makeoptions(['corpus'],[self.corpus.parametres], self.corpus.pathout['Corpus.cira'])
        log.info('time : %f' % (time() - t1))

    def connect(self) :
        self.conn_f = sqlite3.connect(self.corpus.pathout['formes.db'])
        self.cf = self.conn_f.cursor()
        self.cf.execute('CREATE TABLE IF NOT EXISTS uces (id INTEGER, uces TEXT);')
        self.cf.execute('CREATE TABLE IF NOT EXISTS eff (id INTEGER, eff TEXT);')
        self.conn_f.commit()
        self.cf = self.conn_f.cursor()
        self.cf.execute('PRAGMA temp_store=MEMORY;')
        self.cf.execute('PRAGMA journal_mode=MEMORY;')
        self.cf.execute('PRAGMA  synchronous = OFF;')
        self.cf.execute('begin')
        self.conn = sqlite3.connect(self.corpus.pathout['uces.db'])
        self.c = self.conn.cursor()
        self.c.execute('CREATE TABLE IF NOT EXISTS uces (id INTEGER, uces TEXT);')
        self.conn.commit()
        self.c = self.conn.cursor()
        self.c.execute('PRAGMA temp_store=MEMORY;')
        self.c.execute('PRAGMA journal_mode=MEMORY;')
        self.c.execute('PRAGMA  synchronous = OFF;')
        self.c.execute('begin')

    def indexdb(self) :
        #commit index and close db
        self.conn.commit()
        self.conn_f.commit()
        self.cf.execute('CREATE INDEX iduces ON uces (id);')
        self.cf.execute('CREATE INDEX ideff ON eff (id);')
        self.c.close()
        self.cf.close()
        #backup corpora
        self.conn_corpus = sqlite3.connect(self.corpus.pathout['corpus.db'])
        self.ccorpus = self.conn_corpus.cursor()
        self.ccorpus.execute('CREATE TABLE IF NOT EXISTS etoiles (uci INTEGER, et TEXT, paras TEXT);')
        self.ccorpus.execute('CREATE TABLE IF NOT EXISTS luces (uci INTEGER, para INTEGER, uce INTEGER);')
        self.ccorpus.execute('CREATE TABLE IF NOT EXISTS formes (ident INTEGER, forme TEXT, lem TEXT, gram TEXT, freq INTEGER);')
        self.conn_corpus.commit()
        self.ccorpus = self.conn_corpus.cursor()
        self.ccorpus.execute('PRAGMA temp_store=MEMORY;')
        self.ccorpus.execute('PRAGMA journal_mode=MEMORY;')
        self.ccorpus.execute('PRAGMA  synchronous = OFF;')
        self.ccorpus.execute('begin')
        self.backup_corpus()
        self.ccorpus.execute('CREATE INDEX iduci ON luces (uci);')
        self.conn_corpus.commit()
        self.conn_corpus.close()
        #self.corpus.parametres['corpus_ira'] = self.corpus.pathout['corpus.cira']

    def buildcleans(self) :
        if self.corpus.parametres.get('lower', 1) :
            self.cleans.append(self.dolower)
        if self.corpus.parametres.get('firstclean', 1) :
            self.cleans.append(self.firstclean)
        self.rule = self.corpus.parametres.get('keep_caract', u"^a-zA-Z0-9àÀâÂäÄáÁéÉèÈêÊëËìÌîÎïÏòÒôÔöÖùÙûÛüÜçÇßœŒ’ñ.:,;!?*'_-")
        self.cleans.append(self.docharact)
        if self.corpus.parametres.get('expressions', 1) :
            self.cleans.append(self.make_expression)
        if self.corpus.parametres.get('apos', 1) :
            self.cleans.append(self.doapos)
        if self.corpus.parametres.get('tiret', 1):
            self.cleans.append(self.dotiret)

    def make_expression(self,txt) :
         for expression in self.expressions:
            if expression in txt :
                txt = txt.replace(expression, self.expressions[expression][0])
         return txt
    
    def dolower(self, txt) :
        return txt.lower()

    def docharact(self, txt) :
        #rule = u"^a-zA-Z0-9àÀâÂäÄáÁéÉèÈêÊëËìÌîÎïÏòÒôÔöÖùÙûÛüÜçÇßœŒ’ñ.:,;!?*'_-"
        list_keep = u"[" + self.rule + "]+"
        return re.sub(list_keep, ' ', txt)
    
    def doapos(self, txt) :
        return txt.replace(u'\'', u' ')

    def dotiret(self, txt) :
        return txt.replace(u'-', u' ')

    def firstclean(self, txt) :
        txt = txt.replace(u'’',"'")
        txt = txt.replace(u'œ', u'oe')
        return txt.replace('...',u' £ ').replace('?',' ? ').replace('.',' . ').replace('!', ' ! ').replace(',',' , ').replace(';', ' ; ').replace(':',' : ')

    def make_cleans(self, txt) :
        for clean in self.cleans :
            txt = clean(txt)
        return txt

    def backup_uce(self) :
        if self.corpus.idformesuces != {} :
            log.info('backup %i' % len(self.corpus.idformesuces))
            touce = [(`forme`, ' '.join([`val` for val in  self.corpus.idformesuces[forme].keys()])) for forme in self.corpus.idformesuces]
            toeff = [(`forme`, ' '.join([`val` for val in  self.corpus.idformesuces[forme].values()])) for forme in self.corpus.idformesuces]
            self.cf.executemany('INSERT INTO uces VALUES (?,?);', touce)
            self.cf.executemany('INSERT INTO eff VALUES (?,?);', toeff)
        self.corpus.idformesuces = {}        
        self.count = 1

    def backup_corpus(self) :
        log.info('start backup corpus')
        t = time()
        for uci in self.corpus.ucis :
            self.ccorpus.execute('INSERT INTO etoiles VALUES (?,?,?);' ,(uci.ident,' '.join(uci.etoiles), ' '.join(uci.paras,)))
            for uce in uci.uces : 
                self.ccorpus.execute('INSERT INTO luces VALUES (?,?,?);',(`uci.ident`,`uce.para`,`uce.ident`,))
        for forme in self.corpus.formes :
            self.ccorpus.execute('INSERT INTO formes VALUES (?,?,?,?,?);', (`self.corpus.formes[forme].ident`, forme, self.corpus.formes[forme].lem, self.corpus.formes[forme].gram, `self.corpus.formes[forme].freq`,))
        log.info('%f' % (time() - t))

    def dofinish(self) :
        self.corpus.parametres['date'] = datetime.datetime.now().ctime()
        minutes, seconds = divmod(self.time, 60)
        hours, minutes = divmod(minutes, 60)
        self.corpus.parametres['time'] = '%.0fh %.0fm %.0fs' % (hours, minutes, seconds)
        self.corpus.parametres['ucinb'] = self.corpus.getucinb()
        self.corpus.parametres['ucenb'] = self.corpus.getucenb()
        self.corpus.parametres['occurrences'] = self.corpus.gettotocc()
        self.corpus.parametres['formesnb'] = len(self.corpus.formes)
        hapaxnb = self.corpus.gethapaxnb()
        pourhapaxf = (float(hapaxnb) / len(self.corpus.formes)) * 100
        pourhapaxocc = (float(hapaxnb) / self.corpus.parametres['occurrences']) * 100
        self.corpus.parametres['hapax'] = '%i - %.2f %% des formes - %.2f %% des occurrences' % (hapaxnb, pourhapaxf, pourhapaxocc)


class BuildFromAlceste(BuildCorpus) :
    #def __init___(self, infile, parametres_corpus) :
    #    BuildCorpus.__init__(self, infile, parametres_corpus)


    def read_corpus(self, infile) :
        self.limitshow = 0
        self.count = 1
        if self.corpus.parametres['ucimark'] == 0 :
            self.testuci = testetoile
        elif  self.corpus.parametres['ucimark'] == 1 :
            self.testuci = testint
        txt = []
        iduci = -1
        idpara = -1
        iduce = -1
        with codecs.open(infile, 'rU', self.encoding) as f :
            for line in f :
                if self.testuci(line) :
                    iduci += 1
                    if txt != [] :
                        iduce, idpara = self.treattxt(txt, iduce, idpara, iduci - 1)
                        txt = []
                        self.corpus.ucis.append(Uci(iduci, line))
                    else :
                        self.corpus.ucis.append(Uci(iduci, line))
                elif line.startswith(u'-*') :
                    if txt != [] :
                        iduce, idpara = self.treattxt(txt, iduce, idpara, iduci)
                        txt = []
                    idpara += 1
                    self.corpus.ucis[-1].paras.append(line.split()[0])
                elif line.strip() != '' and iduci != -1 :
                    txt.append(line)
        if txt != [] :
            iduce, idpara = self.treattxt(txt, iduce, idpara, iduci)
            del(txt)
        self.backup_uce()

    def treattxt(self, txt, iduce, idpara, iduci) :
        txt = ' '.join(txt)
        #log.debug('ATTENTION CHINOIS -> charactères')
        #clean_chinois = [self.firstclean, self.dolower, self.make_expression, self.doapos, self.dotiret]
        #log.debug('ATTENTION CHINOIS -> list(text)')
        #txt = ' '.join(list(txt))
        txt = self.make_cleans(txt)#, clean_chinois)
        ucetxt = self.make_uces(txt, self.corpus.parametres['douce'])
        if self.corpus.ucis[-1].paras == [] :
            idpara += 1
        for uce in ucetxt :
            iduce += 1
            self.corpus.ucis[-1].uces.append(Uce(iduce, idpara, iduci))
            self.c.execute('INSERT INTO uces VALUES(?,?);', (`iduce`,uce))
            if not self.tolist :
                uce = uce.split()
            else :
                uce = list(uce)
            for word in uce :
                self.last += 1
                self.corpus.add_word(word)
        if self.dlg is not None :
            if self.limitshow > self.count :
                self.dlg.Pulse('uci: %i - uce : %i' % (iduci + 1, iduce +1))
                self.count += 1
                self.limitshow = 0
            else :
                self.limitshow = self.last / 100000
        log.debug(`iduci`, `idpara`, `iduce`)
        if self.last > self.lim :
            self.backup_uce()
            self.last = 0
        return iduce, idpara

    def make_uces(self, txt, douce = True, keep_ponct = False) :
        txt = ' '.join(txt.split())
        if douce :
            out = []
            reste, texte_uce, suite = self.decouper(self.prep_txt(txt), self.ucesize + 15, self.ucesize)
#            print 'reste'
#            print reste
#            print 'texte_uce'
#            print texte_uce
#            print 'suite'
#            print suite
            while reste :
                uce = ' '.join([val for val in texte_uce if val not in self.ponctuation_espace])
                if uce != '' :
                    out.append(uce)
                reste, texte_uce, suite = self.decouper(suite, self.ucesize + 15, self.ucesize)
#                print 'reste'
#                print reste
#                print 'texte_uce'
#                print texte_uce
#                print 'suite'
#                print suite

            uce = ' '.join([val for val in texte_uce if val not in self.ponctuation_espace])
            if uce != '' : 
                print 'RESTEE UUCEEEEEEEEEEEEE', uce
                out.append(uce)
            return out
        else :
            return [' '.join([val for val in txt.split() if val not in self.ponctuation_espace])]

#decouper (list_sep)
#make_uces (decouper)
#treat_txt (make_uces)
#read (treat_txt)

class Builder :
    def __init__(self, parent, dlg = None) :
        self.parent = parent
        self.dlg = dlg
        parametres = DoConf(os.path.join(self.parent.UserConfigPath,'corpus.cfg')).getoptions('corpus')
        parametres['pathout'] = PathOut(parent.filename, 'corpus').mkdirout()
        dial = CorpusPref(parent, parametres)
        dial.CenterOnParent()
        dial.txtpath.SetLabel(parent.filename)
        #dial.repout_choices.SetValue(parametres['pathout'])
        self.res = dial.ShowModal()
        if self.res == 5100 :
            parametres = dial.doparametres()
            parametres['originalpath'] = parent.filename
            PathOut().createdir(parametres['pathout'])
            ReadLexique(self.parent, lang = parametres['lang'])
            self.parent.expressions = ReadDicoAsDico(self.parent.DictPath.get(parametres['lang']+'_exp', 'french_exp'))
            self.parametres = parametres
        dial.Destroy()

    def doanalyse(self) :
        return BuildFromAlceste(self.parent.filename, self.parametres, self.parent.lexique, self.parent.expressions, dlg = self.dlg).corpus


if __name__ == '__main__' :
    t1 = time()
    parametres = {'formesdb':'formes.db', 'ucesdb': 'uces.db', 'corpusdb' : 'corpus.db', 'syscoding' : 'utf-8', 'encoding' : encoding}
    intro = BuildCorpus(infile, parametres)#, tar_in, tar_infouce)#, tar_formes)
    print time() - t1
