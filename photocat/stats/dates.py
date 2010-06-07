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

	def __init__(self):
		StatsProvider.__init__(self)
		self._stats_by_year = {}
		self._stats_by_yearmonth = {}
		self._stats_by_day = {}
		self._stats_by_month = {}
		self._stats_by_weekday = {}
		self._stats_by_hour = {}

	def _compute_stats(self, objects):
		for item in self._get_items(objects):
			shot_date = item.shot_date
			if shot_date:
				tdate = time.localtime(shot_date)
				_add_to_stats(self._stats_by_year, '%Y', tdate, tdate.tm_year)
				_add_to_stats(self._stats_by_yearmonth, "%Y %B", tdate,
						tdate.tm_year * 12 + tdate.tm_mon)
				_add_to_stats(self._stats_by_month, "%B", tdate, tdate.tm_mon)
				_add_to_stats(self._stats_by_day, "%x", tdate, shot_date)
				_add_to_stats(self._stats_by_weekday, "%A", tdate, tdate.tm_wday)
				_add_to_stats(self._stats_by_hour, "%H", tdate, tdate.tm_hour)
			else:
				_add_to_stats_unknown(self._stats_by_year)
				_add_to_stats_unknown(self._stats_by_yearmonth)
				_add_to_stats_unknown(self._stats_by_month)
				_add_to_stats_unknown(self._stats_by_day)
				_add_to_stats_unknown(self._stats_by_weekday)
				_add_to_stats_unknown(self._stats_by_hour)

		yield _("By year"), _get_stats_for_var(self._stats_by_year)
		yield _("By year and month"), _get_stats_for_var(self._stats_by_yearmonth)
		yield _("By month"), _get_stats_for_var(self._stats_by_month)
		yield _("By date"), _get_stats_for_var(self._stats_by_day)
		yield _("By weekday"), _get_stats_for_var(self._stats_by_weekday)
		yield _("By day hour"), _get_stats_for_var(self._stats_by_hour)


def _add_to_stats(var, format_, date, sdate):
	key = time.strftime(format_, date)
	cnt, _skey = var.get(key) or (0, 0)
	var[key] = (cnt + 1, sdate)


def _add_to_stats_unknown(var):
	cnt, _skey = var.get('') or (0, 0)
	var[''] = (cnt + 1, 0)


def _get_stats_for_var(var):
	all_cnt = float(sum((val[0] for val in var.itervalues())))
	res = [((skey, key), val, val / all_cnt) for key, (val, skey)
			in var.iteritems()]
	res.sort()
	return res



# vim: encoding=utf8: ff=unix:
