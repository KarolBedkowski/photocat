#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=W0142
"""
Funkcje pomocnicze 

 handleerrors.py
 Copyright (c) Karol Będkowski, 2007

 This file is part of kPyLibs

 SAG is free software; you can redistribute it and/or modify it under the
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
__revision__	= '$Id: guitools.py 5 2007-06-05 20:27:47Z k $'

__all__			= []


import wx

from dialogs.message_boxes import message_box_error


def handle_exception(function, parent_window, logger=None, raise_exception=False, show_message=True, *args, **kwargs):
	try:
		function(*args, **kwargs)
	except Exception, err:
		if logger is not None:
			logger.exception('error in %s, (%s, %s)' % (str(function), str(args or None), str(kwargs or None)))
		if show_message:
			message_box_error(parent_window, 'Error:\n%s' % repr(err), 'Error')
		if raise_exception:
			raise err






# vim: encoding=utf8: ff=unix: 
