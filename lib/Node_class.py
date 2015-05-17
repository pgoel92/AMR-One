import re;

class node:

	def __init__(self, val, edge_ptrs,edge_ptrs_nr,edge_name):
		self.value = self.DecomposeNodeValue(val);				#value of current node
		self.edge_name = edge_name;		#name of the edge pointing to this node
		self.edge_ptrs = edge_ptrs;		#list of child node objects
		#self.edge_names = edge_names;	#list of edge names for each child node edge
		self.reent = [];				#binary list indicating whether edge is a re-entrancy
		self.edge_ptrs_nr = edge_ptrs_nr;		#list of child node objects excluding ones that are re-entrancies
		self.aligned_to = -1;			#token number of the token this node is aligned to. -1 if the node is unaligned.

	def setValue(self,val):
		self.value = self.DecomposeNodeValue(val);

	def addEdge(self,ptr,reent):
		#self.edge_names.append(name);
		self.edge_ptrs.append(ptr);
		self.edge_ptrs_nr.append(ptr);
		self.reent.append(reent);

	def printSubtree(self,index):
		print index,"(" + self.RecomposeNodeValue(self.value) + ")";
		for i in range(0,len(self.edge_ptrs_nr)):
			#print len(self.edge_ptrs_nr);
			#print self.edge_names[i];
			self.edge_ptrs_nr[i].printSubtree(index+'.'+str(i+1));

	'''
	 Takes as input a node value from an AMR graph
	 and returns the list : [ node_name, concept ]
	 i.e. "a / person" -> [ "a", "person" ]
		  "1992" 	   -> [ "", "1992" ]
	'''	
	def DecomposeNodeValue(self, val):
	
		try:
			i = val.index('/');	
		#If unnamed node
		except ValueError:
			# [ node_name, concept ]
			return ['', val];

		# [ node_name, concept ]
		return [val[:i-1], val[i+2:]];

	def RecomposeNodeValue(self, val_ls):		

		if val_ls[0] == '':
			return val_ls[1];	
		
		return val_ls[0] + " / " + val_ls[1];

	def cleanConcept(self, concept):
	#Takes a concept as input and returns the cleaned version
		#print "__"+concept+"__";   
		if len(concept) > 1 and concept[0] == '"': concept = concept[1:-1];  #Remove quotation marks
		concept = re.sub('\-[0-9]+$','',concept);       #Remove number tags
		
		return concept;

	def linearize(self, addr):

		out = [];

		#If leaf node	
		if len(self.edge_ptrs_nr) == 0:
			#Append ( (incoming_edge_name, concept), node_address ) to output
			out.append(((self.edge_name, self.cleanConcept(self.value[1])), addr));
			return out;
		
		#Add incoming edge name and value to list	
		out.append(((self.edge_name, self.cleanConcept(self.value[1])), addr));

		#Recurse on children
		for i in range(0,len(self.edge_ptrs_nr)):
			child = self.edge_ptrs_nr[i];
			out += child.linearize(addr+'.'+str(i+1));

		return out;


	def getConcepts(self,index):	#Returns a list of concepts and their JAMR node addresses
	
		concepts = [];	
		concepts.append((self.value[1],index));	
		
		if len(self.edge_ptrs) == 0: return concepts;
	
		for i in range(0,len(self.edge_ptrs_nr)):
			child = self.edge_ptrs_nr[i];
			subc = child.getConcepts(index+'.'+str(i+1)); 	
			concepts = concepts + subc;	

		return concepts;

	def getNodeByAddress(self,address,jamr_addr):
		
		role = 0;
		if address[-1] == 'r':
		    address = address[:-2]; 
		    role = 1;
		if address == '1':
		    return self.getValue();
		childnum, newaddress = self.getSubtreeAddress(address);
		return self.getNode(newaddress,role,jamr_addr);
	
	'''
	 Converts the AMR tree into a string.
	'''	
	def generatePrintableAMR(self,s,tabs, nobracket):
	
		#nonewlinelist = ['op1','op2','op3','op4','op5','quant','polarity','month','day'];

		#if nobracket: s = s + self.value;
		#else: s = s + '(' + self.value;			
		child_nobracket = True;
		s = s + '(' + self.RecomposeNodeValue(self.value);

		if len(self.edge_ptrs) == 0: 
			#if nobracket: return s;
			return s + ')';

		for i in range(0,len(self.edge_ptrs)):
			child = self.edge_ptrs[i];
		
			##If special child, don't add brackets and don't add newline
			#if child.edge_name in nonewlinelist:
			#	child_nobracket = True;
			#else: 
			#	child_nobracket = False;
			s = s + '\n' + tabs + ':' + child.edge_name + ' ';
		
			#If not reentrancy, recurse
			if self.reent[i] == 0:
				s = child.generatePrintableAMR(s,tabs + '\t', child_nobracket);
			else:
				v = self.edge_ptrs[i].getValue();
				v = v.split('/');
				s = s + v[0]; 
				

		#if not nobracket : s = s + ')';
		s = s + ')';

		return s;

	def getValue(self):

		return self.RecomposeNodeValue(self.value);

#	def getCorrectEdgeIndex(self,index):	#Skips re-entrancy edges and assigns a new index
#		
#		while self.reent[index] == 1:
#			index = index + 1;
#		return index

	def adjustIndices(self):			#Makes edge_ptrs_nr consistent with JAMR addressing by deleting all re-entrancy edge pointers
		if len(self.edge_ptrs) == 0: 	#Leaf node
			return;
		edge_ptrs_wo_reentrancies = [];
		for i in range(0,len(self.reent)):
			if self.reent[i] != 1:
				edge_ptrs_wo_reentrancies.append(self.edge_ptrs_nr[i]);
		self.edge_ptrs_nr = edge_ptrs_wo_reentrancies;	
		#self.edge_ptrs_nr[i];
		for ptr in self.edge_ptrs_nr:		#Recurse on non-reentrancy edges
			ptr.adjustIndices();

			
#	def printEdgeAndReent(self):
#		if len(self.edge_names) == 0: return;
#		#print self.edge_names;
#		#print self.reent;	
#		#print
#		for edge in self.edge_ptrs:
#			edge.printEdgeAndReent();

	def getNode(self,address,r,jamr_addr):
		
		#address : The address of node relative to the root of the current subtree
		#r : Tells whether or not the address refers to a role	
		#jamr_addr : Tells whether addressing format is from JAMR (1) or ISI (0)
		childnum, newaddress = self.getSubtreeAddress(address);	
		if len(address) == 1:	#if we are 1 step away from target node 
			if not r: 
				if jamr_addr == 1: return self.edge_ptrs_nr[childnum].getValue();
				#print childnum;
				return self.edge_ptrs[childnum].getValue();
			else: return self.edge_ptrs[childnum-1].edge_name;
		else:					
			if len(self.edge_ptrs) == 0: return "Node does not exist";
			elif childnum > len(self.edge_ptrs): return "Node does not exist";	
			else: 
				if jamr_addr == 1: return self.edge_ptrs_nr[childnum].getNode(newaddress,r,jamr_addr);
				return self.edge_ptrs[childnum].getNode(newaddress,r,jamr_addr);	#recurse on child node

	def getSubtreeAddress(self, address):

		i = address.find('.');	
		
		if i == -1: 
			return int(address)-1, address;

		childnum = int(address[0:i])-1;
		return childnum, address[i+1:];
		
	def getNodePointer(self,address,r,jamr_addr):
		
		#address : The address of node relative to the root of the current subtree
		#r : Tells whether or not the address refers to a role	
		#jamr_addr : Tells whether addressing format is from JAMR (1) or ISI (0)
		childnum, newaddress = self.getSubtreeAddress(address);
		#childnum = int(address[0])-1;	
		if address.find('.') == -1:	#if we are 1 step away from target node 
			if not r: 
				if jamr_addr == 1: return self.edge_ptrs_nr[childnum];
				return self.edge_ptrs[childnum];
			else: return self.edge_ptrs[childnum-1].edge_name;
		else:					
			if len(self.edge_ptrs) == 0: return "Node does not exist";
			elif childnum > len(self.edge_ptrs): return "Node does not exist";	
			else: 
				if jamr_addr == 1: return self.edge_ptrs_nr[childnum].getNodePointer(newaddress,r,jamr_addr);
				return self.edge_ptrs[childnum].getNodePointer(newaddress,r,jamr_addr);	#recurse on child node
	
	def ISItoJAMR(self,address, new_address):
		
		childnum = int(address[0]) - 1;
		new_childnum = childnum+1;
		for i in range(0,childnum):	
			if self.reent[i] != 0:
				new_childnum = new_childnum - 1;
		
		if len(address) == 1:
			return new_address + "." + str(new_childnum);
		else:
			if len(self.edge_ptrs) == 0: return "Node does not exist";
			elif childnum > len(self.edge_ptrs): return "Node does not exist";	
			else: 
				return self.edge_ptrs[childnum].ISItoJAMR(address[2:], new_address + "." + str(new_childnum));	#recurse on child node
			
	def isReentrancy(self,address):
			
		childnum = int(address[0])-1;	
		if len(address) == 1:	#if we are 1 step away from target node 
			if self.reent[childnum] == 1: return self.edge_ptrs[childnum].getValue();
			return False;
		else:					
			if len(self.edge_ptrs) == 0: return False;
			elif childnum > len(self.edge_ptrs): return False;	
			else: 
				return self.edge_ptrs[childnum].isReentrancy(address[2:]);	#recurse on child node
		
def increment(amrstr,i): 
	
	if i==len(amrstr)-1: return ('EOF',i);
	return (amrstr[i+1],i+1);

def cloneNodeWithNewEdgename(n, ename):

	return node(n.value, n.edge_ptrs, n.edge_ptrs_nr, ename);

def parse(amrstr,i,varlist,edgename):

	nonreentleaf_edgenames = ['polarity', 'op1', 'op2', 'op3', 'op4', 'op5', 'day', 'month', 'year', 'decade', 'time', 'value', 'quant', 'mode'];

	root = node("",[],[],edgename);				#Create root node
	#print len(amrstr),i	
	cur = amrstr[i];					
	nodeval = '';
	while cur != ':' and cur != ')':	#End conditions for root name
		nodeval = nodeval + cur;	
		(cur,i) = increment(amrstr,i);

	#read variable name from nodeval and store in a list
	k = 0;
	varname = '';
	while nodeval[k]!= ' ':
		varname = varname + nodeval[k];	
		k = k+1;
	varlist[varname] = root;			#Make copy of object and store?

	if cur == ':': root.setValue(nodeval[:-1]);			#Remove space at the end of root name and set it
	else: root.setValue(nodeval);
	#print "Root value set"
	#i = i+1;
	#cur = amrstr[i];
	if cur == ')': 
		(cur,i) = increment(amrstr,i);
		return (root,i);	#If leaf node, return
	else: 								#It's a colon entity
		i=i+1
		cur = amrstr[i];

	#Having read the root node value, read edges in a loop
	reent = 0;
	while cur != ')' and cur != 'EOF':
		edgename = '';
		while cur != ' ':
			edgename = edgename + cur;
			(cur,i) = increment(amrstr,i);
		#print edgename
		i = i+1;						#Read space after edge name
		cur = amrstr[i];	
		if cur == '(':					#If edge points another AMR i.e subtree
			(edgeptr,i) = parse(amrstr,i+1,varlist,edgename);	#Recurse on the nested AMR and save a pointer to it in my current root
			reent = 0;
			cur = amrstr[i];
		else:							#If edge points to a leaf node
			#(cur,i) = increment(amrstr,i);
			leafnodeval = '';
			if cur == '"':							#leafnode is a quoted entity
				leafnodeval += '\"';
				(cur,i) = increment(amrstr,i);
				while cur != '\"':
					leafnodeval = leafnodeval + cur;
					(cur,i) = increment(amrstr,i);
				leafnodeval += '\"';
				(cur,i) = increment(amrstr,i);
			else:
				while cur != ' ' and cur != ')':	#End conditions for a leaf node name
					leafnodeval = leafnodeval + cur;	
					(cur,i) = increment(amrstr,i);
			#print edgename, leafnodeval;
			#if leafnodeval in varlist:			#Re-entrancy
			if leafnodeval in varlist or edgename not in nonreentleaf_edgenames:			#Re-entrancy
			#Note : 2nd condition alone should do the job
				reent = 1;
				try:
					#edgeptr = varlist[leafnodeval];	#Re route re-entrancy to the original node
					edgeptr = cloneNodeWithNewEdgename(varlist[leafnodeval], edgename);		#Re route re-entrancy to the original node
				except KeyError:					#If re-entrancy variable occurs before actual node, create a new node because rerouting not possible
					edgeptr = node(leafnodeval, [], [], edgename);
		#	elif (len(leafnodeval) == 1 or len(leafnodeval) == 2) and leafnodeval not in varlist: 	#Node is a reentrancy but the original node has not occurred.
		#																							#Assumption that variable names can only be 1 or 2 character long
		#		reent = 1;	
		#		edgeptr = node(leafnodeval,[],[],edgename);
			else: edgeptr = node(leafnodeval,[],[],edgename);	#Store pointer to leaf node
		root.addEdge(edgeptr,reent);		#Add new edge to current root
		#print "New edge added"
		#(cur,i) = increment(amrstr,i);
		if cur == ' ': 					#Current root has another child node
			i = i+2;					#Jump to name of edge
			cur = amrstr[i];
			#print cur
	(cur,i) = increment(amrstr,i);
	#print "Returning with current char __" + cur + "__"
	return (root,i);

#def print_amr(amr):
#
#	amr.printSubtree('1');
#
def parse_amr(amr):

		
	(r,i) = parse(amr,1,{},'');
	r.adjustIndices();				#Removes re-entrancy nodes to create edge_ptrs_nr from edge_ptrs
	return r;

#def printStuff(amr):
#		
#	amr.printEdgeAndReent();

def isReent(amr,address):
	
	if address == '1': return False;
	else: return amr.isReentrancy(address[2:]);
#def get_node_by_address(amr_obj,address,jamr_addr):
#
#	role = 0;
#	if address[-1] == 'r':
#		address = address[:-2]; 
#		role = 1;
#	if address == '1':
#		return amr_obj.getValue();
#	else: 
#		return amr_obj.getNode(address[2:],role,jamr_addr);
#	
#	#r.printSubtree('1');
