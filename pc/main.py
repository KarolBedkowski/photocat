#!/usr/bin/python
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
except ImportError, err:
	print 'No psyco........ (%s)' % str(err)
else:
	psyco.full()


import sys
import imp

reload(sys)
try:
	sys.setappdefaultencoding("utf-8")
except:
	sys.setdefaultencoding("utf-8")


def _is_frozen():
	return (hasattr(sys, "frozen")		# new py2exe
			or hasattr(sys, "importers")	# old py2exe
			or imp.is_frozen("__main__"))	# tools/freeze

if not _is_frozen():
	try:
		import wxversion
		wxversion.select('2.8')
	except ImportError, err:
		print 'No wxversion.... (%s)' % str(err)


##########################################################################
# logowanie
import logging
from kabes.tools.logging_setup	import logging_setup
from kabes.wxtools.logging_wx	import logging_setup_wx


DEBUG = sys.argv.count('-d') > 0
if DEBUG:
	sys.argv.remove('-d')
logging_setup('pc.log', DEBUG)

_LOG = logging.getLogger(__name__)


##########################################################################

import wx

from kabes.tools.appconfig	import AppConfig
from kabes.wxtools			import setup_locale

from pc.icons				import icons



class App(wx.App):
	""" wx App class """

	def OnInit(self):
		""" OnInit """

		_LOG.info('App.OnInit')

		app_config = AppConfig()
		locales_dir = app_config.locales_dir
		_LOG.info('run: locale dir: %s' % locales_dir)
		self.locale = locale = wx.Locale(wx.LANGUAGE_DEFAULT)
		locale.AddCatalogLookupPathPrefix(locales_dir)
		locale.AddCatalog('wxstd')
		locale.AddCatalog('pc')

		setup_locale(locale)
		
		_LOG.info('locale: %s' % locale.GetName())

		from kabes.wxtools.iconprovider	import IconProvider

		_LOG.info('App.OnInit: preparing iconprovider...')
		icon_provider = IconProvider(icons)

		from pc.gui.wndmain	import WndMain
		wnd = WndMain(self, DEBUG)
		wnd.Show(True)
		self.SetTopWindow(wnd)

		for arg in sys.argv[1:]:
			if not arg.startswith('-'):
				wnd._open_file(arg)

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
	app_config = AppConfig('pc.cfg', __file__, use_home_dir=use_home_dir, 
			app_name='pc')
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
