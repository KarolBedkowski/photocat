# -*- coding: utf-8 -*-

"""
photocat.engine.collections
-- obsługa katalogów

Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


import os
import logging
import re
import fnmatch

import wx

from photocat.model import Collection, FileImage
from photocat.storage.storage import Storage
from photocat.gui.dlgadddisk import DlgAddDisk
from photocat.lib.formaters import format_human_size
from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools import dialogs
from photocat.engine import errors

_LOG = logging.getLogger(__name__)


def _count_files(path, parent_wnd, title):
	'''_count_files(path, parent_wnd, title) -> int -- polieczenie plików
	w podanej ścieżce
	@param path			-- ścieżka
	@param parent_wnd	-- okno nadrzędne
	@param title		-- tytuł okien
	@return liczba plików do dodania/aktualizacji '''
	dlg_progress = wx.ProgressDialog(title, _("Counting files..."),
			parent=parent_wnd, maximum=1, style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME)

	allfiles = fast_count_files_dirs(path) + 1

	dlg_progress.Destroy()

	if allfiles == 1:
		dialogs.message_box_error(parent_wnd, _('No files found!'), title)
		return

	return allfiles


def _add_or_update_collection(collection, title, data, parent_wnd):
	''' _add_or_update_collection(collection. title, data, parent_wnd) -> Disk
		-- dodanie lub aktualizacja dysku
		@param collection	-- katalog do którego jest dodawany dysk
		@param title		-- tytuł okien
		@param data			-- dane przebudowy/aktualizacji
		@param parent_wnd	-- okno nadrzędne
		@return zaktualizowany/dodany dysk '''

	if collection.readonly:
		raise errors.UpdateDiskError(_("Collection is read-only."))

	data.update(dict(AppConfig().get_items('settings') or []))
	data['path'] = data['disk'].last_path if 'disk' in data and data['disk'] \
			else ''

	dlg = DlgAddDisk(parent_wnd, data, update=data['update'],
			collection=collection)
	result = dlg.ShowModal()
	dlg.Destroy()

	disk = data['disk']
	if result != wx.ID_OK:
		return None

	# kompilacja maski
	maskre_list = [re.compile(fnmatch.translate(mask))
			for mask in data.get('skip_dirs_list') or []]
	data['skip_dirs_list'] = maskre_list

	allfiles = _count_files(data['path'], parent_wnd, title) / 10240

	if allfiles > 0:
		dlg_progress = wx.ProgressDialog(title, "\n", parent=parent_wnd,
				maximum=allfiles + 100, style=(wx.PD_APP_MODAL | wx.PD_REMAINING_TIME \
						| wx.PD_ELAPSED_TIME | wx.PD_CAN_ABORT))
		dlg_progress.SetSize((600, -1))
		dlg_progress.SetMinSize((600, -1))
		dlg_progress.Center()

		path_len = len(data['path']) + 1
		cntr = [0]

		def update_progress(msg):
			''' update progress bar '''
			cntr[0] = cntr[0] + os.path.getsize(msg) / 10240
			if cntr[0] > allfiles:  # zabezpieczenie na dziwne sytuacje
				cntr[0] = max(0, cntr[0] - 10)
			return dlg_progress.Update(cntr[0],
					_("Loading file:\n%s") % msg[path_len:])[0]

		try:
			parent_wnd.SetCursor(wx.HOURGLASS_CURSOR)
			if data['update']:
				collection.update_disk(disk, data['path'], descr=data['descr'],
						options=data, on_update=update_progress, name=data['name'])
			else:
				disk = collection.add_disk(data['path'], data['name'],
						data['descr'], options=data, on_update=update_progress)
			dlg_progress.Update(allfiles + 100, _('Done!'))
		except Exception, err:
			_LOG.exception('_add_or_update_collection(%r)', data)
			dialogs.message_box_error(parent_wnd, _('Error:\n%s') % err, title)
			raise errors.UpdateDiskError(err)
		finally:
			parent_wnd.SetCursor(wx.STANDARD_CURSOR)
			dlg_progress.Destroy()

	return disk


def add_disk_to_collection(collection, parent_wnd):
	''' add_disk_to_collection(collection, parent_wnd) -> Disk -- dodanie dysku
		@param collection	-- katalog do którego jest dodawany dysk
		@param parent_wnd	-- okno nadrzędne
		@return dodany dysk '''
	data = dict(disk=None, update=False)
	return _add_or_update_collection(collection, _("Adding disk"), data,
			parent_wnd)


def update_disk_in_collection(collection, disk, parent_wnd):
	''' update_disk_in_collection(collection, disk, parent_wnd) -> Disk
		-- aktualizacja dysku

		@param collection		-- katalog w którym jest aktualizowany dysk
		@param disk			-- dysk do aktualizacji
		@param parent_wnd	-- okno nadrzędne
		@return zaktualizowany dysk
	'''
	data = dict(name=disk.name, descr=disk.desc, disk=disk, update=True)
	return _add_or_update_collection(collection, _("Updating disk"), data,
			parent_wnd)


def rebuild(collection, parent_wnd):
	''' rebuild(collection, parent_wnd) -> bool -- przebudowa katalogu
		@param collection	-- katalog do przebudowania
		@param parent_wnd	-- okno nadrzędne
		@return True=sukces	'''
	if collection.readonly:
		raise errors.UpdateDiskError(_("Collection is read-only."))

	objects_count = collection.object_in_files
	result = False

	dlg_progress = wx.ProgressDialog(_("Rebuild collection"),
			_("Rebuilding...\nPlease wait."), parent=parent_wnd,
			maximum=objects_count + 2,
			style=(wx.PD_APP_MODAL | wx.PD_REMAINING_TIME | wx.PD_ELAPSED_TIME \
					| wx.PD_CAN_ABORT))

	def update_progress(count):
		''' update progress bar '''
		return dlg_progress.Update(count)[0]

	try:
		parent_wnd.SetCursor(wx.HOURGLASS_CURSOR)
		saved_space = collection.data_provider.rebuild(collection, update_progress)
		dlg_progress.Update(objects_count + 1, _("Saving..."))

		if saved_space < 0:
			dlg_progress.Update(objects_count + 2, _('Rebuild collection aborted'))
		else:
			dlg_progress.Update(objects_count + 2,
					_('Rebuild collection finished\nSaved space: %sB') \
					% format_human_size(saved_space),
			)
		result = True
	except RuntimeError, err:
		_LOG.exception('rebuild error')
		dialogs.message_box_error(parent_wnd,
				_('Error occurred when rebuilding collection:\n%(msg)s') \
				% dict(msg=err.message), _('Rebuild collection file'))

	dlg_progress.Destroy()
	parent_wnd.SetCursor(wx.STANDARD_CURSOR)
	return result


def open_collection(filename):
	''' open_collection(filename) -> Collection -- otwarcie katalogu
		@param filename - pełna ścieżka do pliku
		@retuen obiekt Collection
		@exception OpenCollectionError'''
	_LOG.debug("collections.open_collection(%s)", filename)

	# plik indeksu
	# istnienie
	if not os.path.exists(filename) or not os.path.isfile(filename):
		raise errors.OpenCollectionError(_("File not exists!"))

	# odczyt
	if not os.access(filename, os.R_OK):
		raise errors.OpenCollectionError(_("File not readable"))

	# zapis
	file_writable = os.access(filename, os.W_OK)
	if not file_writable:
		_LOG.debug("file %s not writable", filename)

	# plik danych
	data_file = os.path.splitext(filename)[0] + '.data'
	# istnienie
	if not os.path.exists(data_file) or not os.path.isfile(data_file):
		raise errors.OpenCollectionError(_("Data file not exists!"))

	# odczyt
	if not os.access(data_file, os.R_OK):
		raise errors.OpenCollectionError(_("Data file not readable"))

	# zapisywanie
	data_writable = os.access(data_file, os.W_OK)
	if not data_writable:
		_LOG.debug("file %s not writable", data_file)

	# ścieżka
	path_writable = os.access(os.path.dirname(filename), os.W_OK)
	if not path_writable:
		_LOG.debug("dir with file %s not writable", filename)

	writable = file_writable and path_writable and data_writable
	_LOG.info("collections.open_collection: file %s writable=%r (%r,%r,%r)",
			filename, writable, file_writable, path_writable, data_writable)

	try:
		collection = Storage.load(filename)
		collection.readonly = not writable
		collection.data_provider.open(readonly=not writable)
	except Exception, err:
		raise errors.OpenCollectionError(err)

	return collection


def new_collection(filename):
	''' new_collection(filename) -> Collection -- otwarcie nowego katalogu
		@param filename - pełna ścieżka do pliku
		@retuen obiekt Collection
		@exception OpenCollectionError	'''
	_LOG.debug("collections.open_collection(%s)", filename)
	path = os.path.dirname(filename)
	# ścieżka istnieje
	if not os.path.exists(path):
		raise errors.OpenCollectionError(_("Invalid path"))

	# ścieżka jest zapisywalna
	if not os.access(path, os.W_OK):
		raise errors.OpenCollectionError(_("Path is not writable!"))

	# plik indexu
	# czy plik indeksu istnieje
	if os.path.exists(filename):
		# czy plik jest plikiem
		if os.path.isfile(filename):
			# czy mozna go czytac
			if not os.access(filename, os.R_OK):
				raise errors.OpenCollectionError(_("File not readable"))

			# czy mozna zapisywac
			if not os.access(filename, os.W_OK):
				raise errors.OpenCollectionError(_("File is not writable!"))

		# plik jest katalogiem
		else:
			raise errors.OpenCollectionError(_("Invalid path"))

	# plik danych
	data_file = os.path.splitext(filename)[0] + '.data'
	# czy plik danych istnieje
	if os.path.exists(data_file):
		# można czytać
		if not os.access(data_file, os.R_OK):
			raise errors.OpenCollectionError(_("File not readable"))

		# można zapisywać
		if not os.access(data_file, os.W_OK):
			raise errors.OpenCollectionError(_("File is not writable!"))

	try:
		collection = Collection(filename)
		collection.data_provider.open(True)
	except Exception, err:
		raise errors.OpenCollectionError(err)

	return collection


def check_new_file_exists(filename):
	''' check_new_file_exists(filename) -> (bool, bool, bool) -- sprawdzenie
		czy plik indeksu i danych istnieją
		@param filename - scieżka do pliku indeksu
		@return (istnieje plik indeksu lub danych, istnieje plik indeksu,
				istnieje plik danych)'''
	data_file = os.path.splitext(filename)[0] + '.data'
	index_exists = os.path.exists(filename)
	data_exists = os.path.exists(data_file)
	return (index_exists or data_exists), index_exists, data_exists


def collection_close(collection):
	''' Close @collection '''
	collection.close()
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
				lambda x: x.date_to_check)}


def get_sorting_function(sort_by=SORT_BY_NAME, reverse=False,
		items_as_list=False):
	''' get_sorting_function(sort_by, [reverse], [items_as_list])
	-> (function, reverse) -- zwraca funkcję klucza do sortowania
	@param sort_by	- pole po którym będzie sortowanie (SORT_BY_NAME,
					SORT_BY_DATE, SORT_BY_PATH)
	@param reverse	- (bool) czy sortowanie w odwrotnej kolejności
	@param items_as_list - (bool) czy elementy są podane jako lista czy jako
					lista elementów Thumb'''
	return _SORTING_FUNCTIONS[sort_by][1 if items_as_list else 0], reverse


def fast_count_files_dirs(path):
	""" Szybkie liczenie ile jest plikow i katalogow w ścieżce
		(i w podkatalogach) """

	_image_files_extension = FileImage.IMAGE_FILES_EXTENSION

	def count_folder(path):
		''' count files and dirs in selcted path '''
		content = [os.path.join(path, name) for name in os.listdir(path)
				if not name.startswith('.')]
		content_size = sum(os.path.getsize(item) for item in content
				if os.path.isdir(item) or (os.path.isfile(item)
				and os.path.splitext(item)[1].lower() in _image_files_extension))
		content_size += sum(count_folder(item) for item in content
				if os.path.isdir(item))
		return content_size

	return count_folder(path)


def update_images_from_dict(images, data):
	''' update all @images by @data '''
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
