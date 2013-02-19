# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2008-2011 Pierre Ratinaud
#Lisense: GNU/GPL

import tempfile
from chemins import ffr
import os
import locale
from datetime import datetime
import logging

log = logging.getLogger('iramuteq.printRscript')

class PrintRScript :
    def __init__ (self, analyse):
        log.info('Rscript')
        self.pathout = analyse.pathout
        self.analyse = analyse
        self.parametres = analyse.parametres
        self.scriptout = self.pathout['temp']
        self.script =  u"#Script genere par IRaMuTeQ - %s\n" % datetime.now().ctime()
    
    def add(self, txt) :
        self.script = '\n'.join([self.script, txt])
    
    def defvar(self, name, value) :
        self.add(' <- '.join([name, value]))

    def defvars(self, lvars) :
        for val in lvars :
            self.defvar(val[0],val[1])

    def sources(self, lsources) :
        for source in lsources :
            self.add('source("%s", encoding = \'utf8\')' % source)

    def packages(self, lpks) :
        for pk in lpks :
            self.add('library(%s)' % pk)

    def load(self, l) :
        for val in l :
            self.add('load("%s")' % val)

    def write(self) :
        with open(self.scriptout, 'w') as f :
            f.write(self.script)


class chdtxt(PrintRScript) :
    pass

def Rcolor(color) :
    return str(color).replace(')', ', max=255)')

class Alceste2(PrintRScript) :
    def doscript(self) :
        self.sources(['chdfunct'])
        self.load(['Rdata'])
        lvars = [['clnb', `self.analyse.clnb`], 
                ['Contout', '"%s"' % self.pathout['Contout']],
                ['ContSupOut', '"%s"' % self.pathout['ContSupOut']],
                ['ContEtOut', '"%s"' % self.pathout['ContEtOut']],
                ['profileout', '"%s"' % self.pathout['profils.csv']],
                ['antiout', '"%s"' % self.pathout['antiprofils.csv']],
                ['chisqtable', '"%s"' % self.pathout['chisqtable.csv']],
                ['ptable', '"%s"' % self.pathout['ptable.csv']]]
       
        self.defvars(lvars) 



#    txt = "clnb<-%i\n" % clnb
#    txt += """
#source("%s")
#load("%s")
#""" % (RscriptsPath['chdfunct'], DictChdTxtOut['RData'])
#    txt += """
#dataact<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
#datasup<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
#dataet<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
#""" % (DictChdTxtOut['Contout'], DictChdTxtOut['ContSupOut'], DictChdTxtOut['ContEtOut'])
#    txt += """
#tablesqrpact<-BuildProf(as.matrix(dataact),n1,clnb)
#tablesqrpsup<-BuildProf(as.matrix(datasup),n1,clnb)
#tablesqrpet<-BuildProf(as.matrix(dataet),n1,clnb)
#"""
#    txt += """
#PrintProfile(n1,tablesqrpact[4],tablesqrpet[4],tablesqrpact[5],tablesqrpet[5],clnb,"%s","%s",tablesqrpsup[4],tablesqrpsup[5])
#""" % (DictChdTxtOut['PROFILE_OUT'], DictChdTxtOut['ANTIPRO_OUT'])
#    txt += """
#colnames(tablesqrpact[[2]])<-paste('classe',1:clnb,sep=' ')
#colnames(tablesqrpact[[1]])<-paste('classe',1:clnb,sep=' ')
#colnames(tablesqrpsup[[2]])<-paste('classe',1:clnb,sep=' ')
#colnames(tablesqrpsup[[1]])<-paste('classe',1:clnb,sep=' ')
#colnames(tablesqrpet[[2]])<-paste('classe',1:clnb,sep=' ')
#colnames(tablesqrpet[[1]])<-paste('classe',1:clnb,sep=' ')
#chistabletot<-rbind(tablesqrpact[2][[1]],tablesqrpsup[2][[1]])
#chistabletot<-rbind(chistabletot,tablesqrpet[2][[1]])
#ptabletot<-rbind(tablesqrpact[1][[1]],tablesqrpet[1][[1]])
#"""
#    txt += """
#write.csv2(chistabletot,file="%s")
#write.csv2(ptabletot,file="%s")
#gbcluster<-n1
#write.csv2(gbcluster,file="%s")
#""" % (DictChdTxtOut['chisqtable'], DictChdTxtOut['ptable'], DictChdTxtOut['SbyClasseOut'])
#


def RchdTxt(DicoPath, RscriptPath, mincl, classif_mode, nbt = 9, svdmethod = 'svdR', libsvdc = False, libsvdc_path = None, R_max_mem = False, mode_patate = False):
    txt = """
    source("%s")
    source("%s")
    source("%s")
    source("%s")
    """ % (RscriptPath['CHD'], RscriptPath['chdtxt'], RscriptPath['anacor'], RscriptPath['Rgraph'])
    if R_max_mem :
        txt += """
    memory.limit(%i)
        """ % R_max_mem

    txt += """
    nbt <- %i
    """ % nbt
    if svdmethod == 'svdlibc' and libsvdc :
        txt += """
        svd.method <- 'svdlibc'
        libsvdc.path <- "%s"
        """ % ffr(libsvdc_path)
    elif svdmethod == 'irlba' :
        txt += """
        library(irlba)
        svd.method <- 'irlba'
        libsvdc.path <- NULL
        """
    else :
        txt += """
        svd.method = 'svdR'
        libsvdc.path <- NULL
        """
    if mode_patate :
        txt += """
        mode.patate = TRUE
        """
    else :
        txt += """
        mode.patate = FALSE
        """
    txt +="""
    library(Matrix)
    data1 <- readMM("%s")
    data1 <- as(data1, "dgCMatrix")
    row.names(data1) <- 1:nrow(data1)
    """ % DicoPath['TableUc1']
    
    if classif_mode == 0:
        txt += """
        data2 <- readMM("%s")
        data2 <- as(data2, "dgCMatrix")
        row.names(data2) <- 1:nrow(data2)
        """ % DicoPath['TableUc2']
    txt += """
    chd1<-CHD(data1, x = nbt, mode.patate = mode.patate, svd.method = svd.method, libsvdc.path = libsvdc.path)
    """
    
    if classif_mode == 0:
        txt += """
    chd2<-CHD(data2, x = nbt, mode.patate = mode.patate, svd.method = svd.method, libsvdc.path = libsvdc.path)
    """
    else:
        txt += """
    chd2<-chd1
    """    
    
    txt += """
    #lecture des uce
    listuce1<-read.csv2("%s")
    """ % DicoPath['listeuce1']
    
    if classif_mode == 0:
        txt += """
        listuce2<-read.csv2("%s")
        """ % DicoPath['listeuce2']
        
    txt += """
    rm(data1)
    """
    
    if classif_mode == 0:
        txt += """
        rm(data2)
        """
    txt += """
    classif_mode <- %i
    mincl <- %i
    uceout <- "%s"
    if (classif_mode == 0) {
        chd.result <- Rchdtxt(uceout, chd1, chd2 = chd2, mincl = mincl,classif_mode = classif_mode, nbt = nbt)
    } else {
        chd.result <- Rchdtxt(uceout, chd1, chd2 = chd1, mincl = mincl,classif_mode = classif_mode, nbt = nbt)
    }
    n1 <- chd.result$n1
    classeuce1 <- chd.result$cuce1
    classeuce2 <- chd.result$cuce2
    """ % (classif_mode, mincl, DicoPath['uce'])
    
    txt += """
    tree.tot1 <- make_tree_tot(chd1)
#    open_file_graph("%s", widt = 600, height=400)
#    plot(tree.tot1$tree.cl)
#    dev.off()
    """%DicoPath['arbre1']
    
    if classif_mode == 0:
        txt += """
        tree.tot2 <- make_tree_tot(chd2)
#        open_file_graph("%s", width = 600, height=400)
#        plot(tree.tot2$tree.cl)
#        dev.off()
        """ % DicoPath['arbre2']  
              
    txt += """
    tree.cut1 <- make_dendro_cut_tuple(tree.tot1$dendro_tuple, chd.result$coord_ok, classeuce1, 1, nbt)
    save(tree.cut1, file="%s")
    classes<-n1[,ncol(n1)]
    open_file_graph("%s", width = 600, height=400)
    plot.dendropr(tree.cut1$tree.cl,classes, histo=TRUE)
    open_file_graph("%s", width = 600, height=400)
    plot(tree.cut1$dendro_tot_cl)
    dev.off()
    """ % (DicoPath['Rdendro'], DicoPath['dendro1'], DicoPath['arbre1'])
    
    if classif_mode == 0:
        txt += """
        tree.cut2 <- make_dendro_cut_tuple(tree.tot2$dendro_tuple, chd.result$coord_ok, classeuce2, 2, nbt)
        open_file_graph("%s", width = 600, height=400)
        plot(tree.cut2$tree.cl)
        dev.off()
        open_file_graph("%s", width = 600, height=400)
        plot(tree.cut1$dendro_tot_cl)
        dev.off()
        """ % (DicoPath['dendro2'], DicoPath['arbre2'])
        
    txt += """
    save.image(file="%s")
    """ % DicoPath['RData']
    fileout = open(DicoPath['Rchdtxt'], 'w')
    fileout.write(txt)
    fileout.close()

def RPamTxt(corpus, RscriptPath):
    DicoPath = corpus.pathout
    param = corpus.parametres
    txt = """
    source("%s")
    """ % (RscriptPath['pamtxt'])
    txt += """
    source("%s")
    """ % (RscriptPath['Rgraph'])
    txt += """
    result <- pamtxt("%s", "%s", "%s", method = "%s", clust_type = "%s", clnb = %i)
    n1 <- result$uce
    """ % (DicoPath['TableUc1'], DicoPath['listeuce1'], DicoPath['uce'], param['method'], param['cluster_type'], param['nbcl'] )
    txt += """
    open_file_graph("%s", width=400, height=400)
    plot(result$cl)
    dev.off()
    """ % (DicoPath['arbre1'])
    txt += """
    save.image(file="%s")
    """ % DicoPath['RData']
    fileout = open(DicoPath['Rchdtxt'], 'w')
    fileout.write(txt)
    fileout.close()
    

def RchdQuest(DicoPath, RscriptPath, nbcl = 10, mincl = 10):
    txt = """
    source("%s")
    source("%s")
    source("%s")
    source("%s")
    """ % (RscriptPath['CHD'], RscriptPath['chdquest'], RscriptPath['anacor'],RscriptPath['Rgraph'])

    txt += """
    nbt <- %i - 1
    mincl <- %i
    """ % (nbcl, mincl)

    txt += """
    chd.result<-Rchdquest("%s","%s","%s", nbt = nbt, mincl = mincl)
    n1 <- chd.result$n1
    classeuce1 <- chd.result$cuce1
    """ % (DicoPath['mat01'], DicoPath['listeuce1'], DicoPath['uce'])
    
    txt += """
    tree_tot1 <- make_tree_tot(chd.result$chd)
    open_file_graph("%s", width = 600, height=400)
    plot(tree_tot1$tree.cl)
    dev.off()
    """%DicoPath['arbre1']
    
    txt += """
    tree_cut1 <- make_dendro_cut_tuple(tree_tot1$dendro_tuple, chd.result$coord_ok, classeuce1, 1, nbt)
    tree.cut1 <- tree_cut1
    save(tree.cut1, file="%s")
    open_file_graph("%s", width = 600, height=400)
    classes<-n1[,ncol(n1)]
    plot.dendropr(tree_cut1$tree.cl,classes, histo = TRUE)
    """ % (DicoPath['Rdendro'],DicoPath['dendro1'])
    
    txt += """
    save.image(file="%s")
    """ % DicoPath['RData']
    fileout = open(DicoPath['Rchdquest'], 'w')
    fileout.write(txt)
    fileout.close()
    
def AlcesteTxtProf(DictChdTxtOut, RscriptsPath, clnb, taillecar):
    txt = "clnb<-%i\n" % clnb
    txt += """
source("%s")
load("%s")
""" % (RscriptsPath['chdfunct'], DictChdTxtOut['RData'])
    txt += """
dataact<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
datasup<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
dataet<-read.csv2("%s", header = FALSE, sep = ';',quote = '\"', row.names = 1, na.strings = 'NA')
""" % (DictChdTxtOut['Contout'], DictChdTxtOut['ContSupOut'], DictChdTxtOut['ContEtOut'])
    txt += """
tablesqrpact<-BuildProf(as.matrix(dataact),n1,clnb)
tablesqrpsup<-BuildProf(as.matrix(datasup),n1,clnb)
tablesqrpet<-BuildProf(as.matrix(dataet),n1,clnb)
"""
    txt += """
PrintProfile(n1,tablesqrpact[4],tablesqrpet[4],tablesqrpact[5],tablesqrpet[5],clnb,"%s","%s",tablesqrpsup[4],tablesqrpsup[5])
""" % (DictChdTxtOut['PROFILE_OUT'], DictChdTxtOut['ANTIPRO_OUT'])
    txt += """
colnames(tablesqrpact[[2]])<-paste('classe',1:clnb,sep=' ')
colnames(tablesqrpact[[1]])<-paste('classe',1:clnb,sep=' ')
colnames(tablesqrpsup[[2]])<-paste('classe',1:clnb,sep=' ')
colnames(tablesqrpsup[[1]])<-paste('classe',1:clnb,sep=' ')
colnames(tablesqrpet[[2]])<-paste('classe',1:clnb,sep=' ')
colnames(tablesqrpet[[1]])<-paste('classe',1:clnb,sep=' ')
chistabletot<-rbind(tablesqrpact[2][[1]],tablesqrpsup[2][[1]])
chistabletot<-rbind(chistabletot,tablesqrpet[2][[1]])
ptabletot<-rbind(tablesqrpact[1][[1]],tablesqrpet[1][[1]])
"""
    txt += """
write.csv2(chistabletot,file="%s")
write.csv2(ptabletot,file="%s")
gbcluster<-n1
write.csv2(gbcluster,file="%s")
""" % (DictChdTxtOut['chisqtable'], DictChdTxtOut['ptable'], DictChdTxtOut['SbyClasseOut'])
    if clnb > 2 :
        txt += """
    library(ca)
    colnames(dataact)<-paste('classe',1:clnb,sep=' ')
    colnames(datasup)<-paste('classe',1:clnb,sep=' ')
    colnames(dataet)<-paste('classe',1:clnb,sep=' ')
    rowtot<-nrow(dataact)+nrow(dataet)+nrow(datasup)
    afctable<-rbind(as.matrix(dataact),as.matrix(datasup))
    afctable<-rbind(afctable,as.matrix(dataet))
    colnames(afctable)<-paste('classe',1:clnb,sep=' ')
    afc<-ca(afctable,suprow=((nrow(dataact)+1):rowtot),nd=(ncol(afctable)-1))
    debsup<-nrow(dataact)+1
    debet<-nrow(dataact)+nrow(datasup)+1
    fin<-rowtot
    afc<-AddCorrelationOk(afc)
    """
    #FIXME : split this!!!
        txt += """
    source("%s")
    """ % RscriptsPath['Rgraph']
    
        txt += """
        afc <- summary.ca.dm(afc)
        afc_table <- create_afc_table(afc)
        write.csv2(afc_table$facteur, file = "%s")
        write.csv2(afc_table$colonne, file = "%s")
        write.csv2(afc_table$ligne, file = "%s")
        """ % (DictChdTxtOut['afc_facteur'], DictChdTxtOut['afc_col'], DictChdTxtOut['afc_row'])
    
        txt += """
    PARCEX<-%s
    """ % taillecar
        txt += """
    xyminmax <- PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=1, fin=(debsup-1), xlab = xlab, ylab = ylab)
    """ % (DictChdTxtOut['AFC2DL_OUT'])
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=debsup, fin=(debet-1), xlab = xlab, ylab = ylab, xmin = xyminmax$xminmax[1], xmax = xyminmax$xminmax[2], ymin = xyminmax$yminmax[1], ymax = xyminmax$yminmax[2])
    """ % (DictChdTxtOut['AFC2DSL_OUT'])
        txt += """
        if ((fin - debet) > 2) {
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=debet, fin=fin, xlab = xlab, ylab = ylab, xmin = xyminmax$xminmax[1], xmax = xyminmax$xminmax[2], ymin = xyminmax$yminmax[1], ymax = xyminmax$yminmax[2])
        }
    """ % (DictChdTxtOut['AFC2DEL_OUT'])
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col=TRUE, what='coord', xlab = xlab, ylab = ylab, xmin = xyminmax$xminmax[1], xmax = xyminmax$xminmax[2], ymin = xyminmax$yminmax[1], ymax = xyminmax$yminmax[2])
    """ % (DictChdTxtOut['AFC2DCL_OUT'])
