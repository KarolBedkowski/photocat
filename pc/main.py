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

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2006'
__revision__ = '$Id$'


try:
	# pylint: disable-msg=F0401
	import psyco
except ImportError, err:
	print 'No psyco........ (%s)' % str(err)
else:
	psyco.full()


import os
import sys
import gettext
import locale
import logging

from pc.lib import appconfig
from pc.lib.logging_setup import logging_setup


##########################################################################

reload(sys)
try:
	sys.setappdefaultencoding("utf-8")	# pylint: disable-msg=E1101
except AttributeError:
	sys.setdefaultencoding("utf-8")	# pylint: disable-msg=E1101

# logowanie
DEBUG = sys.argv.count('-d') > 0
if DEBUG:
	sys.argv.remove('-d')
logging_setup('pc.log', DEBUG)

_LOG = logging.getLogger(__name__)


def _setup_locale():
	''' setup locales and gettext '''
	use_home_dir = sys.platform != 'win32'
	app_config = appconfig.AppConfig('pc.cfg', __file__, use_home_dir=use_home_dir,
			app_name='pc')
	locales_dir = app_config.locales_dir
	package_name = 'pc'
	_LOG.info('run: locale dir: %s' % locales_dir)
	try:
		locale.bindtextdomain(package_name, locales_dir)
		locale.bind_textdomain_codeset(package_name, "UTF-8")
	except:
		pass
	default_locale = locale.getdefaultlocale()
	locale.setlocale(locale.LC_ALL, '')
	if sys.platform == 'win32':
		os.environ['LC_ALL'] = os.environ.get('LC_ALL') or default_locale[0]
	gettext.install(package_name, localedir=locales_dir, unicode=True,
			names=("ngettext",))
	gettext.bindtextdomain(package_name, locales_dir)
	gettext.bind_textdomain_codeset(package_name, "UTF-8")

	_LOG.info('locale: %s' % str(locale.getlocale()))


_setup_locale()


##########################################################################

if not appconfig.is_frozen():
	try:
		import wxversion
		try:
			wxversion.select('2.8')
		except wxversion.AlreadyImportedError:
			pass
	except ImportError, err:
		print 'No wxversion.... (%s)' % str(err)

import wx

from pc.icons				import icons
from pc.lib.wxtools.logging_wx	import logging_setup_wx

##########################################################################


class App(wx.App):
	""" wx App class """

	def OnInit(self):	# pylint: disable-msg=C0103
		""" OnInit """

		_LOG.info('App.OnInit')

		_LOG.info('App.OnInit: preparing iconprovider...')
		from pc.lib.wxtools.iconprovider import IconProvider
		IconProvider(icons)

		from pc.gui.wndmain	import WndMain
		wnd = WndMain(self, DEBUG)
		wnd.Show(True)
		self.SetTopWindow(wnd)

		for arg in sys.argv[1:]:
			if not arg.startswith('-'):
				wnd.open_file(arg)

		return True

	def OnExceptionInMainLoop(self):	# pylint: disable-msg=C0103
		''' OnExceptionInMainLoop '''
		_LOG.warn('OnExceptionInMainLoop')
		super(App, self).OnExceptionInMainLoop()

	def OnUnhandledException(self):	# pylint: disable-msg=C0103
		'''OnUnhandledException '''
		_LOG.warn('OnUnhandledException')
		super(App, self).OnUnhandledException()

	def OnFatalException(self):	# pylint: disable-msg=C0103
		''' OnFatalException '''
		_LOG.warn('OnFatalException')
		super(App, self).OnFatalException()


##########################################################################


def run():
	''' Run application '''
	logging_setup_wx()

	_LOG.info('run')
	app_config = appconfig.AppConfig()
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
