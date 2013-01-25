#Author: Pierre Ratinaud
#Copyright (c) 2008-2009 Pierre Ratinaud
#Lisense: GNU/GPL


#fonction pour la double classification
#cette fonction doit etre splitter en 4 ou 5 fonctions

AssignClasseToUce <- function(listuce, chd) {
    print('assigne classe -> uce')
    chd[listuce[,2]+1,]
}

fille<-function(classe,classeuce) {
	listfm<-unique(unlist(classeuce[classeuce[,classe%/%2]==classe,]))
	listf<-listfm[listfm>=classe]
	listf<-unique(listf)
	listf
}


croiseeff <- function(croise, classeuce1, classeuce2) {
    cl1 <- 0
    cl2 <- 1
    for (i in 1:ncol(classeuce1)) {
        cl1 <- cl1 + 2
        cl2 <- cl2 + 2
        clj1 <- 0
        clj2 <- 1
        for (j in 1:ncol(classeuce2)) {
            clj1 <- clj1 + 2
            clj2 <- clj2 + 2
            croise[cl1 - 1, clj1 -1] <- length(which(classeuce1[,i] == cl1 & classeuce2[,j] == clj1))
            croise[cl1 - 1, clj2 -1] <- length(which(classeuce1[,i] == cl1 & classeuce2[,j] == clj2))
            croise[cl2 - 1, clj1 -1] <- length(which(classeuce1[,i] == cl2 & classeuce2[,j] == clj1))
            croise[cl2 - 1, clj2 -1] <- length(which(classeuce1[,i] == cl2 & classeuce2[,j] == clj2))
        }
    }
    croise
}

addallfille <- function(lf) {
    nlf <- list()
    for (i in 1:length(lf)) {
        if (! is.null(lf[[i]])) {
            nlf[[i]] <- lf[[i]]
            filles <- lf[[i]]
            f1 <- filles[1]
            f2 <- filles[2]
            if (f1 > length(lf)) {
                for (j in (length(lf) + 1):f2) {
                    nlf[[j]] <- 0
                }
            }
        } else {
            nlf[[i]] <- 0
        }
    }
nlf
}

getfille <- function(nlf, classe, pf) {
    if (length(nlf[[classe]]) == 1) {
        return(pf)
    } else {
        pf <- c(pf, nlf[[classe]])
        c1 <- nlf[[classe]][1]
        c2 <- nlf[[classe]][2]
        pf <- getfille(nlf, c1, pf)
        pf <- getfille(nlf, c2, pf)
    }
    return(pf)
}

getmere <- function(list_mere, classe) {
    i <- classe
    pf <- NULL
    while (i != 1 ) {
        pf <- c(pf, list_mere[[i]])
        i <- list_mere[[i]]
    }
    pf
}

getfillemere <- function(list_fille, list_mere, classe) {
    return(c(getfille(list_fille, classe, NULL), getmere(list_mere, classe)))
}

