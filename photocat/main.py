#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""
Main class App


Photo Catalog v 1.0  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog

photocat is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.

photocat is distributed in the hope that it will be useful, but WITHOUT ANY
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
except ImportError:
	pass
else:
	psyco.full()


import os
import sys
import gettext
import locale
import logging
import optparse

from photocat.lib import appconfig
from photocat.lib.logging_setup import logging_setup


##########################################################################

reload(sys)
try:
	sys.setappdefaultencoding("utf-8")		# pylint: disable-msg=E1101
except AttributeError:
	sys.setdefaultencoding("utf-8")		# pylint: disable-msg=E1101


def _show_version(ption, opt_str, value, parser, *args, **kwargs):
	from photocat import version
	print version.INFO
	exit(0)


def _parse_opt():
	p = optparse.OptionParser(usage="usage: %prog [options] [collection] ...")
	p.add_option('--debug', '-d', action="store_true", default=False,
			help='enable debug messages')
	p.add_option('--version', action="callback", callback=_show_version,
			help='show information about application version')
	return  p.parse_args()

OPTIONS, ARGUMENTS = _parse_opt()

# logowanie
DEBUG = OPTIONS.debug
logging_setup('photocat.log', DEBUG)

_LOG = logging.getLogger(__name__)


def _setup_locale():
	''' setup locales and gettext '''
	use_home_dir = sys.platform != 'win32'
	app_config = appconfig.AppConfig('photocat.cfg', __file__,
			use_home_dir=use_home_dir, app_name='photocat')
	locales_dir = app_config.locales_dir
	package_name = 'photocat'
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

from photocat.lib.wxtools.logging_wx import logging_setup_wx
from photocat.lib.wxtools import iconprovider


def run():
	''' Run application '''
	logging_setup_wx()

	_LOG.info('run')
	app_config = appconfig.AppConfig()
	app_config.load()

	_LOG.info('run: starting app...')
	app = wx.PySimpleApp(0)
	wx.InitAllImageHandlers()

	iconprovider.init_icon_cache(None, os.path.join(app_config.data_dir, 'art'))

	from photocat.gui.wndmain import WndMain

	wnd = WndMain(app, DEBUG)
	wnd.Show(True)
	app.SetTopWindow(wnd)

	for arg in ARGUMENTS:
		wnd.open_file(arg)

	_LOG.info('run: starting app main loop...')
	app.MainLoop()

	_LOG.info('run: ending...')
	app_config.save()
	del app

	_LOG.info('run: end')


# vim: ff=unix: encoding=utf8:
