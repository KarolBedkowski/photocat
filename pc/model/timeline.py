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

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2007'
__revision__	= '$Id$'

__all__ = ["Timeline"]



import time
import operator



class Timeline(object):
	''' Obiekt przechowywujący linię czasu - zdjęcia pogrupowane wg daty '''

	def __init__(self, date=None, catalog=None, parent=None, level=0):
		''' Timeline(data, [catalog], [parent], [level]) -- konstruktor

			@param date		-- data (str)
			@param catalog	-- katalog do którego jest przypisany timeline
			@param parent	-- nadrzędny obiekt Timeline
			@param level	-- poziom zagnieżdzenia timeline (0=root)
		'''
		self.date		= date
		self.catalog	= catalog
		self.tree_node	= None

		self.parent		= parent
		self.level		= level

		self.reset()


	def reset(self):
		''' timeline.reset() -- wyczyszczenie obiektu '''
		self.dirs		= {}
		self._files		= []


	###################################################################################


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
		''' timeline.subdirs -> [] -- lista pod-obiektów Timeline sortowana wg daty '''
		return sorted(self.dirs.values(), key=operator.attrgetter('date'))


	@property
	def files(self):
		""" timeline.files -> [] -- lista ob FileImage

			Lista  jest filtrowana - tylko poprawne obiekty są zwracane
		"""
		files = filter(lambda x: x.is_valid, self._files)
		self._files = files
		return files


	###################################################################################


	def __add_item(self, item):
		''' timeline.__add_item(item) -- dodanie obiektu '''
		date = item.shot_date
		if date is None or date == 0:
			return

		try:
			date = time.localtime(date)

		except:
			return

		if self.level > 0:
			self._files.append(item)

		if self.level == 3:
			return

		date_part = date[self.level]

		subdir = self.dirs.get(date_part)
		if subdir is None:
			subdir = Timeline(date_part, self.catalog, self, self.level+1)
			self.dirs[date_part] = subdir

		subdir.__add_item(item)


	###################################################################################


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
