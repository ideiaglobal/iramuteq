#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2012-2013 Pierre Ratinaud
#License: GNU/GPL

import os
import codecs
import re


#txtdir = 'dev/factiva_txt'
#fileout = 'dev/factiva_txt_out.txt'
#encodage_in = 'utf8'
#encodage_out = 'utf8'

mois = {u'janvier' : '01', 
        u'février' : '02',
        u'mars' : '03',
        u'avril' : '04', 
        u'mai' : '05',
        u'juin' : '06',
        u'juillet' : '07',
        u'août' : '08',
        u'septembre' : '09',
        u'octobre' : '10',
        u'novembre' : '11',
        u'décembre' : '12', 
        u'january' : '01',
        u'february': '02',
        u'march' : '03',
        u'april': '04',
        u'may': '05',
        u'june' : '06',
        u'july': '07',
        u'august': '08',
        u'september' : '09',
        u'october': '10',
        u'november': '11',
        u'december': '12'}


def parsetxtpaste(txt):
    """
    parser de texte pour factiva
    à partir d'un copier/coller de la fenêtre de visualisation
    merci à Lucie Loubère pour l'astuce :)
    """
    no = ['NS','RE','IPD','CO','IN']  # les balises qui signalent une fin
    txt = txt.splitlines()
    keepline = False
    ucis = []
    for line in txt : 
        if line.startswith(u'Article') :
            lp = line.split()
            if len(lp) > 2  :
                if lp[2] == u'Article' or lp[2] == u'Next' or lp[2] == u'Previous':
                    ucis.append([[u'****'],''])
                    keepline = False
        if line.startswith('SN ') : #source
            jsource = re.sub(u'[\'" !\.?;,:\+\-°&]', '', line[4:])
            source = u'_'.join([u'*source', jsource]).lower()
            #source = '*source_' + line[4:].replace(' ','').replace('\'','').replace(u'´','').replace(u'’','').replace('-','').lower()
            ucis[-1][0].append(source)
        elif line.startswith('PD ') : #date
            datemois = line[4:].split(' ')[1].lower()
            datemois = mois.get(datemois, datemois)
            dateannee = line[4:].split(' ')[2]
            datejour = '%02d' % int(line[4:].split(' ')[0])
            am = '_'.join([u'*am', dateannee, datemois])
            amj = '_'.join([u'*amj', dateannee, datemois, datejour])
            ucis[-1][0].append(am)
            ucis[-1][0].append(amj)
            annee = '_'.join([u'*annee', dateannee])
            ucis[-1][0].append(annee)
        elif line.strip() in no : #fin
            keepline = False
        elif line.startswith('RF ') : #fin
            keepline = False
        elif line.strip() in ['LP', 'TD'] : #debut texte
            keepline = True
        else :
            pass
        if keepline and line.strip() not in ['LP', 'TD', ''] :
            ucis[-1][1] = '\n'.join([ucis[-1][1],line])
    return ucis


def print_ucis(ucis, ofile, encodage) :
    #elimination des articles vides
    ucis = [uci for uci in ucis if uci[1].strip() != '']
    toprint = '\n\n'.join(['\n'.join([' '.join(uci[0]),uci[1]]) for uci in ucis])
    ofile.write(toprint.encode(encodage, errors='replace') + '\n')

class ParseFactivaPaste :
    def __init__(self, txtdir, fileout, encodage_in, encodage_out) :
        files = os.listdir(txtdir) 
        files = [f for f in files if f.split('.')[-1] == 'txt']
        tot = 0
        with open(fileout,'w') as outf : 
            for f in files : 
                print f
                f = os.path.join(txtdir, f) 
                print f
                with codecs.open(f, 'rU', encodage_in) as infile : 
                    content = infile.read() 
                ucis = parsetxtpaste(content)
                print_ucis(ucis, outf, encodage_out)
                tot += len(ucis)
                print 'ok', len(ucis), 'articles', ' - total : ', tot

#for dat in ['2001','2002','2003','2004', '2005','2006','2007','2008','2009','2010','2011'] :
#    path = os.path.join(txtdir,dat)
#    outfile = os.path.join(txtdir, 'corpus_' + dat + '.txt')
#    doparse(path, outfile)


if __name__ == '__main__' :
    doparse(txtdir, fileout, encodage_in, encodage_out)
    print 'fini'
