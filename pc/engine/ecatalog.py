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
from kpylibs.formaters		import format_human_size

from pc.model				import Catalog
from pc.gui.dlgadddisk		import DlgAddDisk

import errors


_LOG = logging.getLogger(__name__)
_ = wx.GetTranslation




def _count_files(path, parent_wnd, title):
	''' _count_files(path, parent_wnd, title) -> int -- polieczenie plików w podanej ścieżce

		@param path			-- ścieżka
		@param parent_wnd	-- okno nadrzędne
		@param title		-- tytuł okien
		@return liczba plików do dodania/aktualizacji
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

		@param catalog		-- katalog do którego jest dodawany dysk
		@param title		-- tytuł okien
		@param data			-- dane przebudowy/aktualizacji
		@param parent_wnd	-- okno nadrzędne
		@return zaktualizowany/dodany dysk
	'''
	appconfig = AppConfig()
	data.update(dict(appconfig.get_items('settings') or []))

	dlg = DlgAddDisk(parent_wnd, data, update=data['update'], catalog=catalog)
	result = dlg.ShowModal()
	dlg.Destroy()

	disk = data['disk']
	if result == wx.ID_OK:
		allfiles = _count_files(data['path'], parent_wnd, title)/10240

		if allfiles > 0:
			dlg_progress = wx.ProgressDialog(title, "\n", parent=parent_wnd, maximum=allfiles+100,
					style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_ELAPSED_TIME|wx.PD_CAN_ABORT)
			dlg_progress.SetSize((600, -1))
			dlg_progress.SetMinSize((600, -1))
			dlg_progress.Center()

			path_len = len(data['path'])+1

			def update_progress(msg, cntr=[0]):
				cntr[0] = cntr[0] + os.path.getsize(msg)/10240
				if cntr[0] > allfiles: # zabezpieczenie na dziwne sytuacje
					cntr[0] = max(0, cntr[0]-10)
				return dlg_progress.Update(cntr[0], _("Loading file:\n%s") % msg[path_len:])[0]

			try:
				parent_wnd.SetCursor(wx.HOURGLASS_CURSOR)
				if data['update']:
					catalog.update_disk(disk, data['path'], descr=data['descr'], options=data,
							on_update=update_progress, name=data['name'])

				else:
					disk = catalog.add_disk(data['path'], data['name'], data['descr'], options=data,
							on_update=update_progress)

				dlg_progress.Update(allfiles+100, _('Done!'))

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

		@param catalog		-- katalog do którego jest dodawany dysk
		@param parent_wnd	-- okno nadrzędne
		@return dodany dysk
	'''
	data = dict(disk=None, update=False)
	return _add_or_update_catalog(catalog, _("Adding disk"), data, parent_wnd)



def update_disk_in_catalog(catalog, disk, parent_wnd):
	''' update_disk_in_catalog(catalog, disk, parent_wnd) -> Disk -- aktualizacja dysku

		@param catalog		-- katalog w którym jest aktualizowany dysk
		@param disk			-- dysk do aktualizacji
		@param parent_wnd	-- okno nadrzędne
		@return zaktualizowany dysk
	'''
	data = dict(name=disk.name, descr=disk.desc, disk=disk, update=True)
	return _add_or_update_catalog(catalog, _("Updating disk"), data, parent_wnd)


def rebuild(catalog, parent_wnd):
	''' rebuild(catalog, parent_wnd) -> bool -- przebudowa katalogu

		@param catalog		-- katalog do przebudowania
		@param parent_wnd	-- okno nadrzędne
		@return True=sukces
	'''
	objects_count = catalog.object_in_files
	result = False

	dlg_progress = wx.ProgressDialog(_("Rebuild catalog"), _("Rebuilding...\nPlease wait."), parent=parent_wnd,
			maximum=objects_count + 2, style=wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_ELAPSED_TIME|wx.PD_CAN_ABORT)

	def update_progress(count):
		return dlg_progress.Update(count)[0]

	try:
		parent_wnd.SetCursor(wx.HOURGLASS_CURSOR)
		saved_space = catalog.data_provider.rebuild(catalog, update_progress)
		dlg_progress.Update(objects_count+1, _("Saving..."))

		if saved_space < 0:
			dlg_progress.Update(objects_count + 2,	_('Rebuild catalog aborted'))
		else:
			dlg_progress.Update(objects_count + 2,
					_('Rebuild catalog finished\nSaved space: %sB') % format_human_size(saved_space),
			)
		result = True

	except Exception, err:
		_LOG.exception('rebuild error')
		dialogs.message_box_error(parent_wnd,
				_('Rebuild catalog error!\n%(msg)s') % dict(msg=err.message),
				'PC')

	finally:
		dlg_progress.Destroy()
		parent_wnd.SetCursor(wx.STANDARD_CURSOR)

	return result

# vim: encoding=utf8: ff=unix:
