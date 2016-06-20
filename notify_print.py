#!/usr/bin/python
import sys
import json


for arg in sys.argv:
    if arg.startsith('!'):
        try:
            obj = json.loads(arg[1:])
            print obj
        except ValueError:
            print 'error json'
    else:
        print arg

print "\n\n\n"