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
        self.scriptout = self.pathout['temp']
        self.script =  u"#Script genere par IRaMuTeQ - %s" % datetime.now().ctime()
    
    def add(self, txt) :
        self.script = '\n'.join([self.script, txt])
    
    def defvar(self, name, value) :
        self.add(' <- '.join([name, value]))

    def defvars(self, lvars) :
        for val in lvars :
            self.defvar(val[0],val[1])

    def sources(self, lsources) :
        for source in lsources :
            self.add('source("%s")' % source)

    def load(self, l) :
        for val in l :
            self.add('load("%s")' % val)

    def write(self) :
        with open(self.scriptout, 'w') as f :
            f.write(self.script)


class chdtxt(PrintRScript) :
    pass


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


def RchdTxt(DicoPath, RscriptPath, mincl, classif_mode, nbt = 9, libsvdc = False, libsvdc_path = None, R_max_mem = False):
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
    if libsvdc :
        txt += """
        libsvdc <- TRUE
        libsvdc.path <- "%s"
        """ % ffr(libsvdc_path)
    else :
        txt += """
        libsvdc <- FALSE
        libsvdc.path <- NULL
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
    chd1<-CHD(data1, x = nbt, libsvdc = libsvdc, libsvdc.path = libsvdc.path)
    """
    
    if classif_mode == 0:
        txt += """
    chd2<-CHD(data2, x = nbt, libsvdc = libsvdc, libsvdc.path = libsvdc.path)
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
#    rm(data1)
    """
    
    if classif_mode == 0:
        txt += """
#        rm(data2)
        """
    txt += """
    chd.result <- Rchdtxt("%s",mincl=%i,classif_mode=%i, nbt = nbt)
    n1 <- chd.result$n1
    classeuce1 <- chd.result$cuce1
    classeuce2 <- chd.result$cuce2
    """ % (DicoPath['uce'], mincl, classif_mode)
    
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
    plot.dendropr(tree.cut1$tree.cl,classes)
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
    DicoPath = corpus.dictpathout
    param = corpus.parametre
    print param
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
    """ % (DicoPath['Act01'], DicoPath['listeuce1'], DicoPath['uce'])
    
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
    plot.dendropr(tree_cut1$tree.cl,classes)
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
        xlab <- paste('facteur 1 - ', round(afc$facteur[1,2],2), sep = '')
        ylab <- paste('facteur 2 - ', round(afc$facteur[2,2],2), sep = '')
        xlab <- paste(xlab, ' %', sep = '')
        ylab <- paste(ylab, ' %', sep = '')
        """
    
        txt += """
    PARCEX<-%s
    """ % taillecar
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=1, fin=(debsup-1), xlab = xlab, ylab = ylab)
    """ % (DictChdTxtOut['AFC2DL_OUT'])
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=debsup, fin=(debet-1), xlab = xlab, ylab = ylab)
    """ % (DictChdTxtOut['AFC2DSL_OUT'])
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='coord', deb=debet, fin=fin, xlab = xlab, ylab = ylab)
    """ % (DictChdTxtOut['AFC2DEL_OUT'])
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col=TRUE, what='coord', xlab = xlab, ylab = ylab)
    """ % (DictChdTxtOut['AFC2DCL_OUT'])
        txt += """
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=1, fin=(debsup-1), xlab = xlab, ylab = ylab)
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=debsup, fin=(debet-1), xlab = xlab, ylab = ylab)
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", what='crl', deb=debet, fin=fin, xlab = xlab, ylab = ylab)
    PlotAfc2dCoul(afc, as.data.frame(chistabletot), "%s", col=TRUE, what='crl', xlab = xlab, ylab = ylab)
    """ % (DictChdTxtOut['AFC2DCoul'], DictChdTxtOut['AFC2DCoulSup'], DictChdTxtOut['AFC2DCoulEt'], DictChdTxtOut['AFC2DCoulCl'])
       
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

    if self.param['cex_txt'] : cex_txt = 'TRUE'
    else : cex_txt = 'FALSE'

    if self.param['tchi'] : tchi = 'TRUE'
    else : tchi = 'FALSE'

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
    ffr(os.path.dirname(self.fileout)))
    return scripts
        
def print_simi3d(self):
    simi3d = self.parent.simi3dpanel
    txt = '#Fichier genere par Iramuteq'
    if simi3d.movie.GetValue() :
        movie = "'" + ffr(os.path.dirname(self.DictPathOut['RData'])) + "'"
    else :
        movie = 'NULL'
    if self.section == 'chd_dist_quest' :
        header = 'TRUE'
    else :
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
            inf <- NA
            di <- matrix(data=%s, nrow=%i, byrow = TRUE)
            di[is.na(di)] <- max(di, na.rm=TRUE) + 2
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
        coord <- barplot(as.matrix(di), beside = TRUE, col = color, space = c(0.1,0.6))
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

