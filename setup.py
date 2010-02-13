#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import time
import sys

try:
	from setuptools import setup
except:
	from distutils.core import setup

from distutils.command.install_data import install_data

if sys.platform == 'win32':
	try:
		import py2exe
	except:
		pass

import pc

version = pc.__version__
release = pc.__release__
build = time.asctime()
data_files_extenstions = ('.mo', )# '.po')


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
		if (os.path.isfile(path) \
				and os.path.splitext(name)[1] in data_files_extenstions):
			result.append(path)
		elif os.path.isdir(path) and name.lower() != 'cvs' \
				and not name.startswith('.'):
			all_results.extend(np_files_for(path))

	if result:
		all_results.append((dirname, result))

	return all_results


def is_package(filename):
	return (os.path.isdir(filename) \
			and os.path.isfile(os.path.join(filename, '__init__.py')))


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
data_files = [(a[3:], b) for a, b in np_files_for('pc')]
data_files.append(('', ['README', "TODO", "LICENCE.txt", "LICENCE_EXIFpy.txt",
		"LICENCE_python.txt", "LICENCE_wxPython.txt", 'CHANGELOG']))


pctarget = dict(
	script="pc.py",
	name="pc",
	version=version,
	description="pc - PhotoCatalog %s (%s) (build: %s)" \
			% (version, release, build),
	company_name="Karol Będkowski",
	copyright="Copyright (C) Karol Będkowski 2007, 2008",
	icon_resources=[(0, "pc/icons/icon.ico")],
	other_resources=[("VERSIONTAG", 1, build)], )


setup(
	name='pc',
	version=version,
	author=pctarget['company_name'],
	author_email='-',
	description=pctarget['description'],
	long_description='-',
	license='GPL v2',
	url='-',
	download_url='-',
	classifiers=[
		'Development Status :: 4 - Beta',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Multimedia :: Graphics',
	],
	packages=packages.keys(),
	package_dir=packages,
	#package_data={'pc.templates': ['*.kid', '*.js', '*.css']},
	data_files=data_files,
	#	cmdclass = {'install_data': smart_install_data},
	include_package_data=True,
	scripts=['pc.py'],
	install_requires=['wxPython>=2.6.0'],
	options={"py2exe": {
		"compressed": 1,
		"optimize": 2,
		"ascii": 0,
		"bundle_files": 2,
		"packages": "PngImagePlugin, JpegImagePlugin, _rl_accel", }},
	zipfile=r"modules.dat",
	#windows = [pctarget],
	console=[pctarget],
)


# vim: encoding=utf8:
