#Author: Pierre Ratinaud
#Copyright (c) 20010 Pierre Ratinaud
#Lisense: GNU/GPL


#fichier genere par IRaMuTeq
source('%s')
typegraph <- %i
what <- %i
x <- %i
y <- %i
z <- %i
qui <- %i
over <- %s
do.select.nb <- %s
select.nb <- %i
do.select.chi <- %s
select.chi <- %i
cex.txt <- %s
txt.min <- %i
txt.max <- %i
fileout <- '%s'
width <- %i
height <- %i
taillecar <- %i
alpha <- %i/100
dofilm <- %s
tchi <- %s
tchi.min <- %i
tchi.max <- %i
dirout <- '%s'

xlab <- paste('facteur ', x, ' -')
ylab <- paste('facteur ', y, ' -')
if (!typegraph == 0) {zlab <- paste('facteur ', z, ' -')}
xlab <- paste(xlab,round(afc_table$facteur[x,2],2),sep = ' ')
xlab <- paste(xlab,' %%',sep = '')
ylab <- paste(ylab,round(afc_table$facteur[y,2],2),sep = ' ')
ylab <- paste(ylab,' %%',sep = '')
if (!typegraph == 0) {
    zlab <- paste(zlab,round(afc_table$facteur[z,2],2),sep = ' ')
    zlab <- paste(zlab,' %%',sep = '')
}

if ( qui == 3 ) {
    if ( what == 0 ) table.in <- afc$colcoord
    if ( what == 1 ) table.in <- afc$colcrl
    rownames(table.in) <- afc$colnames
    if (typegraph == 0) {
        table.in<-table.in[,c(x,y)]
    } else {
        table.in<-table.in[,c(x,y,z)]
        rx <- range(table.in[,1], na.rm = TRUE)
        ry <- range(table.in[,2], na.rm = TRUE)
        rz <- range(table.in[,3], na.rm = TRUE)
    }
    classes <- c(1:clnb)
    maxchi <- 1
    cex.par <- NULL
} else {
    if ( what == 0 ) table.in <- afc$rowcoord
    if ( what == 1 ) table.in <- afc$rowcrl*2
    rownames(table.in) <- afc$rownames
    tablechi <- chistabletot
    rn.keep <- c()
    if (typegraph == 0) {
        table.in<-table.in[,c(x,y)]
    } else {
        table.in<-table.in[,c(x,y,z)]
        rx <- range(table.in[,1], na.rm = TRUE)
        ry <- range(table.in[,2], na.rm = TRUE)
        rz <- range(table.in[,3], na.rm = TRUE)
    }
    if (!is.null(debsup)) {
        if ( qui == 0 ) {
           table.in <- table.in[1:(debsup-1),]
           tablechi <- tablechi[1:(debsup-1),]
           cex.par <- afc$rowmass[1:(debsup-1)]
        }
        if ( qui == 1 ) {
           table.in <- table.in[debsup:(debet-1),] 
           tablechi <- tablechi[debsup:(debet-1),]
           #cex.par <- afc$rowmass[debsup:(debet-1)]
        }
        if ( qui == 2 ) {
           table.in <- table.in[debet:nrow(table.in),] 
           tablechi <- tablechi[debet:nrow(tablechi),]
           #cex.par <- afc$rowmass[debet:nrow(tablechi)]
        }
    }
    
    if (is.null(debsup)) {
        if (qui == 0) {
            if (!is.null(debet)) {
                table.in <- table.in[1:(debet-1),] 
                tablechi <- tablechi[1:(debet-1),]
                cex.par <- afc$rowmass[1:(debet-1)]
            } else {
                cex.par <- afc$rowmass
            }
        } else {
            table.in <- table.in[debet:nrow(table.in),]
            tablechi <- tablechi[debet:nrow(tablechi),]
            #cex.par <- afc$rowmass[debet:nrow(tablechi)]
        }
    }
        
    if (over) {
        rn <- rownames(table.in)
        rownames(table.in) <- 1:nrow(table.in)
        table.in <- unique(table.in)
        rn.keep <- as.numeric(rownames(table.in))
        rownames(table.in) <- rn[rn.keep]
        tablechi <- tablechi[rn.keep,]
        if (qui==0) {
            cex.par <- cex.par[rn.keep]
        } else {
            cex.par <- NULL
        }
    } 
    if (do.select.nb) {
        if (select.nb > nrow(table.in)) select.nb <- nrow(table.in)
        row.keep <- select_point_nb(tablechi, select.nb)
        table.in <- table.in[row.keep,]
        tablechi <- tablechi[row.keep,]
    } else if (do.select.chi) {
        if (select.chi > max(tablechi)) select.chi <- max(tablechi)
        row.keep <- select_point_chi(tablechi, select.chi)
        table.in <- table.in[row.keep,]
        tablechi <- tablechi[row.keep,]
    } else {
        row.keep <- 1:nrow(table.in)
    }
    classes <- apply(tablechi, 1, which.max)
    maxchi <- apply(tablechi, 1, max)
    
    if (cex.txt) {
        #row.keep <- append(row.keep, rn.keep)
        #row.keep <- unique(row.keep)
        cex.par <- cex.par[row.keep]
        cex.par <- norm.vec(cex.par, txt.min/10, txt.max/10)
    } else if (tchi) {
        cex.par <- maxchi
        cex.par <- norm.vec(cex.par, tchi.min/10, tchi.max/10)
    } else {
        cex.par <- NULL
    }
}

if (typegraph == 0) {

    open_file_graph(fileout, width = width, height = height)
    parcex <- taillecar/10
    par(cex = parcex)
    make_afc_graph(table.in, classes, clnb, xlab, ylab, cex.txt = cex.par)

} else {

    vire.nonascii <- function(rnames) {
        print('vire non ascii')
        couple <- list(c('é','e'),
                    c('è','e'),
                    c('ê','e'),
                    c('ë','e'),
                    c('î','i'),
                    c('ï','i'),
                    c('ì','i'),
                    c('à','a'),
                    c('â','a'),
                    c('ä','a'),
                    c('á','a'),
                    c('ù','u'),
                    c('û','u'),
                    c('ü','u'),
                    c('ç','c'),
                    c('ò','o'),
                    c('ô','o'),
                    c('ö','o'),
                    c('ñ','n')
                    )
        for (c in couple) {
            rnames<-gsub(c[1],c[2], rnames)
        }
        rnames
    }
    library(rgl)
    rn <- vire.nonascii(rownames(table.in))
    rgl.open()
    #par3d(windowRect = c(100,100,600,600))
    rgl.bg(col = c('white', "#99bb99"), front = "lines", box=FALSE, sphere = TRUE)
    rgl.lines(c(rx), c(0, 0), c(0, 0), col = "#000000")
    rgl.lines(c(0,0),c(ry),c(0,0),col = "#000000")
    rgl.lines(c(0,0),c(0,0),c(rz),col = "#000000")
    text3d(rx[2]+1,0,0, xlab)
    text3d(0,ry[2]+1,0, ylab)
    text3d(0,0,rz[2]+1, zlab)
    rain = rainbow(clnb)
    colors = rain[classes]
    text3d(table.in[,1], table.in[,2], table.in[,3], rn, col='black')
    if (tchi) {
        maxchi <- norm.vec(maxchi, tchi.min/100, tchi.max/100)
    } else if (!is.null(cex.par)) {
        maxchi <- norm.vec(cex.par, txt.min/100, txt.max/100)
    } else {
        maxchi <- 0.1
    }
    for (i in 1:clnb) {
        text3d(rx[2],(ry[2]+(0.2*i)),0,paste('classe',i),col=rain[i])
    }
    rgl.spheres(table.in, col = colors, radius = maxchi, alpha = alpha)

    if (dofilm) {
        require(tcltk)
        ReturnVal <- tkmessageBox(title="RGL 3 D",message="Cliquez pour commencer le film",icon="info",type="ok")

        movie3d(spin3d(axis=c(0,1,0),rpm=6), movie = 'film', frames = "tmpfilm", duration=10, clean=TRUE, top = TRUE, dir = dirout)
        ReturnVal <- tkmessageBox(title="RGL 3 D",message="Fini !",icon="info",type="ok")
    }

    require(tcltk)
    ReturnVal <- tkmessageBox(title="RGL 3 D",message="Cliquez pour fermer",icon="info",type="ok")
    rgl.close()
}
