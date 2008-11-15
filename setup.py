#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import sys
import time

try:
	from setuptools import setup
except:
	from distutils.core import setup

from distutils.command.install_data import install_data

import pc

version	= pc.__version__
build	= time.asctime()

data_files_extenstions = ('.mo', '.po', '.css', '.js', '.kid')


class smart_install_data(install_data):
	def run(self):
		#need to change self.install_dir to the library dir
		install_cmd = self.get_finalized_command('install')
		self.install_dir = getattr(install_cmd, 'install_lib')
		return install_data.run(self)


def np_files_for(dirname):
	"""Return all non-python-file filenames in dir"""
	result = []
	all_results = []
	for name in os.listdir(dirname):
		path = os.path.join(dirname, name)
		if (os.path.isfile(path) and os.path.splitext(name)[1] in data_files_extenstions):
			result.append(path)
		elif os.path.isdir(path) and name.lower() !='cvs' and not name.startswith('.'):
			all_results.extend(np_files_for(path))

	if result:
		all_results.append((dirname, result))

	return all_results


def is_package(filename):
	return (os.path.isdir(filename) and os.path.isfile(os.path.join(filename,'__init__.py')))


def packages_for(filename, basePackage=""):
	"""Find all packages in filename"""
	set = {}
	for item in os.listdir(filename):
		dir = os.path.join(filename, item)
		if is_package(dir):
			if basePackage:
				moduleName = basePackage + '.' + item
			else:
				moduleName = item
			set[moduleName] = dir
			set.update(packages_for(dir, moduleName))
	return set


packages = packages_for(".")
data_files = (np_files_for('pc'))
data_files.append(('', ['README', "TODO", "LICENCE.txt"]))



setup(
	name='pc',
	version=version,
	author="Karol Będkowski",
	author_email='-',
	description= "pc - Photo Catalog %s buld %s" % (version, build),
	long_description='-',
	license='GPL v2',
	url='-',
	download_url='-',
	classifiers = [
		'Development Status :: 4 - Beta',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Multimedia :: Graphics',
	],
	packages = packages.keys(),
	package_dir = packages,
	#package_data={'pc.templates': ['*.kid', '*.js', '*.css']},
	data_files = data_files,
	cmdclass = {'install_data': smart_install_data},
	include_package_data=True,
	scripts=['pc.py'],
	install_requires=['kid>=0.9.3', 'wxPython>=2.6.0', 'elementtree>=1.2.0']
)


# vim: encoding=utf8: 
