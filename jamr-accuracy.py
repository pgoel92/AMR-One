#!/usr/bin/python

from lib.AMR_class import read_corpus_file

amrobjs = read_corpus_file('../jamr-master/test-jamr');

for obj in amrobjs:
	a = obj.alignments;
	newa = [];
	for alignment in a:
		alignment = alignment.split('|');
		tokens = alignment[0];
		tokens = tokens.split('-');
		concepts = alignment[1];
		concepts = concepts.split('+');
		
		for i in range(int(tokens[0]),int(tokens[1])):
			for concept in concepts:
				newa.append(str(i)+"-"+str(i+1)+"|"+concept);
	obj.setAlignments(newa);

s = '';
for obj in amrobjs:

	s = s + obj.generate_writable();
	s = s + '\n';

print s;
	
