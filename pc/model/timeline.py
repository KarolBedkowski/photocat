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



from file_image	import FileImage



class Timeline(object):
	def __init__(self, name=None, catalog=None, parent=None):
		self.name		= name
		self.files		= []
		self.dirs		= []
		self.catalog	= catalog
		self.tree_node	= None
		
		self.parent		= parent
		self._childs	= {}


	@property
	def files_count(self):
		return len(self.files)


	@property
	def dirs_count(self):
		return len(self.dirs)
	
	
	@property
	def count(self):
		return len(self.dirs) + len(self.files)


	@property
	def caption(self):
		return '%s (%d/%d)' % (self.name, len(self.files), len(self.dirs))


	def remove_item(self, item):
		''' usuniecie elementu z drzea '''
		
		# usuniecie z potomkow
		child_to_del = []
		for key, child in self._childs.iteritems():
			child.remove_item(item)
			if child.count == 0:
				child_to_del.append(key)

		# usuniecie pustych potomkow
		map(self._childs.pop, child_to_del)

		# usuniecie z tego poziomu
		if isinstance(item, FileImage):
			if item in self.files:
				self.files.remove(item)
		elif item in self.dirs:
			self.dirs.remove(item)


	def add_item(self, item, date=None):
		''' dodanie elementu do drzewa '''
		if date is None:
			# najwyższy poziom
			if item.data is None or len(item.data) < 10:
				return
			date = item.date.split(' ')[0]	# data w formacie "yyyy-mm-dd" lub "yyyy-mm-dd ...."
		else:
			# poziom 2
			if isinstance(item, FileImage):
				self.files.append(item)
			else:
				self.dirs.append(item)
			
		if date.count('-') > 0:
			# jezeli nie-ostatni poziom - podzial na 1 czesc i reszte
			first_part_date, date = date.split('-', 2)
			
			#pobranie wg pierwszej czesci
			child = self._childs.get(first_part_date)
			if childs is None:
				# jezeli nie ma - stworzenie
				self._childs[date] = child = Timeline(date, self.catalog, self)
			# dodanie elementu niżej
			child.add_item(item, date)


	def update_item(self, item):
		''' aktualizacja elementu w drzewie '''
		self.remove_item(item)
		self.add_item(item)





# vim: encoding=utf8: ff=unix:

