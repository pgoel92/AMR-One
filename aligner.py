#!/usr/bin/python

from AMR_class import read_corpus_file
import re

def push_alignment(toknum,address,alignment):

	alignment = alignment + " " + str(toknum) + "-" + str(toknum+1) + "|" + address;
	
	return alignment;

def aligner(concepts, tokens):

	alignment = "";	
	for i in range(0,len(concepts)):
		concept = concepts[i][0];
		concept = concept.lower();	
		address = concepts[i][1];
		for j in range(0,len(tokens)):
			token = tokens[j].lower();
			if concept == token:
				#print concept, token
				alignment = push_alignment(j,address,alignment);

	return alignment;

def main():

	amr_objects = read_corpus_file('test/corp');
	for a in amr_objects:
		concept_tuples = a.getConcepts();
		#remove number tags from concepts
		newc = [];
		for tuple in concept_tuples:
			c = re.sub('\-[0-9]+$','',tuple[0]);
			t = (c,tuple[1]);
			newc.append(t);
		
		tokens = a.getTokens();
		a.setAlignments(aligner(newc,tokens));
		s = a.generate_writable();
		print s;

main();
