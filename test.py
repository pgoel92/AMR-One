#!/usr/bin/python

from __future__ import print_function
import sys

def OffsetNodeAddress(addr, offset):
           
		if addr == '': return ''; 
		if offset == 0: return addr;
		addr = addr.split('.')
		new_addr = []; 
		for num in addr:
			if int(num) < 0:
				print("Invalid address: Negative node addresses not supported", file=sys.stderr);
				sys.exit(0);
			new_addr.append(str(int(num) + offset));
            
		return '.'.join(new_addr);

print(OffsetNodeAddress('-1',1));
