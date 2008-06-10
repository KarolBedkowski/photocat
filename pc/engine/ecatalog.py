# -*- coding: utf-8 -*-

"""
pc.engine.catalog
 -- obsługa katalogów
 
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


import os
import logging

import wx

from kpylibs				import dialogs
from kpylibs.appconfig		import AppConfig

from pc.model				import Catalog
from pc.gui.dlgadddisk		import DlgAddDisk

import errors


_LOG = logging.getLogger(__name__)
_ = wx.GetTranslation




def _count_files(path, parent_wnd, title):
	''' _count_files(path, parent_wnd, title) -> int -- polieczenie plików w podanej ścieżce
	'''
	dlg_progress = wx.ProgressDialog(title, _("Counting files..."), parent=parent_wnd, maximum=1,
			style=wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME)

	allfiles = Catalog.fast_count_files_dirs(path) + 1

	dlg_progress.Destroy()
	
	if allfiles == 1:
		dialogs.message_box_error(parent_wnd, _('No files found!'), title)
		return
	
	return allfiles



def _add_or_update_catalog(catalog, title, data, parent_wnd):
	''' _add_or_update_catalog(catalog, title, data, parent_wnd) -> Disk -- dodanie lub aktualizacja dysku
	'''
	appconfig = AppConfig()
	data.update(dict(appconfig.get_items('settings') or []))
	
	dlg = DlgAddDisk(parent_wnd, data, update=data['update'], catalog=catalog)
	result = dlg.ShowModal()
	dlg.Destroy()
	
	disk = data['disk']
	if result == wx.ID_OK:
		allfiles = _count_files(data['path'], parent_wnd, title)
		
		if allfiles > 0:
			dlg_progress = wx.ProgressDialog(title, ("  " * 30), parent=parent_wnd, maximum=allfiles,
					style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE|wx.PD_ELAPSED_TIME|wx.PD_CAN_ABORT)

			def update_progress(msg, cntr=[0]):
				cntr[0] = cntr[0] + os.path.getsize(msg)
				if cntr[0] > allfiles: # zabezpieczenie na dziwne sytuacje
					cntr[0] = max(0, cntr[0]-1000)
				return dlg_progress.Update(cntr[0], msg)[0]

			try:
				parent_wnd.SetCursor(wx.HOURGLASS_CURSOR)
				if data['update']:
					catalog.update_disk(disk, data['path'], descr=data['descr'], options=data, 
							on_update=update_progress, name=data['name'])

				else:
					disk = catalog.add_disk(data['path'], data['name'], data['descr'], options=data,
							on_update=update_progress)

				dlg_progress.Update(allfiles, _('Done!'))
				
			except Exception, err:
				_LOG.exception('_add_or_update_catalog(%r)' % data)
				dialogs.message_box_error(parent_wnd, _('Error:\n%s') % err, title)
				raise errors.UpdateDiskError(err)
			
			finally:
				parent_wnd.SetCursor(wx.STANDARD_CURSOR)
				dlg_progress.Destroy()
	else:
		disk = None
	
	return disk



def add_disk_to_catalog(catalog, parent_wnd):
	''' add_disk_to_catalog(catalog, parent_wnd) -> Disk -- dodanie dysku
	'''
	data = dict(disk=None, update=False)
	return _add_or_update_catalog(catalog, _("Adding disk"), data, parent_wnd)
	


def update_disk_in_catalog(catalog, disk, parent_wnd):
	''' update_disk_in_catalog(catalog, disk, parent_wnd) -> Disk -- aktualizacja dysku
	'''
	data = dict(name=disk.name, descr=disk.desc, disk=disk, update=True)
	return _add_or_update_catalog(catalog, _("Updating disk"), data, parent_wnd)


# vim: encoding=utf8: ff=unix:
