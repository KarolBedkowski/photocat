#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.x (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2010'
__version__ = '2010-10-16'

__all__ = ['format_geopos']


import math


def _format_geopos(degree, latitude=True):
	lit = ["NS", "EW"][0 if latitude else 1][0 if degree > 0 else 1]
	degree = abs(degree)
	mint, stop = math.modf(degree)
	sec, mint = math.modf(mint * 60)
	return "%d %d' %0.2f'' %s" % (stop, mint, sec, lit)


def format_geopos(lon, lat):
	return _format_geopos(lon, False), _format_geopos(lat)
