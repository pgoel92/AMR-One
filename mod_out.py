#!/usr/bin/python
#Merges alignment spans with the output AMR corpus 

from nltk.corpus import stopwords
import nltk
import operator
import re
import sys
import unicodedata

punc = ['"',';','\'',':','.',',','?','!','-','--','...']
concept_freq = 5
cooccuring_freq = 3

def unicode_to_ascii_list(ls):
	newls = [];
	for elt in ls:
		newls.append(unicodedata.normalize('NFKD',elt).encode('ascii','ignore'));
	return newls;

stpwords = unicode_to_ascii_list(stopwords.words('english'));

def tokenize(ls):
	newls = []
	for line in ls:
		temp = []
		for item in line.split():
			item = item.lower();
			if item not in punc and item not in stpwords:
				temp.append(item);
		newls.append(temp);
	return newls
				
def threshold_dict(d,freq):
	swdict_concept = sorted(d.iteritems(), key=operator.itemgetter(1),reverse=True);
	cut_index = 0
	for i in range(0,len(swdict_concept)):
		if swdict_concept[i][1] < freq:
			cut_index = i	
			break
	return swdict_concept[:i]
			

#Split a list of strings l at all strings that exactly match any of the splitters. Does not include the matched string in the split.
def _itersplit(l, splitters):
    current = []
    for item in l:
        if item in splitters:
            yield current
            current = []
        else:
            current.append(item)
    yield current

#Split a list of strings l at all strings that partially match any of the splitters. Includes the matched string in the split.
def _itersplitre(l, splitters):
    current = []
    for item in l:
        if re.match(splitters[0],item):
            yield current
            current = []
       	    current.append(item)
        else:
        	current.append(item)
    yield current

def magicsplit(l, *splitters):
    return [subl for subl in _itersplit(l, splitters) if subl]

def magicsplitre(l, *splitters):
    return [subl for subl in _itersplitre(l, splitters) if subl]

#Takes as input aligned corpus and spans as lists of line strings. Returns lists of chunks corresponding to each sentence in the corpus.
def preprocess(corp_list,span_list):
	
	#Remove HTML tags
	corp=corp_list[5:-3];
	
	#Split the aligned AMR corpus at newlines
	corp = magicsplit(corp,'\n',0);
	
	#anomalies: manually remove sentences in the corpus that do not get aligned
	del corp[95];
	del corp[272];
	del corp[339];
	del corp[681];
	del corp[697];

	#Split the alignemnt spans to correspond with the AMRs in the corpus
	spans = span_list[3:];
	spans = magicsplitre(spans,'Span 1:.*');
	
	current = []
	previous = []
	next = []
	
	#Rearrange spans to include the correct warnings
	newspans = []
	for item in spans:
		for line in item:
			if not re.match('Span.*',line):
				next.append(line);
			else: current.append(line);
		newitem = previous + current;
		newspans.append(newitem);
		previous = next;
		current = [];
		next = [];

	return (corp,newspans);

#Separate spans with unaligned concepts
def separate(corp,spans):

	perfect = [];
	imperfect = [];
	for i in range(0,len(spans)):
		flag = 0;
		for j in range(0,len(spans[i])):
			if re.match('WARNING: Unaligned.*',spans[i][j]):
				flag = 1;
		if flag == 1: 
			imperfect.append(i);
		else: perfect.append(i);

	return (perfect, imperfect);

#Returns two dictionaries : 
#	cdict : Maps unaligned concepts to their count in the corpus
#	wdict : Maps unaligned concepts to their cooccuring words which are also stored in a dictionary mapping them to their counts

def stats(corp,spans,imperfect):

	unaligned_concepts = []
	cooccuring_words = []
	
	for i in range(0,len(spans)):
		chunk = spans[i]
		flag = 0
		for j in range(0,len(chunk)):
			sline = chunk[j];
			if re.match('WARNING: Unaligned.*',sline):
				flag = 1;
				unaligned_concepts.append(sline[27:-1]);
				#print sline[27:-1];
				for k in range(0,len(corp[i])):
					cline = corp[i][k];
					if re.match('.*::snt.*',cline):
						cooccuring_words.append(cline[8:]);
						#print cline[8:];
	
	cooccuring_words = tokenize(cooccuring_words);
	
	#Create a dictionary of unaligned concepts with count
	cdict = {} 
	for elt in unaligned_concepts:
		if elt not in cdict:
			cdict[elt] = 1
		else: cdict[elt] = cdict[elt] + 1
	
	#Create a dictionary of unaligned concepts with cooccuring words
	wdict = {} 
	for i in range(0,len(unaligned_concepts)):
		conc = unaligned_concepts[i];
		if conc not in wdict:
			wdict[conc] = {}
		else:
			for coocc in cooccuring_words[i]:
				if coocc in wdict[conc]:
					wdict[conc][coocc] = wdict[conc][coocc] +  1
				else:
					wdict[conc][coocc] = 1
	
	return (cdict,wdict);	

#	sorted_cdict = sorted(cdict.iteritems(), key=operator.itemgetter(1),reverse=True);
#	for item in sorted_cdict:
#		if item[1] > concept_freq:
#			print item[0]
#			d = cut_sort_dict(wdict[item[0]],item[1]);
#			for elt in d:
#				print elt[1],elt[0]
#			print
	
def write_to_file(corp,span,perfect,imperfect):
	f = open('corp-span','w');
	for i in range(0,len(corp)):
		for line in corp[i]:
			f.write(line);
		f.write('\n');
		for line in span[i]:
			f.write(line);
		f.write('\n');
	f.close();
	f = open('corp-span-perfect','w');
	for i in perfect:
		for line in corp[i]:
			f.write(line);
		f.write('\n');
		for line in span[i]:
			f.write(line);
		f.write('\n');
	f.close();
	f = open('corp-span-imperfect','w');
	for i in imperfect:
		for line in corp[i]:
			f.write(line);
		f.write('\n');
		for line in span[i]:
			f.write(line);
		f.write('\n');
	f.close();

def main():
	

	#Read aligned corpus file
	f=open(sys.argv[1]);
	corp=f.readlines();
	f.close();
	
	#Read span file
	f=open(sys.argv[2]);
	spans=f.readlines();
	f.close();
	
	t = preprocess(corp,spans);
	corp = t[0];
	span = t[1];
	#print len(corp),len(span);

	tsep = separate(corp,span);
	perfect = tsep[0];
	imperfect = tsep[1];
	
	dic = stats(corp,span,imperfect);
	cdict = dic[0];
	wdict = dic[1];
	
	cdict_show = threshold_dict(cdict,concept_freq);
	
	wwdict = {}
	for tup in cdict_show:
		tmpdict = wdict[tup[0]]
		for key in tmpdict:
			keytup = (tup[0],key);
			if keytup not in wwdict:
				wwdict[keytup] = tmpdict[key]; 
			else:
				wwdict[keytup] = wwdict[keytup] + tmpdict[key];

	f = open('freq_unaligned','w');
	for tup in cdict_show:
		f.write(str(tup[1]) + " " + tup[0]);
		f.write('\n');
	f.close();

	f = open('cooccuring_words','w');
	for elt in cdict_show:
		f.write("## " + str(elt[1]) + " " + elt[0] + '\n\n'); 
		tmpdict = wdict[elt[0]];
		tmpdict_show = threshold_dict(tmpdict,cooccuring_freq);
		for item in tmpdict_show:
			f.write(str(item[1]) + " " + item[0] + '\n');
		f.write('\n');
	f.close();	

	f = open('cooccuring_words_two','w');		
	wwshow = threshold_dict(wwdict,0);
	for item in wwshow:
		f.write(str(item[1]) + " (" + item[0][0] +", " + item[0][1] +  ')\n');
	f.close();
	

main();
