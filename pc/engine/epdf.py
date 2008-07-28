# -*- coding: utf-8 -*-

"""
engine/epdf.py

 Photo Catalog v 1.x  (pc)
 Copyright (c) Karol Będkowski, 2004-2008

 This file is part of Photo Catalog

 PC is free software; you can redistribute it and/or modify it under the
 terms of the GNU General Public License as published by the Free Software
 Foundation, version 2.
"""

__author__		= 'Karol Będkowski'
__copyright__	= 'Copyright (C) Karol Będkowski 2008'


import logging
from cStringIO import StringIO

import wx

from reportlab.platypus		import SimpleDocTemplate, Table, Paragraph, Image, Spacer
from reportlab.rl_config	import defaultPageSize
from reportlab.lib.units	import cm, inch
from reportlab.lib.styles	import getSampleStyleSheet
from reportlab.lib.enums	import TA_CENTER

from kpylibs.appconfig		import AppConfig
from kpylibs				import dialogs

_LOG = logging.getLogger(__name__)
_ = wx.GetTranslation



def create_pdf(parent, items):

	filename = dialogs.dialog_file_save(parent, _('Export to PDF'), '*.pdf')
	if filename is None:
		return

	if not filename.lower().endswith('.pdf'):
		filename += '.pdf'

	appconfig	= AppConfig()
	img_width	= appconfig.get('settings', 'thumb_width', 200) / 150 * inch
	img_height	= appconfig.get('settings', 'thumb_height', 200) / 150 * inch

	cols = max(int((defaultPageSize[0] - 2 * cm) / (img_width + 0.5 * cm)), 1)

	_LOG.info('create_pdf filename=%s' % filename)
	try:
		stylesheet = getSampleStyleSheet()
		style = stylesheet['BodyText']
		style.alignment = TA_CENTER
		style.fontSize = 6

		doc = SimpleDocTemplate(filename, leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=2*cm)
		page = []
		data = []
		row	= []

		for idx, item in enumerate(items):
			par = Paragraph(item.name, style)
			par.wrap(img_width, img_height)

			img = StringIO(item.image)
			image = Image(img, 33, 33, kind='%', lazy=2)
			row.append([ image, par ])

			if idx % cols == cols -1:
				data.append(row)
				row = []

		if len(row) > 0:
			while len(row) < cols:
				row.append(Spacer(1, 1))

			data.append(row)

		table = Table(data, style=[('ALIGN',(0,0),(cols-1,len(data)-1),'CENTER')])
		page.append(table)
		doc.build(page)

	except Exception, err:
		_LOG.exception('create_pdf error. file=%s' % filename)
	else:
		dialogs.message_box_info(parent, _('Done!'), _('Export to PDF'))


# vim: encoding=utf8: ff=unix:
