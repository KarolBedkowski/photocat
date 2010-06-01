# -*- coding: utf-8 -*-

"""
engine/epdf.py

Photo Catalog v 1.x  (photocat)
Copyright (c) Karol Będkowski, 2004-2010

This file is part of Photo Catalog
"""

__author__ = 'Karol Będkowski'
__copyright__ = 'Copyright (C) Karol Będkowski 2008'


import logging
from cStringIO import StringIO
import time

import wx

from photocat.lib.appconfig import AppConfig
from photocat.lib.wxtools import dialogs

_LOG = logging.getLogger(__name__)


# próba załadowania reportlab
try:
	from reportlab.platypus import (SimpleDocTemplate, Table, Paragraph,
			Image, Spacer)
	from reportlab.rl_config import defaultPageSize
	from reportlab.lib.units import cm, inch
	from reportlab.lib.styles import getSampleStyleSheet
	from reportlab.lib.enums import TA_CENTER
	from reportlab.pdfbase import pdfmetrics
	from reportlab.pdfbase.ttfonts import TTFont

except ImportError:
	_LOG.warn('reportlab not available')
	EPDF_AVAILABLE = False

else:
	_LOG.info('reportlab loaded')
	EPDF_AVAILABLE = True

###########################################################################

GROUP_BY_NONE = 0
GROUP_BY_DATE = 1
GROUP_BY_PATH = 2

MARGIN_TOP = 0.5 * cm
MARGIN_BOTTOM = 1 * cm
MARGIN_LEFT = MARGIN_RIGHT = 0.5 * cm

###########################################################################


def _create_pdf(parent, items, options=None):
	''' create pdf from given items
	@parent: parent window
	@items: list of items to render
	@options: options for generating pdf
	'''

	appconfig = AppConfig()
	pdfmetrics.registerFont(TTFont('FreeSans',
		appconfig.get_data_file('fonts/freesans.ttf')))

	filename = dialogs.dialog_file_save(parent, _('Export to PDF'), '*.pdf')
	if filename is None:
		return

	if not filename.lower().endswith('.pdf'):
		filename += '.pdf'

	def __my_page(canvas, doc):
		# strona - numer
		canvas.saveState()
		canvas.setFont('FreeSans', 6)
		canvas.drawString(defaultPageSize[0] / 2, MARGIN_BOTTOM, "%d" % doc.page)
		canvas.restoreState()

	img_width = appconfig.get('settings', 'thumb_width', 200) / 150 * inch
	img_height = appconfig.get('settings', 'thumb_height', 200) / 150 * inch

	cols = max(int((defaultPageSize[0] - MARGIN_LEFT - MARGIN_RIGHT) \
			/ (img_width + 0.5 * cm)), 1)

	_LOG.info('create_pdf filename=%s', filename)
	parent.SetCursor(wx.HOURGLASS_CURSOR)
	try:
		stylesheet = getSampleStyleSheet()
		style = stylesheet['BodyText']
		style.alignment = TA_CENTER
		style.fontName = 'FreeSans'
		style.fontSize = 6

		style_header = stylesheet['Heading1']
		style_header.fontSize = 10
		style_header.fontName = 'FreeSans'

		doc = SimpleDocTemplate(filename, leftMargin=MARGIN_LEFT,
				rightMargin=MARGIN_RIGHT, topMargin=MARGIN_TOP,
				bottomMargin=MARGIN_BOTTOM, pageCompression=9)
		page = []

		options = options or {}
		grouping = options.get('group_by')
		if grouping == GROUP_BY_DATE:
			item_value_func = lambda i: time.localtime(i.date_to_check)[:3]
			group_label_func = lambda i: time.strftime('%x',
					time.localtime(i.date_to_check))
			_create_doc_group_by(page, items, style, style_header, img_width,
					img_height, cols, item_value_func, group_label_func, options)
		elif grouping == GROUP_BY_PATH:
			item_value_func = lambda i: i.parent.path
			group_label_func = lambda i: i.disk.name + ": " + i.parent.path
			_create_doc_group_by(page, items, style, style_header, img_width,
					img_height, cols, item_value_func, group_label_func, options)
		else:
			_create_doc_group_none(page, items, style, img_width, img_height,
					cols, options)
		doc.build(page, onLaterPages=__my_page, onFirstPage=__my_page)
	except RuntimeError, err:
		_LOG.exception('create_pdf error. file=%s', filename)
		dialogs.message_box_error(parent, _('Error:\n%s') % str(err),
				_('Export to PDF'))
	else:
		dialogs.message_box_info(parent, _('Done!'), _('Export to PDF'))

	parent.SetCursor(wx.STANDARD_CURSOR)


###########################################################################


def _create_doc_group_none(page, items, style, img_width, img_height, cols,
			options):
	''' draw items without grouping '''
	data = []
	row = []
	show_captions = options.get('show_captions', True)
	col_width = img_width + 0.5 * cm
	table_style = [('ALIGN', (0, 0), (-1, -1), 'CENTER')]

	for idx, item in enumerate(items):
		img = StringIO(item.image)
		image = Image(img, 33, 33, kind='%', lazy=2)

		if show_captions:
			par = Paragraph(item.name, style)
			par.wrap(img_width, img_height)
			row.append([image, par])
		else:
			row.append(image)
		if idx % cols == cols -1:
			data.append(row)
			row = []
	if len(row) > 0:
		while len(row) < cols:
			row.append(Spacer(img_width, img_height))
		data.append(row)

	table = Table(data, col_width, style=table_style)
	page.append(table)


def _create_doc_group_by(page, items, style, style_header, img_width,
		img_height, cols, item_value_func, group_label_func, options):
	''' draw item with grouping '''
	data = []
	row = []
	show_captions = options.get('show_captions', True)
	col_width = img_width + 0.5 * cm
	table_style = [('ALIGN', (0, 0), (-1, -1), 'CENTER')]
	last_item_value = None

	for item in items:
		item_value = item_value_func(item)
		if last_item_value != item_value:
			if len(row) > 0:
				while len(row) < cols:
					row.append(Spacer(img_width, img_height))
				data.append(row)
			if len(data) > 0:
				table = Table(data, col_width, style=table_style)
				#table.hAlign = 'LEFT'
				page.append(table)

			data = []
			row = []
			last_item_value = item_value
			page.append(Spacer(defaultPageSize[0] / 2, 1 * cm))
			page.append(Paragraph(group_label_func(item), style_header))
		img = StringIO(item.image)
		image = Image(img, 33, 33, kind='%', lazy=2)

		if show_captions:
			par = Paragraph(item.name, style)
			par.wrap(img_width, img_height)
			row.append([image, par])
		else:
			row.append(image)
		if len(row) == cols:
			data.append(row)
			row = []

	if len(row) > 0:
		while len(row) < cols:
			row.append(Spacer(img_width, img_height))
		data.append(row)

	if len(data) > 0:
		table = Table(data, col_width, style=table_style)
		#table.hAlign = 'LEFT'
		page.append(table)


###########################################################################


def _create_pdf_no_reportlab(parent, *_argv, **_kwarg):
	''' dummy function for creating pdf-s when no reportlab is available '''
	dialogs.message_box_info(parent,
			'Export to PDF not available!\nNo reportlab!', _('Export to PDF'))


###########################################################################


# pylint: disable-msg=C0103
create_pdf = _create_pdf if EPDF_AVAILABLE else _create_pdf_no_reportlab



# vim: encoding=utf8: ff=unix:
