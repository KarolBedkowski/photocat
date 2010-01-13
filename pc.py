#!/usr/bin/python
# -*- coding: utf-8 -*-
"""

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004-2007

 This file is part of Photo Catalog

 PC is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 PC is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""
from __future__ import with_statement

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= []


import os
import sys
try:
	os.chdir(os.path.dirname(__file__))

except:
	pass

from pc	import run

if '--profile' in sys.argv:
	sys.argv.remove('--profile')
	import cProfile
	print 'Profiling....'
	cProfile.run('run()', 'profile.tmp')
	import pstats
	import time
	with open('profile_result_%d.txt' % int(time.time()), 'w') as out:
		s=pstats.Stats('profile.tmp', stream=out)
#		s.strip_dirs()
		s.sort_stats('cumulative').print_stats('pc', 50)

		out.write('\n\n----------------------------\n\n')

		s.sort_stats('time').print_stats('pc', 50)

elif '--memprofile' in sys.argv:
	sys.argv.remove('--memprofile')
	run()
	import gc
	while gc.collect() > 0:
		pass

	import objgraph
	objgraph.show_most_common_types(20)

	import ipdb
	ipdb.set_trace()

else:
	run()

# vim: encoding=utf8: ff=unix: 
