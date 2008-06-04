#!/usr/bin/python
# -*- coding: utf8 -*-

import os

if __name__ == '__main__':
	for root, dirs, files in os.walk('.', topdown=False):
		for name in files:
			if name.endswith('.pyd') or name.endswith('.pyc') or name.endswith('~') or name.endswith('.pyo') \
					or name.endswith('.log'):
				filename = os.path.join(root, name) 
				print 'Delete ', filename
				os.remove(filename)
	
	if os.path.exists('build'):
		for root, dirs, files in os.walk('build', topdown=False):
			for name in files:
				filename = os.path.join(root, name)
				print 'Delete ', filename
				os.remove(filename)
			for name in dirs:
				filename = os.path.join(root, name)
				print 'Delete dir ', filename
				os.rmdir(filename)

		os.removedirs('build')

# vim: encoding=utf8:ff=unix:
