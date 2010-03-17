#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog

photocat is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.

photocat is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
from __future__ import with_statement

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski 2006-2010'
__revision__ = '$Id$'
__all__ = []


import sys
sys.argv.append('-d')

from photocat.main import run


def _profile():
	''' profile app '''
	import cProfile
	print 'Profiling....'
	cProfile.run('run()', 'profile.tmp')
	import pstats
	import time
	with open('profile_result_%d.txt' % int(time.time()), 'w') as out:
		stat = pstats.Stats('profile.tmp', stream=out)
		#s.strip_dirs()
		stat.sort_stats('cumulative').print_stats('photocat', 50)
		out.write('\n\n----------------------------\n\n')
		stat.sort_stats('time').print_stats('photocat', 50)


def _memprofile():
	''' mem profile app '''
	run()
	import gc
	gc.collect()
	while gc.collect() > 0:
		print 'collect'

	import objgraph
	objgraph.show_most_common_types(20)

	import pdb
	pdb.set_trace()


if '--profile' in sys.argv:
	sys.argv.remove('--profile')
	_profile()
elif '--memprofile' in sys.argv:
	sys.argv.remove('--memprofile')
	_memprofile()
elif '--version' in sys.argv:
	from photocat import version
	print version.INFO
else:
	run()

# vim: encoding=utf8: ff=unix:
