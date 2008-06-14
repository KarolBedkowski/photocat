#!/usr/bin/python2.5
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
Main class App


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


try:
	import psyco
	psyco.full()
except Exception, err:
	print 'No psyco........ (%s)' % str(err)


import os
import sys
import imp

reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except Exception, _:
	sys.setdefaultencoding("utf-8")


##########################################################################
# logowanie
import logging
from kpylibs.logging_setup	import logging_setup
from kpylibs.logging_wx		import logging_setup_wx


debug = sys.argv.count('-d') > 0
if debug:
	sys.argv.remove('-d')
debug =  debug or __debug__
logging_setup('pc.log', debug)

_LOG = logging.getLogger(__name__)


##########################################################################


import wx

from kpylibs.appconfig		import AppConfig

from pc.icons				import icons



class App(wx.App):
	""" wx App class """

	def OnInit(self):
		""" OnInit """

		_LOG.info('App.OnInit')
		self.debug = debug

		app_config = AppConfig()
		locales_dir = app_config.locales_dir
		_LOG.info('run: locale dir: %s' % locales_dir)
		self.locale = locale = wx.Locale(wx.LANGUAGE_DEFAULT)
		locale.AddCatalogLookupPathPrefix(locales_dir)		
		locale.AddCatalog('wxstd')
		locale.AddCatalog('kpylibs')
		locale.AddCatalog('pc')
		_LOG.info('locale: %s' % locale.GetName())

		from kpylibs.iconprovider	import IconProvider
	
		_LOG.info('App.OnInit: preparing iconprovider...')
		icon_provider = IconProvider(icons)

		from pc.gui.wndmain	import WndMain
		wnd = WndMain(self, self.debug)
		wnd.Show(True)
		self.SetTopWindow(wnd)

		argv = sys.argv
		if len(argv) > 1:
			wnd._open_file(argv[-1])

		return True

	def OnExceptionInMainLoop(self):
		_LOG.warn('OnExceptionInMainLoop')
		wx.App.OnExceptionInMainLoop(self)

	def OnUnhandledException(self):
		_LOG.warn('OnUnhandledException')
		wx.App.OnUnhandledException(self)

	def OnFatalException(self):
		_LOG.warn('OnFatalException')
		wx.App.OnFatalException(self)


##########################################################################


def run():

	logging_setup_wx()

	_LOG.info('run')
	use_home_dir = wx.Platform != '__WXMSW__'
	app_config = AppConfig('pc.cfg', __file__, use_home_dir=use_home_dir, app_name='pc')
	app_config.load()

	_LOG.info('run: starting app...')
	app = App(None)

	_LOG.info('run: starting app main loop...')
	app.MainLoop()

	_LOG.info('run: ending...')
	app_config.save()
	del app

	_LOG.info('run: end')




# vim: ff=unix: encoding=utf8:
