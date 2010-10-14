#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable-msg=R0904
"""

PanelOsmMap

rwr 3.x
Copyright (c) Karol Będkowski, 2010

This file is part of rwr3

rwr3 is free software; you can redistribute it and/or modify it under the
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


def log2(x):
	return math.log(x) / math.log(2)


def tileXY(lat, lon, z):
	n = pow(2, z)
	x = (lon + 180) / 360
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
		self.screen_points = []


class _MapWindow(wx.Panel):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, wx.ID_ANY, style=wx.BORDER_SUNKEN | \
				wx.FULL_REPAINT_ON_RESIZE)
		self._data = None
		self._zoom = 0
		self.mapname = 'mapnik'
		self._tiles_on_screen = {}
		self._routes = []
		self._waypoints = []
		self._curr_center = 0
		self._update_timer = None
		self._down_tiles_queue = deque()
		self._drag_pos_start = None
		self._loading_threads = []
		self._highlight = None
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
	def zoom(self):
		return self._zoom

	def destroy(self):
		self._down_tiles_queue.clear()
		for thr in self._loading_threads:
			thr.join(0)
		self._loading_threads = []

	def add_waypoints(self, waypoints):
		if hasattr(waypoints[0], '__iter__'):
			self._waypoints.extend(waypoints)
		else:
			self._waypoints.append(waypoints)

	def set_routes(self, routes):
		self._routes = [_RoutePouints(point, params)
				for point, params in routes]

	def set_highlight(self, pts):
		self._highlight = pts

	def set_map(self, mapname):
		self.mapname = mapname
		self.show_map()
		self.Refresh()

	def set_view(self, min_lon, min_lat, max_lon, max_lat):
		pwidth, pheight = self.GetClientSizeTuple()
		tiles_w, tiles_h = (pwidth / 256 + 2) or 5, (pheight / 256 + 2) or 5
		zoom_lat = log2(360. / abs(max_lat - min_lat)) + log2(tiles_h)
		zoom_lon = log2(360. / abs(max_lon - min_lon)) + log2(tiles_w)
		zoom = self.base_zoom = int(math.floor(min(zoom_lat, zoom_lon)))
		self.map_center = (max_lon + min_lon) / 2, (max_lat + min_lat) / 2
		self.show_map(self.map_center, zoom)

	def show_map(self, map_center=None, zoom=None):
		self._curr_center = map_center = map_center or self._curr_center
		zoom = zoom or self._zoom
		zoom = min(zoom, maps_loader.MAPS[self.mapname]['max_zoom'])
		self._zoom = zoom = max(zoom, maps_loader.MAPS[self.mapname]['min_zoom'])
		pwidth, pheight = self.GetClientSizeTuple()
		ctx, cty = tileXY(map_center[1], map_center[0], zoom)
		self._curr_center_offset = (int(pwidth / 2 - math.modf(ctx)[0] * 256),
				int(pheight / 2 - math.modf(cty)[0] * 256))
		self._ctile = ctx, cty = int(ctx), int(cty)
		tiles = {}
		for x in xrange(pwidth / 256 / 2 + 2):
			for y in range(pheight / 256 / 2 + 2):
				tiles[(-x, -y)] = (ctx - x, cty - y, zoom, self.mapname)
				tiles[(x, -y)] = (ctx + x, cty - y, zoom, self.mapname)
				tiles[(-x, y)] = (ctx - x, cty + y, zoom, self.mapname)
				tiles[(x, y)] = (ctx + x, cty + y, zoom, self.mapname)
		self._down_tiles_queue.clear()
		for tile in tiles.itervalues():
			if tile not in TILES_CACHE:
				self._down_tiles_queue.append(tile)
		self._tiles_on_screen = tiles
		self._do_drawing()

	def find_point_on_xy(self, x, y):
		if not self._routes:
			return None
		point = min((distfunc(data, x, y), data[2])
				for route in self._routes
				for data in route.screen_points)
		return point[1] if point[0] < 50 else None

	def zoom_in(self, center=None):
		center = center or self._curr_center
		self.show_map(center, min(self._zoom + 1,
			maps_loader.MAPS[self.mapname]['max_zoom']))
		self.Refresh()

	def zoom_out(self, center=None):
		center = center or self._curr_center
		self.show_map(center, max(self._zoom - 1,
			maps_loader.MAPS[self.mapname]['min_zoom']))
		self.Refresh()

	def screen2latlon(self, x, y):
		xtile = (x - self._curr_center_offset[0]) / 256. + self._ctile[0]
		ytile = (y - self._curr_center_offset[1]) / 256. + self._ctile[1]
		lat, lon = xy2latlon(xtile, ytile, self._zoom)
		return lon, lat

	def _on_size(self, evt):
		if self._curr_center:
			self.show_map(self._curr_center, self._zoom)

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
		for route in self._routes:
			pts = list(self._get_route_points(route))
			params = route.params
			dc.SetPen(wx.Pen(params.get('color', wx.RED), params.get('width', 3),
				params.get('style', wx.SOLID)))
			dc.DrawLines(pts)
			for point in pts:
				dc.DrawCircle(point.x - 1, point.y - 1, 2)
		# waypoints
		dc.SetPen(wx.Pen(wx.BLUE, 2, wx.SOLID))
		dc.SetFont(wx.Font(7, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
				wx.FONTWEIGHT_NORMAL))
		for wpt_pos_x, wpt_pos_y, wpt_name in self._waypoints:
			x, y = self._latlon2screen(wpt_pos_x, wpt_pos_y)
			sw, sh = dc.GetTextExtent(wpt_name)
			dc.DrawLine(x, y, x + 5, y - 15)
			dc.DrawLine(x + 5, y - 15, x + sw + 8, y - 15)
			dc.DrawText(wpt_name, x + 6, y - 15 - sh)
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
		n = pow(2, self._zoom)
		dx = float(start[0] - stop[0]) / n
		dy = float(start[1] - stop[1]) / n
		if dx != 0. or dy != 0.:
			new_center = self._curr_center[0] + dx, self._curr_center[1] - dy
			self.show_map(new_center, self._zoom)
			self.Refresh()

	def _latlon2screen(self, lon, lat):
		x, y = tileXY(lat, lon, self._zoom)
		x = self._curr_center_offset[0] + (x - self._ctile[0]) * 256
		y = self._curr_center_offset[1] + (y - self._ctile[1]) * 256
		return (x, y)

	def _get_route_points(self, route):
		route.screen_points = []
		for pts in route.points:
			x, y = self._latlon2screen(pts.lon, pts.lat)
			route.screen_points.append((x, y, pts))
			yield wx.Point(x, y)

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
		self._waypoints = []
		self._fill_maps()
		self._current_map = None

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

	def add_waypoints(self, waypoints):
		self._panel_map.add_waypoints(waypoints)

	def set_highlight(self, highlight, center=False):
		self._panel_map.set_highlight(highlight)
		self._panel_map.show_map(highlight if center else None)
		self._panel_map.Refresh()

	def show_map(self, center, zoom):
		self._panel_map.show_map(center, zoom)
		self._panel_map.Refresh()

	def _create_layout(self):
		main_grid = wx.BoxSizer(wx.HORIZONTAL)
		self._panel_map = _MapWindow(self)
		main_grid.Add(self._panel_map, 1, wx.EXPAND | wx.ALL, 5)
		button_sizer = wx.BoxSizer(wx.VERTICAL)
		button_sizer.Add(wx.Button(self, wx.ID_ZOOM_IN), 0, wx.EXPAND)
		button_sizer.Add((6, 6))
		button_sizer.Add(wx.Button(self, wx.ID_ZOOM_OUT), 0, wx.EXPAND)
		button_sizer.Add((12, 12))
		button_sizer.Add(wx.StaticText(self, -1, _("Map")))
		button_sizer.Add((3, 3))
		self._cb_map = wx.Choice(self, -1, choices=['map'])
		self._cb_map.Select(0)
		button_sizer.Add(self._cb_map, 0, wx.LEFT, 6)
		main_grid.Add(button_sizer, 0, wx.EXPAND | wx.ALL, 5)

		self.SetSizerAndFit(main_grid)
		self.Centre(wx.BOTH)

		wx.EVT_BUTTON(self, wx.ID_ZOOM_IN, self._on_btn_zoom_in)
		wx.EVT_BUTTON(self, wx.ID_ZOOM_OUT, self._on_btn_zoom_out)
		self._cb_map.Bind(wx.EVT_CHOICE, self._on_map_select)
		self._panel_map.Bind(wx.EVT_LEFT_DOWN, self._on_mouse_down)
		self._panel_map.Bind(wx.EVT_LEFT_UP, self._on_mouse_up)
		self._panel_map.Bind(wx.EVT_MOUSEWHEEL, self._on_mouse_wheel)

	def _on_mouse_wheel(self, evt):
		x, y = evt.GetPosition()
		center = self._panel_map.screen2latlon(x, y)
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
		self._set_btns_status()

	def _on_mouse_down(self, evt):
		self._mouse_pos = evt.GetPosition()
		evt.Skip()

	def _on_mouse_up(self, evt):
		if evt.GetPosition() == self._mouse_pos:
			x, y = evt.GetX(), evt.GetY()
			point = self._panel_map.find_point_on_xy(x, y)
			if point:
				wx.PostEvent(self, PointSelectedEvent(point=point))
		self._mouse_pos = None
		evt.Skip()

	def _set_btns_status(self):
		map_ = maps_loader.MAPS[self._current_map]
		min_zoom, max_zoom = map_['min_zoom'], map_['max_zoom']
		self.FindWindowById(wx.ID_ZOOM_OUT).Enable(self._panel_map.zoom > min_zoom)
		self.FindWindowById(wx.ID_ZOOM_IN).Enable(self._panel_map.zoom < max_zoom)

	def _fill_maps(self):
		self._cb_map.Clear()
		to_sel = 0
		prev_sel_map = AppConfig().get('map', 'last_map', 'ocm')
		maps = sorted((vmap['name'], key)
				for key, vmap in maps_loader.MAPS.iteritems())
		for idx, (mapname, key) in enumerate(maps):
			self._cb_map.Append(mapname, key)
			if key == prev_sel_map:
				to_sel = idx
		self._cb_map.SetSelection(to_sel)
		self._current_map = prev_sel_map
