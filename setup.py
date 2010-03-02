#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import os.path
import time
import sys

try:
	from setuptools import setup
except:
	from distutils.core import setup

if sys.platform == 'win32':
	try:
		import py2exe
	except:
		pass

from pc import version

build = time.asctime()


def is_package(filename):
	return (os.path.isdir(filename) \
			and os.path.isfile(os.path.join(filename, '__init__.py')))


def packages_for(filename, basePackage=""):
	"""Find all packages in filename"""
	packages = {}
	for item in os.listdir(filename):
		dir = os.path.join(filename, item)
		if is_package(dir):
			if basePackage:
				moduleName = basePackage + '.' + item
			else:
				moduleName = item
			packages[moduleName] = dir
			packages.update(packages_for(dir, moduleName))
	return packages


def find_files(directory, base):
	for name, subdirs, files in os.walk(directory):
		if files:
			yield (os.path.join(base, name), \
					[os.path.join(name, fname) for fname in files])


packages = packages_for(".")

def get_data_files():
	if sys.platform == 'win32':
		doc_dir = locales_dir = data_dir = '.'
	else:
		doc_dir = '/usr/share/doc/pc'
		locales_dir = '/usr/share/locale'
		data_dir = '/usr/share/doc/data'

	yield (doc_dir, ['README', "TODO", "LICENCE.txt", "LICENCE_EXIFpy.txt",
			"LICENCE_python.txt", "LICENCE_wxPython.txt", 'CHANGELOG',
			'LICENCE_ICONS.txt'])

	for x in find_files('data', data_dir):
		yield x
	
	for x in find_files('locale', locales_dir):
		yield x


pctarget = {
	'script': "pc_console.py",
	'name': "pc_console",
	'version': version.VERSION,
	'description': "%s - %s (%s, build: %s)" \
			% (version.NAME, version.DESCRIPTION, version.RELEASE, build),
	'company_name': "Karol Będkowski",
	'copyright': version.COPYRIGHT,
	'icon_resources': [(0, "data/icon.ico")],
	'other_resources': [("VERSIONTAG", 1, build)] }


pctarget_win = pctarget.copy()
pctarget_win.update({'script': "pc.pyw",'name': "pc"})


setup(
	name='pc',
	version=version.VERSION,
	author=pctarget['company_name'],
	author_email='karol.bedkowski@gmail.com',
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
	data_files=list(get_data_files()),
	include_package_data=True,
	scripts=['pc.pyw'],
	install_requires=['wxPython>=2.6.0', 'reportlab>=2', 'Image>=1.1.0'],
	options={"py2exe": {
		"compressed": 1,
		"optimize": 2,
		"ascii": 0,
		"bundle_files": 2,
		"packages": "PngImagePlugin, JpegImagePlugin, _rl_accel", }},
	zipfile=r"modules.dat",
	windows = [pctarget_win],
	console=[pctarget],
)


# vim: encoding=utf8:
