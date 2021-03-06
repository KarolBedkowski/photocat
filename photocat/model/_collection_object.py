# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


import os
import time
import types
import logging

from photocat.engine.efile import get_file_date_size
from photocat.storage.storage_object import StorageObject
from photocat.lib.hlpweakref import create_weakref_proxy

_LOG = logging.getLogger(__name__)


class CollectionObject(StorageObject):
	''' Klasa bazowa dla wszystkich plików i katalogów  w katalogu '''

	__slots__ = ('size', 'date', 'tags', 'desc', 'name', '_parent', '_disk',
			'collection', '_cached_path')

	def __init__(self, oid, name, parent, disk, *args, **kwargs):
		self.size = kwargs.get('size')
		self.date = kwargs.get('date')
		self.tags = kwargs.get('tags')
		self.desc = kwargs.get('desc')
		if self.desc is not None and type(self.desc) != types.UnicodeType:
			self.desc = unicode(self.desc)

		StorageObject.__init__(self, oid, *args, **kwargs)

		self.name = name
		self._parent = create_weakref_proxy(parent)
		self._disk = create_weakref_proxy(disk)
		self.collection = create_weakref_proxy(kwargs.get('collection') \
				or disk.collection)

		self._cached_path = None

	@property
	def parent(self):
		''' katalog nadrzędny '''
		return self._parent

	@property
	def disk(self):
		''' dysk do którego należy element '''
		return self._disk

	@property
	def caption(self):
		""" etykieta obiektu """
		return str(self.name or id(self))

	def _get_info(self):
		result = []
		result.append((0, _('Name'), str(self.name)))
		if self.tags is not None and len(self.tags) > 0:
			result.append((1, _('Tags'), ', '.join(self.tags)))

		result.append((99, '', ''))
		result.append((100, _('Collection'), self.disk.collection.name))
		if self.disk is not None:
			result.append((101, _('Disk'), self.disk.name))

		result.append((199, '', ''))
		if self.date is not None:
			result.append((200, _('File date'),
					time.strftime('%c', time.localtime(self.date))))

		return result

	info = property(_get_info)

	@property
	def parent_id(self):
		''' id obiektu nadrzędnego '''
		return None if self.parent is None else self.parent.id

	@property
	def disk_id(self):
		''' id dysku do którego należy obiekt '''
		return None if self.disk is None else self.disk.id

	@property
	def path(self):
		''' ścieżka do pliku '''
		if self._cached_path is None:
			self._cached_path = (self.name if self.parent is None
					else os.path.join(self.parent.path, self.name))

		return self._cached_path

	@property
	def date_to_check(self):
		''' data do sprawdzenia przy wyszukiwaniu '''
		return self.date

	##########################################################################

	def delete(self):
		''' metoda uruchamiana przy usuwaniu obiektu '''
		StorageObject.delete(self)
		if self.tags is not None and len(self.tags) > 0:
			_LOG.debug('delete tags from %s', self.name)
			self.collection.tags_provider.remove_item(self)

	def load(self, path, _options, on_update):
		""" załadowanie danych o obiekcie """
		self.size, self.date = get_file_date_size(path)
		return on_update(path)

	def update(self, path, _options, on_update):
		''' aktualizacja eleentu
			return: True=obiekt się zmienił
		'''
		old_size = self.size
		old_date = self.date
		self.size, self.date = get_file_date_size(path)
		return (old_size != self.size or old_date != self.date), on_update(path)

	def set_tags(self, tags):
		""" ustawienie tagów dla obiektu """
		# zapamiętanie zmienionych tagów
		if self.tags is None:
			updated_tags = tags

		elif tags is None:
			updated_tags = self.tags

		else:
			updated_tags = [tag for tag in tags if tag not in self.tags] \
					+ [tag for tag in self.tags if tag not in tags]

		self.tags = tuple(tags) if len(tags) > 0 else None
		self.collection.tags_provider.update_item(self)
		return updated_tags

	def check_on_find(self, cmpfunc, add_callback, options,
			_progress_callback=None):
		''' obj.check_on_find(text, [options]) -- sprawdzenie kryteriów
		wyszukiwania '''

		if options.get('search_in_names', True) and self.name \
				and cmpfunc(self.name) and self._check_on_find_date(options):
			add_callback(self)
			return

		if options.get('search_in_descr', True) and self.desc \
				and cmpfunc(self.desc) and self._check_on_find_date(options):
			add_callback(self)
			return

		if options.get('search_in_tags', True) and self.tags \
				and self._check_on_find_date(options):
			for tag in self.tags:
				if cmpfunc(tag):
					add_callback(self)
					return

	##########################################################################

	def _check_on_find_date(self, options):
		''' sprawdznie czy obiekt zawiera sie w danym zakresie  dat. '''
		date = self.date_to_check
		if date is None:
			return True

		if not options.get('search_date', False):
			return True

		return (date >= options.get('search_date_start') \
				and date <= options.get('search_date_end'))

	##########################################################################

	@classmethod
	def _attrlist(cls):
		attribs = StorageObject._attrlist()
		attribs.extend((
				('name', str), ('size', int), ('date', int), ('tags', tuple),
				('desc', str), ('parent_id', int), ('disk_id', int)))
		return attribs





# vim: encoding=utf8: ff=unix:
