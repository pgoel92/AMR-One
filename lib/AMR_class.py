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
		self.AMR_string_printable = '';			#AMR string prints just like in the original file
		self.AMR_aligned_string_printable = '';	#AMR string annotated with alignment information prints in tree format
		self.AMR_string_parsable = '';			#Linearized AMR string
		self.AMR_tree = None;	
		self.AMR_tree_aligned = None;			#AMR tree annotated with alignment information
		self.AMR_dict = {};						#facilitates AMR string and tree lookup by ID
		self.Evaluator = AlignmentEvaluator();

	def read(self,s):
	#reads a string that describes the AMR and parses the string into components
		s = s.split('\n');

		#Read AMR literal
		AMR_lines = s[5:];
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
		snt_line = s[1];	
		self.sentence = snt_line[8:];

		tok_line = s[3];
		self.tokens = (tok_line[8:]).split();
		#print self.tokens;	

		alignment_line = (s[4]).split();
		self.alignments = alignment_line[2:-5];	#remove the ::alignment tag
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
	
	def evaluate_alignments(self, true_str):
	
		self.Evaluator.read(self.alignments, true_str, 0, self.AMR_tree);
		self.Evaluator.evaluate();
		return self.Evaluator.getStatistics();

	def print_alignments(self):
		
		self.Evaluator.print_alignments();

	def generate_printable_AMR(self):

		self.AMR_aligned_string_printable =  self.AMR_tree_aligned.generatePrintableAMR('','\t');
			
	def generate_writable(self):
	
		s = '';
		s = s + "# ::id " + self.ID + '\n';
		s = s + "# ::snt " + self.sentence + '\n';
		s = s + "# ::save-date\n";
		s = s + "# ::tok";
		for i in range(0,len(self.tokens)):
			s = s + ' ' + str(i) + '-' + self.tokens[i];
		s = s + '\n';
		s = s + '# ::alignments ' + ' '.join(self.alignments) + ' * * * * *\n';
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

	def annotate(self, token_number, address):

		if (address == '1'): n = self.AMR_tree_aligned;
		else: n = self.AMR_tree_aligned.getNodePointer(address[2:], 0, 1);	
		v = n.getValue();
		v = v.split();	#v[0] is the variable, v[1] is the '/' character and v[2] is the concept name
		newvar = v[0]+"~"+str(token_number);
		if len(v) > 1: 
			n.setValue(newvar + " " + v[1] + " " + v[2]);
		else: n.setValue(newvar);	

	def convertISItoJAMR(self,address):
		
		if address == '1': return '1';
		return (self.AMR_tree).ISItoJAMR(address[2:],'1');
		
	def getConcepts(self):
			
		return self.AMR_tree.getConcepts('1');

	def getTokens(self):
		
		return self.tokens;	
	
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
		amr_objects.append(a);
		
	return amr_objects;
