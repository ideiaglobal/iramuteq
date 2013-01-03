#* Textometrie 
#* ANR project ANR-06-CORP-029
#* http://textometrie.ens-lsh.fr/
#* 
#* 2008 (C) Textometrie project
#* BSD New and Simplified BSD licenses
#* http://www.opensource.org/licenses/bsd-license.php

## Sylvain Loiseau <sloiseau@u-paris10.fr>

`specificites` <-
function(lexicaltable, types=NULL, parts=NULL) {
  spe <- specificites.probabilities(lexicaltable, types, parts);
  spelog <- matrix(0, nrow=nrow(spe), ncol=ncol(spe));
  spelog[spe < 0.5] <- log10(spe[spe < 0.5]);
  spelog[spe > 0.5] <- abs(log10(1 - spe[spe > 0.5]));
  spelog[spe == 0.5] <- 0;
  spelog[is.infinite(spe)] <- 0;
  spelog <- round(spelog, digits=4);
  rownames(spelog) <- rownames(spe);
  colnames(spelog) <- colnames(spe);
  #class(spelog) <- "specificites";
  #attr(spelog, "l.t") <- spe;
  return(spelog);
}

`specificites.probabilities` <-
function(lexicaltable, types=NULL, parts=NULL) {

 # if (!is.numeric(lexicaltable)) stop("The lexical table must contain numeric values.");

  rowMargin <- rowSums(lexicaltable); # or "F" (the total frequency of all the types).
  colMargin <- colSums(lexicaltable); # or "T" (the size of the parts).
  F <- sum(lexicaltable);             # The grand total (number of tokens in the corpus).

  if (! is.null(types)) {      # Filter on tokens to be considered.
    if(is.character(types)) {  # convert the name of types given with "types" into row index numbers.
      if (is.null(rownames(lexicaltable))) stop("The lexical table has no row names and the \"types\" argument is a character vector.");
      if (! all(types %in% rownames(lexicaltable))) stop(paste(
            "Some requested types are not known in the lexical table: ",
            paste(types[! (types %in% rownames(lexicaltable))], collapse=" "))
          ); 
    } else {
      if (any(types < 1)) stop("The row index must be greater than 0.");
      if (max(types) > nrow(lexicaltable)) stop("Row index must be smaller than the number of rows.");
    }
    lexicaltable <- lexicaltable[types,, drop = FALSE];
    rowMargin <- rowMargin[types];
  }

  if (! is.null(parts)) {      # Filter on parts to be considered.
    if(is.character(parts)) {  # convert the name of parts given with "parts" into col index numbers.
      if (is.null(colnames(lexicaltable))) stop("The lexical table has no col names and the \"parts\" argument is a character vector.");
      if (! all(parts %in% colnames(lexicaltable))) stop(paste(
            "Some requested parts are not known in the lexical table: ",
            paste(parts[! (parts %in% colnames(lexicaltable))], collapse=" "))
         ); 
    } else {
      if (max(parts) > ncol(lexicaltable)) stop("Column index must be smaller than the number of cols.");
      if (any(parts < 1)) stop("The col index must be greater than 0.");
    }
    lexicaltable <- lexicaltable[,parts, drop=FALSE];
    colMargin <- colMargin[parts];
  }

  if (nrow(lexicaltable) == 0 | ncol(lexicaltable) == 0) {
    stop("The lexical table must contains at least one row and one column.");
  }

  specif <- matrix(0.0, nrow=nrow(lexicaltable), ncol=ncol(lexicaltable));

  for(i in 1:ncol(lexicaltable)) {    # We proceed the whole lexical table by column (i.e. by part).

     whiteDrawn <- lexicaltable[,i];  # The frequencies observed in this part for each type.
     white <- rowMargin;     # The total frequencies in the corpus for each type.
     black <- F-white;       # The total complement frequency in the corpus for each type.
     drawn <- colMargin[i];  # The number of tokens in the part.

     independance    <- (white * drawn) / F;         # The theoretic frequency of each type.
     specif_negative <- whiteDrawn <  independance;  # index of observed frequencies below the theoretic frequencies.
     specif_positive <- whiteDrawn >= independance;  # index of observed frequencies above the theoretic frequencies.

     specif[specif_negative,i] <- phyper (
         whiteDrawn[specif_negative], white[specif_negative], black[specif_negative], drawn
         );

     specif[specif_positive,i] <- phyper (
         whiteDrawn[specif_positive] - 1, white[specif_positive], black[specif_positive], drawn
         );
  }

  dimnames(specif) <- dimnames(lexicaltable);

  return(specif);
}

`specificites.lexicon` <-
function(lexicon, sublexicon) {
  spe <- specificites.lexicon.probabilities(lexicon, sublexicon);
  spelog <- matrix(0, nrow=nrow(spe), ncol=ncol(spe));
  spelog[spe < 0.5] <- log10(spe[spe < 0.5]);
  spelog[spe > 0.5] <- abs(log10(1 - spe[spe > 0.5]));
  spelog[spe == 0.5] <- 0;
  spelog[is.infinite(spe)] <- 0;
  spelog <- round(spelog, digits=4);
  rownames(spelog) <- rownames(spe);
  colnames(spelog) <- colnames(spe);
  #class(spelog) <- "specificites";
  #attr(spelog, "l.t") <- spe;
  return(spelog);
}

`specificites.lexicon.new` <-
function(lexicon, sublexicon) {

  if (! all(names(sublexicon) %in% names(lexicon))) stop(
        paste(
          sum(! (names(sublexicon) %in% names(lexicon))),
          "types of the sublexicon not found in the lexicon: ",
          )
      ); 

sub <- numeric(length(lexicon));
names(sub) <- names(lexicon);
sub[names(sublexicon)] <- sublexicon;

  complementary.lexicon <- c(lexicon- sub);
  if (any(complementary.lexicon < 0)) stop("type cannot be more frequent in the sublexicon than in the lexicon");

  lexicaltable <- matrix(c(sub, complementary.lexicon), ncol=2);
  rownames(lexicaltable) <- names(lexicon);
  colnames(lexicaltable) <- c("sublexicon", "complementary");
 #stop(colnames(lexicaltable));
  return(specificites(lexicaltable,NULL,NULL));
}

`specificites.lexicon.probabilities` <-
function(lexicon, sublexicon) {

  if (!is.numeric(lexicon)) stop("The lexicon must contain numeric values.");
  if (!is.numeric(sublexicon)) stop("The sublexicon must contain numeric values.");
  if (is.null(names(lexicon))) stop("The lexicon must contain names.");
  if (is.null(names(sublexicon))) stop("The sub lexicon must contain names.");

  if (! all(names(sublexicon) %in% names(lexicon)))
    stop(
        paste(
          "Some requested types of the sublexicon are not known in the lexicon: ",
          paste(names(sublexicon)[! (names(sublexicon) %in% names(lexicon))], collapse=" ")
          )
        ); 

  F <- sum(lexicon);
  f <- sum(sublexicon);

  # complementary.lexicon <- c(lexicon[names(sublexicon)] - sublexicon, lexicon[!names(lexicon) %in% names(sublexicon)]);

  if (F < f) {
    stop("The lexicon cannot be smaller than the sublexicon");
  }

  whiteDrawn <- numeric(length(lexicon)); # The frequencies observed in this part for each type.
  names(whiteDrawn) <- names(lexicon);
  whiteDrawn[names(sublexicon)] <- sublexicon;
  white <- lexicon; # The total frequencies in the corpus for each type.
  black <- F-white;          # The total complement frequency in the corpus for each type.
  drawn <- f;     # The number of tokens in the part.

  # print(whiteDrawn);
  # print(white);
  # print(black);
  # print(drawn);

  independance    <- (white * drawn) / F;         # The theoretic frequency of each type.

  specif_negative <- whiteDrawn <  independance;  # index of observed frequencies below the theoretic frequencies.
  specif_positive <- whiteDrawn >= independance;  # index of observed frequencies above the theoretic frequencies.

  specif <- double(length(lexicon));

  specif[specif_negative] <-     phyper (
      whiteDrawn[specif_negative],     white[specif_negative], black[specif_negative], drawn
      );

  specif[specif_positive] <- phyper (
      whiteDrawn[specif_positive] - 1, white[specif_positive], black[specif_positive], drawn
      );

  names(specif) <- names(lexicon);

  return(specif);
}

#print.specificites(x, line=20, part=1, form=NULL, ...) {
#  if (all(is.null(line, part))) {
#    stop("either a line or a part must be specified");
#  }
#  if (all(!is.null(line, part))) {
#    stop("only a line or a part must be specified");
#  }
#}
