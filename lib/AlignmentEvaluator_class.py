#!/usr/bin/python

from __future__ import print_function
import sys

#Alignment format specification
#Test alignments
test_tok_addr_separator = '|';
test_tok_range_separator = '-';
test_multiple_addr_separator = '+';
test_addr_child_separator = '.';

#Test alignments
true_tok_addr_separator = '-';
true_tok_range_separator = '_';
true_multiple_addr_separator = '+';
true_addr_child_separator = '.';

class AlignmentEvaluator:

	def __init__(self):
		self.test_tokens = [];
		self.true_tokens = [];
		self.test_addr = [];
		self.true_addr = [];
		self.test_concepts = [];
		self.true_concepts = [];
		self.TP = 0;
		self.FP = 0;
		self.FN = 0;
		self.FP_examples = [];
		self.FN_examples = [];

	def OffsetNodeAddress(self, addr, offset):
               
		if addr == '': return ''; 
		if offset == 0: return addr;

		addr = addr.split(test_addr_child_separator)		#If test and true child separators are not the same, this won't work. I just dont want extra arguments right now.
		new_addr = []; 
		for num in addr:
			if int(num) < 0:
			    print("Invalid address: Negative node addresses not supported", file=sys.stderr);
			    sys.exit(0);
			new_addr.append(str(int(num) + offset));
    
		return test_addr_child_separator.join(new_addr);

	def ConvertISItoJAMR(self, addr, AMR_tree):

		if addr == '1': return '1';
		return (AMR_tree).ISItoJAMR(address[2:],'1');
			
	def read(self, test_alignments, true_alignments,addr_offset, AMR_tree):	#if test address is 0.1.2 and corresponding true address is 1.2.3, then addr_offset is 1
		
		#test_alignments = test_str.split();
		#true_alignments = true_str.split();

		for alignment in test_alignments:
			alignment = alignment.split(test_tok_addr_separator);	#Splits alignment into token and node address
			tokens = alignment[0].split(test_tok_range_separator);	#For token sequences of the form 23-25
			addresses = alignment[1].split(test_multiple_addr_separator);		#For addresses of the form 1.1+1.1.1+1.1.1.1
			start_token = int(tokens[0]);
			if len(tokens) > 1: end_token = int(tokens[1]);
			else: end_token = start_token + 1;
			for i in range(start_token,end_token):	#For each token aligned to the given addresses
				self.test_tokens.append(i);						#Add token to test_tokens
				for address in addresses:
					address = self.OffsetNodeAddress(address, addr_offset);		#Correct the node address by adding offset to each number in the address
					concept = AMR_tree.getNodeByAddress(address, 0); 			#Lookup the AMR tree using the address
					self.test_addr.append(address);		
					self.test_concepts.append(concept);		
		
		for alignment in true_alignments:
			alignment = alignment.split(true_tok_addr_separator);
			tokens = alignment[0].split(true_tok_range_separator);
			addresses = alignment[1].split(true_multiple_addr_separator); 
			start_token = tokens[0];
			if len(tokens) > 1: end_token = tokens[1];
			else: end_token = start_token + 1;
			for i in range(int(start_token),int(end_token)):	#For each token aligned to the given addresses
				self.true_tokens.append(i);						#Add token to test_tokens
				for address in addresses:
					address = OffsetNodeAddress(address, 0);		#Correct the node address by adding offset to each number in the address
					newaddress = ConvertISItoJAMR(address); 		###Convert ISI address to JAMR style address (not a general feature)
					concept = AMR_tree.getNodeByAddress(address); 			#Lookup the AMR tree using the ISI address, which is the most general addressing scheme
					self.test_addr.append(newaddress);						#Add the converted address to the list for comparison
					self.test_concepts.append(concept);		
	
	def print_alignments(self):

		for i in range(0,len(self.test_tokens)):
			print (self.test_tokens)[i] + '-' + self.test_addr[i] + ' ';
		for i in range(0,len(self.true_tokens)):
			print (self.true_tokens)[i] + '-' + self.true_addr[i] + ' ';
