#!/usr/bin/python
# -*- coding: utf8 -*-

import psyco
psyco.full()

import sys
import os

import kid.compiler


print '''

Compile templates...

'''

os.chdir('sag3/templates')

for file in ( fname for fname in os.listdir('./') if fname.endswith('.kid') ):
	print 'compile %s...' % file, 
	if kid.compiler.compile_file(file, force=True, source=True):
		print 'ok'
	else:
		print '-'




for file in ( fname for fname in os.listdir('./') if fname.endswith('.js') or fname.endswith('.css')):
	print 'compile %s...' % file, 
	try:
		fo = open(file.replace('.', '_') + ".py", 'wt')
		
		fo.write('#!/usr/bin/python2.4\n# -*- coding: utf8 -*-\n\n_TMPL = """')
		
		fi = open(file, 'rt')
		while 1:
			line = fi.readline()
			if line == '':
				break
			else:
				fo.write(line)
		fi.close()

		fo.write('''"""


def save(path, filename='%s'):
	import os.path
	filename = os.path.join(path, filename)
	file = open(filename, 'wt')
	file.write(_TMPL)
	file.close()
''' % file)

		fo.close()
	except Exception, err:
		print err
	else:
		print 'ok'


# vim: encoding=utf8: 
