#!/usr/bin/python
# -*- coding: utf8 -*-

import os

to_delete = []

def __add_file(args, path, files):
	[ to_delete.append(os.path.join(path, name)) 
			for name in files 
			if name.endswith('.pyd') or name.endswith('.pyc') or name.endswith('~') or name.endswith('.pyo')
				or name.endswith('.log')
	]


if __name__ == '__main__':
	os.path.walk('.', __add_file, None)


	for filename in to_delete:
		print 'Delete ', filename
		os.unlink(filename)
		


# vim: encoding=utf8:ff=unix:
