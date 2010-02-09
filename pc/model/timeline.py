# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (pc)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2007'
__revision__ = '$Id$'
__all__ = ["Timeline"]


import time
import operator

from pc.lib.hlpweakref			import create_weakref_proxy


class Timeline(object):
	''' Obiekt przechowywujący linię czasu - zdjęcia pogrupowane wg daty '''

	__slots__ = ('date', 'catalog', 'tree_node', 'parent', 'level',
			'dirs', '_files', '__weakref__')

	def __init__(self, date=None, catalog=None, parent=None, level=0):
		''' Timeline(data, [catalog], [parent], [level]) -- konstruktor

			@param date		-- data (str)
			@param catalog	-- katalog do którego jest przypisany timeline
			@param parent	-- nadrzędny obiekt Timeline
			@param level	-- poziom zagnieżdzenia timeline (0=root)
		'''
		self.date = date
		self.catalog = create_weakref_proxy(catalog)
		self.tree_node = None

		self.parent = create_weakref_proxy(parent)
		self.level = level

		self.reset()

	def __del__(self):
		del self.parent
		del self.tree_node
		del self.catalog

	def reset(self):
		''' timeline.reset() -- wyczyszczenie obiektu '''
		self.dirs = {}
		self._files = []

	############################################################################

	@property
	def files_count(self):
		''' timeline.files_count -> int -- liczba plików w obiekcie '''
		return len(self._files)

	@property
	def dirs_count(self):
		''' timeline.dirs_count -> int -- liczba pod-obiektów Timeline '''
		return len(self.dirs)

	@property
	def count(self):
		''' timeline.count -> int -- liczba podobiektów '''
		return len(self.dirs) + len(self._files)

	@property
	def _date(self):
		if self.level < 2:
			return '%02d' % self.date
		return '%s-%02d' % (self.parent._date, self.date)

	@property
	def caption(self):
		''' timeline.caption -> str -- etykieta dla drzewa '''
		return '%s (%d)' % (self._date, len(self._files))

	@property
	def subdirs(self):
		''' timeline.subdirs -> [] -- lista pod-obiektów Timeline sortowana
			wg daty '''
		return sorted(self.dirs.values(), key=operator.attrgetter('date'))

	@property
	def files(self):
		""" timeline.files -> [] -- lista ob FileImage

			Lista  jest filtrowana - tylko poprawne obiekty są zwracane
		"""
		files = [fil for fil in self._files if fil.is_valid]
		self._files = files
		return files

	############################################################################

	def __add_item(self, item):
		''' timeline.__add_item(item) -- dodanie obiektu '''
		date = item.shot_date
		if not date:
			return

		try:
			date = time.localtime(date)

		except:
			return

		if self.level > 0:
			self._files.append(create_weakref_proxy(item))

			if self.level == 3:
				return

		date_part = date[self.level]

		if date_part in self.dirs:
			subdir = self.dirs[date_part]

		else:
			self.dirs[date_part] = subdir = Timeline(date_part, self.catalog,
					self, self.level + 1)

		subdir.__add_item(item)

	############################################################################

	def load(self):
		""" timeline.load() -- załadowanie obiektów do timeline """
		self.reset()

		if self.level != 0:
			return

		def add_dir(directory):
			for item in directory.files:
				if item.is_valid:
					self.__add_item(item)

			for subdir in directory.subdirs:
				if subdir.is_valid:
					add_dir(subdir)

		for item in self.catalog.disks:
			add_dir(item)

		# sortowanie plikow wg daty wykonania zdjecia rekurencyjnie
		def sort_subdir(subdir):
			subdir._files.sort(key=operator.attrgetter('shot_date'))
			for subsubdir in subdir.dirs.itervalues():
				sort_subdir(subsubdir)

		for subdir in self.dirs.itervalues():
			sort_subdir(subdir)



# vim: encoding=utf8: ff=unix:
