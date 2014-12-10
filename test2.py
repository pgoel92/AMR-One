#!/usr/bin/python

from lib.AMR_class import read_corpus_file, AMR
from lib.lemmatizer import mylemmatizer
from nltk.stem.porter import PorterStemmer 
import operator

#amr_objects = read_corpus_file('../Data/Raw/LDC2014E41_DEFT_Phase_1_AMR_Annotation_R4/data/unsplit/deft-p1-amr-r4-dfa.txt');
amr_objects = read_corpus_file('../isi-tests/dev');
#print amr_objects[0].getConcepts(1);
print "Done parsing "+str(len(amr_objects))+" AMRs";
def DistanceFromRoot(addr):
#Takes in the address of the node and returns the distance from root    
	dots = 0;
	for c in addr: 
		if c == '.': dots = dots + 1;

	return dots;

def errlog(s):
		
	f = open('err.log','w');	
	f.write(s+'\n');
	f.close();

def clean(s, amr_id):
	stemmer = PorterStemmer();
	s = s.lower();   
	try: 
		ls = mylemmatizer([s]);
		s = ls[0];
	except UnicodeDecodeError:
		errlog("Error during lemmatization in "+amr_id);
	try:
		s = stemmer.stem(s);
	except UnicodeDecodeError:
		errlog("Error in stemming in "+amr_id);
    
	return s;

f = open('../isi_aligner_2/eng.txt','w');
for amr in amr_objects:
	print amr.ID;
	snt = amr.sentence;
	tokens = snt.split();
	f.write(clean(tokens[0], amr.ID));
	for tok in tokens[1:]:
		tok = clean(tok, amr.ID);
		f.write(" " + tok);	
	#f.write(snt);
	f.write("\n");	
f.close();

f = open('../isi_aligner_2/amr.txt','w');
for amr in amr_objects:
	print amr.ID;
	l = [(x[0],DistanceFromRoot(x[1])) for x in amr.getConcepts(1)];
	l = [clean(x[0], amr.ID) for x in sorted(l,key=lambda x: x[1])];
	f.write(l[0]);
	for concept in l[1:]: 
		f.write(" " + concept);	
	#f.write(amr.AMR_string_parsable);
	f.write("\n");	
f.close();
