#!/usr/bin/python

import sys
import re

txt=sys.argv[1]


re1='.*?'	# Non-greedy match on filler
re2='(asp\\.wrap)'	# Fully Qualified Domain Name 1
re3='.*?'	# Non-greedy match on filler
re4='(".*?")'	# Double Quote String 1

rg = re.compile(re1+re2+re3+re4,re.IGNORECASE|re.DOTALL)
m = rg.search(txt)
if m:
    fqdn1=m.group(1)
    string1=m.group(2)
    print string1.replace('"','')
