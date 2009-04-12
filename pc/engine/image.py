#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
pc.engine.image
 -- engine do obsługi obrazów

 Photo Catalog v 1.0  (pc)
 Copyright (c) Karol Będkowski, 2004, 2005, 2006

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



import logging
_LOG = logging.getLogger(__name__)

import cStringIO

import wx

from pc.model				import FileImage



def load_image_from_item(item):
	''' load_image_from_item(item) -> wx.Image -- załadowanie obrazka z katalogu.

		@return wxImage()
	'''
	img = None
	if isinstance(item, FileImage):
		stream = None
		try:
			stream = cStringIO.StringIO(item.image)
			img		= wx.ImageFromStream(stream)

		except Exception, err:
			_LOG.exception('load_image_from_item %s error' % item.name)
			img = wx.EmptyImage(1, 1)

		finally:
			if stream is not None:
				stream.close()

	else:
		img = wx.EmptyImage(1, 1)

	return img


def load_bitmap_from_item(item):
	''' load_bitmap_from_item(item) -> wx.Bitmap -- załadowanie obrazka z katalogu.

		@return wxImage()
	'''
	img = load_image_from_item(item)
	return img.ConvertToBitmap() if img is not None else None



# vim: encoding=utf8: ff=unix:
