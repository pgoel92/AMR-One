#!/usr/bin/python

from lib.AMR_class import read_corpus_file
from lib.dictlib import counting_dictionary
from lib.lemmatizer import mylemmatizer, clean4, remove_stopwords
from nltk.stem.porter import PorterStemmer 
from subprocess import call
import re
import sys

test_concepts = 0;
test_aligned = 0;
d = {};
polarity_token_list = ['no','not','non','never','n\'t','without'];
symbol_concepts = ['dollar', 'percentage-ent'];
amr_stopwords = []; 
total_pairs = 0;	#Total number of token-concept pairs
pair_dict = counting_dictionary();
pair_pos_dict = {}
atable_flag = 1;

def createTTable(type):

	global total_pairs, pair_dict, pair_pos_dict;
	if type == 'f':
		f = open('../isi_aligner_3/myfttable','w');
	else:
		f = open('../isi_aligner_3/mybttable','w');
	
	for key in pair_dict.keys():
		count = pair_dict.get(key);
		#pos = pair_pos_dict[key];
		if type == 'f':
			f.write(key[0]+" "+key[1]+" "+str(count/float(total_pairs))+"\n");
			#print key[0]+" "+key[1]+" "+str(count/float(total_pairs))+"\n";
		else:
			f.write(key[1]+" "+key[0]+" "+str(count/float(total_pairs))+"\n");
			#print key[1]+" "+key[0]+" "+str(count/float(total_pairs))+"\n";

	f.close();	

def WriteToAtable(i, j, l, m, p, type):
	
	if type == 'f':
		f = open('../isi_aligner_3/fAtable','a');	
	else:
		f = open('../isi_aligner_3/bAtable','a');	
	f.write(str(i)+" "+str(j)+" "+str(l)+" "+str(m)+" "+str(p)+"\n");
	f.close();
	
def preprocess_step4(tok, conc):
#Used to add alignment pairs as new training examples to the dataset

	f = open('new-train-tokens','a');
	f.write(tok+"\n");
	f.close();

	f = open('new-train-concepts','a');
	f.write(conc+"\n");
	f.close();
	
def push_alignment(toknum,address,alignment, BFSpos, pair, posmap, l, m, noalign):

	preprocess_step4(pair[0], pair[1]);

	if noalign == 0:
		#a.annotate(toknum, address);
		newtoknum = posmap[toknum];
		alignment.append(str(newtoknum) + "-" + str(newtoknum+1) + "|" + address);
	
		global pair_dict, pair_pos_dict;
		#if pair not in pair_dict: print "Yes"
		pair_dict.insert(pair, 1);
		#if pair not in pair_pos_dict:
		#	pair_pos_dict[pair] = (toknum, BFSpos);	
	
		if(atable_flag == 1):
			#Add alignment to ATable in the form i, j, l, m, p
			#Forward ATable (eng -> amr)
			WriteToAtable(toknum, BFSpos, l, m, 1, 'f');
			#Backward ATable (amr -> eng)
			WriteToAtable(BFSpos, toknum, m, l, 1, 'b');
	
	return alignment;

def local_clean4(concept):
	
	stemmer = PorterStemmer();	
	try:
		ls = mylemmatizer([concept]);
		concept = ls[0].encode('ascii','ignore');
	except UnicodeDecodeError:
		print "Error in lemmatization"	
	try:
		concept = stemmer.stem(concept).encode('ascii','ignore');
		if len(concept) > 4: concept = concept[:4];
	except UnicodeDecodeError:
		print "Error in stemming"
	
	return concept;

def getConcept(value):	#Takes a raw concept and processes it such that it can be compared with a token 

	value = value.split('/');
	if len(value) > 1: concept = value[1][1:];		#Remove variable
	else: concept = value[0];
	if concept == '': return concept;
	if concept[0] == '"': concept = concept[1:-1];	#Remove quotation marks
	concept = re.sub('\-[0-9]+$','',concept);		#Remove number tags
	concept = concept.lower();				

	return concept;	

def initialize_month_map():

	m = {};
	m['1'] = ['januari','jan','jan.'];	
	m['2'] = ['februari','feb','feb.'];	
	m['3'] = ['march'];	
	m['4'] = ['april','apr'];	
	m['5'] = ['may'];	
	m['6'] = ['june'];	
	m['7'] = ['juli'];
	m['8'] = ['august','aug','aug.'];	
	m['9'] = ['septemb','sept','sept.'];	
	m['10'] = ['octob','oct','oct.'];	
	m['11'] = ['novemb','nov','nov.'];	
	m['12'] = ['decemb','dec','dec.'];	
	
	return m;

def initialize_symbol_map():

	m = {};	
	m['dollar'] = '$';	
	m['percentage-ent'] = '%';
	
	return m;	

def align(tokens, aligned_tokens, amr_node, cnum, posmap, addr, alignment, BFSpos):
#tokens 		: List of tokens in the sentence to be aligned
#aligned_tokens : A binary list of size [1xtoknum] that tells which tokens have already been aligned
#amr_node 		: Pointer to the current AMR tree node being aligned
#addr 			: Address of the current AMR tree node being aligned
#alignment 		: List of alignments that have already been processed 
#amrobj 		: AMR object pointer

	global polarity_token_list;
	global symbol_concepts;
	global amr_stopwords;
	month_map = initialize_month_map();
	symbol_map = initialize_symbol_map();
	
	noalign = 0;
	concept = getConcept(amr_node.getValue());
	if concept in amr_stopwords: 
		#print "AMR stopwords working : ", concept;
		noalign = 1;
	concept = local_clean4(concept);	

	this_concept_aligned = 0;

	for i in range(0,len(tokens)):
		token = tokens[i];
		already_aligned = aligned_tokens[i];
		#print concept, token;	
		#Rule 1 : Polarity 
		if concept == '-' and token in polarity_token_list and not already_aligned: 
			amr_node.aligned_to = i;
			aligned_tokens[i] = 1;
			alignment = push_alignment(i, addr, alignment, BFSpos, (token,concept), posmap, len(tokens), cnum, noalign);
			this_concept_aligned = 1;
			break;

		#Rule 2 : Exact match	
		elif concept == token and not already_aligned: 
			amr_node.aligned_to = i;
			aligned_tokens[i] = 1;
			alignment = push_alignment(i, addr, alignment, BFSpos, (token,concept), posmap, len(tokens), cnum, noalign); 
			this_concept_aligned = 1;
			break;

		#Rule 3 : Symbol
		elif concept in symbol_concepts and token == symbol_map[concept] and not already_aligned:
			amr_node.aligned_to = i;
			aligned_tokens[i] = 1;
			alignment = push_alignment(i, addr, alignment, BFSpos, (token,concept), posmap, len(tokens), cnum, noalign);
			this_concept_aligned = 1;
			break;
		
		#Rule 5 : Month. 
		elif amr_node.edge_name == 'month':			#If current node is the head of a 'month' edge
			try:
				month_name_list = month_map[concept];
			except KeyError:
				return [];
			#print month_name, token
			if token in month_name_list and not already_aligned:
				amr_node.aligned_to = i;	
				aligned_tokens[i] = 1;
				alignment = push_alignment(i, addr, alignment, BFSpos, (token,concept), posmap, len(tokens), cnum, noalign);
				this_concept_aligned = 1;
				break;
		
	if len(amr_node.edge_ptrs_nr) == 0: return alignment;	#Base condition : If leaf node, return;
	
	#Recurse on all children
	for i in range(0,len(amr_node.edge_ptrs_nr)):
		ptr = amr_node.edge_ptrs_nr[i];
		alignment = align(tokens, aligned_tokens, ptr, cnum, posmap, addr + "." + str(i+1), alignment, BFSpos+1);
	
	#The following rules are triggered when all children are done aligning because the children's alignments are needed to align the current node 

	#Rule 6 : Person-of, Thing-of
	if (not this_concept_aligned) and (concept == 'person' or concept == 'thing'):		#Because this rule may encounter already aligned nodes, we need the first if condition 
		for j in range(0,len(amr_node.edge_ptrs)):			#For each outgoing edge
			name = amr_node.edge_ptrs[j].edge_name;
			if re.match('.*-of',name) != None:			#Is it a *-of edge?
				align_to = amr_node.edge_ptrs[j].aligned_to;	
				if align_to != -1:						#Is the head of the *-of edge aligned?
				 	amr_node.aligned_to = align_to;
					aligned_tokens[align_to] = 1;
					alignment = push_alignment(align_to, addr, alignment, BFSpos, (token,concept), posmap, len(tokens), cnum, noalign);
				break;

	return alignment;

def aligner(amrobj):

	tokens = amrobj.getTokens();
	amr = amrobj.getAMRTree();

	newtokens = [];
	for token in tokens:
		newtokens.append(clean4(token));
	
	newtokens, posmap = remove_stopwords(newtokens, 'eng_stopwords.txt', 0);
	
	aligned_tokens = [0] * len(newtokens);
	alignment = align(newtokens, aligned_tokens, amr, amrobj.NumberOfConcepts, posmap, '1', [], 0);	

	return alignment;

def pair_count(amrobj):
	
	tokens = amrobj.getTokens();
	concepts = amrobj.getConcepts(1);

	global total_pairs;
	total_pairs += len(tokens)*len(concepts);		

def load_amr_stopwords():
	
	f = open('amr_stopwords.txt');
	a = f.readlines();	
	f.close();

	global amr_stopwords;
	for word in a:
		stopword = word[:-1];
		amr_stopwords.append(stopword);

def main():

	call(["rm","-f","../isi_aligner_3/fAtable"]);
	call(["rm","-f","../isi_aligner_3/bAtable"]);
	call(["rm","-f","new-train-tokens"]);
	call(["rm","-f","new-train-concepts"]);

	#f = open('../isi_aligner_3/fAtable','w');
	#f.close();
	#f = open('../isi_aligner_3/bAtable','w');
	#f.close();
	load_amr_stopwords();
	amr_objects = read_corpus_file(sys.argv[1]);
	print "Aligning ", len(amr_objects), " AMRs";

	for amrobj in amr_objects:
		pair_count(amrobj);

	k = 1;
	f = open(sys.argv[2],'w');
	for amrobj in amr_objects:
		#print k;	
		amrobj.setAlignments(aligner(amrobj));
		#amrobj.generate_printable_AMR();
		s = amrobj.generate_writable(0);
		if len(amrobj.alignments) != 0:
			f.write(s+"\n");
		k = k+1;
	f.close();

	#global pair_dict;
	#
	#d = pair_dict.sort();

	#for item in d:
	#	print item[1], item[0];
	#createTTable('f');
	#createTTable('b');
	#print polarity_concepts;
	#dt = threshold_dict(d,0);
#	for item in dt:
#		print item[1],item[0];

main();
