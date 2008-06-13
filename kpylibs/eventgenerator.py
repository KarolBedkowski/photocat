#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=W0142, W0212
"""
Klasa dajaca mozliwosc podpinania listnerow pod obiekt

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

__all__			= ['EventGenerator']


import logging
_LOG = logging.getLogger(__name__)

import types


class EventGenerator:
	''' Obiekt umożliwiajacy generowanie wywołań wskazanych metod na określone zdarzenie '''

	def __init__(self, events=None, master_generator=None):
		self._event_master = master_generator
		if master_generator is None:
			self._event_clear()
			self._event_events = events
		else:
			self._event_events		= master_generator._event_events
			self._event_listeners	= master_generator._event_listeners


	def _event_clear(self):
		''' eg._event_clear() -- wyczyszczenie '''
		self._event_listeners = {}


	def event_add_listener(self, event, function):
		''' eg.event_add_listener(event, function)
			-- Dodanie metody do listy

		:param event:		nazwa (id) zdarzenia
		:param function:	funkcja do wywołania
		'''

		if type(function) not in (types.FunctionType, types.MethodType):
			raise TypeError('3 paremter must by function or method!')

		if self._event_events is not None and event not in self._event_events:
			raise ValueError('Invalid event! Available: %s' % str(self._event_events))

		if self._event_listeners.has_key(event):
			self._event_listeners[event].append(function)
		else:
			self._event_listeners[event] = [ function ]


	def event_remove_listener(self, event, function):
		''' eg.event_remove_listener(event, funtion)
			-- Usunięcie metody z listy 

		:param event:		nazwa (id) zdarzenia
		:param function:	funkcja do wywołania
		'''
		listeners = self._event_listeners.get(event)
		if listeners is None:
			return

		listeners.remove(function)
		if len(listeners) == 0:
			del self._event_listeners[event]


	def event_call(self, event, *args, **kwargs):
		''' eg.event_call(event, *args, **kwargs) -> int
			-- Uruchomienie lisnerów dla danego zdarzenia i parametrów.
			Zwraca liczbę uruhomionych metod

		:param event:		nazwa (id) zdarzenia
		:param *args:		parametry
		:param **kwargs:	parametry
		'''

		_LOG.debug('EventGenerator.call(%s, %s, %s)' % (repr(event), repr(args), repr(kwargs)))
		
		executed = 0
		listeners = self._event_listeners.get(event)
		if listeners is not None:
			for function in listeners:
				try:
					function(*args, **kwargs)
				except StandardError:
					_LOG.exception('call %s error' % repr(function))
				else:
					executed += 1
		return executed


	def event_list(self, event):
		''' eg.event_list(event) -> list -- get listeners for event 
		'''
		return self._event_listeners.get(event)


	def __repr__(self):
		return 'EventGenerator: %s' % str(self._event_listeners)




# vim: encoding=utf8: ff=unix: 
