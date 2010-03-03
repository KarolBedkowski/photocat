# -*- coding: utf-8 -*-
'''
validators/validators/type_validator.py

kpylibs 1.x
Copyright (c) Karol Będkowski, 2006-2008

This file is part of kpylibs

kpylibs is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.
'''

import locale

from ._simple_validator import SimpleValidator
from .errors import ValidateError

##############################################################################


class IntValidator(SimpleValidator):

	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _('Integer value required')

		SimpleValidator.__init__(self, error_message)

	def value_from_window(self, value):
		if isinstance(value, int) or isinstance(value, long):
			return value

		try:
			value = locale.atoi(str(value))
		except ValueError:
			raise ValidateError(self._error_message)

		return value


##############################################################################


class FloatValidator(SimpleValidator):

	def __init__(self, error_message=None):
		if error_message is None:
			error_message = _('Float value required')

		SimpleValidator.__init__(self, error_message)

	def value_from_window(self, value):
		if isinstance(value, float):
			return value

		try:
			value = locale.atof(str(value))
		except ValueError:
			raise ValidateError(self._error_message)

		return value



##############################################################################


# vim: encoding=utf8: ff=unix:
