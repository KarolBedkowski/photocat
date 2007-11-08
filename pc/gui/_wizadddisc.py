# -*- coding: utf-8 -*-

"""
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


import  wx
import  wx.wizard as wiz


class _TitledPage(wiz.WizardPageSimple):
    def __init__(self, parent, title):
        wiz.WizardPageSimple.__init__(self, parent)
        
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        
        sizer.Add(wx.StaticText(self, -1, 'Disc name:'))
        self.disc_name = wx.TextCtrl(self, -1)
        sizer.Add(self.disc_name, 1, wx.EXPAND)
        
        self.SetSizer(sizer)
		
		




def show_wizart_add_disc(parent):
	wizard = wiz.Wizard(parent, -1, "Add disc")
	page1 = _TitledPage(wizard, 'Start')
	
	wizard.FitToPage(page1)

	if wizard.RunWizard(page1):
		pass




# vim: encoding=utf8: ff=unix: 
