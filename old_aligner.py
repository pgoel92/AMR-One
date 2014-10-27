#!/usr/bin/python

from lib.AMR_class import read_corpus_file
from lib.dictlib import threshold_dict, count_dict_insert
from nltk.stem.porter import *
import re
import sys

test_concepts = 0;
test_aligned = 0;
d = {};

def push_alignment(toknum,address,alignment):

	alignment.append(str(toknum) + "-" + str(toknum+1) + "|" + address);
	
	return alignment;

def apply_rules(concept,token):

#	global test_concepts;
#	global test_aligned;
#	global d;
	polarity_token_list = ['no','not','non','never','n\'t','without'];
#	if concept == '-': 
#		#polarity_concepts += 1;
#		d = count_dict_insert(d,token);
#		
	if concept == '-' and token in polarity_token_list: return True;
	if concept == token: return True;
	return False;

def aligner(concepts, tokens, a):

	stemmer = PorterStemmer();
	alignment = [];	
	aligned_tokens = [0] * len(tokens);
	for i in range(0,len(concepts)):
		concept = concepts[i][0];
		concept = concept.lower();	
		concept = stemmer.stem(concept);
		address = concepts[i][1];
		for j in range(0,len(tokens)):
			token = tokens[j].lower();
			token = stemmer.stem(token);
			already_aligned = aligned_tokens[j];
			#if concept == token:
			if apply_rules(concept,token) and not already_aligned:
				#print concept, token
				#a.annotate(j,address);
				aligned_tokens[j] = 1;
				alignment = push_alignment(j,address,alignment);

	return alignment;

def main():

	amr_objects = read_corpus_file(sys.argv[1]);
	print;
	print;	#Add blank line to make consistent with JAMR output file format
	for a in amr_objects:
		concept_tuples = a.getConcepts();
		#remove number tags from concepts
		newc = [];
		for tuple in concept_tuples:
			c = re.sub('\-[0-9]+$','',tuple[0]);
			if c[0] == '"': c = c[1:-1];
			t = (c,tuple[1]);
			newc.append(t);
		
		tokens = a.getTokens();
		a.setAlignments(aligner(newc,tokens,a));
		a.generate_printable_AMR();
		s = a.generate_writable();
		print s;
	#print polarity_concepts;
#	dt = threshold_dict(d,0);
#	for item in dt:
#		print item[1],item[0];

main();

