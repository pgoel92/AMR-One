#!/usr/bin/python

from lib.AMR_class import read_corpus_file, AMR
from lib.lemmatizer import mylemmatizer
from nltk.stem.porter import PorterStemmer 
import operator

amr_objects = read_corpus_file('dev/corp');

def DistanceFromRoot(addr):
#Takes in the address of the node and returns the distance from root	
	dots = 0;
	for c in addr: 
		if c == '.': dots = dots + 1;

	return dots;

eng_id = 1;
eng_dict = {};	#Key : Token , Value: [Token ID, Token occurrence count]
amr_id = 1;
amr_dict = {};	#Key : AMR concept, Value: [Concept ID, concept occurrence count]

def clean(s):
	stemmer = PorterStemmer();
	s = s.lower();    
	ls = mylemmatizer([s]);
	s = ls[0];
	s = stemmer.stem(s);
	
	return s;

#Create source (English) dictionary
for amr in amr_objects:
	snt = amr.sentence;
	tokens = snt.split();	#I am not removing punctuation to stay consistent with my rule-based aligner
	for tok in tokens:		
		tok = clean(tok);
		if tok in eng_dict: eng_dict[tok][1] += 1; 	#If token in dict, increase count of token
		else:
			eng_dict[tok] = [eng_id,1];					#else add token to dictionary
			eng_id += 1;

#Write dict to file 
f = open('S.vcb','w');
#sorted_eng_dict = sorted(eng_dict, key=lambda x: x[0]);
sorted_eng_dict = sorted(eng_dict.iteritems(), key=operator.itemgetter(1),reverse=False);
for item in sorted_eng_dict:
	key = item[0];
	value = item[1];
	#print key, value;
	f.write(str(value[0])+" "+key+" "+str(value[1])+"\n");
f.close();

#Create target (AMR) dictionary
for amr in amr_objects:
	l = [(x[0],DistanceFromRoot(x[1])) for x in amr.getConcepts(1)];
	#l = sorted(l,key=lambda x: x[1]);
	concepts = [clean(x[0]) for x in l];
	for concept in concepts:		
		if concept in amr_dict: amr_dict[concept][1] += 1; 	#If concepten in dict, increase count of concepten
		else:
			amr_dict[concept] = [amr_id,1];					#else add token to dictionary
			amr_id += 1;
	
#Write dict to file 
f = open('T.vcb','w');
sorted_amr_dict = sorted(amr_dict.iteritems(), key=operator.itemgetter(1),reverse=False);
for item in sorted_amr_dict:
	key = item[0];
	value = item[1];
	f.write(str(value[0])+" "+key+" "+str(value[1])+"\n");
f.close();
	
#Create sentence pair input file
f = open('ST.snt','w');
for amr in amr_objects:
	snt_ids = [eng_dict[x][0] for x in [clean(y) for y in amr.sentence.split()]];
	l = [(x[0],DistanceFromRoot(x[1])) for x in amr.getConcepts(1)];
	l = sorted(l,key=lambda x: x[1]);
	concept_ids = [amr_dict[item][0] for item in [clean(x[0]) for x in l]];
	f.write("1\n");
	f.write(str(snt_ids[0]));
	for id in snt_ids[1:]:
		f.write(" "+str(id));
	f.write('\n');
	f.write(str(concept_ids[0]));
	for id in concept_ids:
		f.write(" "+str(id));
	f.write('\n');
f.close();
