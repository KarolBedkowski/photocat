#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004, 2005, 2006

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'

__all__ = ['data2font', 'font2data', 'str2color', 'color2str']


import wx

_SETTINGS_KEYS = (
		('thumb_width', 200), ('thumb_height', 200), ('thumb_compression', 50),
		('view_preload', True), ('view_show_captions', True))

_FONT_STYLES = {'wxNORMAL': wx.FONTSTYLE_NORMAL, 'wxSLANT': wx.FONTSTYLE_SLANT,
		'wxITALIC': wx.FONTSTYLE_ITALIC}
_FONT_WEIGHTS = {'wxNORMAL': wx.FONTWEIGHT_NORMAL,
		'wxLIGHT': wx.FONTWEIGHT_LIGHT, 'wxBOLD': wx.FONTWEIGHT_BOLD}
_FONT_FAMILIES = {'wxDEFAULT': wx.FONTFAMILY_DEFAULT,
		'wxDECORATIVE': wx.FONTFAMILY_DECORATIVE, 'wxROMAN': wx.FONTFAMILY_ROMAN,
		'wxSCRIPT': wx.FONTFAMILY_SCRIPT, 'wxSWISS': wx.FONTFAMILY_SWISS,
		'wxMODERN': wx.FONTFAMILY_MODERN, 'wxTELETYPE': wx.FONTFAMILY_TELETYPE}


def data2font(data, prefix, default=None):
	if data.get(prefix + '_font_face') is not None:
		family = _FONT_FAMILIES.get(data[prefix + "_font_family"],
				wx.FONTFAMILY_DEFAULT)
		pointsize = int(data.get(prefix + "_font_size", 12))
		style = _FONT_STYLES.get(data[prefix + "_font_style"],
				wx.FONTSTYLE_NORMAL)
		weight = _FONT_WEIGHTS.get(data[prefix + "_font_weight"],
				wx.FONTWEIGHT_NORMAL)
		underline = data[prefix + "_font_underline"] == 'true'
		face = data[prefix + "_font_face"]
		font = wx.Font(pointsize, family, style, weight, underline, face)
	else:
		font = default

	return font


def font2data(font, prefix):
	data = {}
	data[prefix + '_font_family'] = font.GetFamilyString()
	data[prefix + '_font_face'] = font.GetFaceName()
	data[prefix + '_font_style'] = font.GetStyleString()
	data[prefix + '_font_size'] = font.GetPointSize()
	data[prefix + '_font_weight'] = font.GetWeightString()
	data[prefix + '_font_underline'] = "true" if font.GetUnderlined() else "false"
	data[prefix + '_font'] = font.GetNativeFontInfoUserDesc()
	return data


def str2color(value, default=None):
	if value is None:
		return default

	try:
		red, green, blue = [int(val) for val in value.split(';')]
		return wx.Colour(red, green, blue)
	except Exception:
		return default


def color2str(color):
	return '%d;%d;%d' % (color.Red(), color.Green(), color.Blue())


# vim: encoding=utf8:
