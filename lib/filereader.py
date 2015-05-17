#!/usr/bin/python

'''
 Reads a file containing one sentence per line as space separated tokens.
 Outputs a list containing each sentence as a list of tokens.
'''
def read_sentence_per_line(fname):

	f = open(fname);
	temp = f.readlines();
	f.close();

	return [x[:-1].split() for x in temp];
