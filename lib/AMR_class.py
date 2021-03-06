####
# Concept : A concept is the value of an AMR node after the variable has been removed
# Concept cleaning : Includes removal of quotation marks and stripping out number tags

import re
from Node_class import node, parse_amr;
from AlignmentEvaluator_class import AlignmentEvaluator

class AMR:

	def __init__(self):
		self.ID = '';
		self.date = '';
		self.annotator = '';
		self.sentence = '';
		self.save_date = '';
		self.file = '';
		self.tokens = [];
		self.alignments = '';
		self.alignment_annotator = '';
		self.alignment_date = '';
		self.NumberOfConcepts = 0;
		self.AMR_string_printable = '';			#AMR string prints just like in the original file
		self.AMR_aligned_string_printable = '';	#AMR string annotated with alignment information prints in tree format
		self.AMR_string_parsable = '';			#Linearized AMR string
		self.AMR_tree = None;	
		self.AMR_tree_aligned = None;			#AMR tree annotated with alignment information
		self.AMR_dict = {};						#facilitates AMR string and tree lookup by ID
		self.Evaluator = AlignmentEvaluator();
		
	#	Methods :

	#	read(self,s)
	#	evaluate_alignments
	#	print_alignments
	#	generate_printable_AMR
	#	generate_writable
	#	printAMR
	#	getNodeByAddress
	#	annotate_node
	#	convertISItoJAMR
	#	getConcepts
	#	getTokens
	#	getAlignments
	#	getAMRTree
	#	getAMRStringByID
	#	getAMRTreeByID
	#	setAlignments
	
	def read(self,s):
	#reads a string that describes the AMR and parses the string into components
		s = s.split('\n');
		#Read AMR literal
		if s[3][0] == '#':		#indicates that there is an alignment line
			alignment_line = (s[3]).split();
			self.alignments = alignment_line[2:-5];	#remove the ::alignment tag
			AMR_lines = s[4:];
		else: AMR_lines = s[3:];
		self.AMR_string_printable='\n'.join(AMR_lines);
		self.AMR_aligned_string_printable=self.AMR_string_printable;
		
		AMR_lines = map(lambda s: s.lstrip(),AMR_lines);	
		self.AMR_string_parsable=' '.join(AMR_lines);
	
		ID_line = s[0];
		ID_line = ID_line.split();
		for i in range(0,len(ID_line)):
			prev_token=ID_line[i-1];
			if(prev_token == '::id'):
				self.ID = ID_line[i];
			if(prev_token == '::date'):
				self.date = ID_line[i];
			if(prev_token == '::annotator'):
				self.annotator = ID_line[i];
		self.AMR_tree = parse_amr(self.AMR_string_parsable);		
		self.AMR_tree_aligned = self.AMR_tree;
		self.AMR_dict[self.ID] = [self.AMR_string_printable, self.AMR_tree];	#Ideally, we should be able to generate the printable string from the tree. 
																				#Then we wouldn't have to save the printable string at all.

		self.NumberOfConcepts = len(self.getConcepts(0));
		snt_line = s[1];	
		self.sentence = snt_line[8:];

	#	tok_line = s[3];
	#	self.tokens = (tok_line[8:]).split();
	#	#print self.tokens;	

	#	for i in range(0,len(alignment_line)):	#not sure what this is for, probably some border case
	#		if alignment_line[i] == ':':
	#			break;
	#	alignment_line = alignment_line[:i-1];	
	#	temp_split = alignment_line.split();	
	#	alignments = '';
	#	for item in temp_split[:-5]:			#remove the last 5 tokens after splitting. These are other metadata.
	#		alignments = alignments + " " + item;
	#	alignments = alignments[1:];

		return;
	
	def evaluate_alignments(self, true_alignments):
	
		self.Evaluator.read(self.alignments, true_alignments, 0, self.AMR_tree);
		self.Evaluator.evaluate();
		return self.Evaluator.getStatistics();

	def print_alignments(self):
		
		self.Evaluator.print_alignments();

	def generate_printable_AMR(self):

		self.AMR_aligned_string_printable =  self.AMR_tree_aligned.generatePrintableAMR('','\t');
		
	'''
	 Generates the AMR in corpus format. If annotation_flag is set, checks if alignment string is null,
	 if not, adds alignments to the nodes. 
	'''
	def generate_writable(self, annotation_flag):
	
		s = '';
		s = s + "# ::id " + self.ID + '\n';
		tokens = self.sentence.split();
		sentencewithnum = '';
		for i in range(0,len(tokens)):
			sentencewithnum += (tokens[i]+'-'+str(i)+' ');
		s = s + "# ::snt " + sentencewithnum[:-1] + '\n';
		s = s + "# ::save-date\n";
		#s = s + "# ::tok";
		#for i in range(0,len(self.tokens)):
		#	s = s + ' ' + str(i) + '-' + self.tokens[i];
		#s = s + '\n';
		s = s + '# ::alignments ' + ' '.join(self.alignments) + ' * * * * *\n';
		if annotation_flag and len(self.alignments) != 0:
			for alignment in self.alignments:
				alignment = alignment.split('|');
				address = alignment[1];
				toknum = alignment[0].split('-');
				toknum = toknum[0];
				self.annotate_node(address, toknum);	
			self.AMR_aligned_string_printable = self.AMR_tree_aligned.generatePrintableAMR('','\t',False);
		s = s + self.AMR_aligned_string_printable;
		s = s + '\n';
		
		return s;

	def printAMR(self):
		
		self.AMR_tree.printSubtree('1');
		return;

	def getNodeByAddress(self,address,jamr_addr):
        
		role = 0;
		if address[-1] == 'r':
			address = address[:-2]; 
			role = 1;
		if address == '1':
			return (self.AMR_tree).getValue();
		return (self.AMR_tree).getNode(address[2:],role,jamr_addr);

	def getSubtreeAddress(self, address):
	
		i = address.find('.');  
		
		if i == -1: 
			return int(address)-1, address;
		
		childnum = int(address[0:i])-1;
		return childnum, address[i+1:];

	'''
	 Find the AMR node using given address and annotates the concept with given
	 token number.
	'''
	def annotate_node(self, address, token_number):

		#If my getNode and getNodeByAddress functions were designed better, I wouldn't have to access the tree directly. 
		#Right now, those functions return the value at node. Instead, they should simply return the node itself.
		#Now there's too many strings attached to those functions and I'm afraid I'll mess something up.
		if (address == '1'): node = self.AMR_tree_aligned;
		else: 
			c, addr = self.getSubtreeAddress(address);
			node = self.AMR_tree_aligned.getNodePointer(addr, 0, 1);	

		v = node.getValue();
		i = v.find('/');
	
		if i == -1 or v[0] == '"':	#leaf node
			newval = v+"~"+str(token_number);
		else:
			v = v.split();	#v[0] is the variable, v[1] is the '/' character and v[2] is the concept name
			newval = v[0]+"~"+str(token_number) + " / " + v[2];

		node.setValue(newval);

	def convertISItoJAMR(self,address):
		
		if address == '1': return '1';
		return (self.AMR_tree).ISItoJAMR(address[2:],'1');
	
	def cleanConcept(self, concept):
	#Takes a concept as input and returns the cleaned version
		#print "__"+concept+"__";	
		if len(concept) > 1 and concept[0] == '"': concept = concept[1:-1];  #Remove quotation marks
		concept = re.sub('\-[0-9]+$','',concept);       #Remove number tags
	
		return concept;
	
	def getConcepts(self, clean):
	#clean == 1 means the concepts should be cleaned. 
	#Returns a list of tuples of the form (concept, address).

		clist = self.AMR_tree.getConcepts('1');
		if clean: 
			cleanclist = [(self.cleanConcept(x[0]),x[1]) for x in clist];
			clist = cleanclist;
		return clist;
	
	def linearize(self):	

		linearAMR = self.AMR_tree.linearize('1');
		return linearAMR;
		
	def getTokens(self):
		
		return (self.sentence).split();	
	
	def getAlignments(self):
		
		return self.alignments;
	
	def getAMRTree(self):
		
		return self.AMR_tree;

	def getAMRStringByID(self,ID):
		
		return self.AMR_dict[ID][0];
	
	def getAMRTreeByID(self,ID):
		
		return self.AMR_dict[ID][1];

	def setAlignments(self,alignments):
		
		self.alignments = alignments;

#Reads a corpus file and returns a list of AMR objects	
def read_corpus_file(fname):

	amr_objects = [];	
	
	f=open(fname);
	s=f.read();
	f.close();
	
	s = s.split('\n\n');	
	del s[0];
	del s[-1];
	
	for amr_desc in s:
		a = AMR();
		a.read(amr_desc);
		#print a.ID;
		amr_objects.append(a);
		
	return amr_objects;
