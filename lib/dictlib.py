#!/usr/bin/python

import operator

def count_dict_insert(d,k):
    if k in d:
        d[k] = d[k] + 1;
    else: d[k] = 1;
    return d;

def threshold_dict(d,freq):
    swdict_concept = sorted(d.iteritems(), key=operator.itemgetter(1),reverse=True);
    cut_index = 0 
    for i in range(0,len(swdict_concept)):
        if swdict_concept[i][1] < freq:
            cut_index = i   
            break
    return swdict_concept
