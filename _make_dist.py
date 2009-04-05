#!/usr/bin/python -OO
# -*- coding: utf8 -*-

import psyco
psyco.full()

import sys
import time
import os

from distutils.core import setup
import py2exe


import pc

version	= pc.__version__
release = pc.__release__
build	= time.asctime()

manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

RT_MANIFEST = 24


pc = dict(
	script = "pc.py",
	name = "pc",
	version = version,
	description = "pc - PhotoCatalog %s (%s) (build: %s)" % (version, release, build),
	company_name = "Karol Będkowski",
	copyright = "Copyright (C) Karol Będkowski 2007, 2008",
	icon_resources = [(0, "pc/icons/icon.ico")],
	other_resources = [("VERSIONTAG", 1, build), (RT_MANIFEST, 1, manifest_template % dict(prog="pc"))],
)


data_files_extenstions = ('.mo', '.po', '.css', '.js', '.kid')

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


data_files = [ (a[3:], b) for a, b in np_files_for('pc') ]
data_files.append(('',
	['README', "TODO", "LICENCE.txt", "LICENCE_EXIFpy.txt", "LICENCE_python.txt", "LICENCE_wxPython.txt",
		'CHANGELOG']
))



# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
	sys.argv.append("py2exe")
	sys.argv.append("-q")

setup(
	# The first three parameters are not required, if at least a
	# 'version' is given, then a versioninfo resource is built from
	# them and added to the executables.
	options = {"py2exe": {
						"compressed":	1,
						"optimize":		2,
						"ascii":		0,
						"bundle_files":	1,
						"packages":		"PngImagePlugin, JpegImagePlugin, _rl_accel",
				}},


	# targets to build
	zipfile = r"modules.dat",
	windows = [pc],
	#console = [pc],
	data_files = data_files
#	[
#			("locale\\pl_PL\\LC_MESSAGES", ["pc\\locale\\pl_PL\\LC_MESSAGES\\pc.mo"]),
#			("locale\\pl_PL\\LC_MESSAGES", ["pc\\locale\\pl_PL\\LC_MESSAGES\\wxstd.mo"]),
#			('', ['README', 'TODO', 'LICENCE.txt']),
#			("templates\\default", ["pc\\locale\\pl_PL\\LC_MESSAGES\\wxstd.mo"]),
#	],
)


# vim: encoding=utf8: ff=unix:
