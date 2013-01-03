# #* Textometrie 
# #* ANR project ANR-06-CORP-029
# #* http://textometrie.ens-lsh.fr/
# #* 
# #* 2008 (C) Textometrie project
# #* BSD New and Simplified BSD licenses
# #* http://www.opensource.org/licenses/bsd-license.php
# 
# ## Sylvain Loiseau <sloiseau@u-paris10.fr>
# 
# ##
# ## Ex. : type1 = 7 occ., type2 = 4 occ., separator = 11
# ## Cf. Lafon, 1981 : 120 sqq.
# ##
# ## phyper(0:4, 4, 7 + 11, 7)
# ##
# 
# ##
# ## wrapper for the function "cooccurrences.directed.contexts" given a factor as
# ## corpus and a separator.
# ##

cooccurrences <- function(corpus) {
 stop("not implemented yet");
}

# 
# `cooccurrences.directed.corpus` <-
# function (corpus, separator) {
#   if (! is.factor(corpus)) stop("The corpus must be a factor.");
#   if (! is.character(separator)) stop("Separator must be a character vector.");
#   if (length(separator) != 1) stop("Separator must be a character of length 1");
# 
#   corpus <- corpus[drop=TRUE];
#   frequencies = table(corpus);
#   separatorfrequency = frequencies[separator];
#   if (is.na(separatorfrequency)) {
#     separatorfrequency = 0;
#   }
#   frequencies = frequencies[names(frequencies) != separator];
#   types <- levels(corpus);
#   types <- types[types != separator];
# 
#   contexts = get.contexts(corpus, separator);
# 
#   return(cooccurrences.directed.contexts(contexts, types, frequencies, separatorfrequency));
# }
# 
# ##
# ## Compute all the cooccurrence indices according to a context list (see the "get.contexts" function"),
# ## the vector of types to be taken into account, their frequency, and the separator frequency.
# ##
# ## Compute the cooccurrency index (based on hypergeometric cumulative
# ## probability) for each directed pair of token and return a matrix with tokens as column names
# ## and row names where each cell give a cooccurrency index
# ##
# 
# `cooccurrences.directed.contexts` <-
# function(contexts, types, type.frequencies, separator.frequency) {
# 
#   all.cooccurrences.index <- matrix(0.0, nrow=length(types), ncol=length(type));
#   rownames(all.cooccurrences.index) <- types;
#   colnames(all.cooccurrences.index) <- types;
# 
#   for (i in 1:length(types)) {
#     type = types[i];
#     typefrequency = frequencies[i];
#     for (j in c(1:(types-1), (types + 1):length(types))) {
#       othertype = types[j];
#       othertypefrequency = frequencies[j];
#       cooccurrences = cooccurrences.frequency(contexts, type, othertype);
#       all.cooccurrences.index[type, othertype] <-
#         cooccurrences.directed.cooccurrents(cooccurrences, type, othertype, separatorfrequency);
#     }
#   }
# 
#   return(all.cooccurrences.index);
# }
# 
# ##
# ## In a list of contexts (see the "get.contexts" function), count the number of contexts
# ## having both at least one occurrence of type1 and at least one occurrence of type2.
# ##
# 
# `cooccurrences.frequency` <-
# function(contexts, type1, type2) {
# 
#   if (! is.character(type1)) stop("Type1 must be a character vector.");
#   if (length(type1) != 1) stop("Type1 must be a character of length 1");
#   if (! is.character(type2)) stop("Type2 must be a character vector.");
#   if (length(type2) != 1) stop("Type2 must be a character of length 1");
#   
#   is.cooccurring <- sapply(contexts,
#       function(x) {
#       if(type1 %in% x && type2 %in% x) return(1) else return(0)
#       }
#       );
#   return(sum(is.cooccurring));
# }
# 
# ##
# ## 
# ##
# 
# `cooccurrences.directed.cooccurrents` <-
# function(cooccurrences, type1, type2, separator) {
#   if (! is.integer(cooccurrences)) stop("cooccurrences must be integer.");
#   if (! is.integer(type1)) stop("type1 must be integer.");
#   if (! is.integer(type2)) stop("type2 must be integer.");
#   if (! is.integer(separator)) stop("separator must be integer.");
#   ph <- phyper(found, type2, type1 + separator, type1);
#   return(ph);
# }
# 
# ##
# ## Create a list of character vectors according to a character vector and a separator string.
# ##
# 
# `get.contexts` <-
# function(corpus, separator) {
#   if (! is.factor(corpus)) stop("The corpus must be a factor.");
#   if (! is.character(separator)) stop("Separator must be a character vector.");
#   if (length(separator) != 1) stop("Separator must be a vector of length 1");
# 
#   index.separator = which(corpus == separator);
#   contexts = list();
#   lastindex = 1;
#   for(i in 1:(length(index.separator))) {
#     contexts[[i]] = as.character(corpus[lastindex:(index.separator[i]-1)]);
#     lastindex=index.separator[i] + 1;
#   }
#   contexts[[length(contexts) + 1]] <- as.character(corpus[lastindex:length(corpus)]);
#   return(contexts);
# }
# 
# ##
# ## Create a lexical table according to a character vector and a separator string.
# ##
# 
# `get.lexical.table` <-
# function(corpus, separator) {
#   if (! is.factor(corpus)) stop("The corpus must be a factor.");
#   if (! is.character(separator)) stop("Separator must be a character vector.");
#   if (length(separator) == 1) stop("Separator must be a character of length 1");
# 
#   contexts = get.contexts(corpus, separator);
# 
#   corpus <- corpus[drop=TRUE];
#   types <- levels(corpus);
#   types <- types[types != separator];
# 
#   lexical.table <- matrix(0, nrow=length(contexts), ncol=length(types));
#   colnames(lexical.table) <- types;
# 
#   for (i in 1:length(contexts)) {
#     freq.list <- table(contexts[[i]]);
#     lexical.table[i, names(freq.list)] <- freq.list;
#   }
#   
#   return(lexical.table);
# }
# 
# `cooccurrences` <-
# function(type1, type2, separator) {
# #    max = ifelse(f > g, 2*g, i)
# #    #choose(T, t);
# }
# 
