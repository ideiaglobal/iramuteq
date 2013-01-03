#*
#* Textometrie 
#* ANR project ANR-06-CORP-029
#* http://textometrie.ens-lsh.fr/
#* 
#* 2008 (C) Textometrie project
#* BSD New and Simplified BSD licenses
#* http://www.opensource.org/licenses/bsd-license.php

`pareto` <-
function (x) {
  op <- par(mar = c(5, 4, 4, 5) + 0.1)
  par(las=2)
  if( ! inherits(x, "table") ) {
    x <- table(x)
  }
  x <- rev(sort(x))
  plot( x, type='h', axes=F)
  # , lwd=16
  axis(2)
  points( x, type='h', lwd=6) # , col=heat.colors(length(x)) 
  
  y <- cumsum(x)/sum(x)
  par(new=T)
  plot(y, type="b", lwd=3, pch=7, axes=F, xlab='', ylab='', main='')
  points(y, type='h')
  axis(4)
  #print(names(x))
  axis(1, at=1:length(x), labels=names(x))
  par(op)
  title("Pareto graphic with cumulative frequency");
}