#nbt nbcl = nbt+1 tcl=((nbt+1) *2) - 2  n1[,ncol(n1)], nchd1[,ncol(nchd1)]
Rchdtxt<-function(uceout, chd1, chd2 = NULL, mincl=0, classif_mode=0, nbt = 9) {
	#FIXME: le nombre de classe peut etre inferieur
    nbcl <- nbt + 1
    tcl <- ((nbt+1) * 2) - 2
    #Assignation des classes
	classeuce1<-AssignClasseToUce(listuce1,chd1$n1)
	if (classif_mode==0) {
		classeuce2<-AssignClasseToUce(listuce2,chd2$n1)
    } else {
		classeuce2<-classeuce1
    }

	#calcul des poids (effectifs)

    makepoids <- function(classeuce, poids) {
        cl1 <- 0
        cl2 <- 1
        for (i in 1:nbt) {
            cl1 <- cl1 + 2
            cl2 <- cl2 + 2
            poids[cl1 - 1] <- length(which(classeuce[,i] == cl1))
            poids[cl2 - 1] <- length(which(classeuce[,i] == cl2))
        }
        poids
    }

#	makepoids<-function(classeuce,poids) {
#	    for (classes in 2:(tcl + 1)){
#		    for (i in 1:ncol(classeuce)) {
#		        if (poids[(classes-1)]<length(classeuce[,i][classeuce[,i]==classes])) {
#		            poids[(classes-1)]<-length(classeuce[,i][classeuce[,i]==classes])
#		        }
#		    }
#	    }
#	    poids
#	}
    print('make poids')
	poids1<-vector(mode='integer',length = tcl)
	poids1<-makepoids(classeuce1,poids1)
	if (classif_mode==0) {
		poids2<-vector(mode='integer',length = tcl)
		poids2<-makepoids(classeuce2,poids2)
	} else {
		poids2<-poids1
	}
    
    print('croisement classif')

#    croise=matrix(ncol=tcl,nrow=tcl)
#
#    docroise <- function(croise, classeuce1, classeuce2) {
#    	#production du tableau de contingence
#    	for (i in 1:ncol(classeuce1)) {
#    	    #poids[i]<-length(classeuce1[,i][x==classes])
#    	    for (j in 1:ncol(classeuce2)) {
#    		    tablecroise<-table(classeuce1[,i],classeuce2[,j])
#    		    tabcolnames<-as.numeric(colnames(tablecroise))
#    		    #tabcolnames<-c(tabcolnames[(length(tabcolnames)-1)],tabcolnames[length(tabcolnames)])
#    		    tabrownames<-as.numeric(rownames(tablecroise))
#    		    #tabrownames<-c(tabrownames[(length(tabrownames)-1)],tabrownames[length(tabrownames)])
#    		    for (k in (ncol(tablecroise)-1):ncol(tablecroise)) {
#    		        for (l in (nrow(tablecroise)-1):nrow(tablecroise)) {
#    		            croise[(tabrownames[l]-1),(tabcolnames[k]-1)]<-tablecroise[l,k]
#    		        }
#    		    }
#    	    }
#    	}
#        croise
#    }
    croise <- croiseeff( matrix(ncol=tcl,nrow=tcl), classeuce1, classeuce2)
    if (classif_mode == 0) {ind <- (nbcl * 2)} else {ind <- nbcl}
	if (mincl==0){
		mincl<-round(nrow(classeuce1)/ind)
	}
	if (mincl<3){
		mincl<-3
	}
    print(mincl)	
	#print('table1')
	#print(croise)
	#tableau des chi2 signes
    print('croise chi2')
	#chicroise<-croise

#    nr <- nrow(classeuce1)
#    newchicroise <- function(croise, mincl, nr, poids1, poids2) {
#        chicroise <- croise
#        chicroise[which(croise < mincl)] <- 0
#        tocompute <- which(chicroise > 0, arr.ind = TRUE)
#        for (i in 1:nrow(tocompute)) {
#            chitable <- matrix(ncol=2,nrow=2)
#            chitable[1,1] <- croise[tocompute[i,1],  tocompute[i,2]]
#            chitable[1,2] <- poids1[tocompute[i,1]] - chitable[1,1]
#            chitable[2,1] <- poids2[tocompute[i,2]] - chitable[1,1]
#            chitable[2,2] <- nr - poids2[tocompute[i,2]] - chitable[1,2]
#            chitest<-chisq.test(chitable,correct=FALSE)
#            chicroise[tocompute[i,1],  tocompute[i,2]] <- ifelse(chitable[1,1] > chitest$expected[1,1], round(chitest$statistic,digits=7), -round(chitest$statistic,digits=7))
#        }
#        chicroise
#    }
#
        

	dochicroise <- function(croise, mincl) {
        chicroise <- croise
        for (i in 1:nrow(croise)) {
	        for (j in 1:ncol(croise)) {
	            if (croise[i,j]==0) {
	                chicroise[i,j]<-0
	            } else if (croise[i,j]<mincl) { 
	                chicroise[i,j]<-0
	            } else {
	                chitable<-matrix(ncol=2,nrow=2)
	                chitable[1,1]<-croise[i,j]
	                chitable[1,2]<-poids1[i]-chitable[1,1]
	                chitable[2,1]<-poids2[j]-chitable[1,1]
	                chitable[2,2]<-nrow(classeuce1)-poids2[j]-chitable[1,2]
	                chitest<-chisq.test(chitable,correct=FALSE)
	                if ((chitable[1,1]-chitest$expected[1,1])<0) {
	                    chicroise[i,j]<--round(chitest$statistic,digits=7)
	                } else {
	                    chicroise[i,j]<-round(chitest$statistic,digits=7)
	        #print(chitest)
	                }
	            }
	        }   
	    }
        chicroise
    }
    chicroise <- dochicroise(croise, mincl)
    print('fin croise')
	#print(chicroise)
	#determination des chi2 les plus fort
	chicroiseori<-chicroise

    doxy <- function(chicroise) {
        listx <- NULL
        listy <- NULL
        listxy <- which(chicroise > 3.84, arr.ind = TRUE)
        #print(listxy)
        val <- chicroise[which(chicroise > 3.84)]
        ord <- order(val, decreasing = TRUE)
        listxy <- listxy[ord,]
        #for (i in 1:nrow(listxy)) {
        #    if ((!listxy[,2][i] %in% listx) & (!listxy[,1][i] %in% listy)) {
        #        listx <- c(listx, listxy[,2][i])
        #        listy <- c(listy, listxy[,1][i])
        #    }
        #}
        xy <- list(x = listxy[,2], y = listxy[,1])
        xy
    }
    xy <- doxy(chicroise)
    print(xy)
    listx <- xy$x
    listy <- xy$y

#	maxi<-vector()
#	chimax<-vector()
#	for (i in 1:tcl) {
#	    maxi[i]<-which.max(chicroise)
#	    chimax[i]<-chicroise[maxi[i]]
#	    chicroise[maxi[i]]<-0
#	}
#	testpres<-function(x,listcoord) {
#	    for (i in 1:length(listcoord)) {
#		    if (x==listcoord[i]) {
#		        return(-1)
#		    } else {
#		        a<-1
#		    }
#	    }
#	    a
#	}
#	c.len=nrow(chicroise)
#	r.len=ncol(chicroise)
#	listx<-c(0)
#	listy<-c(0)
#	rang<-0
#	cons<-list()
#	#on garde une valeur par ligne / colonne
#	for (i in 1:length(maxi)) {
#	#coordonnées de chi2 max
#        #coord <- arrayInd(maxi[i], dim(chicroise))
#        #x.co <- coord[1,2]
#        #y.co <- coord[1,1]
#	    x.co<-ceiling(maxi[i]/c.len)
#	    y.co<-maxi[i]-(x.co-1)*c.len
#        #print(x.co)
#        #print(y.co)
#        #print(arrayInd(maxi[i], dim(chicroise)))
#	    a<-testpres(x.co,listx)
#	    b<-testpres(y.co,listy)
#	    
#	    if (a==1) {
#			if (b==1) {
#			    rang<-rang+1
#			    listx[rang]<-x.co
#			    listy[rang]<-y.co
#			}
#	    }
#	    cons[[1]]<-listx
#	    cons[[2]]<-listy
#	}
	#pour ecrire les resultats
	for (i in 1:length(listx)) {
	    txt<-paste(listx[i]+1,listy[i]+1,sep=' ')
	    txt<-paste(txt,croise[listy[i],listx[i]],sep=' ')
	    txt<-paste(txt,chicroiseori[listy[i],listx[i]],sep=' ')
	    print(txt)
	}

	#colonne de la classe
	#trouver les filles et les meres 
	trouvefillemere<-function(classe,chd) {
	    unique(unlist(chd[chd[,classe%/%2]==classe,]))
	}


#----------------------------------------------------------------------
    findbestcoord <- function(classeuce1, classeuce2) {
        #fillemere1 <- NULL
        #fillemere2 <- NULL

        #fillemere1 <- unique(classeuce1)
        #if (classif_mode == 0) {
        #    fillemere2 <- unique(classeuce2)
        #} else {
        #    fillemere2 <- fillemere1
        #}

        #
        listcoordok <- list()
        maxcl <- 0
        nb <- 0
        lf1 <- addallfille(chd1$list_fille) 
        if (classif_mode == 0) {
            lf2 <- addallfille(chd2$list_fille)
        } else {
            lf2 <- lf1
        }
        lme1 <- chd1$list_mere
        if (classif_mode == 0) {
            lme2 <- chd2$list_mere
        } else {
            lme2 <- lme1
        }
        for (first in 1:length(listx)) {
            coordok <- NULL
            f1 <- NULL
            f2 <- NULL
            listxp<-listx
    	    listyp<-listy
            
    	    #listxp<-listx[first:length(listx)]
    	    #listxp<-c(listxp,listx[1:(first-1)])
    	    #listyp<-listy[first:length(listy)]
    	    #listyp<-c(listyp,listy[1:(first-1)])
            listxp <- listxp[order(listx, decreasing = TRUE)]
            listyp <- listyp[order(listx, decreasing = TRUE)]
            #listxp<-c(listxp[first:length(listx)], listx[1:(first-1)])
            #listyp<-c(listyp[first:length(listy)], listy[1:(first-1)])
            for (i in 1:length(listx)) {
                if( (!(listxp[i]+1) %in% f1) & (!(listyp[i]+1) %in% f2) ) {
                    #print(listyp[i]+1)
                    #print('not in')
                    #print(f2)
                    coordok <- rbind(coordok, c(listyp[i] + 1,listxp[i] + 1))
                    #print(c(listyp[i] + 1,listxp[i] + 1))
                    un1 <- getfillemere(lf2, chd2$list_mere, listxp[i] + 1)
                    f1 <- c(f1, un1)
                    f1 <- c(f1, listxp[i] + 1)
                    un2 <- getfillemere(lf1, chd1$list_mere, listyp[i] + 1)
                    f2 <- c(f2, un2)
                    f2 <- c(f2, listyp[i] + 1)
                }
                #print(coordok)
            }
            #if (nrow(coordok) > maxcl) {
                nb <- 1
            #    listcoordok <- list()
                listcoordok[[nb]] <- coordok
            #    maxcl <- nrow(coordok)
            #} else if (nrow(coordok) == maxcl) {
                nb <- nb + 1
            #    listcoordok[[nb]] <- coordok
            #}
        }
        listcoordok <- unique(listcoordok)
        print(listcoordok)
        best <- 1
        if (length(listcoordok) > 1) {
            maxchi <- 0
            for (i in 1:length(listcoordok)) {
                chi <- NULL
                uce <- NULL
                for (j in 1:nrow(listcoordok[[i]])) {
                    chi<-c(chi,croise[(listcoordok[[i]][j,1]-1),(listcoordok[[i]][j,2]-1)])
                    uce<-c(uce,chicroiseori[(listcoordok[[i]][j,1]-1),(listcoordok[[i]][j,2]-1)])
                }
            	if (maxchi < sum(chi)) {
            	    maxchi <- sum(chi)
            	    suce <- sum(uce)
            	    best <- i
            	}
            }
        print(suce/nrow(classeuce1))
        }
        listcoordok[[best]]
    }
#---------------------------------------------------------------------------------   
	#pour trouver une valeur dans une liste
	#is.element(elem, list)
	#== elem%in%list
    oldfindbestcoord <- function(listx, listy) {
    	coordok<-NULL
    	trouvecoordok<-function(first) {
    	    fillemere1<-NULL
    	    fillemere2<-NULL
    	    listxp<-listx
    	    listyp<-listy
    	    listxp<-listx[first:length(listx)]
    	    listxp<-c(listxp,listx[1:(first-1)])
    	    listyp<-listy[first:length(listy)]
    	    listyp<-c(listyp,listy[1:(first-1)])
    	    for (i in 1:length(listxp)) {
    	        if (!(listxp[i]+1)%in%fillemere1) {
    		        if (!(listyp[i]+1)%in%fillemere2) {
    		            coordok<-rbind(coordok,c(listyp[i]+1,listxp[i]+1))
    		            fillemere1<-c(fillemere1,trouvefillemere(listxp[i]+1,chd2$n1))
    		            fillemere2<-c(fillemere2,trouvefillemere(listyp[i]+1,chd1$n1))
    		        }
    	       }
    	    }
    	    coordok
    	}
    #fonction pour trouver le nombre maximum de classes
    	findmaxclasse<-function(listx,listy) {
    	    listcoordok<-list()
    	    maxcl<-0
    	    nb<-1
    	    for (i in 1:length(listy)) {
    			coordok<-trouvecoordok(i)
    			if (maxcl <= nrow(coordok)) {
    			    maxcl<-nrow(coordok)
    			    listcoordok[[nb]]<-coordok
    			    nb<-nb+1
    			}
    	    }
    	    listcoordok<-unique(listcoordok)
            print(listcoordok)
    		#si plusieurs ensemble avec le meme nombre de classe, on conserve
    		#la liste avec le plus fort chi2
    	    if (length(listcoordok)>1) {
    		    maxchi<-0
    		    best<-NULL
    		    for (i in 1:length(listcoordok)) {
    		        chi<-NULL
    		        uce<-NULL
    		        if (nrow(listcoordok[[i]])==maxcl) {
    		            for (j in 1:nrow(listcoordok[[i]])) {
    		                chi<-c(chi,croise[(listcoordok[[i]][j,1]-1),(listcoordok[[i]][j,2]-1)])
    		                uce<-c(uce,chicroiseori[(listcoordok[[i]][j,1]-1),(listcoordok[[i]][j,2]-1)])
    		            }
    		            if (maxchi < sum(chi)) {
    		                maxchi <- sum(chi)
    		                suce <- sum(uce)
    		                best <- i
    		            } 
    		        }
    		    }
    	    }
    	    print((maxchi/nrow(classeuce1)*100))
    	    listcoordok[[best]]
    	}
        print('cherche max')
	    coordok<-findmaxclasse(listx,listy)
	    coordok
    }
	#findmaxclasse(listx,listy)
	#coordok<-trouvecoordok(1)
    #coordok <- oldfindbestcoord(listx, listy)
    coordok <- findbestcoord(listx, listy)


	lfilletot<-function(classeuce,x) {
	    listfille<-NULL
	    for (classe in 1:nrow(coordok)) {
			listfille<-unique(c(listfille,fille(coordok[classe,x],classeuce)))
			listfille
	    }
	}
    print('listfille')
	listfille1<-lfilletot(classeuce1,1)
	listfille2<-lfilletot(classeuce2,2)

	#utiliser rownames comme coordonnees dans un tableau de 0
	Assignclasse<-function(classeuce,x) {
	    nchd<-matrix(0,ncol=ncol(classeuce),nrow=nrow(classeuce))
	    for (classe in 1:nrow(coordok)) {
			clnb<-coordok[classe,x]
			colnb<-clnb%/%2
            nchd[which(classeuce[,colnb]==clnb), colnb:ncol(nchd)] <- classe
	    }
	    nchd
	}
	print('commence assigne new classe')
	nchd1<-Assignclasse(classeuce1,1)
	if (classif_mode==0) {
		nchd2<-Assignclasse(classeuce2,2)
	} else {
		nchd2<-nchd1
    }
	print('fini assign new classe')
	#croisep<-matrix(ncol=nrow(coordok),nrow=nrow(coordok))
    nchd2[which(nchd1[,ncol(nchd1)]==0),] <- 0
    nchd2[which(nchd1[,ncol(nchd1)]!=nchd2[,ncol(nchd2)]),] <- 0
    nchd1[which(nchd2[,ncol(nchd2)]==0),] <- 0

	print('fini croise')
	elim<-which(nchd1[,ncol(nchd1)]==0)
	keep<-which(nchd1[,ncol(nchd1)]!=0)
	n1<-nchd1[nchd1[,ncol(nchd1)]!=0,]
	n2<-nchd2[nchd2[,ncol(nchd2)]!=0,]
	#clnb<-nrow(coordok)
	print('fini')
	write.csv2(nchd1[,ncol(nchd1)],uceout)
	res <- list(n1 = nchd1, coord_ok = coordok, cuce1 = classeuce1, cuce2 = classeuce2)
	res
}
