`printrepartition` <-function(positions, names, colors, styles, widths, corpusname, Xmin, T, doCumulative, structurepositions, strutnames, graphtitle, bande) {
	options(scipen=1000)

	linestyle = 1
	linewidth = 1

		if (length(positions) > length(colors)) stop("colors list size too small");
		if (length(positions) > length(names)) stop("names list size too small");
		if (length(positions) > length(styles)) stop("styles list size too small");
		if (length(positions) > length(widths)) stop("widths list size too small");
	
	# if (length(structurepositions) > length(strutnames)) stop("structure names list size too small");

	doCumu <- (doCumulative == "true")

	maxX = T
	maxY = 0
	draw = 0

	# set maxX and maxY the ranges
	if(!doCumu)
	{
		for(i in 1:length(names))
		{
			x = positions[[i]]
			              if(length(x) > 0)
			              {
			            	  d = density(x, bw=bande)
			            	  m = max(d[["y"]])
			            	  if(maxY < m)
			            		  maxY <- m
			              }
		}
		maxY=2*maxY
	}
	else
	{
		for(i in 1:length(names))
		{
			my <- length(positions[[i]])
			if(maxY < my)
				maxY <- my
		}
	}

	# draw curves
	for(i in 1:length(names))
	{
		#line styles and width update
		linestyle = linestyle + 1
		if(linestyle >= 6)
		{
			linestyle = 1
			linewidth = linewidth+ 1
		}
		x = positions[[i]]
		              if(length(x) > 0)
		              {
		            	  y = 1:length(x)

				  y <- c( c(0), y , c(y[[length(x)]]) )
				  x <- c( c(x[[1]]), x , c(maxX) )

		            	  if(draw == 0)# first draw
		            	  {
		            		  if(doCumu)
		            		  {

plot(x, y, type="s", xlab=paste("T = ", maxX), main = graphtitle, ylab="Occurrences", ylim=c(0, maxY), xlim=c(Xmin, maxX), pch=15, col=colors[i], lty=styles[i], lwd=widths[i], xaxs="i", yaxs="i")
		            		  }
		            		  else
		            		  {
plot(density(x, bw=bande), type="l", xlab=paste("T = ", maxX), graphtitle, ylab="Density", ylim=c(0, maxY), xlim=c(Xmin, maxX), pch=15, col=colors[i], lty=styles[i], lwd=widths[i], xaxs="i", yaxs="i")
		            		  }
		            	  }
		            	  else #next draws
		            	  {
		            		  if(doCumu)
		            		  {
points(x, y, type="s", pch=15, col=colors[i], lty=styles[i], lwd=widths[i])
		            		  }
		            		  else
		            		  {
points(density(x, bw=bande), type="l", pch=15, col=colors[i], lty=styles[i], lwd=widths[i])
		            		  }
		            	  }
		            	  rm(y)
		            	  draw <- draw + 1
		              }
	}

	# draw legend
	for(i in 1:length(names))
		names[i] = paste(names[i], length(positions[[i]]))

	if(draw > 0)
		legend("topleft", names, inset = .02, col = colors, lty=styles, lwd=widths)

	# draw hist of struct
	y = c()
	if(length(structurepositions) > 0)
	{
		for(i in 1:length(structurepositions))
		{
			y[i] <- maxY
			text(structurepositions[[i]], maxY*0.70, strutnames[[i]], cex = .8, srt=-90, adj = c(0,0))
		}
		points(structurepositions, y, type="h", ylim=c(0, maxY), xlim=c(Xmin, maxX))
	}
}

