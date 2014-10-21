#!/usr/bin/python

import numpy as np;
import operator;
import os;
import re;
import sys;

def threshold_dict(d,freq):
    swdict_concept = sorted(d.iteritems(), key=operator.itemgetter(1),reverse=True);
    cut_index = 0 
    for i in range(0,len(swdict_concept)):
        if swdict_concept[i][1] < freq:
            cut_index = i   
            break
    return swdict_concept[:i]

def preprocess(corp,true):
	
	#Extract '::tok' and '::alignments' from corp file
	newcorp = [];
	snt = []
	for line in corp:
		if re.match('# ::tok.*',line):
			line = line.split();
			snt.append(line[2:]);	
		elif re.match('# ::align.*',line):
			line = line.split();
			snt.append(line[2:-5]);		
			newcorp.append(snt);
			snt = [];

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

def isAlignmentCorrect(jamr_nodes,true_nodes,i): 	
	
	#print jamr_nodes;
	#for nodes in true_nodes:
	#	if len(nodes) > 1: print nodes;
	for nodes in true_nodes[i]:
		if re.match(".*"+nodes+".*",jamr_nodes): 
			return True;
	
	return False;	

def populate_bin_arrays(jamr_alignment,true_alignment,toknum):		
	
	true = np.array([0] * toknum);
	jamr = np.array([0] * toknum);
	correct = np.array([1] * toknum);
	role = np.array([0] * toknum);
	true_nodes = [[] for i in range(toknum)];	

	for alignment in true_alignment:
		t = alignment.split('-');	
		tok = int(t[0]);
		nodes = t[1];
		true[tok] = 1;
		#print t[1]+"___";
		if nodes[-1] == 'r':
			role[tok] = 1;
			nodes = nodes[:-2];
		true_nodes[tok].append(nodes);
	
	for alignment in jamr_alignment:
		t = alignment.split('|');
		jamr_nodes = correct_node_indices(t[1]);
		span = t[0].split('-');
		for i in range(int(span[0]),int(span[1])):
			jamr[i] = 1;
			if not isAlignmentCorrect(jamr_nodes,true_nodes,i): correct[i] = 0;

	return (true,jamr,correct,role);	

def evaluate(bin_arrays):

	true = bin_arrays[0];
	jamr = bin_arrays[1];
	correct = bin_arrays[2];
	role = bin_arrays[3];
	
	role_aligned_correctly = true & jamr & correct & role; #True Positives
	role_aligned_incorrectly = true & jamr & np.logical_not(correct) & role; #True Negatives
	role_not_aligned_but_shouldve = np.logical_not(jamr) & true & role; #False negatives
	role_not_aligned_and_shouldntve = np.logical_not(jamr | true) & role; #False positives
	
	nonrole_aligned_correctly = true & jamr & correct & np.logical_not(role); #True Positives
	nonrole_aligned_incorrectly = true & jamr & np.logical_not(correct) & np.logical_not(role); #True Negatives
	nonrole_not_aligned_but_shouldve = np.logical_not(jamr) & true & np.logical_not(role); #False negatives
	nonrole_not_aligned_and_shouldntve = np.logical_not(jamr | true) & np.logical_not(role); #False positives
	
	roleTP = sum(role_aligned_correctly);
	roleTN = sum(role_aligned_incorrectly);
	roleFN = sum(role_not_aligned_but_shouldve);
	nonroleTP = sum(nonrole_aligned_correctly);
	nonroleTN = sum(nonrole_aligned_incorrectly);
	nonroleFN = sum(nonrole_not_aligned_but_shouldve);
	
	#print true & jamr & correct;
	#print true & jamr & np.logical_not(correct);
	#print np.logical_not(jamr) & true;
	#print not_aligned_and_shouldntve;

	return (roleTP,roleTN,roleFN,nonroleTP,nonroleTN,nonroleFN);

def unaligned_tokens(bin_arrays,tokens,roledic,nonroledic):
	
	true = bin_arrays[0];
	jamr = bin_arrays[1];
	correct = bin_arrays[2];
	role = bin_arrays[3];
	
	role_aligned_correctly = true & jamr & correct & role; #True Positives
	role_aligned_incorrectly = true & jamr & np.logical_not(correct) & role; #True Negatives
	role_not_aligned_but_shouldve = np.logical_not(jamr) & true & role; #False negatives
	role_not_aligned_and_shouldntve = np.logical_not(jamr | true) & role; #False positives
	
	nonrole_aligned_correctly = true & jamr & correct & np.logical_not(role); #True Positives
	nonrole_aligned_incorrectly = true & jamr & np.logical_not(correct) & np.logical_not(role); #True Negatives
	nonrole_not_aligned_but_shouldve = np.logical_not(jamr) & true & np.logical_not(role); #False negatives
	nonrole_not_aligned_and_shouldntve = np.logical_not(jamr | true) & np.logical_not(role); #False positives
	

	for i in range(0,len(role_aligned_incorrectly)):
		if role_aligned_incorrectly[i] == 1:
			bad_token = tokens[i]
			if bad_token not in roledic: roledic[bad_token] = 1;
			else: roledic[bad_token] = roledic[bad_token] + 1;

	for i in range(0,len(role_not_aligned_but_shouldve)):
		if role_not_aligned_but_shouldve[i] == 1:
			bad_token = tokens[i]
			if bad_token not in roledic: roledic[bad_token] = 1;
			else: roledic[bad_token] = roledic[bad_token] + 1;

	for i in range(0,len(nonrole_aligned_incorrectly)):
		if nonrole_aligned_incorrectly[i] == 1:
			bad_token = tokens[i]
			if bad_token not in nonroledic: nonroledic[bad_token] = 1;
			else: nonroledic[bad_token] = nonroledic[bad_token] + 1;

	for i in range(0,len(nonrole_not_aligned_but_shouldve)):
		if nonrole_not_aligned_but_shouldve[i] == 1:
			bad_token = tokens[i]
			if bad_token not in nonroledic: nonroledic[bad_token] = 1;
			else: nonroledic[bad_token] = nonroledic[bad_token] + 1;

	return (roledic,nonroledic);

def main():

	roleTP = 0;
	roleTN = 0;
	roleFN = 0;
	nonroleTP = 0;
	nonroleTN = 0;
	nonroleFN = 0;
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
	corp = t[0];	#List of (tokens,alignment) pairs for each sentence
	true = t[1];	#List of true alignments for each sentence
	number_of_sentences = len(t[0]);

	roledic = {};
	nonroledic = {};
	for i in range(0,number_of_sentences):
		bin_arrays = populate_bin_arrays(corp[i][1],true[i],len(corp[i][0]));
		stats = evaluate(bin_arrays);
		unaligned_tokens(bin_arrays,corp[i][0],roledic,nonroledic);
		roleTP = roleTP + stats[0];
		roleTN = roleTN + stats[1];
		roleFN = roleFN + stats[2];
		nonroleTP = nonroleTP + stats[3];
		nonroleTN = nonroleTN + stats[4];
		nonroleFN = nonroleFN + stats[5];
	
	r = threshold_dict(roledic,0);	
	nr = threshold_dict(nonroledic,0);
	
	for key,value in nr:
		print value, key
	RolePrecision = float(roleTP*100)/(roleTP+roleTN);	
	RoleRecall = float(roleTP*100)/(roleTP+roleFN);
	NonRolePrecision = float(nonroleTP*100)/(nonroleTP+nonroleTN);	
	NonRoleRecall = float(nonroleTP*100)/(nonroleTP+nonroleFN);
	AllPrecision = float((roleTP+nonroleTP)*100)/(roleTP+nonroleTP+roleTN+nonroleTN);
	AllRecall = float((roleTP+nonroleTP)*100)/(roleTP+nonroleTP+roleFN+nonroleFN);
#	print RolePrecision, RoleRecall;
#	print NonRolePrecision, NonRoleRecall;
#	print AllPrecision, AllRecall
	
main();