#        txt += """
 #   PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=1, fin=(debsup-1), xlab = xlab, ylab = ylab)
 #   PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=debsup, fin=(debet-1), xlab = xlab, ylab = ylab)
  #  PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=debet, fin=fin, xlab = xlab, ylab = ylab)
 #   PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col=TRUE, what='crl', xlab = xlab, ylab = ylab)
 #   """ % (DictChdTxtOut['AFC2DCoul'], DictChdTxtOut['AFC2DCoulSup'], DictChdTxtOut['AFC2DCoulEt'], DictChdTxtOut['AFC2DCoulCl'])
       
    txt += """
#rm(dataact)
#rm(datasup)
#rm(dataet)
rm(tablesqrpact)
rm(tablesqrpsup)
rm(tablesqrpet)
save.image(file="%s")
""" % DictChdTxtOut['RData']
    file = open(DictChdTxtOut['RTxtProfGraph'], 'w')
    file.write(txt)
    file.close()


def write_afc_graph(self):
    if self.param['over'] : over = 'TRUE'
    else : over = 'FALSE'

    if self.param['do_select_nb'] : do_select_nb = 'TRUE'
    else : do_select_nb = 'FALSE'

    if self.param['do_select_chi'] : do_select_chi = 'TRUE'
    else : do_select_chi = 'FALSE'

    if self.param['do_select_chi_classe'] : do_select_chi_classe = 'TRUE'
    else : do_select_chi_classe = 'FALSE'

    if self.param['cex_txt'] : cex_txt = 'TRUE'
    else : cex_txt = 'FALSE'

    if self.param['tchi'] : tchi = 'TRUE'
    else : tchi = 'FALSE'

    if self.param['svg'] : svg = 'TRUE'
    else : svg = 'FALSE'

    with open(self.RscriptsPath['afc_graph'], 'r') as f:
        txt = f.read()

#    self.DictPathOut['RData'], \
    scripts = txt % (self.RscriptsPath['Rgraph'],\
    self.param['typegraph'], \
    self.param['what'], \
    self.param['facteur'][0],\
    self.param['facteur'][1], \
    self.param['facteur'][2], \
    self.param['qui'], \
    over,  do_select_nb, \
    self.param['select_nb'],  \
    do_select_chi, \
    self.param['select_chi'], \
    do_select_chi_classe, \
    self.param['nbchic'], \
    cex_txt, \
    self.param['txt_min'], \
    self.param['txt_max'], \
    self.fileout, \
    self.param['width'], \
    self.param['height'],\
    self.param['taillecar'], \
    self.param['alpha'], \
    self.param['film'], \
    tchi,\
    self.param['tchi_min'],\
    self.param['tchi_max'],\
    ffr(os.path.dirname(self.fileout)),\
    svg)
    return scripts
        
def print_simi3d(self):
    simi3d = self.parent.simi3dpanel
    txt = '#Fichier genere par Iramuteq'
    if simi3d.movie.GetValue() :
        movie = "'" + ffr(os.path.dirname(self.DictPathOut['RData'])) + "'"
    else :
        movie = 'NULL'
    
    #if self.corpus.parametres['type'] == 'corpus' :
    #    header = 'TRUE'
    #else :
    #    header = 'FALSE'
    header = 'FALSE'
    txt += """
    dm<-read.csv2("%s",row.names=1,header = %s)
    load("%s")
    """ % (self.DictPathOut['Contout'], header, self.DictPathOut['RData'])
    
    txt += """
    source("%s")
    """ % self.parent.RscriptsPath['Rgraph']


    txt += """
    make.simi.afc(dm,chistabletot, lim=%i, alpha = %.2f, movie = %s)
    """ % (simi3d.spin_1.GetValue(), float(simi3d.slider_1.GetValue())/100, movie)
    tmpfile = tempfile.mktemp(dir=self.parent.TEMPDIR)
    tmp = open(tmpfile,'w')
    tmp.write(txt)
    tmp.close()
    return tmpfile

def dendroandbarplot(table, rownames, colnames, rgraph, tmpgraph, intxt = False, dendro=False) :
    if not intxt :
        txttable = 'c(' + ','.join([','.join(line) for line in table]) + ')'
    rownb = len(rownames)
    rownames = 'c("' + '","'.join(rownames) + '")'
    colnames = 'c("' + '","'.join(colnames) + '")'
    if not intxt :
        #FIXME
        txt = """
            di <- matrix(data=%s, nrow=%i, byrow = TRUE)
            rownames(di)<- %s
            colnames(di) <- %s
        """ % (txttable, rownb, rownames, colnames)
    else :
        txt = intxt
    txt += """
        load("%s")
        library(ape)
        source("%s")
        height <- (30*ncol(di)) + (15*nrow(di))
        height <- ifelse(height <= 400, 400, height)
        width <- 500
        open_file_graph("%s", width=width, height=height)
        plot.dendro.lex(tree.cut1$tree.cl, di)
        """ % (ffr(dendro),ffr(rgraph),  ffr(tmpgraph))
    return txt

