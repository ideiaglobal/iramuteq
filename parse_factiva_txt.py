#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2012-2013 Pierre Ratinaud
#Lisense: GNU/GPL

import os
import codecs


#txtdir = 'dev/factiva_txt'
#fileout = 'dev/factiva_txt_out.txt'
#encodage_in = 'utf8'
#encodage_out = 'utf8'


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
        if line.startswith('Article') :
            lp = line.split()
            if len(lp) > 2  :
                if lp[2] == 'Article' :
                    ucis.append([[u'****'],''])
                    keepline = False
        if line.startswith('SN ') : #source
            source = '*source_' + line[4:].replace(' ','').replace('\'','').replace(u'´','').replace(u'’','').replace('-','').lower()
            ucis[-1][0].append(source)
        elif line.startswith('PD ') : #date
            mois_annee = '*ma_' + line[4:].split(' ')[1] + line[4:].split(' ')[2]
            ucis[-1][0].append(mois_annee)
            annee = u'*annee_' + line[4:].split(' ')[2]
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
    ofile.write(toprint.encode(encodage))

class ParseFactivaPaste :
    def __init__(self, txtdir, fileout, encodage_in, encodage_out) :
        files = os.listdir(txtdir) 
        with open(fileout,'w') as outf : 
            for f in files : 
                f= os.path.join(txtdir, f) 
                with codecs.open(f, 'rU', encodage_in) as infile : 
                    content = infile.read() 
                ucis = parsetxtpaste(content)
                print_ucis(ucis, outf, encodage_out)

#for dat in ['2001','2002','2003','2004', '2005','2006','2007','2008','2009','2010','2011'] :
#    path = os.path.join(txtdir,dat)
#    outfile = os.path.join(txtdir, 'corpus_' + dat + '.txt')
#    doparse(path, outfile)


if __name__ == '__main__' :
    doparse(txtdir, fileout, encodage_in, encodage_out)
    print 'fini'
