#!/usr/bin/python

"""
This is a way to save the startup time when running img2py on lots of
files...
"""

import sys, os

from wx.tools import img2py

os.chdir('pc/icons')
os.unlink('icons.py')

command_lines = [ '-u -n _%s_ %s icons.py' % (name[:-4], name) 
		for name in os.listdir('.')
		if name.endswith('.png')
]

for lp, line in enumerate(command_lines):
	args = line.split()
	if lp > 0:
		args.insert(0, '-a')
	img2py.main(args)

