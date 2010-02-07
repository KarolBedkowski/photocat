# -*- coding: utf-8 -*-
# pylint: disable-msg=C0103
"""
Konfiguracja programu


 kPyLibs.appconfig
 Copyright (c) Karol Będkowski, 2007

 This file is part of kPyLibs

 kPyLibs is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.

 SAG is distributed in the hope that it will be useful, but WITHOUT ANY
 WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
 FOR A PARTICULAR PURPOSE.	See the GNU General Public License for more
 details.

 You should have received a copy of the GNU General Public License along
 with this program; if not, write to the Free Software Foundation, Inc.,
 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""


__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2006'
__revision__	= '$Id$'

__all__			= []


import sys
import os
import imp
import logging
_LOG = logging.getLogger(__name__)

from itertools import izip
import ConfigParser


from pc.lib.singleton import Singleton


class AppConfig(Singleton):
	''' konfiguracja aplikacji '''

	def _init(self, filename, main_file_path=None, use_home_dir=False, app_name=None):
		_LOG.debug('__init__(%s)' % filename)

		self.main_is_frozen = self._main_is_frozen()
		self.main_dir = self._main_dir()
		self.main_file_path = main_file_path

		if use_home_dir and app_name is not None:
			self.config_path = os.path.join(os.path.expanduser('~'), '.config', app_name)
			if not os.path.exists(self.config_path):
				try:
					os.makedirs(self.config_path)

				except:
					_LOG.exception('Error creating config directory: %s' % self.config_path)
					self.config_path = self.main_dir

		else:
			self.config_path = self.main_dir

		self._filename = os.path.join(self.config_path, filename)
		self._config = ConfigParser.SafeConfigParser()

		self.clear()

		_LOG.debug('AppConfig.__init__: frozen=%s, main_dir=%s, config=%s' %
				(self.main_is_frozen, self.main_dir, self._filename))


	def clear(self):
		self.last_open_files = []
		map(self._config.remove_section, self._config.sections())
		self._runtime_params = {}


	###########################################################################

	# dostęp do _runtime_params
	def __len__(self):
		return self._runtime_params.__len__()

	def __getitem__(self, key):
		return self._runtime_params.__getitem__(key)

	def __setitem__(self, key, value):
		self._runtime_params.__setitem__(key, value)

	def __delitem__(self, key):
		self._runtime_params.__delitem__(key)

	def __iter__(self):
		self._runtime_params.__iter__()


	def _get_debug(self):
		return self._runtime_params.get('DEBUG', False)

	def _set_debug(self, value):
		self._runtime_params['DEBUG'] = value

	debug = property(_get_debug, _set_debug)


	###########################################################################


	def load(self):
		if os.path.exists(self._filename):
			_LOG.debug('load')
			cfile = None
			try:
				cfile = open(self._filename, 'r')
				self._config.readfp(cfile)

			except StandardError:
				_LOG.exception('load error')

			else:
				self._after_load(self._config)

			if cfile is not None:
				cfile.close()

			_LOG.debug('load end')


	def save(self):
		_LOG.debug('save')

		self._before_save(self._config)

		cfile = None
		try:
			cfile = open(self._filename, 'w')
			self._config.write(cfile)

		except StandardError:
			_LOG.exception('save error')

		if cfile is not None:
			cfile.close()

		_LOG.debug('save end')


	def add_last_open_file(self, filename):
		if filename in self.last_open_files:
			self.last_open_files.remove(filename)

		self.last_open_files.insert(0, filename)
		self.last_open_files = self.last_open_files[:7]


	@property
	def locales_dir(self):
		if self.main_is_frozen:
			locales_dir = os.path.join(self.main_dir, 'locale')

		else:
			if self.main_file_path is None:
				path = os.path.join(os.path.dirname(__file__), '..')

			else:
				path = os.path.dirname(self.main_file_path)

			locales_dir = os.path.join( path ,  'locale')

		return locales_dir


	def _main_is_frozen(self):
		return (hasattr(sys, "frozen")		# new py2exe
				or hasattr(sys, "importers")	# old py2exe
				or imp.is_frozen("__main__"))	# tools/freeze


	def _main_dir(self):
		if self.main_is_frozen:
			return os.path.abspath(os.path.dirname(sys.executable))

		return os.path.abspath(os.path.dirname(sys.argv[0]))


	def _after_load(self, config):
		self.last_open_files = [ val[1] for val in sorted(config.items('last_files')) ]


	def _before_save(self, config):
		if config.has_section('last_files'):
			config.remove_section('last_files')

		config.add_section('last_files')

		last_open_files = self.last_open_files[:7]
		for fidn, fname in enumerate(last_open_files):
			config.set('last_files', 'file%d' % fidn, fname)


	def get(self, section, key, default=None):
		if self._config.has_section(section) and self._config.has_option(section, key):
			try:
				return eval(self._config.get(section, key))

			except:
				_LOG.exception('AppConfig.get(%s, %s, %r)' % (section, key, default))

		return default


	def get_items(self, section):
		if self._config.has_section(section):
			try:
				items = self._config.items(section)
				result = tuple(( (key, eval(val)) for key, val in items ))
				return result

			except:
				_LOG.exception('AppConfig.get(%s)' % section)

		return None


	def set(self, section, key, val):
		if not self._config.has_section(section):
			self._config.add_section(section)

		self._config.set(section, key, repr(val))


	def set_items(self, section, key, items):
		config = self._config
		self._remove_and_create_section(config, section)

		for idx, item in enumerate(items):
			config.set(section, '%s%05d' % (key, idx), repr(item))


	def _remove_and_create_section(self, config, section):
		if config.has_section(section):
			config.remove_section(section)

		config.add_section(section)



if __name__ == '__main__':
	acfg = AppConfig('test.cfg')
	acfg.last_open_files = ['1', '2', 'q', 'w']
	print id(acfg), acfg.last_open_files
	acfg.save()

	acfg.clear()
	print id(acfg), acfg.last_open_files

	acfg = AppConfig('test.cfg')
	acfg.load()
	print id(acfg), acfg.last_open_files



# vim: encoding=utf8: ff=unix:
