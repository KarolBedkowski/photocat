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


from itertools import izip
import cStringIO

import wx

from pc.lib.ThumbnailCtrl import *



class MyScrolledThumbnail(ScrolledThumbnail):
	def __init__(self, *argv, **kwagrs):
		ScrolledThumbnail.__init__(self, *argv, **kwagrs)
		self.SetThumbSize(200, 200)

		
	def ListDirectory(self, directory, fileExtList):
		print 'ListDirectory ', self._folder.name
		
		if self._folder is None:
			return []
		
		return self._folder.files
	
		
	def LoadImages(self, newfile, imagecount):
		""" Methods That Load Images On ThumbnailCtrl. Used Internally. """	

		stream = cStringIO.StringIO(newfile.image)
		img = wx.ImageFromStream(stream)
		originalsize = (img.GetWidth(), img.GetHeight())
		
		try:
			self._items[imagecount]._threadedimage = img
			self._items[imagecount]._originalsize = originalsize
			self._items[imagecount]._bitmap = img
		except:
			return
		
	
		
	def ShowDir(self, dir, filter=THUMB_FILTER_IMAGES):
		""" Shows Thumbnails For A Particular Folder. """
		
		if filter >= 0:
			self._filter = filter
			
		#self.SetCaption(dir.name)
		
		self._isrunning = False	
		
		# update items
		self._items = []

		if isinstance(dir, list) or isinstance(dir, tuple):
			filenames = dir
		else:
			filenames = dir.files
			
		self.images = filenames

		for files in filenames:
			self._items.append(Thumb(self, dir, files, files.name, files.size, files.date))

		items = self._items[:]
		
		for idx, img in izip(xrange(len(filenames)), filenames):
			self.LoadImages(img, idx)

		self._selectedarray = []
		self.UpdateProp()
		self.Refresh()
	

	@property
	def selected_items(self):
		return self._selectedarray



class MyThumbnailCtrl(ThumbnailCtrl):
	def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, thumboutline=THUMB_OUTLINE_IMAGE,
				 thumbfilter=THUMB_FILTER_IMAGES):
		
		wx.Panel.__init__(self, parent, id, pos, size)	 

		self._sizer = wx.BoxSizer(wx.VERTICAL)

		self._combo = wx.ComboBox(self, -1, style=wx.CB_DROPDOWN | wx.CB_READONLY)
		self._scrolled = MyScrolledThumbnail(self, -1, thumboutline=thumboutline,
										   thumbfilter=thumbfilter)

		subsizer = wx.BoxSizer(wx.HORIZONTAL)
		subsizer.Add((3, 0), 0)
		subsizer.Add(self._combo, 0, wx.EXPAND | wx.TOP, 3)
		subsizer.Add((3, 0), 0)
		self._sizer.Add(subsizer, 0, wx.EXPAND | wx.ALL, 3)
		self._sizer.Add(self._scrolled, 1, wx.EXPAND)

		self.SetSizer(self._sizer)

		self._sizer.Show(0, False)		
		self._sizer.Layout()

		methods = ["GetSelectedItem", "GetPointed", "GetHighlightPointed", "SetHighlightPointed",
				   "SetThumbOutline", "GetThumbOutline", "GetPointedItem", "GetItem",
				   "GetItemCount", "GetThumbWidth", "GetThumbHeight", "GetThumbBorder",
				   "ShowFileNames", "SetPopupMenu", "GetPopupMenu", "SetGlobalPopupMenu",
				   "GetGlobalPopupMenu", "SetSelectionColour", "GetSelectionColour",
				   "EnableDragging", "SetThumbSize", "GetThumbSize", "ShowDir",
				   "GetShowDir", "SetSelection", "GetSelection", "SetZoomFactor",
				   "GetZoomFactor", "SetCaptionFont", "GetCaptionFont", "GetItemIndex",
				   "InsertItem", "RemoveItemAt", "IsSelected", "Rotate", "ZoomIn", "ZoomOut",
				   "EnableToolTips", "GetThumbInfo", "GetOriginalImage"]

		for method in methods:
			setattr(self, method, getattr(self._scrolled, method))

		self._combochoices = []
		self._showcombo = False
		self._subsizer = subsizer
		
		self._combo.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
		
		self.SetZoomFactor(2.0)

		
		
		
	@property
	def selected_item(self):
		sel = self.GetSelection()
		if sel >= 0:
			return self._scrolled.images[sel]
		return None
	

	def select_item(self, item):
		index = self._scrolled.images.index(item)
		self.SetSelection(index)
		

	@property
	def selected_items(self):
		return self._scrolled.selected_items

# vim: encoding=utf8: ff=unix: 
