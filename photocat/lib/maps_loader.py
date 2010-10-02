# -*- coding: utf-8 -*-

"""
rwr 3.x
Copyright (c) Karol Będkowski, 2010

This file is part of rwr3

rwr3 is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.
"""

import os
import os.path
import time
import urllib2
import logging


_LOG = logging.getLogger(__name__)

MAPS = {
	"mapnik": {
		'name': 'OpenStreetMap',
		'url': "http://tile.openstreetmap.org/mapnik/%(z)d/%(x)d/%(y)d.png",
		"cache": os.path.expanduser('~/Maps/OSM/'),
		'max_zoom': 17,
		'min_zoom': 2,
		'ext': 'png',
	},
	"ocm": {
		'name': 'OpenCycleMap',
		'url': "http://a.andy.sandbox.cloudmade.com/tiles/cycle/" + \
				"%(z)d/%(x)d/%(y)d.png",
		'cache': os.path.expanduser('~/Maps/opencyclemap/'),
		'max_zoom': 17,
		'min_zoom': 2,
		'ext': 'png',
	},
	"google_maps": {
		'name': 'Google Maps',
		'url': "http://mt%(s)d.google.com/vt/lyrs=m@132&x=%(x)d&y=%(y)d" + \
				"&z=%(z)d&s=Gali/",
		'cache': os.path.expanduser('~/Maps/google_maps/'),
		'max_zoom': 17,
		'min_zoom': 2,
		'ext': 'png',
		'num_servers': 4,
	},
	"google_sat": {
		'name': 'Google Sat',
		'url': "http://khm%(s)d.google.com/kh/v=69&x=%(x)d&y=%(y)d&z=%(z)d" + \
				"&s=Galile&lowres=1",
		'cache': os.path.expanduser('~/Maps/google_sat/'),
		'max_zoom': 17,
		'min_zoom': 2,
		'ext': 'jpg',
		'num_servers': 4,
	},
	"google_terain": {
		'name': 'Google Terain',
		'url': "http://mt%(s)d.google.com/vt/lyrs=t@125,r@132&x=%(x)d&y=%(y)d" + \
				"&z=%(z)d&s=Gali/",
		'cache': os.path.expanduser('~/Maps/google_terain/'),
		'max_zoom': 15,
		'min_zoom': 2,
		'ext': 'png',
		'num_servers': 4,
	},
	"emapi": {
		'name': 'Emapi.pl',
		'url': "http://emapi.pl/Default.aspx?tileX=%(x)d&tileY=%(y)d" + \
				"&zoom=%(z)d&layer=std&fun=GetMap&userID=pasat",
		'cache': os.path.expanduser('~/Maps/emapi/'),
		'max_zoom': 19,
		'min_zoom': 2,
		'ext': 'png',
		'req_prop': [
				("Cookie", "currentView="),
				("Referer", "http://emapi.pl/?referer="),
		]
	},
	'ovi': {
		'name': 'Ovi Nokia/Maps',
		'url': 'http://maptile.maps.svc.ovi.com/maptiler/maptile/newest/' + \
				'normal.day/%(z)d/%(x)d/%(y)d/256/png8?token=...' + \
				'&referer=maps.ovi.com',
		'cache': os.path.expanduser('~/Maps/ovi/'),
		'ext': 'png',
		'max_zoom': 18,
		'min_zoom': 2,
	},
}

_MAP_SCALES = {0: (128, 20000000),
		1: (128, 10000000),
		2: (128, 5000000),
		3: (128, 2500000),
		4: (102, 1000000),
		5: (102, 500000),
		6: (82, 200000),
		7: (82, 100000),
		8: (82, 50000),
		9: (98, 30000),
		10: (130, 20000),
		11: (130, 10000),
		12: (130, 5000),
		13: (104, 2000),
		14: (104, 1000),
		15: (104, 500),
		16: (104, 250),
		17: (84, 100),
}

_OSM_GPX_UPLOAD_URL = "http://api.openstreetmap.org/api/0.6/gpx/create"

_LAST_USED_SERVER = {}


def get_tile_url(mapname, x, y, z):
	map_ = MAPS[mapname]
	server = _LAST_USED_SERVER.get(mapname, 0) + 1
	if server >= map_.get('num_servers', 0):
		server = 0
	_LAST_USED_SERVER[mapname] = server
	zoom = max(min(z, map_['max_zoom']), map_['min_zoom'])
	return map_['url'] % dict(x=x, y=y, z=zoom, s=server)


def load_tile(x, y, zoom, map_='ocm'):
	tile_path = os.path.join(MAPS[map_].get('cache',
			os.path.expanduser('~/Maps/' + map_)), str(zoom), str(x),
			str(y) + '.' + MAPS[map_]['ext'])
	data = None
	if os.path.exists(tile_path):
		if os.path.getmtime(tile_path) > time.time() - 2592000 and \
				os.path.getsize(tile_path) > 0:
			try:
				with open(tile_path, 'rb') as tile_file:
					data = tile_file.read()
			except IOError:
				_LOG.exception('load_tile: open title %d, %d, %d error',
						x, y, zoom)
	if not data:
		_LOG.info('load_tile: downloading %d,%d,%d' % (x, y, zoom))
		data = None
		for try_no in xrange(3):
			try:
				url = get_tile_url(map_, x, y, zoom)
				req = urllib2.Request(url)
				_LOG.debug('load_tile: %s', url)
				req_prop = MAPS[map_].get('req_prop')
				if req_prop:
					for key, val in req_prop:
						req.add_header(key, val)
				img = urllib2.urlopen(req)
				if img.getcode() == 200:
					if img.info().type in ('image/png', 'image/jpeg'):
						data = img.read()
					break
			except:
				_LOG.exception('load_tile: load title %d, %d, %d error', x, y,
						zoom)
				time.sleep(1)
				_LOG.info('load_tile: downloading %d,%d,%d try %d', x, y,
						zoom, try_no)
		if data:
			tile_dir = os.path.dirname(tile_path)
			try:
				os.makedirs(tile_dir)
			except OSError:
				pass
			with open(tile_path, 'wb') as tile_file:
				tile_file.write(data)
		_LOG.info('load_tile: downloading %d,%d,%d success (%d)', x, y, zoom,
				len(data or ''))
	return data or None


def get_map_scale(zoom):
	return _MAP_SCALES[zoom]
