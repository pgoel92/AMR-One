#!/usr/bin/python

import sys
from lib.AMR_class import read_corpus_file

def read_true_file(truefile):
#True file name -> list of lists of true alignments

	f=open(truefile);
	truelines = f.readlines();
	f.close();

	newtrue = []; 
	truelines = truelines[6:-2:3];	#Save the alignment strings
	for line in truelines:
		line = line[:-1].split();
		line = line[2:];
		newtrue.append(line);
	
	return newtrue;

def main():

	corpfile = sys.argv[1];
	truefile = sys.argv[2];

	AMR_objects = read_corpus_file(corpfile);	
	true_alignments = read_true_file(truefile);	

	if(len(AMR_objects) != len(true_alignments)): 
		print "Error : Unequal number of Test and True alignments";
		sys.exit(0);
	
	for i in range(0,len(AMR_objects)):
		amrobj = AMR_objects[i];
		true = true_alignments[i];
		
		amrobj.evaluate_alignments(true);
		amrobj.print_alignments();
		print;

main();
	
