#!/usr/bin/python

from nltk import pos_tag
from nltk.corpus import wordnet
from nltk.stem.wordnet import WordNetLemmatizer

morphy_tag = {'NN':wordnet.NOUN,'JJ':wordnet.ADJ,'VB':wordnet.VERB,'RB':wordnet.ADV}
l = WordNetLemmatizer();

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
