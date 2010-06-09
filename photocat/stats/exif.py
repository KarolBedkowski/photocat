# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-09"


import re
import locale

from ._stats_provider import StatsProvider


_RE_MATCH_DIV = re.compile(r'(\d+(?:\/\d+)?)')


def _parse_div(value, keep_float=True):
	if _RE_MATCH_DIV.match(value) and '/' in value:
		p1, p2 = value.split('/', 1)
		if p1 == '0' or p2 == '0':
			return 0
		value = float(p1) / float(p2)
	else:
		try:
			value = float(value)
		except ValueError:
			print value
			return None

	if not keep_float and value > 1:
		value = int(value)
	return value


def _calculate_float(value):
	value = _parse_div(value) or 0
	return value, locale.format('%0.1f', value)


def _calc_lens(value):
	if not value.startswith('[') or not value.endswith(']'):
		return value, value
	values = _RE_MATCH_DIV.findall(value)
	if not value or len(values) != 4:
		return value, value
	values = [_parse_div(val) for val in values]
	if int(values[0]) != float(values[0]):
		length = locale.format('%0.2f-%0.2f', (float(values[0]), float(values[1])))
	else:
		length = '%d-%d' % (int(values[0]), int(values[1]))
	if float(values[2]) >= 0.1:
		app = locale.format('%0.1f-%0.1f', (float(values[2]), float(values[3])))
		return values[0], length + '  [' + app + ']'
	return values[0], length


def _calc_length(value):
	value = _parse_div(value) or 0
	value = int(value / 10) * 10
	return (value, '%d-%d' % (value, value + 10))


def _calc_time(value):
	valuep = _parse_div(value)
	return valuep, value


def _calc_simple(value):
	return value, value


def _calc_iso(value):
	values = _RE_MATCH_DIV.findall(value)
	if values:
		iso = values[-1]
		if int(iso):
			return int(iso), str(iso)
	return (None, '')


class ExifLens(StatsProvider):
	name = _('EXIF')

	_keys = {'EXIF FNumber': (_('F number'), _calculate_float),
			'EXIF FocalLength': (_('Focal Length'), _calc_length),
			'EXIF ExposureTime': (_('Exposure time'), _calc_time),
			'MakerNote LensMinMaxFocalMaxAperture': (_('Lens'), _calc_lens),
			'EXIF Flash': (_("Flash"), _calc_simple),
			'Image Model': (_("Camera model"), _calc_simple),
			'MakerNote ISOSetting': (_("ISO"), _calc_iso),
	}

	def _compute_stats(self, objects):
		stats = dict((key, {}) for key in self._keys.iterkeys())
		for item in self._get_items(objects):
			exif = item.exif_data
			if not exif:
				continue
			for key, (_name, calc_func) in self._keys.iteritems():
				value = calc_func(exif[key]) if key in exif else (None, '')
				cnt = stats[key].get(value, 0) + 1
				stats[key][value] = cnt
		for key, value in stats.iteritems():
			all_count = float(sum(value.itervalues()))
			keystats = [(sval, scnt, scnt / all_count) for sval, scnt
					in value.iteritems()]
			keystats.sort()
			yield (self._keys[key][0], keystats)


# vim: encoding=utf8: ff=unix:
