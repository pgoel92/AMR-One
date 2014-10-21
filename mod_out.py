#!/usr/bin/python

import re
#Merges alignment spans with the output AMR corpus 

f=open('out');
corp=f.readlines();
f.close();

#Remove HTML tags
corp=corp[4:-3];

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

#Split the AMR corpus at newlines
corp = magicsplit(corp,'\n',0);
del corp[126]
#for arr in corp: print arr

#Split the alignemnt spans to correspond with the AMRs in the corpus
f=open('out-spans');
spans=f.readlines();
f.close();

spans = spans[3:];
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
	newitem = previous + current
	newspans.append(newitem);
	previous = next
	current = []
	next = []	

#print len(corp) == len(newspans)

#Separate spans with unaligned concepts
unaligned = 0
perfect = []
imperfect = []
unaligned_concepts = []
cooccuring_words = []
for i in range(0,len(newspans)):
	flag = 0
	for j in range(0,len(newspans[i])):
		if re.match('WARNING: Unaligned.*',newspans[i][j]):
			flag = 1
			unaligned_concepts.append(newspans[i][j][27:-1]);
			#print newspans[i][j]
			for k in range(0,len(corp[i])):
				if re.match('.*::snt.*',corp[i][k]):
					cooccuring_words.append(corp[i][k][8:]);
					#print corp[i][k][8:]

	if flag == 1: 
		unaligned = unaligned + 1;
		imperfect.append(i);
	else: perfect.append(i);

#Create a dictionary of unaligned concepts
dict = {} 
for elt in unaligned_concepts:
	if elt not in dict:
		dict[elt] = 1
	else: dict[elt] = dict[elt] + 1

import operator
sorted_dict = sorted(dict.iteritems(), key=operator.itemgetter(1),reverse=True);
for item in sorted_dict:
	print item

#for i in range(0,len(unaligned_concepts)):
#	print cooccuring_words[i]
#	print unaligned_concepts[i]
#	print
f = open('corp-span-perfect','w');
for i in perfect:
	for line in corp[i]:
		f.write(line);
	f.write('\n');
	for line in newspans[i]:
		f.write(line);
	f.write('\n');
f.close();
f = open('corp-span-imperfect','w');
for i in imperfect:
	for line in corp[i]:
		f.write(line);
	f.write('\n');
	for line in newspans[i]:
		f.write(line);
	f.write('\n');
f.close();
