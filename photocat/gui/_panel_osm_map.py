#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""

PanelOsmMap

rwr 3.x
Copyright (c) Karol Będkowski, 2010

This file is part of photocat

photocat is free software; you can redistribute it and/or modify it under the
terms of the GNU General Public License as published by the Free Software
Foundation, version 2.
"""

import time
import math
import cStringIO
import logging
import threading
from collections import deque

import wx
import wx.lib.newevent

from photocat.lib import maps_loader
from photocat.lib.appconfig import AppConfig


_LOG = logging.getLogger(__name__)
(TileUpdatedEvent, EVT_TILE_UPDATED) = wx.lib.newevent.NewEvent()
(PointSelectedEvent, EVT_POINT_SELECTED) = wx.lib.newevent.NewEvent()
(MapDClickEvent, EVT_MAP_DCLICK) = wx.lib.newevent.NewEvent()


class _TilesCache:
	"""docstring for TileCache"""
	def __init__(self):
		self._cache = {}
		self._lock = threading.Lock()

	def __contains__(self, key):
		with self._lock:
			return key in self._cache

	def __setitem__(self, key, value):
		with self._lock:
			self._cache[key] = value

	def __getitem__(self, key):
		with self._lock:
			return self._cache[key]

TILES_CACHE = _TilesCache()
_LOG2 = math.log(2)


def log2(x):
	return math.log(x) / _LOG2


def tileXY(lat, lon, z):
	n = pow(2, z)
	x = (lon + 180) / 360.
	y = (1 - math.log(math.tan(math.radians(lat)) + \
			1 / math.cos(math.radians(lat))) / math.pi) / 2
	return x * n, y * n


def xy2latlon(x, y, z):
	n = float(pow(2, z))
	lon = 360. * (x / n) - 180
	lat = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
	return lat, lon


def distfunc(data, x_, y_):
	return math.sqrt((data[0] - x_) ** 2 + (data[1] - y_) ** 2)


def nth_element_iter(seq, nth):
	for idx, item in enumerate(seq):
		if idx % nth == 0:
			yield item


class _DownloadThread(threading.Thread):
	def __init__(self, window, tiles_in_queue):
		threading.Thread.__init__(self)
		self.tiles_in_queue = tiles_in_queue
		self.window = window

	def run(self):
		while True:
			try:
				tile = self.tiles_in_queue.popleft()
			except IndexError:
				try:
					time.sleep(0.2)
				except:
					pass
				continue
			try:
				data = maps_loader.load_tile(*tile)
			except Exception, err:
				_LOG.exception('_MapWindow._update_map error: ' + str(err))
			else:
				if data:
					try:
						wx.PostEvent(self.window, TileUpdatedEvent(
							tile=tile, data=data))
					except TypeError:
						pass


class _RoutePouints:
	def __init__(self, points, params):
		self.points = points
		self.params = params


class _MapWindow(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SUNKEN | \
				wx.FULL_REPAINT_ON_RESIZE)
		self._data = None
		self.zoom = 0
		self.mapname = 'mapnik'
		self._tiles_on_screen = {}
		self.routes = []
		self.waypoints = []
		self._curr_center = 0
		self._update_timer = None
		self._down_tiles_queue = deque()
		self._drag_pos_start = None
		self._loading_threads = []
		self._highlight = None
		self._track_color_cb = None
		self._no_data_img = wx.Image(AppConfig().get_data_file('art/nodata.png'))\
				.ConvertToBitmap()
		self._scroll_timer = None
		size = wx.Display().GetClientArea()
		self._buffer = wx.EmptyBitmap(size.width, size.height)

		self._start_threads()

		self.Bind(wx.EVT_SIZE, self._on_size)
		self.Bind(wx.EVT_PAINT, self._on_paint)
		self.Bind(EVT_TILE_UPDATED, self._on_update_tile)
		self.Bind(wx.EVT_LEFT_DOWN, self._on_right_down)
		self.Bind(wx.EVT_LEFT_UP, self._on_right_up)

	def __del__(self):
		if self._loading_threads:
			self.destroy()

	@property
	def center(self):
		return self._curr_center

	def destroy(self):
		self._down_tiles_queue.clear()
		for thr in self._loading_threads:
			thr.join(0)
		self._loading_threads = []

	def add_waypoints(self, waypoints):
		if hasattr(waypoints[0], '__iter__'):
			self.waypoints.extend(waypoints)
		else:
			self.waypoints.append(waypoints)

	def set_routes(self, routes):
		self.routes = [_RoutePouints(point, params)
				for point, params in routes]

	def set_highlight(self, pts):
		self._highlight = pts

	def set_map(self, mapname):
		self.mapname = mapname

	def set_view(self, min_lon, min_lat, max_lon, max_lat):
		pwidth, pheight = self.GetClientSizeTuple()
		tiles_w, tiles_h = (pwidth / 256) or 5, (pheight / 256) or 5
		zoom_lat = log2(360. / abs(max_lat - min_lat))
		zoom_lon = log2(360. / abs(max_lon - min_lon)) * 2
		zoom = self.base_zoom = int(math.floor(min(zoom_lat, zoom_lon)))
		self.map_center = (max_lon + min_lon) / 2, (max_lat + min_lat) / 2
		self.show_map(self.map_center, zoom)

	def show_map(self, map_center=None, zoom=None):
		self._curr_center = map_center = map_center or self._curr_center
		zoom = zoom or self.zoom
		zoom = min(zoom, maps_loader.MAPS[self.mapname]['max_zoom'])
		self.zoom = zoom = max(zoom, maps_loader.MAPS[self.mapname]['min_zoom'])
		pwidth, pheight = self.GetClientSizeTuple()
		ctx, cty = tileXY(map_center[1], map_center[0], zoom)
		self._curr_center_offset = (int(pwidth / 2 - math.modf(ctx)[0] * 256),
				int(pheight / 2 - math.modf(cty)[0] * 256))
		self._ctile = ctx, cty = int(ctx), int(cty)
		tiles = {}
		maxn = pow(2, zoom)

		def add_valid(x, y):
			new_x, new_y = ctx + x, cty + y
			if new_x >= 0 and new_y >= 0 and new_x < maxn and new_y < maxn:
				tiles[(x, y)] = (new_x, new_y % maxn, zoom, self.mapname)

		for x in xrange(pwidth / 256 / 2 + 2):
			for y in range(pheight / 256 / 2 + 2):
				add_valid(-x, -y)
				add_valid(x, -y)
				add_valid(-x, y)
				add_valid(x, y)
		self._down_tiles_queue.clear()
		for tile in tiles.itervalues():
			if tile not in TILES_CACHE:
				self._down_tiles_queue.append(tile)
		self._tiles_on_screen = tiles
		self._do_drawing()

	def set_tracks_color_cb(self, color_cb=None):
		self._track_color_cb = color_cb

	def zoom_in(self, center=None):
		center = center or self._curr_center
		self.show_map(center, min(self.zoom + 1,
			maps_loader.MAPS[self.mapname]['max_zoom']))
		self.Refresh()

	def zoom_out(self, center=None):
		center = center or self._curr_center
		self.show_map(center, max(self.zoom - 1,
			maps_loader.MAPS[self.mapname]['min_zoom']))
		self.Refresh()

	def screen2latlon(self, x, y):
		xtile = (x - self._curr_center_offset[0]) / 256. + self._ctile[0]
		ytile = (y - self._curr_center_offset[1]) / 256. + self._ctile[1]
		lat, lon = xy2latlon(xtile, ytile, self.zoom)
		return lat, lon

	def _on_size(self, evt):
		if self._curr_center:
			self.show_map(self._curr_center, self.zoom)

	def _on_paint(self, evt):
		wx.BufferedPaintDC(self, self._buffer, wx.BUFFER_VIRTUAL_AREA)

	def _do_drawing(self):
		(pwidth, pheight) = self.GetClientSizeTuple()
		dc = wx.BufferedDC(None, self._buffer)
		dc.Clear()
		dc.BeginDrawing()
		xoffs, yofff = self._curr_center_offset
		# tiles
		for (xpos, ypos), tile in self._tiles_on_screen.iteritems():
			img = self._no_data_img
			if tile in TILES_CACHE:
				img = TILES_CACHE[tile]
			dc.DrawBitmap(img, xoffs + xpos * 256, yofff + ypos * 256)
		# rotues
		paint_rect = wx.Rect(0, 0, pwidth, pheight)
		for route in self.routes:
			pts = list(self._get_route_points(route))
			params = route.params
			pena = wx.Pen(params.get('color', wx.BLACK), params.get('width', 2),
				params.get('style', wx.SOLID))
			pen = wx.Pen(params.get('color', wx.RED), params.get('width', 3),
				params.get('style', wx.SOLID))
			pen2 = wx.Pen(params.get('color', wx.BLACK), params.get('width', 5),
				params.get('style', wx.SOLID))
			dc.SetPen(pen)
			prev_point = None
			for point, trkpt in pts:
				if prev_point and (paint_rect.Contains(prev_point) or \
						paint_rect.Contains(point)):
					# arrow
					alen = self.zoom / 2.
					if alen > 7:
						slopy = math.atan2((point.y - prev_point.y),
								(point.x - prev_point.x))
						coss, sins = math.cos(slopy), math.sin(slopy)
						dc.SetPen(pena)
						dc.DrawLine(point.x, point.y,
								point.x + int(-alen * coss - (alen * sins)),
								point.y + int(-alen * sins + (alen * coss)))
						dc.DrawLine(point.x, point.y,
								point.x + int(-alen * coss + (alen * sins)),
								point.y + int(-alen * sins - (alen * coss)))
					# arrow - end
					dc.SetPen(pen2)
					dc.DrawLine(prev_point.x, prev_point.y, point.x, point.y)
					if self._track_color_cb:
						pen.SetColour(self._track_color_cb(trkpt))
						dc.SetPen(pen)
						dc.DrawLine(prev_point.x, prev_point.y, point.x, point.y)
				prev_point = point
		# waypoints
		dc.SetPen(wx.Pen(wx.BLUE, 2, wx.SOLID))
		dc.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
				wx.FONTWEIGHT_NORMAL))
		dc.SetBrush(wx.WHITE_BRUSH)
		for wpt_pos_x, wpt_pos_y, wpt_name in self.waypoints:
			x, y = self._latlon2screen(wpt_pos_x, wpt_pos_y)
			if paint_rect.Contains((x, y)):
				sw, sh = dc.GetTextExtent(wpt_name)
				x1, y1 = x + 5, y - 15
				dc.DrawLine(x, y, x1, y1)
				dc.DrawRectangle(x1, y1, sw + 6, -sh - 6)
				dc.DrawText(wpt_name, x1 + 3, y1 - sh - 3)
		# higlight
		if self._highlight:
			hlx, hly = self._latlon2screen(self._highlight[0], self._highlight[1])
			dc.SetPen(wx.Pen(wx.BLUE, 1))
			dc.DrawLine(0, hly, pwidth, hly)
			dc.DrawLine(hlx, 0, hlx, pheight)
		# scale
		scale_with, scale_label = self._get_scale()
		dc.SetPen(wx.Pen(wx.BLACK, 2))
		dc.DrawLine(10, pheight - 10, 10 + scale_with, pheight - 10)
		dc.DrawLine(10, pheight - 12, 10, pheight - 8)
		dc.DrawLine(10 + scale_with / 2, pheight - 12, 10 + scale_with / 2,
				pheight - 8)
		dc.DrawLine(10 + scale_with, pheight - 12, 10 + scale_with, pheight - 8)
		dc.DrawText(scale_label, 15 + scale_with, pheight - 20)
		dc.EndDrawing()

	def _on_right_down(self, event):
		self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
		self.CaptureMouse()
		self._drag_pos_start = event.GetPosition()
		self._scroll_timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self._on_timer_scroll, id=self._scroll_timer.GetId())
		self._scroll_timer.Start(100)
		event.Skip()

	def _on_right_up(self, event):
		if self._scroll_timer:
			self._scroll_timer.Stop()
			self.Disconnect(self._scroll_timer.GetId())
			self._scroll_timer.Destroy()
			self._scroll_timer = None
		if self._drag_pos_start:
			drag_pos_stop = event.GetPosition()
			self._scroll_to_pos(self._drag_pos_start, drag_pos_stop)
			self._drag_pos_start = None
		self.SetCursor(wx.STANDARD_CURSOR)
		self.ReleaseMouse()
		event.Skip()

	def _on_update_tile(self, event):
		img = wx.ImageFromStream(cStringIO.StringIO(event.data))
		if img.IsOk():
			TILES_CACHE[event.tile] = img.ConvertToBitmap()
		if not self._update_timer:
			self._update_timer = wx.CallLater(250, self._on_timer_update)

	def _on_timer_update(self):
		self._update_timer = None
		self._do_drawing()
		self.Refresh()
		if len(self._down_tiles_queue):
			self._update_timer = wx.CallLater(250, self._on_timer_update)

	def _on_timer_scroll(self, evt):
		if self._drag_pos_start:
			pos = self.ScreenToClient(wx.GetMousePosition())
			self._scroll_to_pos(self._drag_pos_start, pos)
			self._drag_pos_start = pos

	def _scroll_to_pos(self, start, stop):
		n = pow(2, self.zoom)
		dx = float(start[0] - stop[0]) / n
		dy = float(start[1] - stop[1]) / n
		if dx != 0. or dy != 0.:
			new_center = self._curr_center[0] + dx, self._curr_center[1] - dy
			self.show_map(new_center, self.zoom)
			self.Refresh()

	def _latlon2screen(self, lon, lat):
		x, y = tileXY(lat, lon, self.zoom)
		x = self._curr_center_offset[0] + (x - self._ctile[0]) * 256
		y = self._curr_center_offset[1] + (y - self._ctile[1]) * 256
		return (x, y)

	def _get_route_points(self, route):
		points = route.points
		if self.zoom < 14:
			step = int(pow(1.5, 15 - self.zoom))
			_LOG.debug('_MapWindow._get_route_points step=%d', step)
			points = nth_element_iter(route.points, step)
		for pts in points:
			x, y = self._latlon2screen(pts.lon, pts.lat)
			yield wx.Point(x, y), pts

	def _start_threads(self, count=5):
		for x in xrange(count):
			thr = _DownloadThread(self, self._down_tiles_queue)
			thr.setDaemon(True)
			thr.start()
			self._loading_threads.append(thr)

	def _get_scale(self):
		width, label = maps_loader.get_map_scale(self.zoom)
		if label > 1000:
			return width, '%d km' % (label / 1000)
		return width, '%d m' % label


class PanelOsmMap(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1)
		self._highlight = None
		self._create_layout()
		self._mouse_pos = None
		self._tracks = []
		self._fill_maps()
		self._current_map = AppConfig().get('map', 'last_map', 'mapnik')
		self._panel_map.set_map(self._current_map)

	@property
	def panel(self):
		return self._panel_map

	@property
	def center_zoom(self):
		return self._panel_map.center, self._panel_map.zoom

	def destroy(self):
		self._panel_map.destroy()

	def add_track(self, track, params):
		self._tracks.append((track, params))
		min_lat = min(item.lat for data in self._tracks for item in data[0])
		min_lon = min(item.lon for data in self._tracks for item in data[0])
		max_lat = max(item.lat for data in self._tracks for item in data[0])
		max_lon = max(item.lon for data in self._tracks for item in data[0])
		self._panel_map.set_view(min_lon, min_lat, max_lon, max_lat)
		self._panel_map.set_routes(self._tracks)
		self._on_map_select(None)
		self._set_btns_status()

	def clear_waypoints(self):
		self._panel_map.waypoints = []

	def add_waypoints(self, waypoints):
		self._panel_map.add_waypoints(waypoints)

	def set_highlight(self, highlight, center=False):
		self._panel_map.set_highlight(highlight)
		self._panel_map.show_map(highlight if center else None)
		self._panel_map.Refresh()

	def show_map(self, center, zoom):
		self._panel_map.show_map(center, zoom)
		self._panel_map.Refresh()

	def set_tracks_color_cb(self, color_cb):
		self._panel_map.set_tracks_color_cb(color_cb)
		self._panel_map.show_map()
		self._panel_map.Refresh()
		self._zoom_slider.SetFocus()

	def _create_layout(self):
		main_grid = wx.BoxSizer(wx.HORIZONTAL)
		self._panel_map = _MapWindow(self)
		main_grid.Add(self._panel_map, 1, wx.EXPAND | wx.ALL, 5)
		self._zoom_slider = wx.Slider(self._panel_map, -1, 5, 10, 10, pos=(6, 6),
				size=(-1, 150), style=wx.SL_VERTICAL)
		self._cb_map = wx.Choice(self._panel_map, -1, choices=['map'],
				size=(200, -1))
		self._cb_map.Select(0)

		self.SetSizerAndFit(main_grid)
		self.Centre(wx.BOTH)

		self._cb_map.Bind(wx.EVT_CHOICE, self._on_map_select)
		self._panel_map.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
		self._panel_map.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
		self._panel_map.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)
		self._panel_map.Bind(wx.EVT_LEFT_DCLICK, self._on_map_dclick)
		self.Bind(wx.EVT_SCROLL, self._on_zoom_slider, self._zoom_slider)
		self.Bind(wx.EVT_SIZE, self._on_size)

	def _on_mouse_wheel(self, evt):
		x, y = evt.GetPosition()
		lat, lon = self._panel_map.screen2latlon(x, y)
		center = lon, lat
		if evt.GetWheelRotation() < 0:
			self._on_btn_zoom_out(None, center)
		else:
			self._on_btn_zoom_in(None, center)

	def _on_btn_zoom_out(self, _evt, center=None):
		self._panel_map.zoom_out(center)
		self._set_btns_status()

	def _on_btn_zoom_in(self, _evt, center=None):
		self._panel_map.zoom_in(center)
		self._set_btns_status()

	def _on_map_select(self, _evt):
		map_name = self._cb_map.GetClientData(self._cb_map.GetSelection())
		self._current_map = map_name
		AppConfig().set('map', 'last_map', map_name)
		self._panel_map.set_map(map_name)
		self._panel_map.show_map()
		self._panel_map.Refresh()
		self._set_btns_status()

	def _on_mouse_down(self, evt):
		self._mouse_pos = evt.GetPosition()
		evt.Skip()

	def _on_mouse_up(self, evt):
		if evt.GetPosition() == self._mouse_pos:
			x, y = evt.GetX(), evt.GetY()
			lat, lon = self._panel_map.screen2latlon(x, y)
			pixelzoom = 180. / pow(2, self._panel_map.zoom)
			wx.PostEvent(self, PointSelectedEvent(lat=lat, lon=lon,
					pixels=pixelzoom))
		self._mouse_pos = None
		evt.Skip()

	def _on_map_dclick(self, evt):
		x, y = evt.GetX(), evt.GetY()
		lat, lon = self._panel_map.screen2latlon(x, y)
		pixelzoom = 180. / pow(2, self._panel_map.zoom)
		wx.PostEvent(self, MapDClickEvent(lat=lat, lon=lon,
			zoom=self._panel_map.zoom, pixelzoom=pixelzoom))
		evt.Skip()

	def _on_size(self, evt):
		wx.CallAfter(self._do_layout)
		evt.Skip()

	def _on_zoom_slider(self, evt):
		zoom = evt.GetPosition()
		self._panel_map.show_map(zoom=zoom)
		self._panel_map.Refresh()

	def _set_btns_status(self):
		map_ = maps_loader.MAPS[self._current_map]
		min_zoom, max_zoom = map_['min_zoom'], map_['max_zoom']
		self._zoom_slider.SetRange(min_zoom, max_zoom)
		self._zoom_slider.SetValue(self._panel_map.zoom)

	def _fill_maps(self):
		self._cb_map.Clear()
		to_sel = 0
		prev_sel_map = AppConfig().get('map', 'last_map', 'mapnik')
		maps = sorted((vmap['name'], key)
				for key, vmap in maps_loader.MAPS.iteritems())
		for idx, (mapname, key) in enumerate(maps):
			self._cb_map.Append(mapname, key)
			if key == prev_sel_map:
				to_sel = idx
		self._cb_map.SetSelection(to_sel)
		self._current_map = prev_sel_map
		self._cb_map.Fit()

	def _do_layout(self):
		self._cb_map.SetPosition((self._panel_map.GetSizeTuple()[0] - \
				self._cb_map.GetSizeTuple()[0] - 6, 6))
