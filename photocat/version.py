# -*- coding: utf-8 -*-
"""
Licence and version informations.
"""

__author__ = 'Karol Będkowski'

try:
	_('photocat')
except NameError:
	_ = lambda x: x


SHORTNAME = 'photocat'
NAME = _("Photo Catalog")
VERSION = '1.9.0a3'
VERSION_INFO = (1, 9, 0, 'alfa', 3)
RELEASE = '2010-10-16'
DESCRIPTION = _('''Photo collection manager''')
DEVELOPERS = '''Karol Będkowski'''
TRANSLATORS = '''Karol Będkowski'''
COPYRIGHT = 'Copyright (C) Karol Będkowski, 2004-2010'
LICENSE = _('''\
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.


Also please check LICENCE files from distribution.
''')


INFO = _("""\
%(name)s version %(version)s (%(release)s)
%(copyright)s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

For details please see COPYING file.
""") % dict(name=NAME, version=VERSION, copyright=COPYRIGHT, release=RELEASE)
