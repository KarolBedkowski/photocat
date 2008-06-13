# -*- coding: utf-8 -*-
# pylint: disable-msg=W0212
"""
 
 
 kPyLibs
 Copyright (c) Karol Będkowski, 2007

 This file is part of kPyLibs

 kPyLibs is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 SAG is distributed in the hope that it will be useful, but WITHOUT ANY
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

__all__			= ['MyObject']


import types


class MyObject:
	''' Klasa bazowa dla obiektów '''

	def __init__(self):
		pass


	def __repr__(self):
		return '<%s(%d): %s>' % (self.__class__.__name__, id(self),
				', '.join((
					"%s='%s'" % (str(key), repr(val)) 
					for key, val in self._get_attributes() 
				))
		)


	def attributes_update_fast(self, values):
		''' obj.attributes_update_fast(values) -- szybkie uaktualnienie warotsi atrybutuow

			values - słownik wartości
		'''
		attributes = self._get_attributes_keys()
		[ setattr(self, key, val) for key, val in values.iteritems() if key in attributes ]



	def attributes_update(self, values=None, if_null=False, filter_keys=False, **kwarg):
		''' obj.update([values], [if_null], [**kwarg]) -> Int -- uaktualnenie atrybutów klasy 
		
			values - słownik wartosci do ustalenia
			if_null - jezeli True uaktuanieane sa tylko wartosci None
			
			Ret: ilosc zmian
		'''

		slots = None
		if filter_keys:
			if hasattr(self, '__slots__'):
				slots = self.__slots__
			elif hasattr(self, '__dict__'):
				slots = self.__dict__.keys()

		def updateself(values_dict):
			''' updateself(values) -- uaktualnienie wartosci '''
			changed = 0
			for key, val in values_dict.items():
				if slots is None or key in slots:
					if not (key.startswith('_') or type(val) in (types.MethodType, types.ClassType, types.FunctionType)):
						
						if hasattr(self.__class__, key):
							continue
												
						if len(str(val)) == 0:
							val = None

						curr_val = getattr(self, key)
						if len(str(curr_val)) == 0:
							curr_val = None

						if if_null:
							if curr_val is None and val != curr_val:
								setattr(self, key, val)
								changed += 1
						elif curr_val != val:
							setattr(self, key, val)
							changed += 1

			return changed

		updated = 0
		if values is not None:
			updated = updateself(values)

		if kwarg is not None:
			updated += updateself(kwarg)

		return updated


	@property
	def dict(self):
		''' obj.dict -> dict() -- pobranie atrybutow klasy '''
		return dict(self._get_attributes())


	@property
	def dict_not_none(self):
		''' obj.dict_not_none -> dict() -- pobranie atrybutow klasy których wartości != None'''
		attr = ( (key, val) for key, val in self._get_attributes() if val is not None )
		return dict(attr)


	def _get_attributes(self):
		atr =  (
				(key, val)
				for key, val in vars(self).iteritems()
				if not key.startswith('_') 
					and type(val) not in (types.MethodType, types.ClassType, types.FunctionType)
					and not hasattr(self.__class__, key)
		)
		return atr


	def _get_attributes_keys(self):
		if hasattr(self.__class__, '_myobject_attributes_keys'):
			return self.__class__._myobject_attributes_keys

		atr = self._get_attributes()
		keys = [ key for key, val in atr ]
		setattr(self.__class__, '_myobject_attributes_keys', keys)
		return keys




# vim: encoding=utf8: ff=unix: 
