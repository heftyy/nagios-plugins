#!/usr/bin/python

import os
import sys


def main(argv):
    print 'Number of arguments:', len(sys.argv), 'arguments.'
    print 'Argument List:', str(sys.argv)
    print '---------------------------------------------------------------'
    print '---------------------------------------------------------------'
    return 0

if __name__ == '__main__':
    pid = str(os.getpid())
    sys.exit(main(sys.argv))
