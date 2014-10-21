import re
from Node_class import node, parse_amr;
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
		self.new_alignments = '';
		self.alignment_annotator = '';
		self.alignment_date = '';
		self.AMR_string_printable = '';
		self.AMR_aligned_string_printable = '';
		self.AMR_string_parsable = '';
		self.AMR_tree = None;	
		self.AMR_tree_aligned = None;

	def read(self,s):
	#reads a string that describes the AMR and parses the string into components
		s = s.split('\n');

		#Read AMR literal
		AMR_lines = s[5:];
		self.AMR_string_printable='\n'.join(AMR_lines);
		
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
	
		snt_line = s[1];	
		self.sentence = snt_line[8:];

		tok_line = s[3];
		self.tokens = (tok_line[8:]).split();
		#print self.tokens;	

		alignment_line = s[4];
		alignment_line = alignment_line[15:];
		for i in range(0,len(alignment_line)):
			if alignment_line[i] == ':':
				break;
		alignment_line = alignment_line[:i-1];
		temp_split = alignment_line.split();
		alignments = '';
		for item in temp_split[:-5]:
			alignments = alignments + " " + item;
		self.alignments = alignments[1:];
		return;

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
		s = s + '# ::alignments' + self.new_alignments + ' * * * * *\n';
		s = s + self.AMR_string_printable;
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
		
		if address == '1':
			return (self.AMR_tree).getValue();
		return (self.AMR_tree).ISItoJAMR(address[2:],'1');
		
	def getConcepts(self):
			
		return self.AMR_tree.getConcepts('1');

	def getTokens(self):
		
		return self.tokens;	
	
	def getAlignments(self):
		
		return self.alignments;
	
	def getAMRTree(self):
		
		return self.AMR_tree;

	def setAlignments(self,alignments):
		
		self.new_alignments = alignments;

#Reads a corpus file and returns a list of AMR objects	
def read_corpus_file(fname):

	f=open(fname);
	s=f.read();
	f.close();
	
	s = s.split('\n\n');	
	del s[0];
	del s[-1];
	amr_objects = [];	
	for amr_desc in s:
		a = AMR();
		a.read(amr_desc);
		amr_objects.append(a);
		amr_str = a.AMR_string_parsable;
		amr_tree = parse_amr(amr_str);	
		a.AMR_tree = amr_tree;
		a.AMR_tree_aligned = amr_tree;	#Do they both point to the same object in memory?
		
	return amr_objects;
