#!/usr/bin/python

import sys

#Alignment format specification
#Test alignments
test_tok_addr_separator = '|';
test_tok_range_separator = '-';
test_multiple_addr_separator = '+';
test_addr_child_separator = '.';

#True alignments
true_tok_addr_separator = '-';
true_tok_range_separator = '_';
true_multiple_addr_separator = '+';
true_addr_child_separator = '.';

class AlignmentEvaluator:

	def __init__(self):
		self.test_tokens = [];					#List of tokens aligned in the test set. If a token is aligned to multiple concepts, it occurs multiple times.
		self.true_tokens = [];					#List of tokens aligned in the true set. If a token is aligned to multiple concepts, it occurs multiple times.
		self.test_addr = [];					#List of addresses aligned in the test set.
		self.true_addr = [];
		self.test_concepts = [];
		self.true_concepts = [];
		self.TP = 0;
		self.FP = 0;
		self.FN = 0;
		self.FP_examples = [];
		self.FN_examples = [];
		self.test_role_count = 0;	#Debugging purposes
		self.true_role_count = 0;	#Debugging purposes

	def OffsetNodeAddress(self, addr, offset):
               
		if addr == '': return ''; 
		if offset == 0: return addr;

		addr = addr.split(test_addr_child_separator)		#If test and true child separators are not the same, this won't work. I just dont want extra arguments right now.
		new_addr = []; 
		for num in addr:
			if int(num) < 0:
			    print "Invalid address: Negative node addresses not supported";
			    sys.exit(0);
			new_addr.append(str(int(num) + offset));
    
		return test_addr_child_separator.join(new_addr);

	def ConvertISItoJAMR(self, addr, AMR_tree):

		if addr == '1': return '1';
		return (AMR_tree).ISItoJAMR(addr[2:],'1');
	
	def isRole(self, addr):
		
		return addr[-1] == 'r';	

	def RoleFunction(self, addr):
		
		return;

	def read(self, test_alignments, true_alignments,addr_offset, AMR_tree):	#if test address is 0.1.2 and corresponding true address is 1.2.3, then addr_offset is 1
	
		#test_alignments = test_str.split();
		#true_alignments = true_str.split();
		#print AMR_tree.generatePrintableAMR('','\t');
		for alignment in test_alignments:
			alignment = alignment.split(test_tok_addr_separator);	#Splits alignment into token and node address
			tokens = alignment[0].split(test_tok_range_separator);	#For token sequences of the form 23-25
			addresses = alignment[1].split(test_multiple_addr_separator);		#For addresses of the form 1.1+1.1.1+1.1.1.1
			start_token = int(tokens[0]);
			if len(tokens) > 1: end_token = int(tokens[1]);
			else: end_token = start_token + 1;

			atleast_one_non_role = 0;
			for i in range(start_token,end_token):	#For each token aligned to the given addresses
				for address in addresses:
					if self.isRole(address):			#Do not count role alignments towards accuracy
						self.test_role_count += 1;
						self.RoleFunction(address);		#For future analysis of role tokens
					else:
						atleast_one_non_role = 1;
						address = self.OffsetNodeAddress(address, addr_offset);		#Correct the node address by adding offset to each number in the address
						#print address;
						concept = AMR_tree.getNodeByAddress(address, 1); 			#Lookup the AMR tree using the address
						self.test_addr.append(address);		
						self.test_concepts.append(concept);		
				if atleast_one_non_role: self.test_tokens.append(str(i));						#Add token to test_tokens
		
		for alignment in true_alignments:
			alignment = alignment.split(true_tok_addr_separator);
			tokens = alignment[0].split(true_tok_range_separator);
			addresses = alignment[1].split(true_multiple_addr_separator); 
			start_token = int(tokens[0]);
			if len(tokens) > 1: end_token = int(tokens[1]);
			else: end_token = start_token + 1;
	
			atleast_one_non_role = 0;
			for i in range(start_token,end_token):	#For each token aligned to the given addresses
				for address in addresses:
					if self.isRole(address):			#Do not count role alignments towards accuracy
						self.true_role_count += 1;
						self.RoleFunction(address);		#For future analysis of role tokens
					else:
						atleast_one_non_role = 1;
						address = self.OffsetNodeAddress(address, 0);		#Correct the node address by adding offset to each number in the address
						newaddress = self.ConvertISItoJAMR(address, AMR_tree); 		###Convert ISI address to JAMR style address (not a general feature)
						#print address, newaddress;
						concept = AMR_tree.getNodeByAddress(address,0); 			#Lookup the AMR tree using the ISI address, which is the most general addressing scheme
						#print address, concept; 
						self.true_addr.append(newaddress);						#Add the converted address to the list for comparison
						self.true_concepts.append(concept);		
				if atleast_one_non_role: self.true_tokens.append(str(i));						#If all alignments are roles, then true_addr would be empty
																								#In that case, do not add token to true_tokens;
		
		#if len(test_alignments) != len(self.test_tokens)	or len(test_alignments) != len(self.test_addr): print "Error";
		#if len(true_alignments) != (len(self.true_tokens) + self.role_count): print "Error";
		#if len(true_alignments) != (len(self.true_addr) + self.role_count): print "Error";

	def evaluate(self):

		test_alignments = [];	
		true_alignments = [];	

		for i in range(0,len(self.test_tokens)):
			test_alignments.append((self.test_tokens)[i] + '-' + (self.test_addr)[i]);
		for i in range(0,len(self.true_tokens)):
			true_alignments.append((self.true_tokens)[i] + '-' + (self.true_addr)[i]);
		for elt in test_alignments:
			if elt in true_alignments:			#True Positive
				self.TP += 1;	
			else: 								#False Positive
				self.FP += 1;
				self.FP_examples.append(elt);
		
		for elt in true_alignments:
			if elt not in test_alignments:		#False Negative
				self.FN += 1;
				self.FN_examples.append(elt);

	def getStatistics(self):
			
		return (self.TP, self.FP, self.FN);

	def print_result(self):

		print "False Positives : ";
		for elt in self.FP_examples:
			print elt;
		print "False Negatives : ";
		for elt in self.FN_examples:
			print elt;

	def print_alignments(self):
	
		for i in range(0,len(self.test_tokens)):
			print (self.test_tokens)[i] + '-' + (self.test_addr)[i] + ' ',
		print;
		for i in range(0,len(self.true_tokens)):
			print (self.true_tokens)[i] + '-' + (self.true_addr)[i] + ' ',
		print;
