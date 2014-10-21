#!/usr/bin/python

from my_amr_parser import parse_amr
from my_amr_parser import get_node_by_address
from my_amr_parser import printStuff
from my_amr_parser import print_amr
from my_amr_parser import isReent
import numpy as np;
import operator;
import os;
import re;
import sys;

role_dic = {} #Stores role tokens paired with a list of aligned edges
roletoknum = 0;
num_amr = 0;
FP_examples = [];
FN_examples = {};
FP_dict = {};
FN_dict = {};
Aligned_reentrancies = 0;
reent_aligned_tokens = []

def get_concept_name(c):
	c1 = c.split('/');
	if len(c1) > 1: return c1[1][1:];
	return c

def count_dict_insert(d,k):
	if k in d:
		d[k] = d[k] + 1;
	else: d[k] = 1;
	return d;

def threshold_dict(d,freq):
    swdict_concept = sorted(d.iteritems(), key=operator.itemgetter(1),reverse=True);
    cut_index = 0 
    for i in range(0,len(swdict_concept)):
        if swdict_concept[i][1] < freq:
            cut_index = i   
            break
    return swdict_concept

def remove_leading_spaces(s):

	for i in range(0,len(s)):
		if s[i] != ' ': break;		
	
	return s[i:];

def preprocess(corp,true):
	
	#Extract '::tok','::alignments' and the AMR from corp file into tuples
	newcorp = [];
	snt = []
	amr_lines = False;
	amr = '';
	for line in corp:
		if amr_lines == True:
			if line == "\n": #End of AMR
				snt.append(amr[1:]);		#Add the AMR string to current tuple
				newcorp.append(snt);	#Add the current tuple to list
				snt = [];
				amr = '';
				amr_lines = False;
				continue;
			else: amr = amr + ' ' + remove_leading_spaces(line[:-1]);		
		else:
			if re.match('# ::tok.*',line):	#Tokens 
				line = line.split();
				snt.append(line[2:]);	
			elif re.match('# ::align.*',line):	#Alignment
				line = line.split();
				snt.append(line[2:-5]);		
				amr_lines = True;				#Next line is an AMR line
		

	#Extract '::alignments' from true file
	newtrue = [];
	temptrue = true[6:-2:3];
	for line in temptrue:
		line = line[:-1].split();
		line = line[2:];
		newtrue.append(line);

	return (newcorp,newtrue);

def correct_node_indices(s):
	
	news = "";
	for c in s:
		if c >= '0' and c <= '8':
			news = news + chr(ord(c)+1);	
		else: news = news + c;
	
	return news;

def isAlignmentCorrect(jamr_nodes,true_nodes,token,amr): 	
	
	#print jamr_nodes;
	#for nodes in true_nodes:
	#	if len(nodes) > 1: print nodes;
	correct = 0;
	incorrect = 0;
	global FP_dict;
	global FP_examples;
	global Aligned_reentrancies
	global reent_aligned_tokens
	for truenode in true_nodes:
		for jamrnode in jamr_nodes:
			#print truenode, jamrnode
			if truenode == jamrnode: 
				correct = correct + 1;
				#print "True"
			else:
				incorrect = incorrect + 1;
				#print amr;
				#print jamrnode;
			#	cj =  get_node_by_address(amr,jamrnode,1);
			#	#print cj;
			#	#print truenode;
			#	ct =  get_node_by_address(amr,truenode,0);
			#	
			#	r = isReent(amr,truenode);
			#	if r!= False:
			#		reent_aligned_tokens.append((token,r));
			#		Aligned_reentrancies = Aligned_reentrancies + 1;
					
				#print ct;
			#	print
			#	#print
			#	jamr_concept = get_concept_name(cj)
			#	true_concept = get_concept_name(ct)
			#	FP_examples.append((token,jamr_concept,true_concept));
			#	FP_dict = count_dict_insert(FP_dict,jamr_concept);
			#	if jamr_concept in FP_dict:
			#		FP_dict[jamr_concept] = FP_dict[jamr_concept] + 1;
			#	else: FP_dict[jamr_concept] = 1;
			#	#print "False"
	
	return (correct,incorrect);

def populate_bin_arrays(jamr_alignment,true_alignment,toklist):		

	toknum = len(toklist);	
	true = np.array([0] * toknum);
	jamr = np.array([0] * toknum);
	correct = np.array([1] * toknum);
	role = np.array([0] * toknum);
	true_nodes = [[] for i in range(toknum)];	
	jamr_nodes = [[] for i in range(toknum)];	

	total_aligned_tokens_isi = 0;
	one_to_many = 0;
	total_alignments_jamr = len(jamr_alignment);
	many_to_many = 0;

	for alignment in true_alignment:
		t = alignment.split('-');	
		tok = int(t[0]);				#token number
		node = t[1];					#aligned to
		true[tok] = 1;					#mark gold token as aligned
		#print t[1]+"___";
		global roletoknum;
		if node[-1] == 'r':			#if role token, mark as role but don't count in score. Instead add token and it's alignment to a dictionary used to keep track
			roletoknum += 1;
			#role[tok] = 1;
			role_token = toklist[tok];
			if role_token not in role_dic:
				role_dic[role_token] = 1;
			else: role_dic[role_token] += 1;
			#role = extract role using address node[:-2]; TODO
			#if token not in role_dict:
				#role_dict[token] = role;
			#else:
				#role_dict[token].append(role);

		else: true_nodes[tok].append(node);
	
	for elt in true_nodes:
		if len(elt) > 0: total_aligned_tokens_isi += 1;
		if len(elt) > 1: one_to_many += 1;	

	for alignment in jamr_alignment:
		t = alignment.split('|');
		nodes = correct_node_indices(t[1]);
		nodes = nodes.split('+');
		if len(nodes) > 1: many_to_many += 1;
		span = t[0].split('-');
		for i in range(int(span[0]),int(span[1])):
			jamr[i] = 1;
			jamr_nodes[i] = nodes;
			#if len(true_nodes) != 0:		#if role token aligned to only an edge, then it's true_nodes list is empty
			#	correct[i] = isAlignmentCorrect(jamr_nodes,true_nodes,i);

	return (jamr, true, jamr_nodes,true_nodes, (total_aligned_tokens_isi, one_to_many, total_alignments_jamr, many_to_many));	

def evaluate(bin_arrays,toklist,amr):

	jamr = bin_arrays[0];
	true = bin_arrays[1];
	jamr_nodes = bin_arrays[2];
	true_nodes = bin_arrays[3];
	
	#nonrole_aligned_correctly = true & jamr & correct & np.logical_not(role); #True Positives
	#nonrole_aligned_incorrectly = true & jamr & np.logical_not(correct) & np.logical_not(role); #False positives 
	aligned_and_shouldve = true & jamr;
	#print toklist;
	#print aligned_and_shouldve;	
	#print "######"
	aligned = sum(aligned_and_shouldve);
	
	TP = 0;
	FP = 0;
	
	#print amr;
	amr_obj = parse_amr(amr);
	#print_amr(amr_obj);
	#print;
	#print "######";
	#amr_obj = [];
	#printStuff(amr_obj);

	for i in range(0,len(aligned_and_shouldve)):
		if aligned_and_shouldve[i]:
			#print toklist[i], jamr_nodes[i]
			(correct,incorrect) = isAlignmentCorrect(jamr_nodes[i],true_nodes[i],toklist[i],amr_obj);  
			TP = TP + correct;
			FP = FP + incorrect;
	#print
	not_aligned_but_shouldve = np.logical_not(jamr) & true; #True Negative
	not_aligned_and_shouldntve = np.logical_not(jamr | true); #False negative

	global FN_dict;
	global FN_examples;

#	for i in range(0,len(not_aligned_but_shouldve)):
#		if not_aligned_but_shouldve[i]:	
#			token = toklist[i];
#			for addr in true_nodes[i]:
#				tconcept = get_node_by_address(amr_obj,addr,0);
#				t = tconcept.split('/');
#				if len(t) > 1: tconcept = t[1][1:];
#			
#				if tconcept in FN_examples:
#					if token in FN_examples[tconcept]:
#						FN_examples[tconcept][token] = FN_examples[tconcept][token] + 1;
#					else: FN_examples[tconcept][token] = 1;
#				else: FN_examples[tconcept] = {};
#
#				if tconcept in FN_dict:
#					FN_dict[tconcept] = FN_dict[tconcept] + 1;
#				else: FN_dict[tconcept] = 1;

	TN = sum(not_aligned_but_shouldve);
	FN = sum(not_aligned_and_shouldntve);

	#print TP,FP,TN,FN	
	#print true & jamr & correct;
	#print true & jamr & np.logical_not(correct);
	#print np.logical_not(jamr) & true;
	#print not_aligned_and_shouldntve;

	return (TP,FP,TN,FN);

def main():

	TP = 0;
	FP = 0;
	TN = 0;
	FN = 0;

	#Read JAMR output file
	f=open(sys.argv[1]);
	dir=os.path.basename(sys.argv[1]);
	clines = f.readlines();
	f.close();

	#Read true alignment file
	f=open(sys.argv[2]);
	tlines = f.readlines();
	f.close();

	t = preprocess(clines,tlines);	
	corp = t[0];	#List of (tokens,alignments,amr) triplets for each sentence
	true = t[1];	#List of true alignments for each sentence
	N = len(t[0]);  #Number of sentences
	total_tokens = 0;
	#roledic = {};
	#nonroledic = {};
	tot_isi = 0;
	one_to_many = 0;	
	tot_jamr = 0;
	many_to_many = 0;

	for i in range(0,N):
	
		toklist = corp[i][0];
		amr = corp[i][2];
		#if len(amr) == 0: print toklist
		total_tokens = total_tokens + len(toklist);
		jamr_alignments = corp[i][1];
		true_alignments = true[i];
		bin_arrays = populate_bin_arrays(jamr_alignments,true_alignments,toklist);
		stats = evaluate(bin_arrays,toklist,amr);
		many_stats = bin_arrays[4];		
		tot_isi += many_stats[0];
		one_to_many += many_stats[1];
		tot_jamr += many_stats[2];
		many_to_many += many_stats[3];
		
		TP = TP + stats[0];
		FP = FP + stats[1];
		TN = TN + stats[2];
		FN = FN + stats[3];

	#print total_tokens;
	#print TP,FP,TN,FN;	
	#r = threshold_dict(roledic,0);	
	#nr = threshold_dict(nonroledic,0);
	Precision = float(TP*100)/(TP+FP);	
	Recall = float(TP*100)/(TP+TN);
	print "Precision : ",Precision;
	print "Recall : ",Recall;
#	print
#	print "One to many alignments : ",(one_to_many/float(tot_isi))*100,"percent";
#	print "Many to many alignments : ",(many_to_many/float(tot_jamr))*100,"percent";
#	print
#	print "Total no. of role tokens : ",roletoknum;
#	print "No. of role tokens per sentence : ",roletoknum/float(N);
#	global Aligned_reentrancies
#	global reent_aligned_tokens
#	print Aligned_reentrancies	
#	print reent_aligned_tokens
#	print;
#	for ex in FP_examples:
#		print ex[0],"	",ex[1],"	",ex[2]
	

	
main();
#FN_d = threshold_dict(FN_dict,3);
#print "Token	JAMR alignment	ISI alignment";
#for elt in FP_examples:
#	print "#####"
#	print "(",elt[0],",",elt[1],",",elt[2],")"
#	print
#	d=threshold_dict(FN_examples[elt[0]],0);
#	for item in d:
#		print item[1],item[0]
#	print
#print FN_d
#for item in FN_d:
#	print "#####";
#	print item[0];
#	print item[1];
#	z = threshold_dict(item[1],3);
#	print z
#	for elt in z:
#		print elt[1], elt[0]
#	print;
	
