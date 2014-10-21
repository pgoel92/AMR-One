import re
from my_amr_parser import node, parse_amr;
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
		self.AMR_string_parsable = '';
		self.AMR_tree = None;	

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
		
		alignment_line = s[4];
		alignment_line = alignment_line[15:];
		for i in range(0,len(alignment_line)):
			if alignment_line[i] == ':':
				break;
		self.alignments = alignment_line[:i-1];
		return;

	def generate_writable(self):
	
		s = '';
		s = s + "# ::id " + self.ID + '\n';
		s = s + "# ::snt " + self.sentence + '\n';
		s = s + "# ::tok";
		for tok in self.tokens:
			s = s + ' ' + tok;
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
			return (self.AMR_tree).getVal();
		return (self.AMR_tree).getNode(address[2:],role,jamr_addr);

	def getConcepts(self):
			
		return self.AMR_tree.getConcepts('1');

	def getTokens(self):
		
		return self.tokens;	

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
		
	return amr_objects;
