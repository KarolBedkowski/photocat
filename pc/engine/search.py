#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
pc.engine.search
 -- engine do wyszukiwnania danych w katalogu

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004, 2005, 2006 

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

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= ['DlgProperties']


import logging
_LOG = logging.getLogger(__name__)

import time
import re

import wx
_ = wx.GetTranslation

from kpylibs.appconfig		import AppConfig



def get_catalogs_to_search(catalogs, options, selected_item):
	""" get_catalogs_to_search(catalogs, options, selected_item) -> [] -- zwraca liste obiektów do przeszukania
		Na podstawie opcji określa co przeszukiwać.
	"""
	catalogs_to_search = catalogs
	if options is not None:
		search_in_catalog = options.get('search_in_catalog', _("<all>"))
		if search_in_catalog == _("<all>"):
			pass
		elif search_in_catalog == _("<current catalog>"):
			catalogs_to_search = [ selected_item.catalog ]
		elif search_in_catalog == _("<current disk>"):
			catalogs_to_search = [ selected_item.disk ]
		elif search_in_catalog == _("<current dir>"):
			catalogs_to_search = [ selected_item ]
		else:
			search_in_catalog = search_in_catalog.split(": ", 1)[1]
			catalogs_to_search = [cat for cat in catalogs if cat.name == search_in_catalog ]
			
	subdirs_count = sum(( cat.subdirs_count for cat in catalogs_to_search ))
	
	return catalogs_to_search, subdirs_count
	

	
def find(what, options, catalogs, insert_func, progress_funct):
	""" find(what, options, catalogs, insert_func, progress_funct) -> string  -- wyszukanie informacji
	"""
	match_case = options is not None and options.get('opt_match_case', False)
	regex = options is not None and options.get('opt_regex', False)
		
	if not match_case:
		what = what.lower()

	_LOG.debug('find: "%s"' % what)

	if regex:
		textre = re.compile(what, (0 if match_case else re.I))
		cmpfunc = lambda x: textre.search(x)
	else:
		if match_case:
			cmpfunc = lambda x: (x.find(what) > -1)
		else:
			cmpfunc = lambda x: (x.lower().find(what) > -1)
		
	[ catalog.check_on_find(cmpfunc, insert_func, options, progress_funct) for catalog in catalogs ]

	return what



def update_last_search(text):
	''' update_last_search(text) -> [] -- aktualzacja listy poptrzednich wyszukiwań
	'''
	last = AppConfig().get_items('last_search')
	if last is None:
		last = []
	else:
		last = [l[1] for l in last]
		if len(last) > 19:
			last = last[:19]
	last.insert(0, text)
	AppConfig().set_items('last_search', 'text', last)
	return last


# vim: encoding=utf8: ff=unix:
