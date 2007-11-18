#!/usr/bin/python

"""
This is a way to save the startup time when running img2py on lots of
files...
"""

import sys, os

from wx.tools import img2py

os.chdir('pc/icons')
os.unlink('icons.py')

f = file('icons.py', 'w')
f.write(
"""
from wx import ImageFromStream, BitmapFromImage
#from wx import EmptyIcon
import cStringIO

""")
f.close()

command_lines = [ '-u -a -n _%s_ %s icons.py' % (name[:-4], name) 
		for name in os.listdir('.')
		if name.endswith('.png')
]

for line in command_lines:
	args = line.split()
	img2py.main(args)

