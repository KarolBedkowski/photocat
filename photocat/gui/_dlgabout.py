#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0901, R0904
"""
Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2008

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006-2008'
__revision__ = '$Id$'

__all__ = ['show_about_box']


import wx


def show_about_box(parent):
	from photocat import version

	info = wx.AboutDialogInfo()
	info.SetName(version.NAME)
	info.SetVersion(version.VERSION)
	info.SetCopyright(version.COPYRIGHT)
	info.SetDevelopers(version.DEVELOPERS.splitlines())
	info.SetTranslators(version.TRANSLATORS.splitlines())
	info.SetLicense(version.LICENSE)
	info.SetDescription(version.DESCRIPTION + "\n" + version.RELEASE)
	wx.AboutBox(info)





# vim: encoding=utf8:
