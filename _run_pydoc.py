#!/usr/bin/python
import os
import sys
import pydoc

import sys
reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except:
	sys.setdefaultencoding("utf-8")


class KPyDocRunner:

	def __init__(self, dir):
		self.__main_dir = dir

		self.__root = None
		self.__module_path = None

		self.__files = []

	def run(self):
		self.__find_root()
		self.__find_files()

		os.chdir('doc.dev/pydoc')

		sys.path.append(self.__root)

		results = []
		
		for filename in self.__files:
			pydoc.writedoc(filename)


	def __find_root(self):
		self.__root = ''
		self.__module_path = ''


	def __add_file_to_list(self, args, path, files):
		tests = [ name[:-3] for name in files if name.endswith('.py') ]
		tests += [ name for name in files if os.path.isdir(os.path.join(path, name)) and os.path.exists(os.path.join(path, name, '__init__.py')) ]
		if len(tests) > 0:
			while path.startswith('.'): 
				path = path[1:]
			module_path = '.'.join(path.split(os.path.sep))
			if module_path:
				[ self.__files.append(module_path + '.' + name) for name in tests ]
			else:
				[ self.__files.append(name) for name in tests ]


	def __find_files(self):
		os.path.walk(self.__main_dir, self.__add_file_to_list, None)


if __name__ == '__main__':
	sys.path.append('../..')
	KPyDocRunner('sag3').run()

