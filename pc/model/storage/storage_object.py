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
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'


from types	import DictType

from kpylibs.singleton	import Singleton



class _IdProvider(Singleton):
	def init(self):
		self.last_id = 0


	def set(self, id):
		if id < 0:
			return self.get()
		if id > self.last_id:
			self.last_id = id
		return id


	def get(self):
		self.last_id += 1
		return self.last_id



##########################################################################


_id_provider = _IdProvider()


##########################################################################



class StorageObject(object):
	def __init__(self, id, *args, **kwargs):
		self._id = None
		self._invalid = False

		if id is not None:
			self._id = _id_provider.set(id)


	def _get_id(self):
		if self._id is None:
			self._id = _id_provider.get()
		return self._id

	def _set_id(self, id):
		self._id = _id_provider.set(id)

	id = property(_get_id, _set_id)
	

	@property
	def childs_to_store(self):
		return []
	

	##########################################################################
	

	def delete(self):
		''' metoda uruchamiana przy usuwaniu obiektu '''
		self._invalid = True


	def set_attributes(self, data):
		[ setattr(self, key, val) for key, val in data.iteritems() if hasattr(self, key) ]


	def encode(self):
		result = {}
		for key in self.__preserveattr__().keys():
			val = getattr(self, key)
			if val is not None:
				result[key] = val

		return "%s|%d|%r" % (self.__class__.__name__, self.id, result)

	##########################################################################


	@classmethod
	def _attrlist(cls):
		''' lista nazw atrybutow klasy do zpisania.
			Metoda powinna być redefiniowana
		'''
		return []


	@classmethod
	def __preserveattr__(cls):
		'''zwraca listę nazw atrybutów klasy, które powinny być zapisane'''
		if hasattr(cls, '_storageobject_attributes'):
			return cls._storageobject_attributes

		attrlist = dict(cls._attrlist())
		setattr(cls, '_storageobject_attributes', attrlist)
		return attrlist


	@classmethod
	def decode(cls, data):
		#attributes = cls.__preserveattr__() # nie potrzebne?
		eval_data = eval(data)

		if type(eval_data) != DictType:
			raise Exception('unknow data: "%s" type=%s' % (eval_data, type(eval_data)))

		return eval_data



# vim: encoding=utf8: ff=unix:
