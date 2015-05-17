#!/usr/bin/python

from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem.porter import PorterStemmer

morphy_tag = {'NN':wordnet.NOUN,'JJ':wordnet.ADJ,'VB':wordnet.VERB,'RB':wordnet.ADV}
l = WordNetLemmatizer();

def clean(s):
    stemmer = PorterStemmer();
    s = s.lower();   
    try: 
        ls = mylemmatizer([s]);
        s = ls[0].encode('ascii','ignore');
    except UnicodeDecodeError:
        print "Error during lemmatization";
    try:
        s = stemmer.stem(s).encode('ascii','ignore');
    except UnicodeDecodeError:
        print "Error in stemming in ";
    
    return s;

def clean4(s):
    stemmer = PorterStemmer();
    s = s.lower();   
    try: 
        ls = mylemmatizer([s]);
        s = ls[0].encode('ascii','ignore');
    except UnicodeDecodeError:
        print "Error during lemmatization : ", "__"+s+"__";
    try:
        s = stemmer.stem(s).encode('ascii','ignore');
        if len(s) > 4: s = s[:4];
    except UnicodeDecodeError:
        print "Error in stemming : ", "__"+s+"__";
    
    return s;

def remove_stopwords(tokenls, stopwordfile, file_wr):
#Removes stopwords from tokenls and saves a mapping from old indices to new ones in a file called "stopword_posmap"	
#file_wr = 1 means the mapping should be written to a file. file_wr = 0 means it should be returned by the function
	
	f = open(stopwordfile);
	stopwords = f.readlines();
	f.close();
	stopwords = [x[:-1] for x in stopwords];

	newtokenls = [];
	mapls = [];
	posmap = {};
	k = 0;

	for i in range(0,len(tokenls)):
		if tokenls[i] not in stopwords:
			newtokenls.append(tokenls[i]);
			posmap[k] = i;
			mapls.append(str(i));
			k = k+1;

	if file_wr == 1:
		f = open('stopword_posmap_eng','a');
		f.write(' '.join(mapls)+"\n");
		f.close();
		return newtokenls;
	elif file_wr == 2:
		f = open('stopword_posmap_amr','a');
		f.write(' '.join(mapls)+"\n");
		f.close();
		return newtokenls;
	else:
		return newtokenls, posmap;

def get_stopword_posmap(mapstr): 
#Taking as input a line from the file "stopword_posmap", this function returns a map from new positions to original positions	
	orig_posls = mapstr.split();	
	map = {};

	for i in range(0,len(orig_posls)):
		map[i] = orig_posls[i];	

	return map;

def mylemmatizer(ls):
	
	ls_tagged = pos_tag(ls);
	tags = [x[1] for x in ls_tagged];
	
	newls = []	
	for i in range(0,len(ls)):
		tag = tags[i];
		try:
			wordnet_tag = morphy_tag[tag[:2]];
		except KeyError:
			continue;
		newls.append(l.lemmatize(ls[i],wordnet_tag));
	
	if len(newls) == 0: return ls;
	return newls;	
