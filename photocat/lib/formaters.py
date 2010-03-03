#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Formaters

KPyLibs
Copyright (c) Karol Będkowski, 2004-2007

This file is part of KPyLibs

KPyLibs is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id: wnd_shell.py 5 2007-06-05 20:27:47Z k $'
__all__ = ['format_size']


import locale


_RZAD_WIELKOSCI = ('', 'k', 'm', 'g', 't')
_RZAD_WIELKOSCI_U = ('', 'K', 'M', 'G', 'T')


def format_size(value, human_readable=False, base=1024, reduce_at=None,
		separate=False, format=None, upper=False):
	''' format_size(value, [human_readable]) -> string -- rozmiar w ludzkiej
	postaci '''
	if format is None:
		value = int(value)
	else:
		value = float(value)
	postfix = ''

	if human_readable:
		reduce_at = reduce_at or base
		idx = 0
		while value > reduce_at and idx < 5:
			idx += 1
			value /= base
		postfix = (upper and _RZAD_WIELKOSCI_U or _RZAD_WIELKOSCI)[idx]

	if format is not None:
		#str_value = format % value
		str_value = locale.format(format, value)
	else:
		str_value = str(value)

	if separate:
		end = ''
		output = []
		if format is not None:
			splited = str_value.split(locale.localeconv()['decimal_point'])
			if len(splited) == 2:
				end = locale.localeconv()['decimal_point'] + splited[1]
				str_value = splited[0]

		while len(str_value) > 0:
			output.insert(0, str_value[-3:])
			str_value = str_value[:-3]

		str_value = ' '.join(output) + end

	return str_value + postfix


def format_human_size(value, format="%0.2f"):
	return format_size(value, human_readable=True, format=format, upper=True)




# vim: encoding=utf8:
