#!/usr/bin/python2.4
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Storage - _blocks.py

 KPyLibs
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

 This file is part of KPyLibs

 KPyLibs is free software; you can redistribute it and/or modify it under the
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
__revision__	= '$Id: wnd_shell.py 5 2007-06-05 20:27:47Z k $'

__all__			= []


import logging
_LOG = logging.getLogger(__name__)

from struct import unpack, calcsize, pack



class _UsedBlockBlock:
	def __init__(self, id):
		self._id = id
		self._next_id = 0


class _UsedBlocks:
	def __init__(self):
		# lista pustych blokow (offset, size)
		self._used_blocks = {}


	def 
		
	

# vim: encoding=utf8:
