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
import re
import fnmatch

import wx

from kabes.wxtools			import dialogs
from kabes.tools.appconfig	import AppConfig
from kabes.tools.formaters	import format_human_size

from pc.model				import Catalog, FileImage
from pc.storage.storage		import Storage
from pc.gui.dlgadddisk		import DlgAddDisk

import errors
import image


_LOG = logging.getLogger(__name__)
_ = wx.GetTranslation



def _count_files(path, parent_wnd, title):
	''' _count_files(path, parent_wnd, title) -> int -- polieczenie plików 
		w podanej ścieżce

		@param path			-- ścieżka
		@param parent_wnd	-- okno nadrzędne
		@param title		-- tytuł okien
		@return liczba plików do dodania/aktualizacji
	'''
	dlg_progress = wx.ProgressDialog(title, _("Counting files..."), 
			parent=parent_wnd, maximum=1, 
			style=wx.PD_APP_MODAL|wx.PD_ELAPSED_TIME)

	allfiles = fast_count_files_dirs(path) + 1

	dlg_progress.Destroy()

	if allfiles == 1:
		dialogs.message_box_error(parent_wnd, _('No files found!'), title)
		return

	return allfiles



def _add_or_update_catalog(catalog, title, data, parent_wnd):
	''' _add_or_update_catalog(catalog, title, data, parent_wnd) -> Disk 
		-- dodanie lub aktualizacja dysku

		@param catalog		-- katalog do którego jest dodawany dysk
		@param title		-- tytuł okien
		@param data			-- dane przebudowy/aktualizacji
		@param parent_wnd	-- okno nadrzędne
		@return zaktualizowany/dodany dysk
	'''

	if catalog.readonly:
		raise errors.UpdateDiskError(_("Catalog is read-only."))

	appconfig = AppConfig()
	data.update(dict(appconfig.get_items('settings') or []))

	dlg = DlgAddDisk(parent_wnd, data, update=data['update'], catalog=catalog)
	result = dlg.ShowModal()
	dlg.Destroy()

	disk = data['disk']
	if result != wx.ID_OK:
		return None
	
	# kompilacja maski
	mask_list = data.get('skip_dirs_list') or []
	maskre_list = [ re.compile(fnmatch.translate(mask)) for mask in mask_list ]
	data['skip_dirs_list'] = maskre_list

	allfiles = _count_files(data['path'], parent_wnd, title)/10240

	if allfiles > 0:
		dlg_progress = wx.ProgressDialog(title, "\n", parent=parent_wnd, 
				maximum=allfiles+100,
				style=(wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_ELAPSED_TIME \
						|wx.PD_CAN_ABORT))
		dlg_progress.SetSize((600, -1))
		dlg_progress.SetMinSize((600, -1))
		dlg_progress.Center()

		path_len = len(data['path'])+1

		def update_progress(msg, cntr=[0]):
			cntr[0] = cntr[0] + os.path.getsize(msg)/10240
			if cntr[0] > allfiles: # zabezpieczenie na dziwne sytuacje
				cntr[0] = max(0, cntr[0]-10)
			return dlg_progress.Update(cntr[0], 
					_("Loading file:\n%s") % msg[path_len:])[0]

		try:
			parent_wnd.SetCursor(wx.HOURGLASS_CURSOR)
			if data['update']:
				catalog.update_disk(disk, data['path'], descr=data['descr'], 
						options=data, on_update=update_progress, 
						name=data['name'])

			else:
				disk = catalog.add_disk(data['path'], data['name'], 
						data['descr'], options=data, on_update=update_progress)

			dlg_progress.Update(allfiles+100, _('Done!'))

		except Exception, err:
			_LOG.exception('_add_or_update_catalog(%r)', data)
			dialogs.message_box_error(parent_wnd, _('Error:\n%s') % err, title)
			raise errors.UpdateDiskError(err)

		finally:
			parent_wnd.SetCursor(wx.STANDARD_CURSOR)
			dlg_progress.Destroy()

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
	''' update_disk_in_catalog(catalog, disk, parent_wnd) -> Disk 
		-- aktualizacja dysku

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
	if catalog.readonly:
		raise errors.UpdateDiskError(_("Catalog is read-only."))

	objects_count = catalog.object_in_files
	result = False

	dlg_progress = wx.ProgressDialog(_("Rebuild catalog"), 
			_("Rebuilding...\nPlease wait."), parent=parent_wnd,
			maximum=objects_count + 2, 
			style=(wx.PD_APP_MODAL|wx.PD_REMAINING_TIME|wx.PD_ELAPSED_TIME \
					|wx.PD_CAN_ABORT))

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
					_('Rebuild catalog finished\nSaved space: %sB') \
					% format_human_size(saved_space),
			)

		result = True

	except Exception, err:
		_LOG.exception('rebuild error')
		dialogs.message_box_error(parent_wnd,
				_('Rebuild catalog error!\n%(msg)s') % dict(msg=err.message),
				'PC')

	dlg_progress.Destroy()
	parent_wnd.SetCursor(wx.STANDARD_CURSOR)

	return result



def open_catalog(filename):
	''' open_catalog(filename) -> Catalog -- otwarcie katalogu

		@param filename - pełna ścieżka do pliku
		@retuen obiekt Catalog
		@exception OpenCatalogError
	'''
	_LOG.debug("ecatalog.open_catalog(%s)" , filename)

	# plik indeksu
	# istnienie
	if not os.path.exists(filename) or not os.path.isfile(filename):
		raise errors.OpenCatalogError(_("File not exists!"))

	# odczyt
	if not os.access(filename, os.R_OK):
		raise errors.OpenCatalogError(_("File not readable"))

	# zapis
	file_writable = os.access(filename, os.W_OK)
	if not file_writable:
		_LOG.debug("file %s not writable", filename)

	# plik danych
	data_file = os.path.splitext(filename)[0] + '.data'
	# istnienie
	if not os.path.exists(data_file) or not os.path.isfile(data_file):
		raise errors.OpenCatalogError(_("Data file not exists!"))

	# odczyt
	if not os.access(data_file, os.R_OK):
		raise errors.OpenCatalogError(_("Data file not readable"))

	# zapisywanie
	data_writable = os.access(data_file, os.W_OK)
	if not data_writable:
		_LOG.debug("file %s not writable", data_file)

	# ścieżka
	path_writable = os.access(os.path.dirname(filename), os.W_OK)
	if not path_writable:
		_LOG.debug("dir with file %s not writable", filename)

	writable = file_writable and path_writable and data_writable
	_LOG.info("ecatalog.open_catalog: file %s writable=%r (%r,%r,%r)", filename,
			writable, file_writable, path_writable, data_writable)

	try:
		catalog = Storage.load(filename)
		catalog.readonly = not writable
		catalog.data_provider.open(readonly=not writable)

	except Exception, err:
		raise errors.OpenCatalogError(err)

	return catalog


def new_catalog(filename):
	''' new_catalog(filename) -> Catalog -- otwarcie nowego katalogu

		@param filename - pełna ścieżka do pliku
		@retuen obiekt Catalog
		@exception OpenCatalogError
	'''
	_LOG.debug("ecatalog.open_catalog(%s)", filename)

	path = os.path.dirname(filename)

	# ścieżka istnieje
	if not os.path.exists(path):
		raise errors.OpenCatalogError(_("Invalid path"))

	# ścieżka jest zapisywalna
	if not os.access(path, os.W_OK):
		raise errors.OpenCatalogError(_("Path is not writable!"))

	# plik indexu
	# czy plik indeksu istnieje
	if os.path.exists(filename):
		# czy plik jest plikiem
		if os.path.isfile(filename):
			# czy mozna go czytac
			if not os.access(filename, os.R_OK):
				raise errors.OpenCatalogError(_("File not readable"))

			# czy mozna zapisywac
			if not os.access(filename, os.W_OK):
				raise errors.OpenCatalogError(_("File is not writable!"))

		# plik jest katalogiem
		else:
			raise errors.OpenCatalogError(_("Invalid path"))

	# plik danych
	data_file = os.path.splitext(filename)[0] + '.data'
	# czy plik danych istnieje
	if os.path.exists(data_file):
		# można czytać
		if not os.access(data_file, os.R_OK):
			raise errors.OpenCatalogError(_("File not readable"))

		# można zapisywać
		if not os.access(data_file, os.W_OK):
			raise errors.OpenCatalogError(_("File is not writable!"))

	try:
		catalog = Catalog(filename)
		catalog.data_provider.open(True)

	except Exception, err:
		raise errors.OpenCatalogError(err)

	return catalog



def check_new_file_exists(filename):
	''' check_new_file_exists(filename) -> (bool, bool, bool) -- sprawdzenie 
		czy plik indeksu i danych istnieją

		@param filename - scieżka do pliku indeksu
		@return (istnieje plik indeksu lub danych, istnieje plik indeksu, 
				istnieje plik danych)
	'''
	data_file = os.path.splitext(filename)[0] + '.data'
	index_exists = os.path.exists(filename)
	data_exists = os.path.exists(data_file)
	return (index_exists or data_exists), index_exists, data_exists


def catalog_close(catalog):
	catalog.close()
#	image.clear_cache()



SORT_BY_NAME = 0
SORT_BY_DATE = 1
SORT_BY_PATH = 2

# sorting functions
_SORTING_FUNCTIONS = {
		SORT_BY_NAME: (lambda x: x.image.name, lambda x: x.name),
		SORT_BY_PATH: (lambda x: x.image.disk.name + ": " + x.image.parent.path,
				lambda x: x.disk.name + ": " + x.parent.path),
		SORT_BY_DATE: (lambda x: x.image.date_to_check,  
				lambda x: x.date_to_check)
}

def get_sorting_function(sort_by=SORT_BY_NAME, reverse=False, 
		items_as_list=False):
	''' get_sorting_function(sort_by, [reverse], [items_as_list]) 
		-> (function, reverse) -- zwraca funkcję klucza do sortowania

		@param sort_by - pole po którym będzie sortowanie (SORT_BY_NAME, 
				SORT_BY_DATE, SORT_BY_PATH)
		@param reverse - (bool) czy sortowanie w odwrotnej kolejności
		@param items_as_list - (bool) czy elementy są podane jako lista czy 
				jako lista elementów Thumb
	'''
	return _SORTING_FUNCTIONS[sort_by][1 if items_as_list else 0], reverse



def fast_count_files_dirs(path):
	""" Szybkie liczenie ile jest plikow i katalogow w ścieżce 
		(i w podkatalogach) """

	_image_files_extension = FileImage.IMAGE_FILES_EXTENSION

	def count_folder(path):
		content = [ os.path.join(path, name)
				for name
				in os.listdir(path)
				if not name.startswith('.')
		]

		content_size = sum((
			os.path.getsize(item)
			for item in content
			if os.path.isdir(item) or (os.path.isfile(item)
					and os.path.splitext(item)[1].lower() in _image_files_extension
			)
		))

		content_size += sum( ( count_folder(item) for item in content 
				if os.path.isdir(item) ) )
		return content_size

	return count_folder(path)



def update_images_from_dict(images, data):
	changed_tags = {}
	for image in images:
		for key, val in data.iteritems():
			if key == 'tags':
				for key in image.set_tags(val):
					changed_tags.__setitem__(key, None)

			elif hasattr(image, key):
				setattr(image, key, val)
	
	return changed_tags.keys()




# vim: encoding=utf8: ff=unix:
