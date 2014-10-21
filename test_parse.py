#!/usr/bin/python

from parser_old import parse_amr
from parser_old import print_amr

a = '(r / report-01 :ARG0 (p4 / person :ARG0-of (r2 / research-01)) :ARG1 (c / cause-01 :ARG0 (a2 / asbestos :mod (f / form) :ARG1-of (u / use-01 :ARG2 (m / make-01 :ARG1 (p / product :ARG0-of (f2 / filter-02) :mod (c2 / cigarette :name (n / name :op1 "Kent")))) :time (o / once))) :ARG1 (h2 / high :domain (p3 / percentage :ARG3-of (i / include-91 :ARG1 (p7 / person :ARG1-of (d / die-01 :ARG1-of (c4 / cause-01 :ARG0 (c3 / cancer)))) :ARG2 (p6 / person :ARG0-of (w2 / work-01) :ARG1-of (e / expose-01 :ARG2 a2 :time (b / before :op1 (n2 / now) :quant (m2 / more-than :op1 (t / temporal-quantity :quant 30 :unit (y / year)))))))))))';

amr= parse_amr(a)
print_amr(amr);

