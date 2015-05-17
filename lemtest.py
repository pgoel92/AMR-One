#!/usr/bin/python

from lib.lemmatizer import mylemmatizer

f = open('zz');
test = f.readlines();
f.close();

ls = [x[:-1] for x in test];
ls = mylemmatizer(ls);

print ls;
