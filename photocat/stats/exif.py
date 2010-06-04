# -*- coding: utf-8 -*-

"""
 Photo Catalog v 1.0  (photocat)
 Copyright (c) Karol Będkowski, 2004-2010

 This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-04"


from photocat.model import Directory, Collection, FileImage

from ._stats_provider import StatsProvider


def _calculate_float(value, to_str=True):
	if '/' in value:
		p1, p2 = value.split('/', 1)
		if p1 == '0' or p2 == '0':
			return 0
		if '/' in p2:
			return value
		value = float(p1) / float(p2)
		if to_str:
			value = '%0.1f' % value
	return value

def _calcualate_int(value):
	try:
		value = int(float(_calculate_float(value)))
	except Exception, err:
		print value, err
	return value

def _calc_lens(value):
	if not value.startswith('[') or not value.endswith(']'):
		return value
	values = value[1:-1].split(', ')
	if len(values) != 4:
		return value
	length = '-'.join((str(_calcualate_int(values[0])),
			str(_calcualate_int(values[1]))))
	app = '-'.join((str(_calculate_float(values[2])),
			str(_calculate_float(values[3]))))
	return length + ' ' + app


class ExifLens(StatsProvider):
	name = _('EXIF lens stats')

	_keys = {'EXIF FNumber': (_('F number'), _calculate_float),
			'EXIF FocalLength': (_('Focal Length'), _calcualate_int),
			'EXIF ExposureTime': (_('Exposure time'), str),
			'MakerNote LensMinMaxFocalMaxAperture' : (
					_('Lens'), _calc_lens),
	}

	def get_stats(self, objects):
		stats = dict((key, {}) for key in self._keys.iterkeys())
		for item in self._get_items(objects):
			exif = item.exif_data
			if not exif:
				continue
			for key, (_name, calc_func) in self._keys.iteritems():
				value = calc_func(exif[key]) if key in exif else ''
				cnt = stats[key].get(value, 0) + 1
				stats[key][value] = cnt
		for key, value in stats.iteritems():
			all_count = float(len(value))
			keystats = [(sval, scnt, scnt/all_count) for sval, scnt
					in value.iteritems()]
			keystats.sort()
			yield (self._keys[key][0], keystats)

	def _get_items(self, objects):
		for obj in objects:
			if isinstance(obj, Collection):
				for item in self._find_itmes_in_collection(obj):
					yield item
			elif isinstance(obj, Directory):
				for item in self._find_itmes_in_dir(obj):
					yield item
			elif isinstance(obj, FileImage):
				yield obj

	def _find_itmes_in_collection(self, collection):
		for disk in collection.disks:
			for item in self._find_itmes_in_dir(disk):
				yield item

	def _find_itmes_in_dir(self, directory):
		for subdir in directory.subdirs:
			for item in self._find_itmes_in_dir(subdir):
				yield item
		for img in directory.files:
			yield img



# vim: encoding=utf8: ff=unix:
