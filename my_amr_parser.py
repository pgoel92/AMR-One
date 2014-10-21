class node():

	def __init__(self, val, edge_ptrs,edge_ptrs_nr,edge_names):
		self.value = val;				#value of current node
		self.edge_ptrs = edge_ptrs;		#list of child node objects
		self.edge_names = edge_names;	#list of edge names for each child node edge
		self.reent = [];				#binary list indicating whether edge is a re-entrancy
		self.edge_ptrs_nr = edge_ptrs_nr;#list of child node objects excluding ones that are re-entrancies

	def setValue(self,val):
		self.value = val;

	def addEdge(self,name,ptr,reent):
		self.edge_names.append(name);
		self.edge_ptrs.append(ptr);
		self.edge_ptrs_nr.append(ptr);
		self.reent.append(reent);

	def printSubtree(self,index):
		print self.value,
		for i in range(0,len(self.edge_ptrs_nr)):
			#print len(self.edge_ptrs_nr);
			#print self.edge_names[i];
			self.edge_ptrs_nr[i].printSubtree(index+'.'+str(i+1));

	def getVal(self):
		return self.value

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
	
	def printEdgeAndReent(self):
		if len(self.edge_names) == 0: return;
		#print self.edge_names;
		#print self.reent;	
		#print
		for edge in self.edge_ptrs:
			edge.printEdgeAndReent();

	def getNode(self,address,r,jamr_addr):
		
		#address : The address of node relative to the root of the current subtree
		#r : Tells whether or not the address refers to a role	
		#jamr_addr : Tells whether addressing format is from JAMR (1) or ISI (0)
		childnum = int(address[0])-1;	
		if len(address) == 1:	#if we are 1 step away from target node 
			if not r: 
				if jamr_addr == 1: return self.edge_ptrs_nr[childnum].getVal();
				#print childnum;
				return self.edge_ptrs[childnum].getVal();
			else: return self.edge_names[childnum-1];
		else:					
			if len(self.edge_ptrs) == 0: return "Node does not exist";
			elif childnum > len(self.edge_ptrs): return "Node does not exist";	
			else: 
				if jamr_addr == 1: return self.edge_ptrs_nr[childnum].getNode(address[2:],r,jamr_addr);
				return self.edge_ptrs[childnum].getNode(address[2:],r,jamr_addr);	#recurse on child node

	def isReentrancy(self,address):
			
		childnum = int(address[0])-1;	
		if len(address) == 1:	#if we are 1 step away from target node 
			if self.reent[childnum] == 1: return self.edge_ptrs[childnum].getVal();
			return False;
		else:					
			if len(self.edge_ptrs) == 0: return False;
			elif childnum > len(self.edge_ptrs): return False;	
			else: 
				return self.edge_ptrs[childnum].isReentrancy(address[2:]);	#recurse on child node
		
def increment(amrstr,i): 
	
	if i==len(amrstr)-1: return ('EOF',i);
	return (amrstr[i+1],i+1);

def parse(amrstr,i,varlist):

	root = node("",[],[],[]);				#Create root node
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
			(edgeptr,i) = parse(amrstr,i+1,varlist);	#Recurse on the nested AMR and save a pointer to it in my current root
			reent = 0;
			cur = amrstr[i];
		else:							#If edge points to a leaf node
			#(cur,i) = increment(amrstr,i);
			leafnodeval = '';
			while cur != ' ' and cur != ')':	#End conditions for a leaf node name
				leafnodeval = leafnodeval + cur;	
				(cur,i) = increment(amrstr,i);
			if leafnodeval in varlist:			#Re-entrancy
				#print leafnodeval
				reent = 1;
				edgeptr = varlist[leafnodeval];	#Re route re-entrancy to the original node

			else: edgeptr = node(leafnodeval,[],[],[]);	#Store pointer to leaf node
		root.addEdge(edgename,edgeptr,reent);		#Add new edge to current root
		#print "New edge added"
		#(cur,i) = increment(amrstr,i);
		if cur == ' ': 					#Current root has another child node
			i = i+2;					#Jump to name of edge
			cur = amrstr[i];
			#print cur
	(cur,i) = increment(amrstr,i);
	#print "Returning with current char __" + cur + "__"
	return (root,i);

def print_amr(amr):

	amr.printSubtree('1');

def parse_amr(amr):

		
	(r,i) = parse(amr,1,{});
	r.adjustIndices();
	return r;

def printStuff(amr):
		
	amr.printEdgeAndReent();

def isReent(amr,address):
	
	if address == '1': return False;
	else: return amr.isReentrancy(address[2:]);
def get_node_by_address(amr_obj,address,jamr_addr):

	role = 0;
	if address[-1] == 'r':
		address = address[:-2]; 
		role = 1;
	if address == '1':
		return amr_obj.getVal();
	else: 
		return amr_obj.getNode(address[2:],role,jamr_addr);
	
	#r.printSubtree('1');
