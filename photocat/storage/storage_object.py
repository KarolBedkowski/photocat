# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2007

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


from types	import DictType

from photocat.lib.singleton import Singleton


class _IdProvider(Singleton):

	def _init(self, *_args, **_kwds):
		self.last_id = 0

	def set(self, oid):
		if oid < 0:
			return self.get()

		if oid > self.last_id:
			self.last_id = oid

		return oid

	def get(self):
		self.last_id += 1
		return self.last_id


##########################################################################

_ID_PROVIDER = _IdProvider()

##########################################################################


class StorageObject(object):
	__slots__ = ('_invalid', '_id')
	FV3_CLASS_NAME = 0

	def __init__(self, oid, *args, **kwargs):
		self._invalid = False
		self._id = None if oid is None else _ID_PROVIDER.set(oid)

	def _get_id(self):
		if not self._id:
			self._id = _ID_PROVIDER.get()

		return self._id

	def _set_id(self, oid):
		self._id = _ID_PROVIDER.set(oid)

	id = property(_get_id, _set_id)

	@property
	def childs_to_store(self):
		return []

	@property
	def is_valid(self):
		return not self._invalid

	##########################################################################

	def delete(self):
		''' metoda uruchamiana przy usuwaniu obiektu '''
		self._invalid = True

	def set_attributes(self, data):
		for key, val in data.iteritems():
			if hasattr(self, key):
				setattr(self, key, val)

	def encode(self):
		result = {}
		for key in self.__preserveattr__().iterkeys():
			val = getattr(self, key)
			if val is not None:
				result[key] = val

		return '|'.join((self.__class__.__name__, str(self.id), repr(result)))

	def encode3(self):
		result = {}
		for key in self.__preserveattr__().iterkeys():
			val = getattr(self, key)
			if val is not None:
				result[key] = val

		return self.id, self.FV3_CLASS_NAME, result

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
			return getattr(cls, '_storageobject_attributes')

		attrlist = dict(cls._attrlist())
		setattr(cls, '_storageobject_attributes', attrlist)
		return attrlist

	@classmethod
	def decode(cls, data):
		#attributes = cls.__preserveattr__() # nie potrzebne?
		eval_data = eval(data)

		if type(eval_data) != DictType:
			raise Exception('unknow data: "%s" type=%s' % (eval_data,
					type(eval_data)))

		return eval_data



# vim: encoding=utf8: ff=unix:
