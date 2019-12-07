import os
import sys
#path = '/home/pierre/workspace/iramuteq'
#sys.path.append(path)
#import iracmd
from functions import DoConf, read_chd, ReadProfileAsDico
from export_html import DoHTML
from chemins import ConstructPathOut, ChdTxtPathOut, FFF, ffr, PathOut, StatTxtPathOut, simipath
from layout import SimiLayout
from textsimi import *
from analyse_merge import AnalyseMerge

#corpusin = '/home/pierre/fac/lerass/formation_iramuteq/giletsjaunes-2018-12-01/giletsjaunes-2018-12-01_corpus_1/Corpus.cira'
#corpusin = "/home/pierre/fac/lerass/giletsjaunes/corpus_vrdb_vi_ss_et_corpus_1/Corpus.cira"
#corpusin ="/home/pierre/fac/lerass/giletsjaunes/corpus_vrdb_vi_ss_et_pascal/Corpus.cira"
#corpusin = '/home/pierre/fac/lerass/granddebat/20190321-LE-GRAND-DEBAT_corpus_1/Corpus.cira'
#corpusin ='/home/pierre/fac/etudiant/grumet/M2/Corpus_focus_GRUMET_corpus_2/Corpus.cira'

#cmd = iracmd.CmdLine(args=['-r',corpusin], AppliPath = path)

#analysein = "/home/pierre/fac/lerass/formation_iramuteq/giletsjaunes-2018-12-01/giletsjaunes-2018-12-01_corpus_1/giletsjaunes-2018-12-01_alceste_2/Analyse.ira"
#analysein = "/home/pierre/fac/lerass/giletsjaunes/corpus_vrdb_vi_ss_et_corpus_1/corpus_vrdb_vi_ss_et_alceste_1/Analyse.ira"
#analysein ="/home/pierre/fac/lerass/giletsjaunes/corpus_vrdb_vi_ss_et_pascal/corpus_vrdb_vi_ss_et_alceste_1/Analyse.ira"
#analysein = "/home/pierre/fac/lerass/granddebat/20190321-LE-GRAND-DEBAT_corpus_1/20190321-LE-GRAND-DEBAT_alceste_1/Analyse.ira"
#analysein = "/home/pierre/fac/etudiant/grumet/M2/Corpus_focus_GRUMET_corpus_2/Corpus_focus_GRUMET[5682]_alceste_3/Analyse.ira"
#parametres = DoConf(analysein).getoptions()

#actives = cmd.corpus.make_actives_nb(10000, 1)[0]
#actives = dict(zip(actives,actives))
#print len(actives)
#print cmd.ConfigPath


class MergeClusterGraph :
    def __init__(self, ira, corpus, parametres) :
        self.ira = ira
        self.corpus = corpus
        self.parametres = parametres
        self.pathout = PathOut(parametres['ira'])
        self.pathout.basefiles(ChdTxtPathOut)
        self.corpus.make_ucecl_from_R(self.pathout['uce'])
        self.encoding = self.parametres['encoding']
        self.clnb = parametres['clnb']
        dictprofile = ReadProfileAsDico(self.pathout['PROFILE_OUT'], True, self.encoding)
        self.dograph(dictprofile)

    def dograph(self, dictprofile) :
        tomerge = []
        #OUTCH!!First cluster removed !!
        #print 'ELMINATION CLUSTER 1'
        for i in range(0, self.clnb):
            self.pathout = PathOut(self.parametres['ira'])
            simiparam = DoConf(self.ira.ConfigPath['simitxt']).getoptions()
            simiparam['coeff'] = 3
            simiparam['cexfromchi'] = True
            profclasse = dictprofile[`i+1`]
            line1 = profclasse.pop(0)
            classen = [line for line in profclasse if line[0] != '*' and line[0] != '*****']
            try :
                self.lenact = profclasse.index([u'*****', u'*', u'*', u'*', u'*', u'*', '', ''])
                profclasse.pop(self.lenact)
            except ValueError:
                try :
                    self.lenact = profclasse.index([u'*', u'*', u'*', u'*', u'*', u'*', '', ''])
                    profclasse.pop(self.lenact)
                except ValueError:
                    self.lenact = len(profclasse)
            try :
                self.lensup = profclasse.index([u'*', u'*', u'*', u'*', u'*', u'*', '', ''])
                self.lensup = self.lensup - self.lenact
                profclasse.pop(self.lensup)
            except ValueError:
                self.lensup = len(profclasse) - self.lenact
            self.lenet = len(profclasse) - (self.lenact + self.lensup)
#            print self.lenact, self.lensup, self.lenet
            for l,  line in enumerate(classen) :
                line[0] = l
            dictdata = dict(zip([l for l in range(0,len(classen))], classen))

            if self.lenact != 0 :
                self.la = [dictdata[l][6] for l in range(0, self.lenact)]
                self.lchi = [dictdata[l][4] for l in range(0, self.lenact)]
                self.lfreq = [dictdata[l][1] for l in range(0, self.lenact)]
            else :
                self.la = []
                self.lchi = []
                self.lfreq = []
            print 'cluster : ', i
            simi = SimiFromCluster(self.ira, self.corpus, self.la, self.lfreq,
                            self.lchi, i, parametres = simiparam, limit=100)
            tomerge.append(simi.parametres['ira'])
            print tomerge
        newparam = {'type': 'merge', 'fileout' : '/tmp/test.txt'}
        newparam['graphs'] = tomerge
        AnalyseMerge(self.ira, newparam, dlg=None)


#MergeClusterGraph(cmd, cmd.corpus, parametres)
