#!/usr/bin/python
# -*- coding: utf8 -*-

import os
import os.path
import time
import sys

try:
	from setuptools import setup
	from setuptools import Command
except ImportError:
	from distutils.core import setup
	from distutils.cmd import Command


if sys.platform == 'win32':
	try:
		import py2exe
	except ImportError:
		pass

from photocat import version

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
		doc_dir = '/usr/share/doc/photocat'
		locales_dir = '/usr/share/locale'
		data_dir = '/usr/share/doc/data'

	yield (doc_dir, ['AUTHORS', 'README', "TODO", "COPYING",
			"LICENCE_python.txt", "LICENCE_wxPython.txt", 'ChangeLog',
			'LICENCE_ICONS.txt'])

	for x in find_files('data', data_dir):
		yield x

	for x in find_files('locale', locales_dir):
		yield x


def _delete_dir(path):
	if os.path.exists(path):
		for root, dirs, files in os.walk(path, topdown=False):
			for name in files:
				filename = os.path.join(root, name)
				print 'Delete ', filename
				os.remove(filename)
			for name in dirs:
				filename = os.path.join(root, name)
				print 'Delete dir ', filename
				os.rmdir(filename)
		os.removedirs(path)


class CleanupCmd(Command):
	"""docstring for cleanup"""

	description = "cleanup all files"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		for root, dirs, files in os.walk('.', topdown=False):
			for name in files:
				nameext = os.path.splitext(name)[-1]
				if (name.endswith('~') or name.startswith('profile_result_')
						or name.endswith('-stamp')
						or nameext in ('.pyd', '.pyc', '.pyo', '.log', '.tmp',
							'.swp', '.db', '.cfg', '.debhelper', '.substvars')):
					filename = os.path.join(root, name)
					print 'Delete ', filename
					os.remove(filename)
		_delete_dir('build')
		_delete_dir('debian/photocat')
		if os.path.exists('hotshot_edi_stats'):
			os.remove('hotshot_edi_stats')


class MakeMoCommand(Command):
	"""docstring for cleanup"""

	description = "create mo files"
	user_options = []

	def initialize_options(self):
		pass

	def finalize_options(self):
		pass

	def run(self):
		po_langs = (filename[:-3] for filename in os.listdir('po')
				if filename.endswith('.po'))
		for lang in po_langs:
			print 'creating mo for', lang
			path = os.path.join('locale', lang, 'LC_MESSAGES')
			if not os.path.exists(path):
				os.makedirs(path)
			os.execl('/usr/bin/msgfmt', '/usr/bin/msgfmt', 'po/%s.po' % lang,
					'-o', os.path.join(path, '%s.mo' % version.SHORTNAME))


cmdclass = {'cleanup': CleanupCmd,
		'make_mo' : MakeMoCommand,
}


pctarget = {
	'script': "photocat_dbg.py",
	'name': "photocat_dbg",
	'version': version.VERSION,
	'description': "%s - %s (%s, build: %s)" \
			% (version.NAME, version.DESCRIPTION, version.RELEASE, build),
	'company_name': "Karol Będkowski",
	'copyright': version.COPYRIGHT,
	'icon_resources': [(0, "data/art/icon.ico")],
	'other_resources': [("VERSIONTAG", 1, build)] }


pctarget_win = pctarget.copy()
pctarget_win.update({'script': "photocat.pyw",'name': "photocat"})


setup(
	name='photocat',
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
	scripts=['photocat.pyw'],
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
	cmdclass=cmdclass,
)


# vim: encoding=utf8:
