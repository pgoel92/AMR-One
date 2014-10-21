#!/usr/bin/python
import re

punc = ['"',';',':','.',',','?','!','-','--']
def get_avg_length(filename):

	f = open(filename);
	f = f.readlines();
	lnum = 0.0;
	llen = 0.0;
	max_len = 0;
	for line in f:
		if re.match('.*::tok .*',line):
			lnum = lnum + 1;
			tokens = line[8:].split();
			newtokens = []
			for tok in tokens:
				if tok not in punc:
					newtokens.append(tok);	
			sntlen = len(newtokens);
			if sntlen > max_len: 
				max_len = sntlen;
				max_line = line;
			llen = llen + sntlen;

	print max_len
	print max_line
	print llen/lnum;

get_avg_length('corp-span-perfect');		
get_avg_length('corp-span-imperfect');		