def barplot(table, rownames, colnames, rgraph, tmpgraph, intxt = False) :
    if not intxt :
        txttable = 'c(' + ','.join([','.join(line) for line in table]) + ')'
    #width = 100 + (15 * len(rownames)) + (100 * len(colnames))
    #height =  len(rownames) * 15
    rownb = len(rownames)
    #if height < 400 :
    #    height = 400
    rownames = 'c("' + '","'.join(rownames) + '")'
    colnames = 'c("' + '","'.join(colnames) + '")'

    if not intxt :
        #FIXME
        txt = """
            di <- matrix(data=%s, nrow=%i, byrow = TRUE)
            toinf <- which(di == Inf)
            tominf <- which(di == -Inf)
            if (length(toinf)) {
                di[toinf] <- NA
                valmax <- max(di, na.rm = TRUE)
                if (valmax <= 0) {
                    valmax <- 2
                } else {
                    valmax <- valmax + 2
                }
                di[toinf] <- valmax
            }
            if (length(tominf)) {
                di[tominf] <- NA
                valmin <- min(di, na.rm = TRUE)
                if (valmin >=0) {
                    valmin <- -2
                } else {
                    valmin <- valmin - 2
                }
                di[tominf] <- valmin
            }
            rownames(di)<- %s
            colnames(di) <- %s
        """ % (txttable, rownb, rownames, colnames)
    else :
        txt = intxt
    txt += """
        source("%s")
        color = rainbow(nrow(di))
        width <- 100 + (20*length(rownames(di))) + (100 * length(colnames(di)))
        height <- nrow(di) * 15
        if (height < 400) { height <- 400}
        open_file_graph("%s",width = width, height = height)
    	par(mar=c(0,0,0,0))
	    layout(matrix(c(1,2),1,2, byrow=TRUE),widths=c(3,lcm(7)))
        par(mar=c(2,2,1,0))
        yp = ifelse(length(toinf), 0.2, 0)
        ym = ifelse(length(tominf), 0.2, 0)
        ymin <- ifelse(!length(which(di < 0)), 0, min(di) - ym)
        coord <- barplot(as.matrix(di), beside = TRUE, col = color, space = c(0.1,0.6), ylim=c(ymin, max(di) + yp))
        if (length(toinf)) {
            coordinf <- coord[toinf]
            valinf <- di[toinf]
            text(x=coordinf, y=valinf + 0.1, 'i')
        }
        if (length(tominf)) {
            coordinf <- coord[toinf]
            valinf <- di[toinf]
            text(x=coordinf, y=valinf - 0.1, 'i')
        }            
        c <- colMeans(coord)
        c1 <- c[-1]
        c2 <- c[-length(c)]
        cc <- cbind(c1,c2)
        lcoord <- apply(cc, 1, mean)
        abline(v=lcoord)
        if (min(di) < 0) {
            amp <- abs(max(di) - min(di))
        } else {
            amp <- max(di)
        }
        if (amp < 10) {
            d <- 2
        } else {
            d <- signif(amp%%/%%10,1)
        }
        mn <- round(min(di))
        mx <- round(max(di))
        for (i in mn:mx) {
            if ((i/d) == (i%%/%%d)) { 
                abline(h=i,lty=3)
            }
        }
        par(mar=c(0,0,0,0))
        plot(0, axes = FALSE, pch = '')
        legend(x = 'center' , rownames(di), fill = color)
        dev.off()
        """ % (rgraph, ffr(tmpgraph))    
    return txt

#def RAfcUci(DictAfcUciOut, nd=2, RscriptsPath='', PARCEX='0.8'):
#    txt = """
#    library(ca)
#    nd<-%i
#    """ % nd
#    txt += """
#    dataact<-read.csv2("%s")
#    """ % (DictAfcUciOut['TableCont'])#, encoding)
#    txt += """
#    datasup<-read.csv2("%s")
#    """ % (DictAfcUciOut['TableSup'])#, encoding)
#    txt += """
#    dataet<-read.csv2("%s")
#    """ % (DictAfcUciOut['TableEt'])#, encoding)
#    txt += """
#    datatotsup<-cbind(dataact,datasup)
#    datatotet<-cbind(dataact,dataet)
#    afcact<-ca(dataact,nd=nd)
#    afcsup<-ca(datatotsup,supcol=((ncol(dataact)+1):ncol(datatotsup)),nd=nd)
#    afcet<-ca(datatotet,supcol=((ncol(dataact)+1):ncol(datatotet)),nd=nd)
#    afctot<-afcsup$colcoord
#    rownames(afctot)<-afcsup$colnames
#    colnames(afctot)<-paste('coord. facteur',1:nd,sep=' ')
#    afctot<-cbind(afctot,mass=afcsup$colmass)
#    afctot<-cbind(afctot,distance=afcsup$coldist)
#    afctot<-cbind(afctot,intertie=afcsup$colinertia)
#    rcolet<-afcet$colsup
#    afctmp<-afcet$colcoord[rcolet,]
#    rownames(afctmp)<-afcet$colnames[rcolet]
#    afctmp<-cbind(afctmp,afcet$colmass[rcolet])
#    afctmp<-cbind(afctmp,afcet$coldist[rcolet])
#    afctmp<-cbind(afctmp,afcet$colinertia[rcolet])
#    afctot<-rbind(afctot,afctmp)
#    write.csv2(afctot,file = "%s")
#    source("%s")
#    """ % (DictAfcUciOut['afc_row'], RscriptsPath['Rgraph'])
#    txt += """
#    PARCEX=%s
#    """ % PARCEX
#    #FIXME
#    txt += """
#    PlotAfc(afcet,filename="%s",toplot=c%s, PARCEX=PARCEX)
#    """ % (DictAfcUciOut['AfcColAct'], "('none','active')")
#    txt += """
#    PlotAfc(afcsup,filename="%s",toplot=c%s, PARCEX=PARCEX)
#    """ % (DictAfcUciOut['AfcColSup'], "('none','passive')")
#    txt += """PlotAfc(afcet,filename="%s", toplot=c%s, PARCEX=PARCEX)
#    """ % (DictAfcUciOut['AfcColEt'], "('none','passive')")
#    txt += """
#    PlotAfc(afcet,filename="%s", toplot=c%s, PARCEX=PARCEX)
#    """ % (DictAfcUciOut['AfcRow'], "('all','none')")
#    f = open(DictAfcUciOut['Rafcuci'], 'w')
#    f.write(txt)
#    f.close()

class PrintSimiScript(PrintRScript) :
    def make_script(self) :
        self.txtgraph = ''
        self.packages(['igraph', 'proxy', 'Matrix'])
        self.sources([self.analyse.parent.RscriptsPath['simi'], self.analyse.parent.RscriptsPath['Rgraph']])
        txt = ''
        if not self.parametres['keep_coord'] and not self.parametres['type'] == 'simimatrix':
            txt += """
            dm.path <- "%s"
            cn.path <- "%s"
            selected.col <- "%s"
            """ % (self.pathout['mat01.csv'], self.pathout['actives.csv'], self.pathout['selected.csv'])
            if 'word' in self.parametres :
                txt += """
                word <- TRUE
                index <- %i + 1
                """ % self.parametres['word']
            else :
                txt += """
                word <- FALSE
                """
            txt += """
            dm <-readMM(dm.path)
            cn <- read.table(cn.path, sep='\t', quote='"')
            colnames(dm) <- cn[,1]
            sel.col <- read.csv2(selected.col, header = FALSE)
            sel.col <- sel.col[,1] + 1
            if (!word) {
                dm <- dm[, sel.col]
            } else {
                forme <- colnames(dm)[index]
                if (!index %in% sel.col) {
                    sel.col <- append(sel.col, index)
                }
                dm <- dm[, sel.col]
                index <- which(colnames(dm) == forme)
            }
            """
        elif not self.parametres['keep_coord'] and self.parametres['type'] == 'simimatrix' :
            txt += """
            dm.path <- "%s"
            selected.col <- "%s"
            """ % (self.pathout['mat01.csv'], self.pathout['selected.csv'])
            if 'word' in self.parametres :
                txt += """
                word <- TRUE
                index <- %i + 1
                """ % self.parametres['word']
            else :
                txt += """
                word <- FALSE
                """
            txt += """
            dm <-read.csv2(dm.path)
            dm <- as.matrix(dm)
            sel.col <- read.csv2(selected.col, header = FALSE)
            sel.col <- sel.col[,1] + 1
            if (!word) {
                dm <- dm[, sel.col]
            } else {
                forme <- colnames(dm)[index]
                if (!index %in% sel.col) {
                    sel.col <- append(sel.col, index)
                }
                dm <- dm[, sel.col]
                index <- which(colnames(dm) == forme)
            }
            """
        else :
            txt += """
            load("%s")
            """ % self.pathout['RData.RData']
        
        if self.parametres['coeff'] == 0 :
            method = 'cooc'
            if not self.parametres['keep_coord'] :
                txt += """
                method <- 'cooc'
                mat <- make.a(dm)
                """
        else :
            if not self.parametres['keep_coord'] :
                txt += """
                dm <- as.matrix(dm)
                """
        if self.parametres['coeff'] == 1 :
            method = 'prcooc'
            txt += """
            method <- 'Russel'
            mat <- simil(dm, method = 'Russel', diag = TRUE, upper = TRUE, by_rows = FALSE)
            """
        elif self.analyse.indices[self.parametres['coeff']] == 'binomial' :
            method = 'binomial'
            if not self.parametres['keep_coord'] :
                txt += """
                method <- 'binomial'
                mat <- binom.sim(dm)
                """
        elif self.parametres['coeff'] != 0 :
            method = self.analyse.indices[self.parametres['coeff']]
            if not self.parametres['keep_coord'] :
                txt += """
                method <-"%s"
                mat <- simil(dm, method = method, diag = TRUE, upper = TRUE, by_rows = FALSE)
                """ % self.analyse.indices[self.parametres['coeff']]
        if not self.parametres['keep_coord'] :
            txt += """
            mat <- as.matrix(stats::as.dist(mat,diag=TRUE,upper=TRUE))
            mat[is.na(mat)] <- 0
            if (length(which(mat == Inf))) {
                infp <- which(mat == Inf)
                mat[infp] <- NA
                maxmat <- max(mat, na.rm = TRUE)
                if (maxmat > 0) {
                maxmat <- maxmat + 1
                } else {
                    maxmat <- 0
                }
                mat[infp] <- maxmat
            }
            if (length(which(mat == -Inf))) {
                infm <- which(mat == -Inf)
                mat[infm] <- NA
                minmat <- min(mat, na.rm = TRUE)
                if (maxmat < 0) {
                minmat <- minmat - 1
                } else {
                    minmat <- 0
                }
                mat[infm] <- minmat
            }
            """
        if 'word' in self.parametres and not self.parametres['keep_coord'] :
            txt += """
            mat <- graph.word(mat, index)
            cs <- colSums(mat)
            if (length(cs)) mat <- mat[,-which(cs==0)]
            rs <- rowSums(mat)
            if (length(rs)) mat <- mat[-which(rs==0),]
            if (length(cs)) dm <- dm[, -which(cs==0)]
            """

        if self.parametres['layout'] == 0 : layout = 'random'
        if self.parametres['layout'] == 1 : layout = 'circle'
        if self.parametres['layout'] == 2 : layout = 'frutch'
        if self.parametres['layout'] == 3 : layout = 'kawa'
        if self.parametres['layout'] == 4 : layout = 'graphopt'


        self.filename=''
        if self.parametres['type_graph'] == 0 : type = 'tkplot'
        if self.parametres['type_graph'] == 1 : 
            graphnb = 1
            type = 'nplot'
            dirout = os.path.dirname(self.pathout['mat01'])
            while os.path.exists(os.path.join(dirout,'graph_simi_'+str(graphnb)+'.png')):
                graphnb +=1
            self.filename = ffr(os.path.join(dirout,'graph_simi_'+str(graphnb)+'.png'))
        if self.parametres['type_graph'] == 2 : type = 'rgl'

        if self.parametres['arbremax'] : 
            arbremax = 'TRUE'
            self.txtgraph += ' - arbre maximum'
        else : arbremax = 'FALSE'
        
        if self.parametres['coeff_tv'] : 
            coeff_tv = self.parametres['coeff_tv_nb']
            tvminmax = 'c(NULL,NULL)'
        elif not self.parametres['coeff_tv'] or self.parametres.get('sformchi', False) :
            coeff_tv = 'NULL'
            tvminmax = 'c(%i, %i)' %(self.parametres['tvmin'], self.parametres['tvmax'])
        if self.parametres['coeff_te'] : coeff_te = 'c(%i,%i)' % (self.parametres['coeff_temin'], self.parametres['coeff_temax'])
        else : coeff_te = 'NULL'
        
        if self.parametres['vcex'] or self.parametres.get('cexfromchi', False) :
            vcexminmax = 'c(%i/10,%i/10)' % (self.parametres['vcexmin'],self.parametres['vcexmax'])
        else :
            vcexminmax = 'c(NULL,NULL)'
        if not self.parametres['label_v'] : label_v = 'FALSE'
        else : label_v = 'TRUE'

        if not self.parametres['label_e'] : label_e = 'FALSE'
        else : label_e = 'TRUE'
        
        if self.parametres['seuil_ok'] : seuil = str(self.parametres['seuil'])
        else : seuil = 'NULL'
            
        cols = str(self.parametres['cols']).replace(')',', max=255)')
        cola = str(self.parametres['cola']).replace(')',',max=255)')

        txt += """
        minmaxeff <- %s
        """ % tvminmax
        txt += """
        vcexminmax <- %s
        """ % vcexminmax
        txt += """
        cex = %i/10
        """ % self.parametres['cex']

        if self.parametres['film'] : 
            txt += """
            film <- "%s"
            """ % self.pathout['film']
        else : 
            txt += """
            film <- NULL
            """
        txt += """
        seuil <- %s
        """ % seuil
        
        txt += """
        label.v <- %s
        label.e <- %s
        """ % (label_v, label_e)
        txt += """
        cols <- rgb%s
        cola <- rgb%s
        """ % (cols, cola)
        txt += """
        width <- %i
        height <- %i
        """ % (self.parametres['width'], self.parametres['height'])
        if self.parametres['keep_coord'] :
            txt += """
            coords <- try(coords, TRUE)
            if (!is.matrix(coords)) {
                coords<-NULL
            }
            """
        else :
            txt += """
            coords <- NULL
            """
        txt += """
        alpha <- %i/100
        """ % self.parametres['alpha']
        txt += """
        alpha <- %i/100
        """ % self.parametres['alpha']
#############################################
        if  self.parametres.get('bystar',False) :
            txt += """
            et <- list()
            """
            for i, line in enumerate(self.parametres['listet']) :
                txt+= """
                et[[%i]] <- c(%s)
                """ % (i+1, ','.join([`val + 1` for val in line]))
            txt+= """
            unetoile <- c('%s')
            """ % ("','".join([val for val in self.parametres['selectedstars']]))
            txt += """
            fsum <- NULL
            rs <- rowSums(dm)
            for (i in 1:length(unetoile)) {
                print(unetoile[i])
                tosum <- et[[i]]
                if (length(tosum) > 1) {
                    fsum <- cbind(fsum, colSums(dm[tosum,]))
                } else {
                    fsum <- cbind(fsum, dm[tosum,])
                }
            }
            source("%s")
            lex <- AsLexico2(fsum, chip=TRUE)
            dcol <- apply(lex[[4]],1,which.max)
            toblack <- apply(lex[[4]],1,max)
            gcol <- rainbow(length(unetoile))
            #gcol[2] <- 'orange'
            vertex.label.color <- gcol[dcol]
            vertex.label.color[which(toblack <= 3.84)] <- 'black'
            leg <- list(unetoile=unetoile, gcol=gcol)  
            cols <- vertex.label.color
            chivertex.size <- norm.vec(toblack, vcexminmax[1],  vcexminmax[2])
            
            """ % (self.analyse.parent.RscriptsPath['chdfunct'])
        else :
            txt += """
            vertex.label.color <- 'black' 
            chivertex.size <- 1
            leg<-NULL
            """
#############################################        

#        txt += """
#        eff <- colSums(dm)
#        g.ori <- graph.adjacency(mat, mode='lower', weighted = TRUE)
#        w.ori <- E(g.ori)$weight
#        if (max.tree) {
#            if (method == 'cooc') {
#                E(g.ori)$weight <- 1 / w.ori
#            } else {
#                E(g.ori)$weigth <- 1 - w.ori
#            }
#            g.max <- minimum.spanning.tree(g.ori)
#            if (method == 'cooc') {
#                E(g.max)$weight <- 1 / E(g.max)$weight
#            } else {
#                E(g.max)$weight <- 1 - E(g.max)$weight
#            }
#            g.toplot <- g.max
#        } else {
#            g.toplot <- g.ori
#        }
#        """
        if self.parametres['com'] :
            com = `self.parametres['communities']`
        else :
            com = 'NULL'
        if self.parametres['halo'] :
            halo = 'TRUE'
        else :
            halo = 'FALSE'
        txt += """
        communities <- %s
        halo <- %s
        """ % (com, halo)
        txt += """
        eff <- colSums(dm)
        x <- list(mat = mat, eff = eff)
        graph.simi <- do.simi(x, method='%s', seuil = seuil, p.type = '%s', layout.type = '%s', max.tree = %s, coeff.vertex=%s, coeff.edge = %s, minmaxeff = minmaxeff, vcexminmax = vcexminmax, cex = cex, coords = coords, communities = communities, halo = halo)
        """ % (method, type, layout, arbremax, coeff_tv, coeff_te)
            
        if self.parametres.get('bystar',False) :
            if self.parametres.get('cexfromchi', False) :
                txt+="""
                    label.cex<-chivertex.size
                    """
            else :
                txt+="""
                label.cex <- NULL
                """
            if self.parametres.get('sfromchi', False) :
                txt += """
                vertex.size <- norm.vec(toblack, minmaxeff[1], minmaxeff[2])
                """
            else :
                txt += """
                vertex.size <- NULL
                """
        else :
            if self.parametres['type'] == 'clustersimitxt' : 
                txt += """
                lchi <- read.table("%s")
                lchi <- lchi[,1]
                """ % ffr(self.parametres['tmpchi'])
                txt += """
                    lchi <- lchi[sel.col]
                    """
            if self.parametres['type'] == 'clustersimitxt' and self.parametres.get('cexfromchi', False) :
                txt += """ 
                label.cex <- norm.vec(lchi, vcexminmax[1], vcexminmax[2])
                """
            else :
                txt += """
            if (is.null(vcexminmax[1])) {
                label.cex <- NULL
            } else {
                label.cex <- graph.simi$label.cex
            }
            """
            if self.parametres['type'] == 'clustersimitxt' and self.parametres.get('sfromchi', False) :
                txt += """ 
                vertex.size <- norm.vec(lchi, minmaxeff[1], minmaxeff[2])
                if (!length(vertex.size)) vertex.size <- 0
                """
            else :
                txt += """
            if (is.null(minmaxeff[1])) {
                vertex.size <- 0
            } else {
                vertex.size <- graph.simi$eff
            }
            """
        #txt += """ vertex.size <- NULL """
        if self.parametres['svg'] : svg = 'TRUE'
        else : svg = 'FALSE'
        txt += """
        svg <- %s
        """ % svg
        txt += """
        vertex.col <- cols
        if (!is.null(graph.simi$com)) {
            com <- graph.simi$com
            colm <- rainbow(length(com))
            if (vertex.size != 0 || graph.simi$halo) {
                vertex.label.color <- 'black'
                vertex.col <- colm[membership(com)]
            } else {
                vertex.label.color <- colm[membership(com)]
            }
        }
        coords <- plot.simi(graph.simi, p.type='%s',filename="%s", vertex.label = label.v, edge.label = label.e, vertex.col = vertex.col, vertex.label.color = vertex.label.color, vertex.label.cex=label.cex, vertex.size = vertex.size, edge.col = cola, leg=leg, width = width, height = height, alpha = alpha, movie = film, svg = svg)
        save.image(file="%s")
        """ % (type, self.filename, self.pathout['RData'])
        
        self.add(txt)
        self.write()

class WordCloudRScript(PrintRScript) :
    def make_script(self) :
        self.sources([self.analyse.parent.RscriptsPath['Rgraph']])
        self.packages(['wordcloud'])
        bg_col = Rcolor(self.parametres['col_bg'])
        txt_col = Rcolor(self.parametres['col_text'])
        if self.parametres['svg'] :
            svg = 'TRUE'
        else :
            svg = 'FALSE'
        txt = """
        svg <- %s
        """ % svg
        txt += """
        act <- read.csv2("%s", header = FALSE, row.names=1, sep='\t')
        selected.col <- read.table("%s")
        toprint <- as.matrix(act[selected.col[,1] + 1,])
        rownames(toprint) <- rownames(act)[selected.col[,1] + 1]
        maxword <- %i
        if (nrow(toprint) > maxword) {
            toprint <- as.matrix(toprint[order(toprint[,1], decreasing=TRUE),])
            toprint <- as.matrix(toprint[1:maxword,])
        }
        open_file_graph("%s", width = %i, height = %i , svg = svg)
        par(bg=rgb%s)
        wordcloud(row.names(toprint), toprint[,1], scale=c(%f,%f), random.order=FALSE, colors=rgb%s)
        dev.off()
        """ % (ffr(self.analyse.pathout['actives_eff.csv']), ffr(self.analyse.pathout['selected.csv']), self.parametres['maxword'], ffr(self.parametres['graphout']), self.parametres['width'], self.parametres['height'], bg_col, self.parametres['maxcex'], self.parametres['mincex'], txt_col)
        self.add(txt)
        self.write()
