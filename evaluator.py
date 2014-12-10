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

	TP = 0;	
	FP = 0;
	FN = 0;

	for i in range(0,len(AMR_objects)):

		amrobj = AMR_objects[i];

		#print amrobj.ID;
		#print amrobj.tokens;
		#print amrobj.alignments;
		#print amrobj.AMR_string_printable;

		true = true_alignments[i];
		#(tp, fp, fn) = amrobj.evaluate_alignments(true);
		try:
			(tp, fp, fn) = amrobj.evaluate_alignments(true);
		except IndexError:
			continue;
		TP = TP + tp;
		FP = FP + fp;
		FN = FN + fn;
	Precision = (TP/float(TP+FP))*100;
	Recall = (TP/float(TP+FN))*100;
	print "Precision : ", Precision;
	print "Recall : ", Recall;
	print;
	print;
	for i in range(0,len(AMR_objects)):

		amrobj = AMR_objects[i];
		true = true_alignments[i];
		
		print "#" +amrobj.ID;
		print "#" +' '.join(amrobj.tokens);
		print "#" +' '.join(amrobj.alignments);
		print "#" +' '.join(true);
		print amrobj.AMR_string_printable;
		print;
		evaluator = amrobj.Evaluator;
		evaluator.print_result();
		print;
		
main();
