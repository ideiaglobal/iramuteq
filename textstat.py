#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2012 Pierre Ratinaud
#License: GNU/GPL

from chemins import ffr
from analysetxt import AnalyseText
from functions import sortedby, progressbar, exec_rcode, check_Rresult 
import tempfile
from time import sleep
import logging

logger = logging.getLogger('iramuteq.textstat')



class Stat(AnalyseText) :
    def doanalyse(self) :
        self.make_stats()

    def preferences(self) :
        return self.parametres

    def make_stats(self):
        if self.dlg :
            if not 'dlg' in dir(self) :
                self.dlg = progressbar(self, 7)

        formes = self.corpus.lems
        tot = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].freq > 1]
        tot = sortedby(tot, 2,1)
        tot = [[i, val] for i, val in enumerate(tot)]
        hapax = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].freq == 1]
        hapax = sortedby(hapax, 1, 1)
        hapax = [[i, val] for i, val in enumerate(hapax)]
        act = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].act == 1]
        act = sortedby(act, 2, 1)
        act = [[i, val] for i, val in enumerate(act)]
        supp = [[forme, formes[forme].freq, formes[forme].gram] for forme in formes if formes[forme].act == 2]        
        supp = sortedby(supp, 2, 1)

        supp = [[i, val] for i, val in enumerate(supp)]

        self.result = {u'total' : dict(tot), u'formes_actives' : dict(act), u'formes_supplémentaires' : dict(supp), u'hapax' : dict(hapax), u'glob' : ''}
        occurrences = sum([val[1][1] for val in tot]) + len(hapax)
        phapax = (float(len(hapax)) / float(occurrences)) * 100
        phapax_forme = (float(len(hapax)) / (float(len(formes)))) * 100
        moy_occu_mot = float(occurrences) / float(len(formes))
        txt = ''.join([_(u'Abstract').decode('utf8'), '\n'])
        txt += ''.join([_(u'Number of texts').decode('utf8'),' : ', '%i\n' % len(self.corpus.ucis)])
        txt += ''.join([_(u"Number of occurrences").decode('utf8'),' : %i\n' % occurrences])
        txt += ''.join([_(u'Number of forms').decode('utf8'), ' : %i\n' % (len(formes))])
        txt += ''.join([_(u"Number of hapax").decode('utf8'),' : %i (%.2f%%' % (len(hapax),phapax), _(u'of occurrences').decode('utf8'), ' - %.2f%% ' % phapax_forme, _(u'of forms').decode('utf8'), ')\n']) 
        #print float(occurrences), float(len(self.corpus.ucis))
        txt += ''.join([_(u"Mean of occurrences by text").decode('utf8'), ' : %.2f' % (float(occurrences)/float(len(self.corpus.ucis)))])
        if self.dlg :
            self.dlg.Update(7, u'Ecriture...')
        self.result['glob'] = txt
        self.print_result()
        # for Zipf grap
        txt = """
        source("%s")
        tot <- read.csv2("%s", header = FALSE, row.names = 1)
        """ % (ffr(self.parent.RscriptsPath['Rgraph']), ffr(self.pathout['total.csv']))
        if len(hapax) :
            txt += """
            hapax <- read.csv2("%s", header = FALSE, row.names = 1)
            tot <- rbind(tot, hapax)
            """ % ffr(self.pathout['hapax.csv'])
        txt += """
        open_file_graph("%s", width = 400, height = 400)
        plot(tot[,1], log = 'xy', xlab='log(rangs)', ylab = 'log(frequences)', col = 'red', pch=16)
        dev.off()
        """ % (ffr(self.pathout['zipf.png']))
        tmpscript = tempfile.mktemp(dir=self.parent.TEMPDIR)
        with open(tmpscript, 'w') as f :
            f.write(txt)
        pid = exec_rcode(self.parent.RPath, tmpscript, wait = False)
        while pid.poll() == None :
            sleep(0.2)
        check_Rresult(self.parent, pid)
        if self.dlg :
            self.dlg.Destroy()

    def print_result(self) :
        for key in self.result :
            if key != 'glob' :
                dico = self.result[key]
                toprint = [[dico[val][0],`dico[val][1]`, dico[val][2]] for val in dico]
                with open(self.pathout['%s.csv' % key], 'w') as f :
                    f.write('\n'.join([';'.join([val for val in ligne]) for ligne in toprint]).encode(self.parent.syscoding))
            else :
                with open(self.pathout['%s.txt' % 'glob'], 'w') as f :
                    f.write(self.result['glob'].encode(self.parent.syscoding))
