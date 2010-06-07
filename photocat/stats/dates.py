# -*- coding: utf-8 -*-

"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (c) Karol Będkowski, 2006-2010'
__version__ = "2010-06-07"


import time

from ._stats_provider import StatsProvider


class DatesStats(StatsProvider):
	name = _('Dates')

	_stats_def = {
		'year': (_("By year"), "%Y", lambda x, y: x.tm_year),
		'yemo': (_("By year and month"), "%Y %B", lambda x, y: x.tm_year * 12 + \
				x.tm_mon),
		'mont': (_("By month"), "%B", lambda x, y: x.tm_mon),
		'date': (_("By date"), "%x", lambda x, y: y),
		'weda': (_("By weekday"), "%A", lambda x, y: x.tm_wday),
		'hour': (_("By day hour"), "%H", lambda x, y: x.tm_hour),
	}

	def __init__(self):
		StatsProvider.__init__(self)
		self._stats = dict((key, {}) for key in self._stats_def.iterkeys())

	def _compute_stats(self, objects):
		for item in self._get_items(objects):
			shot_date = item.shot_date
			if shot_date:
				tdate = time.localtime(shot_date)
				for skey, (_name, val_e, sort_f) in self._stats_def.iteritems():
					sdict = self._stats[skey]
					key = time.strftime(val_e, tdate)
					cnt, sortval = sdict.get(key) or (0, sort_f(tdate, shot_date))
					sdict[key] = (cnt + 1, sortval)
			else:
				for skey, (_name, _val_e, _sort_f) in self._stats_def.iteritems():
					sdict = self._stats[skey]
					cnt, _skey = sdict.get('') or (0, 0)
					sdict[''] = (cnt + 1, 0)

		for skey, (name, _val_e, _sort_f) in self._stats_def.iteritems():
			sdict = self._stats[skey]
			all_cnt = float(sum((val[0] for val in sdict.itervalues())))
			res = (((skey, key), val, val / all_cnt) for key, (val, skey)
					in sdict.iteritems())
			yield name, sorted(res)

# vim: encoding=utf8: ff=unix:
