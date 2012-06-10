#!/bin/env python
# -*- coding: utf-8 -*-
#Author: Pierre Ratinaud
#Copyright (c) 2009-2010 Pierre Ratinaud
#Lisense: GNU/GPL

from chemins import ConstructPathOut, construct_simipath, ffr
from functions import print_liste, exec_rcode, read_list_file, check_Rresult, indices_simi, treat_var_mod
from dialog import PrefSimi, SelectColDial, OptLexi
from listlex import *
import wx
import wx.lib.agw.aui as aui
from numpy import *
import os
import tempfile
import datetime
from ConfigParser import RawConfigParser
from time import sleep

class DoSimi():
    def __init__(self, parent, param = None, isopen = False, fromprof = False, pathout = False, filename ='', gparent = False, wordgraph = False, listactives = False, actives = False, cmd = False, openfromprof=False):
#------------------------------------------------------------------- 
        self.fromprof = fromprof
        self.wordgraph = wordgraph
        self.listactives = listactives
        self.actives = actives
        self.openfromprof = openfromprof
        self.cmd = cmd
        if param is not None and fromprof:
            self.paramsimi = param
        else :
            self.paramsimi = {'coeff' : 0,
                          'layout' : 2,
                          'type' : 1,
                          'arbremax' : 1,
                          'coeff_tv' : 0,
                          'coeff_tv_nb' : 10,
                          'tvprop' : 1,
                          'tvmin' : 5,
                          'tvmax' : 30,
                          'coeff_te' : 1,
                          'coeff_temin' : 1,
                          'coeff_temax' : 10,
                          'label_v': 1,
                          'label_e': 1,
                          'vcex' : 0,
                          'vcexmin' : 8,
                          'vcexmax' : 25,
                          'cex' : 10,
                          'seuil_ok' : 0,
                          'seuil' : 1,
                          'cols' : (255,0,0),
                          'cola' : (200,200,200),
                          'width' : 800,
                          'height' : 800,
                          'first' : True,
                          'keep_coord' : False,
                          'alpha' : 10,
                          'film' : False,
                          }
        self.types = indices_simi
        if fromprof :
            self.parent = parent.parent
            self.Source = parent
        else :
            self.parent = parent   
            self.Source = None
           
        self.RPath = self.parent.PathPath.get('PATHS', 'rpath')
        if not isopen :
            if not fromprof :
                self.tableau = self.parent.tableau
            else :
                self.tableau = parent.tableau
            self.tableau.parametre['mineff'] = 0
            self.dial = PrefSimi(parent, -1, self.paramsimi, self.types)
            self.dial.CenterOnParent()
            self.val = self.dial.ShowModal()
            if self.val == wx.ID_OK :
                self.paramsimi = self.make_param()
                self.dial.Destroy()
                if self.paramsimi.get('bystar', False) :
                    variables = treat_var_mod(self.tableau.listet)
                    dial = OptLexi(self.parent)
                    dial.listet = self.tableau.listet
                    var = [v for v in variables]
                    dial.variables = var
                    for et in var :
                        dial.list_box_1.Append(et)
                    dial.CenterOnParent()
                    val = dial.ShowModal()
                    if val == wx.ID_OK :
                        if dial.choice.GetSelection() == 1 :
                            listet = [self.tableau.listet[i] for i in dial.list_box_1.GetSelections()]
                        else :
                            listet = variables[var[dial.list_box_1.GetSelections()[0]]]
                        dial.Destroy()
                        self.tableau.etline = self.Source.corpus.make_etline(listet)

                dlg = wx.ProgressDialog("Traitements",
                                       "Veuillez patienter...",
                                       maximum=4,
                                       parent=self.parent,
                                       style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME
                                        )
                dlg.Center()
                count = 1
                keepGoing = dlg.Update(count)
        #-------------------------------------------------------------------
                self.DictForme = {}
                self.Min = 10
                self.Linecontent = []
        #-----------------------------------------------------------
                count += 1
                if not fromprof :
                    self.pathout = ConstructPathOut(parent.tableau.parametre['filename'], 'Simi')
                    self.DictPathOut = construct_simipath(self.pathout)
                    self.parent.tableau.dictpathout = self.DictPathOut
                    dlg.Update(count, u"passage en O/1")
                    self.parent.tableau.make_01_from_selection(range(0,self.parent.tableau.colnb))
                    #self.Linecontent = parent.table
                    #self.ListTo01Form()
                else :
                    self.pathout = pathout
                    self.DictPathOut = construct_simipath(self.pathout)
                    self.DictPathOut['mat01'] = fromprof
                self.PrintScript()
                count += 1
                dlg.Update(count, u"R...") 
                self.DoR(dlg)
                self.make_ira()
                count += 1
                dlg.Update(count, u"") 
                dlg.Destroy()
                #self.dial.Destroy()
                #self.dolayout()
                from openanalyse import OpenAnalyse
                if self.fromprof :
                    fromprof = True
                else:
                    fromprof = False
                OpenAnalyse(self.parent, self.DictPathOut['ira'], False, simifromprof=fromprof)
            else:
                self.dial.Destroy()
        else :
            self.tableau = gparent.tableau
            if 'corpus' in dir(gparent) :
                self.Source = gparent
            self.tableau.parametre['mineff'] = 0
            self.DictPathOut = construct_simipath(os.path.abspath(os.path.dirname(filename)))
            self.dolayout()
            self.paramsimi['first'] = False
            self.paramsimi['coeff'] = int(param.get('simi', 'indice'))
            self.paramsimi['layout'] = int(param.get('simi', 'layout'))
            self.paramsimi['seuil_ok'] = param.getboolean('simi', 'seuil_ok')
            self.paramsimi['seuil'] = int(param.get('simi', 'seuil'))
            if param.get('simi', 'wordgraph') == 'False' :
                self.wordgraph = False
            else :
                self.wordgraph = param.get('simi', 'wordgraph')
            if 'listet' in dir(self.tableau) :
                self.paramsimi['stars'] = self.tableau.listet
                self.paramsimi['bystar'] = False
                self.paramsimi['cexfromchi'] = True
                self.paramsimi['tvprop'] = False
                self.paramsimi['sfromchi'] = False
                self.paramsimi['coeff_te'] = True
                self.paramsimi['coeff_tv'] = True
                self.paramsimi['coeff_tv_nb'] = 0
                self.paramsimi['label_e'] = False
                self.paramsimi['width'] = 1000
                self.paramsimi['height'] = 1000
         

    def make_param(self) :
        if self.paramsimi['first'] :
            keep_coord = False
        else :
            keep_coord = self.dial.check_coord.GetValue()
        self.select = self.dial.check_colch.GetValue()

        paramsimi = {'coeff' : self.dial.choice1.GetSelection(),
                          'layout' : self.dial.choice2.GetSelection(),
                          'type' : self.dial.choice3.GetSelection(),
                          'arbremax' : self.dial.check1.GetValue(),
                          'coeff_tv' : self.dial.check_s_size.GetValue(),
                          'coeff_tv_nb' : self.dial.spin_tv.GetValue(),
                          'tvprop' : self.dial.check2.GetValue(),
                          'tvmin' : self.dial.spin_tvmin.GetValue(),
                          'tvmax' : self.dial.spin_tvmax.GetValue(),
                          'coeff_te' : self.dial.check3.GetValue(),
                          'coeff_temin' : self.dial.spin_temin.GetValue(),
                          'coeff_temax' : self.dial.spin_temax.GetValue(),
                          'label_e' : self.dial.check_elab.GetValue(),
                          'label_v' : self.dial.check_vlab.GetValue(),
                          'vcex' : self.dial.check_vcex.GetValue(),
                          'vcexmin' : self.dial.spin_vcexmin.GetValue(),
                          'vcexmax' : self.dial.spin_vcexmax.GetValue(),
                          'cex' : self.dial.spin_cex.GetValue(),
                          'seuil_ok' : self.dial.check_seuil.GetValue(),
                          'seuil' : self.dial.spin_seuil.GetValue(),
                          'cols' : self.dial.cols.GetColour(),
                          'cola' : self.dial.cola.GetColour(),
                          'width' : self.dial.spin_width.GetValue(),
                          'height' : self.dial.spin_height.GetValue(),
                          'first' : False,
                          'keep_coord' : keep_coord,
                          'alpha' : self.dial.slider_sphere.GetValue(),
                          'film' : self.dial.film.GetValue()
                          }
        if 'cexfromchi' in self.paramsimi :
            paramsimi['cexfromchi'] = self.dial.checkit.GetValue()
        if 'sfromchi' in self.paramsimi :
            paramsimi['sfromchi'] = self.dial.checki.GetValue()
        if 'vlabcolor' in self.paramsimi :
           paramsimi['vlabcolor'] = self.paramsimi['vlabcolor']
        if 'check_bystar' in dir(self.dial) :
            paramsimi['bystar'] = self.dial.check_bystar.GetValue()
            paramsimi['stars'] = self.paramsimi['stars']
        return paramsimi
        
    def make_ira(self):
        self.tableau.save_tableau(self.DictPathOut['db'])
        conf = RawConfigParser()
        conf.read(self.DictPathOut['ira'])
        if not 'simi' in conf.sections() :
            conf.add_section('simi')
        date = datetime.datetime.now().ctime()
        conf.set('simi', 'date', str(date))
        conf.set('simi', 'indice', self.paramsimi['coeff'])
        conf.set('simi','layout', self.paramsimi['layout'])
        conf.set('simi', 'seuil_ok', self.paramsimi['seuil_ok'])
        conf.set('simi', 'seuil', str(self.paramsimi['seuil']))
        conf.set('simi', 'wordgraph', self.wordgraph)
        fileout = open(self.DictPathOut['ira'], 'w')
        conf.write(fileout)
        fileout.close()
        
    def PrintScript(self):
        if self.select :
            if self.listactives :
                lactives = self.listactives
            else :
                lactives = self.tableau.listactives
            if self.actives :
                acts = self.actives
            else :
                acts = self.tableau.actives
            dictcol = [[i, [active, acts[active][0]]] for i, active in enumerate(lactives)]
            dictcol = dict(dictcol)
            dlg = SelectColDial(self.parent)
            listcol = ListForSpec(dlg, self, dictcol, ['forme', 'eff'])
            dlg.bSizer2.Add( listcol, 2, wx.ALL|wx.EXPAND, 5 )
            dlg.m_sdbSizer2.AddButton( dlg.m_sdbSizer2OK )
            dlg.m_sdbSizer2.Realize()
            dlg.bSizer2.Add( dlg.m_sdbSizer2, 0, wx.EXPAND, 5 )
            dlg.Layout()
            if not 'selected_col' in dir(self.tableau) :
                for row in xrange(listcol.list.GetItemCount()):
                    listcol.list.Select(row)
            else :
                for row in self.tableau.selected_col :
                    listcol.list.Select(row)
            dlg.CenterOnParent()
            val = dlg.ShowModal()
            datas = [listcol.getColumnText(listcol.list.GetFirstSelected(),0)]
            last = listcol.list.GetFirstSelected()
            lastl = [listcol.list.GetFirstSelected()]
            while listcol.list.GetNextSelected(last) != -1:
                last = listcol.list.GetNextSelected(last)
                lastl.append(last)
                datas.append(listcol.getColumnText(last,0))
            dlg.Destroy()
            datas = [lactives.index(val) for val in datas]
            self.tableau.selected_col = lastl
            self.tableau.datas = datas
            datas = str(tuple(datas))
        elif not self.select and 'selected_col' in dir(self.tableau) :
            datas = str(tuple(self.tableau.datas))
        elif self.wordgraph :
            col = self.tableau.listactives.index(self.wordgraph)

        tmpchi = False
        if (self.fromprof or self.openfromprof) and (self.paramsimi.get('cexfromchi', False) or self.paramsimi.get('sfromchi', False)):
            if 'lchi' in dir(self.tableau) :
                tmpchi = tempfile.mktemp(dir=self.parent.TEMPDIR)
                with open(tmpchi, 'w') as f:
                    f.write('\n'.join([str(val) for val in self.tableau.lchi]))

        active_file = tempfile.mktemp(dir=self.parent.TEMPDIR)
        if self.listactives :
            lactives = self.listactives
        else :
            lactives = self.tableau.listactives
        self.tableau.listactives = lactives
        with open(active_file, 'w') as f: 
            f.write('\n'.join(lactives))

        txt = '#script genere par Iramuteq'
        txt += """
        library('igraph')
        library('proxy')
        library('Matrix')
        """
        if os.path.exists(self.DictPathOut['RData']) :
            txt += """
            load("%s")
            """ % self.DictPathOut['RData']
        if not self.paramsimi['keep_coord'] :
            #FIXME : beurk!!
            i = 0
            market = False
            with open(self.DictPathOut['mat01'],'r') as f :
                for line in f.readlines() :
                    if 'MatrixMarket' in line :
                        market = True
                        break
                    elif i >= 1 :
                        market = False
                        break
                    i += 1
            print market
            #if (self.fromprof or 'fromtxt' in self.tableau.parametre or self.openfromprof) and not self.actives :
            if market :
                txt += """
                dm <-readMM("%s")
                """ % self.DictPathOut['mat01']
            else :
                txt += """
                dm <- read.csv2("%s")
                """ % self.DictPathOut['mat01']
            txt += """    
            dm <- as.matrix(dm)
            #dml <- apply(dm, 2, as.logical)
            """
            if not self.paramsimi['keep_coord'] :
                txt += """
                cn <- read.table("%s", sep=';', quote='"')
                colnames(dm) <- cn[,1]
                #colnames(dml) <- cn[,1]
                """ % ffr(active_file)
        if 'selected_col' in dir(self.tableau) and not self.paramsimi['keep_coord']:
            txt += """
            #dml <- dml[, c%s+1]
            dm <- dm[, c%s+1]
            """ % (datas, datas)
        txt += """
        source("%s")
        source("%s")
        """ % (self.parent.RscriptsPath['simi'],self.parent.RscriptsPath['Rgraph'])

        self.txtgraph = ''
        self.txtgraph += self.types[self.paramsimi['coeff']]
        if not self.paramsimi['keep_coord'] :
            if self.paramsimi['coeff'] == 0 :
                method = 'cooc'
                txt += """
                method <- 'cooc'
                mat <- make.a(dm)
                """
            elif self.paramsimi['coeff'] == 1 :
                method = 'prcooc'
                txt += """
                method <- 'Russel'
                mat <- simil(dm, method = 'Russel', diag = TRUE, upper = TRUE, by_rows = FALSE)
                """
            elif self.types[self.paramsimi['coeff']] == 'binomial' :
                method = 'binomial'
                txt += """
                method <- 'binomial'
                mat <- binom.sim(dm)
                """
            else :
                method = self.types[self.paramsimi['coeff']]
                txt += """
                method <-"%s"
                mat <- simil(dm, method = method, diag = TRUE, upper = TRUE, by_rows = FALSE)
                """ % self.types[self.paramsimi['coeff']]
            txt += """
            mat <- as.matrix(stats::as.dist(mat,diag=TRUE,upper=TRUE))
            mat[is.na(mat)] <- 0
            mat[is.infinite(mat)] <- 0
            """
            if self.types[self.paramsimi['coeff']] not in ['cooccurrence', 'Chi-squared', 'Mozley', 'Stiles'] :
                txt += """
                mat <- mat * 100
                """
            if self.wordgraph :
                txt += """
                mat <- graph.word(mat, %i)
                """ % (col + 1)
            txt += """
            eff <- colSums(dm)
            x <- list(mat = mat, eff = eff)
            """
        else :
            method = ''
        if self.paramsimi['layout'] == 0 : layout = 'random'
        if self.paramsimi['layout'] == 1 : layout = 'circle'
        if self.paramsimi['layout'] == 2 : layout = 'frutch'
        if self.paramsimi['layout'] == 3 : layout = 'kawa'
        if self.paramsimi['layout'] == 4 : layout = 'graphopt'
        
        self.filename=''
        if self.paramsimi['type'] == 0 : type = 'tkplot'
        if self.paramsimi['type'] == 1 : 
            graphnb = 1
            type = 'nplot'
            dirout = os.path.dirname(self.DictPathOut['mat01'])
            while os.path.exists(os.path.join(dirout,'graph_simi_'+str(graphnb)+'.png')):
                graphnb +=1
            self.filename = ffr(os.path.join(dirout,'graph_simi_'+str(graphnb)+'.png'))
        if self.paramsimi['type'] == 2 : type = 'rgl'
     
        if self.paramsimi['arbremax'] : 
            arbremax = 'TRUE'
            self.txtgraph += ' - arbre maximum'
        else : arbremax = 'FALSE'
        
        if self.paramsimi['coeff_tv'] : 
            coeff_tv = self.paramsimi['coeff_tv_nb']
            tvminmax = 'c(NULL,NULL)'
        elif not self.paramsimi['coeff_tv'] or self.paramsimi.get('sformchi', False) :
            coeff_tv = 'NULL'
            tvminmax = 'c(%i, %i)' %(self.paramsimi['tvmin'], self.paramsimi['tvmax'])
        txt += """
        minmaxeff <- %s
        """ % tvminmax
        
        if self.paramsimi['coeff_te'] : coeff_te = 'c(%i,%i)' % (self.paramsimi['coeff_temin'], self.paramsimi['coeff_temax'])
        else : coeff_te = 'NULL'
        
        if self.paramsimi['vcex'] or self.paramsimi.get('cexfromchi', False) :
            vcexminmax = 'c(%i/10,%i/10)' % (self.paramsimi['vcexmin'],self.paramsimi['vcexmax'])
        else :
            vcexminmax = 'c(NULL,NULL)'   

        txt += """
        vcexminmax <- %s
        """ % vcexminmax

        txt += """
        cex = %i/10
        """ % self.paramsimi['cex']

        if not self.paramsimi['label_v'] : label_v = 'FALSE'
        else : label_v = 'TRUE'

        if not self.paramsimi['label_e'] : label_e = 'FALSE'
        else : label_e = 'TRUE'
        
        if self.paramsimi['seuil_ok'] : seuil = str(self.paramsimi['seuil'])
        else : seuil = 'NULL'

        if self.paramsimi['film'] : 
            txt += """
            film <- "%s"
            """ % self.DictPathOut['film']
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

        cols = str(self.paramsimi['cols']).replace(')',', max=255)')
        cola = str(self.paramsimi['cola']).replace(')',',max=255)')

        txt += """
        cols <- rgb%s
        cola <- rgb%s
        """ % (cols, cola)

        txt += """
        width <- %i
        height <- %i
        """ % (self.paramsimi['width'], self.paramsimi['height'])

        if self.paramsimi['keep_coord'] :
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
        """ % self.paramsimi['alpha']

        if  self.paramsimi.get('bystar',False) :
            txt += """
            et <- list()
            """
            for i,et in enumerate(self.tableau.etline) :
                txt+= """
                et[[%i]] <- c(%s)
                """ % (i+1, ','.join(et[1:]))
            txt+= """
            unetoile <- c('%s')
            """ % ("','".join([val[0] for val in self.tableau.etline]))
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
            
            """ % (self.parent.RscriptsPath['chdfunct'])
        else :
            txt += """
            vertex.label.color <- 'black' 
            chivertex.size <- 1
            leg<-NULL
            """
        #if not self.paramsimi['keep_coord'] :
        txt += """
            graph.simi <- do.simi(x, method='%s', seuil = seuil, p.type = '%s', layout.type = '%s', max.tree = %s, coeff.vertex=%s, coeff.edge = %s, minmaxeff = minmaxeff, vcexminmax = vcexminmax, cex = cex, coords = coords)
            """ % (method, type, layout, arbremax, coeff_tv, coeff_te)
        #txt += """
        if self.paramsimi.get('bystar',False) :
            if self.paramsimi.get('cexfromchi', False) :
                txt+="""
                    label.cex<-chivertex.size
                    """
            else :
                txt+="""
                label.cex <- NULL
                """
            if self.paramsimi.get('sfromchi', False) :
                txt += """
                vertex.size <- norm.vec(toblack, minmaxeff[1], minmaxeff[2])
                """
            else :
                txt += """
                vertex.size <- NULL
                """
        else :
            if tmpchi :
                txt += """
                lchi <- read.table("%s")
                lchi <- lchi[,1]
                """ % ffr(tmpchi)
                if 'selected_col' in dir(self.tableau) :
                    txt += """
                    lchi <- lchi[c%s+1]
                    """ % datas
            if tmpchi and self.paramsimi.get('cexfromchi', False) :
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
            if tmpchi and self.paramsimi.get('sfromchi', False) :
                txt += """ 
                vertex.size <- norm.vec(lchi, minmaxeff[1], minmaxeff[2])
                """
            else :
                txt += """
            if (is.null(minmaxeff[1])) {
                vertex.size <- NULL
            } else {
                vertex.size <- graph.simi$eff
            }
            """
        txt += """ vertex.size <- NULL """
        txt += """
        coords <- plot.simi(graph.simi, p.type='%s',filename="%s", vertex.label = label.v, edge.label = label.e, vertex.col = cols, vertex.label.color = vertex.label.color, vertex.label.cex=label.cex, vertex.size = vertex.size, edge.col = cola, leg=leg, width = width, height = height, alpha = alpha, movie = film)
        save.image(file="%s")
        """ % (type, self.filename, self.DictPathOut['RData'])

        self.tmpfile = tempfile.mktemp(dir=self.parent.TEMPDIR)
        tmpscript = open(self.tmpfile, 'w')
        tmpscript.write(txt)
        tmpscript.close()

        if type == 'nplot':
            if os.path.exists(self.DictPathOut['liste_graph']):
                graph_simi = read_list_file(self.DictPathOut['liste_graph'])
                graph_simi.append([os.path.basename(self.filename), self.txtgraph])
            else :
                graph_simi = [[os.path.basename(self.filename), self.txtgraph]]
            print_liste(self.DictPathOut['liste_graph'], graph_simi)
        
    def DoR(self, dlg):
        if self.paramsimi['type'] == 1 :
            graph = False
            wait = False
        else : 
            graph = True
            wait = True
        pid = exec_rcode(self.RPath, self.tmpfile, wait = wait, graph = graph)
        if self.paramsimi['type'] == 1 :
            while pid.poll() == None :
                    if not self.cmd :
                        dlg.Pulse(u'R ...')
                        sleep(0.2)
                    else :
                        sleep(0.2)
            check_Rresult(self.parent, pid)
    
    def dolayout(self):
        if os.path.exists(self.DictPathOut['liste_graph']) :
            list_graph = read_list_file(self.DictPathOut['liste_graph'])
        else : 
            list_graph = [['','']]
        notebook_flags =  aui.AUI_NB_DEFAULT_STYLE | aui.AUI_NB_TAB_EXTERNAL_MOVE | aui.AUI_NB_TAB_MOVE | aui.AUI_NB_TAB_FLOAT
        self.tabsimi = aui.AuiNotebook(self.parent.nb, -1, wx.DefaultPosition)
        self.tabsimi.SetAGWWindowStyleFlag(notebook_flags)
        self.tabsimi.SetArtProvider(aui.ChromeTabArt())
        if 'corpus' in dir(self.Source) :
            self.tabsimi.corpus = self.Source.corpus
        self.graphpan = GraphPanelSimi(self.tabsimi, self.DictPathOut, list_graph)
        self.graphpan.Bind(wx.EVT_BUTTON, self.redosimi, self.graphpan.butafc)
        self.graphpan.Bind(wx.EVT_BUTTON, self.export, self.graphpan.butexport)
        self.tabsimi.AddPage(self.graphpan, 'Graph')
        self.parent.nb.AddPage(self.tabsimi, 'Analyse de graph')
        self.parent.ShowTab(True)
        self.parent.nb.SetSelection(self.parent.nb.GetPageCount() - 1)

    def export(self, evt) :
        fileout = os.path.join(os.path.dirname(self.DictPathOut['ira']), "graphout")
        format_graph = 'gml'
        i=1
        while os.path.exists(fileout + '_%i.' % i + format_graph) :
            i += 1
        fileout_graph = fileout + '_%i.' % i + format_graph 
        fileout_table = fileout + '_table_%i.csv' % i
        Rtxt = """
        library(igraph)
        load("%s")
        fileout <- "%s"
        fileout.table <- "%s"
        format <- "%s"
        id <- (1:length(graph.simi$mat.eff)) - 1
        id <- paste(id, '.0', sep='')
        table.out <- cbind(Id=id, Label=id, Name=graph.simi$v.label, labelcex=graph.simi$label.cex, eff=graph.simi$mat.eff)
        write.graph(graph.simi$graph, fileout, format=format)
        write.csv2(table.out, file = fileout.table, row.names=FALSE)
        """ % (self.DictPathOut['RData'], ffr(fileout_graph), ffr(fileout_table), format_graph)
        tmpfile = tempfile.mktemp(dir=self.parent.TEMPDIR)
        with open(tmpfile, 'w') as f :
            f.write(Rtxt)
        res =  exec_rcode(self.RPath, tmpfile, wait = False)
        check_Rresult(self.parent,res)
        print 'export', Rtxt
 
    def redosimi(self,evt) :
        if self.openfromprof :
            if 'cexfromchi' not in self.paramsimi:
                self.paramsimi['cexfromchi'] = False
                self.paramsimi['sfromchi'] = False
        self.dial = PrefSimi(self.parent, -1, self.paramsimi, self.types)
        self.dial.CenterOnParent()
        val = self.dial.ShowModal()
        if val == wx.ID_OK :
            self.paramsimi = self.make_param()
            self.dial.Destroy()
            if self.paramsimi.get('bystar',False) :
                variables = treat_var_mod(self.paramsimi['stars'])
                dial = OptLexi(self.parent)
                dial.listet = self.paramsimi['stars']
                var = [v for v in variables]
                dial.variables = var
                for et in var :
                    dial.list_box_1.Append(et)
                dial.CenterOnParent()
                val = dial.ShowModal()
                if val == wx.ID_OK :
                    if dial.choice.GetSelection() == 1 :
                        listet = [dial.listet[i] for i in dial.list_box_1.GetSelections()]
                    else :
                        listet = variables[var[dial.list_box_1.GetSelections()[0]]]
                    self.tableau.etline = self.Source.corpus.make_etline(listet)

            dlg = wx.ProgressDialog("Traitements",
                                    "Veuillez patienter...",
                                     maximum=2,
                                     parent=self.parent,
                                     style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT)
            dlg.Center()
            self.PrintScript()
            self.DoR(dlg)
            dlg.Destroy()
            self.make_ira()
            if self.paramsimi['type'] == 1:
                self.graphpan.sizer_3.Add(wx.StaticBitmap(self.graphpan.panel_1, -1, wx.Bitmap(self.filename, wx.BITMAP_TYPE_ANY)), 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
                self.graphpan.sizer_3.Add(wx.StaticText(self.graphpan.panel_1,-1,self.txtgraph), 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
                self.graphpan.sizer_3.Fit(self.graphpan.panel_1)
                self.graphpan.Layout()
                self.graphpan.panel_1.Scroll(0,self.graphpan.panel_1.GetScrollRange(wx.VERTICAL))
        else :
            self.dial.Destroy()

        
class GraphPanelSimi(wx.Panel):
    def __init__(self,parent, dico, list_graph):
        wx.Panel.__init__(self,parent)
        self.afcnb = 1
        self.Dict = dico
        self.dirout = os.path.dirname(self.Dict['ira'])
        self.parent = self.GetParent()#parent
        self.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, 0, "courier"))
        self.labels = []
        self.listimg = []
        self.tabsimi = self.parent.GetParent()
        self.ira = self.tabsimi.GetParent()
        self.panel_1 = wx.ScrolledWindow(self, -1, style=wx.TAB_TRAVERSAL)
        afc_img = wx.Image(os.path.join(self.ira.images_path,'button_simi.jpg'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.butafc = wx.BitmapButton(self, -1, afc_img)
        export_img = wx.Image(os.path.join(self.ira.images_path,'button_export.jpg'), wx.BITMAP_TYPE_ANY).ConvertToBitmap()
        self.butexport = wx.BitmapButton(self, -1, export_img)
        
        for i in range(0,len(list_graph)):
            if os.path.exists(os.path.join(self.dirout,list_graph[i][0])) :
                self.listimg.append(wx.StaticBitmap(self.panel_1, -1, wx.Bitmap(os.path.join(self.dirout,list_graph[i][0]), wx.BITMAP_TYPE_ANY)))
                self.labels.append(wx.StaticText(self.panel_1, -1, list_graph[i][1]))
                
        self.__set_properties()
        self.__do_layout()

    def __set_properties(self):
        self.panel_1.EnableScrolling(True,True)
        #self.panel_1.SetSize((1000,1000))
        self.panel_1.SetScrollRate(20, 20)

    def __do_layout(self):    
        self.sizer_1 = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer_2 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_3 = wx.BoxSizer(wx.VERTICAL)
        self.sizer_2.Add(self.butafc, 0, 0, 0)
        self.sizer_2.Add(self.butexport, 0, 0, 0)
        for i in range(0, len(self.listimg)):
            self.sizer_3.Add(self.listimg[i], 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
            self.sizer_3.Add(self.labels[i], 0, wx.ALIGN_CENTER_HORIZONTAL, 0)
        self.panel_1.SetSizer(self.sizer_3)
        self.sizer_1.Add(self.sizer_2, 0, wx.EXPAND, 0)
        self.sizer_1.Add(self.panel_1, 1, wx.EXPAND, 0)
        self.SetSizer(self.sizer_1) 
