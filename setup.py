#!/opt/python/bin/python2.6

from distutils.core import setup

import nesoni

import sys, os
if not os.path.isfile(sys.executable):
    print
    print 'Python thinks this is its executable:', sys.executable
    print
    print 'I disagree.'
    print
    print 'If using sudo, try sudo -E'
    print
    sys.exit(1)

setup(name='nesoni',
      version=nesoni.VERSION,
      
      packages = [
          'nesoni', 
          'treemaker'
      ],
      
      package_data = {
          'treemaker' : ['*.pyx'],
          'nesoni' : ['*.pyx'],
      },
      
      scripts=['nesoni_scripts/nesoni'],
)