#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
photocat.engine.search
-- engine do wyszukiwnania danych w katalogu

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004, 2005, 2006

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


import logging
import re

from photocat.lib.appconfig import AppConfig


_LOG = logging.getLogger(__name__)


def get_collections_to_search(collections, options, selected_item):
	""" get_collections_to_search(collections, options, selected_item) -> []
		-- zwraca liste obiektów do przeszukania

		Na podstawie opcji określa co przeszukiwać.

		@param collections		- lista katalogow do przeszukania
		@param options		- opcje do wyszukania
		@param selected_item - aktualnie wybrany element

		Opcje:
			- search_in_collection - gdzie szukać """
	collections_to_search = collections
	if options is not None:
		search_in_collection = options.get('search_in_collection', _("<all>"))
		if search_in_collection == _("<all>"):
			pass

		elif search_in_collection == _("<current collection>"):
			collections_to_search = [selected_item.collection]
		elif search_in_collection == _("<current disk>"):
			collections_to_search = [selected_item.disk]
		elif search_in_collection == _("<current dir>"):
			collections_to_search = [selected_item]
		else:
			# wyszukiwanie w konkretnym katalogu
			search_in_collection = search_in_collection.split(": ", 1)[1]
			collections_to_search = [cat for cat in collections
					if cat.name == search_in_collection]

	subdirs_count = sum((cat.subdirs_count for cat in collections_to_search))
	return collections_to_search, subdirs_count


def find(what, options, collections, insert_func, progress_funct):
	""" find(what, options, collections, insert_func, progress_funct) -> string
	-- wyszukanie informacji

	@param what			- string do wyszukania
	@param options		- opcje wyszukania
	@param insert_func	- callback do wstawiania rezultatów
	@param progress_funct	- callback do pokazywania postępów / przerywania
	@return szukany string

	Opcje:
		- opt_match_case	- dopasowanie wielkości liter (def=False)
		- opt_regex			- wyszukiwanie po regex (def=False) """
	options = options or {}
	match_case = options.get('opt_match_case', False)
	regex = options.get('opt_regex', False)

	if not match_case:
		what = what.lower()

	_LOG.debug('find: "%s"', what)
	if regex:
		# wyszukiwanie po regex
		textre = re.compile(what, (0 if match_case else re.I))
		cmpfunc = textre.search
	else:
		if match_case:
			# z dopasowaniem case
			cmpfunc = lambda x: (x.find(what) > -1)
		else:
			# bez dopasowania case
			cmpfunc = lambda x: (x.lower().find(what) > -1)

	for collection in collections:
		collection.check_on_find(cmpfunc, insert_func, options, progress_funct)

	return what


def update_last_search(text):
	''' update_last_search(text) -> [string] -- aktualzacja listy poptrzednich
	wyszukiwań
	@return lista ostatnich wyszukiwań
	Na liście nie pojawią się duble.  '''
	last = get_last_search()
	if text in last:
		# jeżeli text jest już gdzieś na liście - usunięcie go
		last.remove(text)
	elif len(last) > 19:
		# obcięcie listy do 19 elementow
		last = last[:19]

	last.insert(0, text)
	AppConfig().set_items('last_search', 'text', last)

	return last


def get_last_search():
	''' get_last_search() -> [str] -- lista ostatnich wyszukian
	@return lista ostatnich wyszukiwań '''
	last = AppConfig().get_items('last_search') or []
	last = [l[1] for l in last]

	return last



# vim: encoding=utf8: ff=unix:
