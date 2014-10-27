#!/usr/bin/python

from lib.AMR_class import read_corpus_file
from lib.dictlib import threshold_dict, count_dict_insert
from nltk.stem.porter import *
import re
import sys

test_concepts = 0;
test_aligned = 0;
d = {};
polarity_token_list = ['no','not','non','never','n\'t','without'];

def push_alignment(toknum,address,alignment):

	alignment.append(str(toknum) + "-" + str(toknum+1) + "|" + address);
	
	return alignment;

def getConcept(value):	#Takes a raw concept and processes it such that it can be compared with a token 

	stemmer = PorterStemmer();	
	
	value = value.split('/');
	if len(value) > 1: concept = value[1][1:];		#Remove variable
	else: concept = value[0];
	if concept[0] == '"': concept = concept[1:-1];	#Remove quotation marks
	concept = re.sub('\-[0-9]+$','',concept);		#Remove number tags
	concept = concept.lower();				
	concept = stemmer.stem(concept);
	
	return concept;
		
def align(tokens, aligned_tokens, amr, addr, alignment):

	global polarity_token_list;

	concept = getConcept(amr.getValue());

	for i in range(0,len(tokens)):
		token = tokens[i];
		already_aligned = aligned_tokens[i];
		#print concept, token;	
		#Rule 1 : Exact match	
		if concept == token and not already_aligned: 
			amr.aligned_to = i;
			aligned_tokens[i] = 1;
			alignment = push_alignment(i, addr, alignment); 

		#Rule 2 : Polarity 
		if concept == '-' and token in polarity_token_list and not already_aligned: 
			amr.aligned_to = i;
			aligned_tokens[i] = 1;
			alignment = push_alignment(i, addr, alignment);

		#Rule 3 : Month. This rule is different because here I will need to align a child node. I will then recurse on that child again. I will need to make sure that it should not be processed again.
	if len(amr.edge_ptrs_nr) == 0: return alignment;
	
	#Recurse on all children
	for i in range(0,len(amr.edge_ptrs_nr)):
		ptr = amr.edge_ptrs_nr[i];
		alignment = align(tokens, aligned_tokens, ptr, addr + "." + str(i+1), alignment);
	
	#The following rules are triggered when all children are done aligning because they need their alignments to align the current node 

	#Rule 3 : Person-of, Thing-of
	if concept == 'person' or concept == 'thing':
		for j in range(0,len(amr.edge_names)):			#For each outgoing edge
			name = amr.edge_names[j];
			if re.match('.*-of',name) != None:			#Is it a *-of edge?
				align_to = amr.edge_ptrs[j].aligned_to;
				if align_to != -1:
				 	amr.aligned_to = align_to;
					aligned_tokens[align_to] = 1;
					alignment = push_alignment(align_to, addr, alignment);
				break;

	return alignment;

def aligner(tokens, amr):

	stemmer = PorterStemmer();
	alignment = [];	
	newtokens = [];	
	for token in tokens:
		newtoken = token.lower();
		newtoken = stemmer.stem(newtoken);
		newtokens.append(newtoken);

	aligned_tokens = [0] * len(newtokens);
	alignment = align(newtokens, aligned_tokens, amr, '1', []);	
#	for i in range(0,len(concepts)):
#		concept = concepts[i][0];
#		concept = concept.lower();	
#		concept = stemmer.stem(concept);	
#		address = concepts[i][1];
#		for j in range(0,len(tokens)):
#			token = tokens[j].lower();
#			token = stemmer.stem(token);
#			#print concept,token
#			#if concept == token:
#			if apply_rules(concept,token):
#				#print concept, token
#				#a.annotate(j,address);
#				alignment = push_alignment(j,address,alignment);

	return alignment;

def main():

	amr_objects = read_corpus_file(sys.argv[1]);
	print;
	print;	#Add blank line to make consistent with JAMR output file format
	for a in amr_objects:
		#concept_tuples = a.getConcepts();
		#remove number tags from concepts
	#	newc = [];
	#	for tuple in concept_tuples:
	#		c = re.sub('\-[0-9]+$','',tuple[0]);
	#		t = (c,tuple[1]);
	#		newc.append(t);
	#	
		tokens = a.getTokens();
		amr = a.getAMRTree();
		#print a.ID;
		a.setAlignments(aligner(tokens,amr));
		a.generate_printable_AMR();
		s = a.generate_writable();
		print s;
	#print polarity_concepts;
#	dt = threshold_dict(d,0);
#	for item in dt:
#		print item[1],item[0];

main();
