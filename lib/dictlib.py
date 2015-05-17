#!/usr/bin/python

import operator

class counting_dictionary:

	def __init__(self):
		
		self.d = {};

	def insert(self, key, count):
	    if key in self.d:
	        self.d[key] = self.d[key] + count;
	    else: self.d[key] = count;

	def get(self, key):
		return self.d[key];

	def keys(self):
		return self.d.keys();

	'''
	 Returns a list of all keys whose counts are less than or equal to
	 threshold_count.
	'''
	def threshold(self, threshold_count):

	    sorted_d = sorted(self.d.iteritems(), key=operator.itemgetter(1),reverse=True);
	    cut_index = 0;
	    for i in range(0,len(sorted_d)):
	        if sorted_d[i][1] < threshold_count:
	            cut_index = i;
	            break;
	    return [x[0] for x in sorted_d[cut_index:]];

	def sort(self):

		return self.threshold(0);

	def number_of_elements(self):
		
		return len(self.d);

class value_dictionary:

	def __init__(self):
		
		self.d = {};

	def insert(self, item, value):
	    if item not in self.d: 
			self.d[item] = value;

	def get(self, key):
		return self.d[key];	
			
	def keys(self):
		return self.d.keys();
 
	def exists(self, key):
		return key in self.d;	
	'''
	 Returns a list of all keys whose counts are less than or equal to
	 threshold_count.
	'''
	def threshold(self, threshold_count):

	    sorted_d = sorted(self.d.iteritems(), key=operator.itemgetter(1),reverse=True);
	    cut_index = 0;
	    for i in range(0,len(sorted_d)):
	        if sorted_d[i][1] < threshold_count:
	            cut_index = i;
	            break;
	    return [x for x in sorted_d[cut_index:]];
	
	def number_of_elements(self):
		
		return len(self.d);
	

class myset:
	
	def __init__(self):
		
		self.d = {};

	def insert(self, item):
		if item not in self.d:	self.d[item] = 1;

	def exists(self, item):
		return item in self.d;

	def keys(self):
		return self.d.keys();
