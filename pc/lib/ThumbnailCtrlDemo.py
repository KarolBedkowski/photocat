import wx
import os

import ThumbnailCtrl as TC

#-----------------------------------------------------------------------------
# PATH & FILE FILLING (OS INDEPENDENT)
#-----------------------------------------------------------------------------

def opj(path):
    """Convert paths to the platform-specific separator"""
    str = apply(os.path.join, tuple(path.split('/')))
    # HACK: on Linux, a leading / gets lost...
    if path.startswith('/'):
        str = '/' + str
    return str

#-----------------------------------------------------------------------------

#----------------------------------------------------------------------
# Get Some Icon For The Demo
#----------------------------------------------------------------------

def GetMondrianData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\
\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00qID\
ATX\x85\xed\xd6;\n\x800\x10E\xd1{\xc5\x8d\xb9r\x97\x16\x0b\xad$\x8a\x82:\x16\
o\xda\x84pB2\x1f\x81Fa\x8c\x9c\x08\x04Z{\xcf\xa72\xbcv\xfa\xc5\x08 \x80r\x80\
\xfc\xa2\x0e\x1c\xe4\xba\xfaX\x1d\xd0\xde]S\x07\x02\xd8>\xe1wa-`\x9fQ\xe9\
\x86\x01\x04\x10\x00\\(Dk\x1b-\x04\xdc\x1d\x07\x14\x98;\x0bS\x7f\x7f\xf9\x13\
\x04\x10@\xf9X\xbe\x00\xc9 \x14K\xc1<={\x00\x00\x00\x00IEND\xaeB`\x82' 

def GetMondrianBitmap():
    return wx.BitmapFromImage(GetMondrianImage())

def GetMondrianImage():
    import cStringIO
    stream = cStringIO.StringIO(GetMondrianData())
    return wx.ImageFromStream(stream)

def GetMondrianIcon():
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(GetMondrianBitmap())
    return icon


class MyLog(wx.PyLog):
    
    def __init__(self, textCtrl):
        
        wx.PyLog.__init__(self)
        self.tc = textCtrl

    def DoLogString(self, message, dummy):
        if self.tc:
            if not message.startswith("Debug"):
                self.tc.AppendText(message + '\n')
            

class ThumbnailCtrlDemo(wx.Frame):

    def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self.SetIcon(GetMondrianIcon())

        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -1])
        # statusbar fields
        statusbar_fields = [("ThumbnailCtrl Demo, Andrea Gavana @ 10 Dec 2005"),
                            ("Welcome To wxPython!")]

        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)

        self.SetMenuBar(self.CreateMenuBar())
        
        splitter = wx.SplitterWindow(self, -1, style=wx.CLIP_CHILDREN | wx.SP_3D | wx.WANTS_CHARS | wx.SP_LIVE_UPDATE)
        splitter2 = wx.SplitterWindow(splitter, -1, style=wx.CLIP_CHILDREN | wx.SP_3D)  
      
        self.panel_1 = wx.Panel(splitter2, -1)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        scroll = TC.ThumbnailCtrl(splitter, -1)
        
        scroll.ShowFileNames()
        scroll.ShowDir(os.getcwd())

        self.TC = scroll
        
        self.thumbsizer_staticbox = wx.StaticBox(self.panel_1, -1, "Thumb Style")
        self.customsizer_staticbox = wx.StaticBox(self.panel_1, -1, "Thumb Customization")
        self.optionsizer_staticbox = wx.StaticBox(self.panel_1, -1, "More Options")
        self.dirsizer_staticbox = wx.StaticBox(self.panel_1, -1, "Directory Selection")
        self.dirbutton = wx.Button(self.panel_1, -1, "Change Directory")
        self.radiostyle1 = wx.RadioButton(self.panel_1, -1, "THUMB_OUTLINE_NONE", style=wx.RB_GROUP)
        self.radiostyle2 = wx.RadioButton(self.panel_1, -1, "THUMB_OUTLINE_FULL")
        self.radiostyle3 = wx.RadioButton(self.panel_1, -1, "THUMB_OUTLINE_RECT")
        self.radiostyle4 = wx.RadioButton(self.panel_1, -1, "THUMB_OUTLINE_IMAGE")
        self.highlight = wx.CheckBox(self.panel_1, -1, "Highlight On Pointing")
        self.showfiles = wx.CheckBox(self.panel_1, -1, "Show Filenames")
        self.enabledragging = wx.CheckBox(self.panel_1, -1, "Enable Drag And Drop")
        self.setpopup = wx.CheckBox(self.panel_1, -1, "Set Popup Menu On Thumbs")
        self.setgpopup = wx.CheckBox(self.panel_1, -1, "Set Global Popup Menu")
        self.showcombo = wx.CheckBox(self.panel_1, -1, "Show Folder ComboBox")
        self.enabletooltip = wx.CheckBox(self.panel_1, -1, "Enable Thumb ToolTips")
        self.textzoom = wx.TextCtrl(self.panel_1, -1, "1.4")
        self.zoombutton = wx.Button(self.panel_1, -1, "Set Zoom Factor")
        self.fontbutton = wx.Button(self.panel_1, -1, "Set Caption Font")
        self.colourbutton = wx.Button(self.panel_1, -1, "Set Selection Colour")

        self.radios = [self.radiostyle1, self.radiostyle2, self.radiostyle3,
                       self.radiostyle4]
        self.thumbstyles = ["THUMB_OUTLINE_NONE", "THUMB_OUTLINE_FULL", "THUMB_OUTLINE_RECT",
                            "THUMB_OUTLINE_IMAGE"]
        
        self.__set_properties()
        self.__do_layout()

        self.panel_1.SetSizer(sizer)
        sizer.Layout()
    
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChangeOutline, self.radiostyle1)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChangeOutline, self.radiostyle2)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChangeOutline, self.radiostyle3)
        self.Bind(wx.EVT_RADIOBUTTON, self.OnChangeOutline, self.radiostyle4)
        self.Bind(wx.EVT_CHECKBOX, self.OnHighlight, self.highlight)
        self.Bind(wx.EVT_CHECKBOX, self.OnShowFiles, self.showfiles)
        self.Bind(wx.EVT_CHECKBOX, self.OnEnableDragging, self.enabledragging)
        self.Bind(wx.EVT_CHECKBOX, self.OnSetPopup, self.setpopup)
        self.Bind(wx.EVT_CHECKBOX, self.OnSetGlobalPopup, self.setgpopup)
        self.Bind(wx.EVT_CHECKBOX, self.OnShowComboBox, self.showcombo)
        self.Bind(wx.EVT_CHECKBOX, self.OnEnableToolTips, self.enabletooltip)
        self.Bind(wx.EVT_BUTTON, self.OnSetZoom, self.zoombutton)
        self.Bind(wx.EVT_BUTTON, self.OnSetFont, self.fontbutton)
        self.Bind(wx.EVT_BUTTON, self.OnSetColour, self.colourbutton)
        self.Bind(wx.EVT_BUTTON, self.OnSetDirectory, self.dirbutton)
        # end wxGlade

        self.TC.Bind(TC.EVT_THUMBNAILS_SEL_CHANGED, self.OnSelChanged)
        self.TC.Bind(TC.EVT_THUMBNAILS_POINTED, self.OnPointed)
        self.TC.Bind(TC.EVT_THUMBNAILS_DCLICK, self.OnDClick)

        # Set up a log window
        self.log = wx.TextCtrl(splitter2, -1,
                               style = wx.TE_MULTILINE|wx.TE_READONLY|wx.HSCROLL)

        # But instead of the above we want to show how to use our own wx.Log class
        wx.Log_SetActiveTarget(MyLog(self.log))
        
        # add the windows to the splitter and split it.
        splitter2.SplitHorizontally(self.panel_1, self.log, -100)
        splitter.SplitVertically(scroll, splitter2, 180)

        splitter.SetMinimumPaneSize(140)
        splitter2.SetMinimumPaneSize(60)

        # Make the splitter on the right expand the top window when resized
        def SplitterOnSize(evt):
            splitter = evt.GetEventObject()
            sz = splitter.GetSize()
            splitter.SetSashPosition(sz.height - 100, False)
            evt.Skip()

        splitter2.Bind(wx.EVT_SIZE, SplitterOnSize)
        
        self.SetMinSize((700,590))
        self.CenterOnScreen()

        
    def __set_properties(self):
        # begin wxGlade: MyFrame.__set_properties
        self.radiostyle4.SetValue(1)
        self.showfiles.SetValue(1)
        self.zoombutton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.fontbutton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.dirbutton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        self.colourbutton.SetFont(wx.Font(8, wx.DEFAULT, wx.NORMAL, wx.BOLD, 0, ""))
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MyFrame.__do_layout
        
        splitsizer = wx.BoxSizer(wx.VERTICAL)
        optionsizer = wx.StaticBoxSizer(self.optionsizer_staticbox, wx.VERTICAL)
        zoomsizer = wx.BoxSizer(wx.HORIZONTAL)
        customsizer = wx.StaticBoxSizer(self.customsizer_staticbox, wx.VERTICAL)
        thumbsizer = wx.StaticBoxSizer(self.thumbsizer_staticbox, wx.VERTICAL)
        radiosizer = wx.BoxSizer(wx.VERTICAL)
        dirsizer = wx.StaticBoxSizer(self.dirsizer_staticbox, wx.HORIZONTAL)
        dirsizer.Add(self.dirbutton, 0, wx.LEFT|wx.BOTTOM|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 3)
        splitsizer.Add(dirsizer, 0, wx.EXPAND|wx.TOP|wx.LEFT, 5)
        radiosizer.Add(self.radiostyle1, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 3)
        radiosizer.Add(self.radiostyle2, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 3)
        radiosizer.Add(self.radiostyle3, 0, wx.LEFT|wx.TOP|wx.ADJUST_MINSIZE, 3)
        radiosizer.Add(self.radiostyle4, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        thumbsizer.Add(radiosizer, 1, wx.EXPAND, 0)
        splitsizer.Add(thumbsizer, 0, wx.TOP|wx.EXPAND|wx.LEFT, 5)
        customsizer.Add(self.highlight, 0, wx.LEFT|wx.TOP|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        customsizer.Add(self.showfiles, 0, wx.LEFT|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        customsizer.Add(self.enabledragging, 0, wx.LEFT|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        customsizer.Add(self.setpopup, 0, wx.LEFT|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        customsizer.Add(self.setgpopup, 0, wx.LEFT|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        customsizer.Add(self.showcombo, 0, wx.LEFT|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        customsizer.Add(self.enabletooltip, 0, wx.LEFT|wx.BOTTOM|wx.ADJUST_MINSIZE, 3)
        splitsizer.Add(customsizer, 0, wx.TOP|wx.EXPAND|wx.LEFT, 5)
        zoomsizer.Add(self.textzoom, 1, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 3)
        zoomsizer.Add(self.zoombutton, 0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 3)
        optionsizer.Add(zoomsizer, 1, wx.EXPAND, 0)
        optionsizer.Add(self.fontbutton, 0, wx.ALL|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 3)
        optionsizer.Add(self.colourbutton, 0, wx.TOP|wx.LEFT|wx.ALIGN_CENTER_VERTICAL|wx.ADJUST_MINSIZE, 3)
        splitsizer.Add(optionsizer, 0, wx.EXPAND | wx.TOP|wx.LEFT, 5)
        self.panel_1.SetAutoLayout(True)
        self.panel_1.SetSizer(splitsizer)
        splitsizer.Fit(self.panel_1)
        

    def CreateMenuBar(self):

        file_menu = wx.Menu()
        
        AS_EXIT = wx.NewId()        
        file_menu.Append(AS_EXIT, "&Exit")
        self.Bind(wx.EVT_MENU, self.OnClose, id=AS_EXIT)

        help_menu = wx.Menu()

        AS_ABOUT = wx.NewId()        
        help_menu.Append(AS_ABOUT, "&About...")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=AS_ABOUT)

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")        

        return menu_bar        


    def OnClose(self, event):
        
        self.Destroy()


    def OnAbout(self, event):

        msg = "This Is The About Dialog Of The ThumbnailCtrl Demo.\n\n" + \
              "Author: Andrea Gavana @ 10 Dec 2005\n\n" + \
              "Please Report Any Bug/Requests Of Improvements\n" + \
              "To Me At The Following Adresses:\n\n" + \
              "andrea.gavana@agip.it\n" + "andrea_gavana@tin.it\n\n" + \
              "Welcome To wxPython " + wx.VERSION_STRING + "!!"
              
        dlg = wx.MessageDialog(self, msg, "ThumbnailCtrl Demo",
                               wx.OK | wx.ICON_INFORMATION)
        
        dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False))
        dlg.ShowModal()
        dlg.Destroy()


    def OnSetDirectory(self, event):

        dlg = wx.DirDialog(self, "Choose A Directory With Images:",
                           defaultPath=os.getcwd(),
                           style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

        # If the user selects OK, then we process the dialog's data.
        # This is done by getting the path data from the dialog - BEFORE
        # we destroy it. 
        if dlg.ShowModal() == wx.ID_OK:
            self.TC.ShowDir(dlg.GetPath())
            self.log.write("OnSetDirectory: Directory Changed To: " + dlg.GetPath() + "\n")

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
        
        
    def OnChangeOutline(self, event): # wxGlade: MyFrame.<event_handler>

        radio = event.GetEventObject()
        pos = self.radios.index(radio)

        if pos == 0:
            self.TC.SetThumbOutline(TC.THUMB_OUTLINE_NONE)
        elif pos == 1:
            self.TC.SetThumbOutline(TC.THUMB_OUTLINE_FULL)
        elif pos == 2:
            self.TC.SetThumbOutline(TC.THUMB_OUTLINE_RECT)
        elif pos == 3:
            self.TC.SetThumbOutline(TC.THUMB_OUTLINE_IMAGE)

        self.TC.Refresh()
        
        self.log.write("OnChangeOutline: Outline Changed To: " + self.thumbstyles[pos] + "\n")        
        event.Skip()


    def OnHighlight(self, event): # wxGlade: MyFrame.<event_handler>

        if self.highlight.GetValue() == 1:
            self.TC.SetHighlightPointed(True)
            self.log.write("OnHighlight: Highlight Thumbs On Pointing\n")
        else:
            self.TC.SetHighlightPointed(False)
            self.log.write("OnHighlight: Don't Highlight Thumbs On Pointing\n")
            
        event.Skip()


    def OnShowFiles(self, event): # wxGlade: MyFrame.<event_handler>

        if self.showfiles.GetValue() == 1:
            self.TC.ShowFileNames(True)
            self.log.write("OnShowFiles: Thumbs File Names Shown\n")
        else:
            self.TC.ShowFileNames(False)
            self.log.write("OnShowFiles: Thumbs File Names Not Shown\n")

        self.TC.Refresh()
        
        event.Skip()


    def OnEnableDragging(self, event):

        if self.enabledragging.GetValue() == 1:
            self.TC.EnableDragging(True)
            self.log.write("OnEnableDragging: Thumbs Drag And Drop Enabled\n")
        else:
            self.TC.EnableDragging(False)
            self.log.write("OnEnableDragging: Thumbs Drag And Drop Disabled\n")

        self.TC.Refresh()
        
        event.Skip()
        

    def OnSetPopup(self, event): # wxGlade: MyFrame.<event_handler>

        if self.setpopup.GetValue() == 1:
            menu = self.CreatePopups()
            self.TC.SetPopupMenu(menu)
            self.log.write("OnSetPopup: Popups Enabled On Thumbs\n")
        else:
            self.TC.SetPopupMenu(None)
            self.log.write("OnSetPopup: Popups Disabled On Thumbs\n")
        
        event.Skip()


    def OnSetGlobalPopup(self, event):

        if self.setgpopup.GetValue() == 1:
            menu = self.CreateGlobalPopups()
            self.TC.SetGlobalPopupMenu(menu)
            self.log.write("OnSetGlobalPopup: Popups Enabled Globally (No Selection Needed)\n")
        else:
            self.TC.SetGlobalPopupMenu(None)
            self.log.write("OnSetGlobalPopup: Popups Disabled Globally (No Selection Needed)\n")
            
        event.Skip()


    def OnShowComboBox(self, event):

        if self.showcombo.GetValue() == 1:
            self.log.write("OnShowComboBox: Directory ComboBox Shown\n")
            self.TC.ShowComboBox(True)
        else:
            self.log.write("OnShowComboBox: Directory ComboBox Hidden\n")
            self.TC.ShowComboBox(False)

        event.Skip()


    def OnEnableToolTips(self, event):

        if self.enabletooltip.GetValue() == 1:
            self.log.write("OnEnableToolTips: File Information On ToolTips Enabled\n")
            self.TC.EnableToolTips(True)
        else:
            self.log.write("OnEnableToolTips: File Information On ToolTips Disabled\n")
            self.TC.EnableToolTips(False)

        event.Skip()
        
        
    def OnSetZoom(self, event): # wxGlade: MyFrame.<event_handler>

        val = self.textzoom.GetValue().strip()

        try:
            val = float(val)
        except:
            errstr = "Error: Non Floating Value For The Text Control! "
            dlg = wx.MessageDialog(self, errstr, "ThumbnailCtrlDemo Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.textzoom.SetValue("1.4")
            return


        if val < 1.0:
            errstr = "Error: Zoom Factor Must Be Greater Than 1.0 "
            dlg = wx.MessageDialog(self, errstr, "ThumbnailCtrlDemo Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.textzoom.SetValue("1.4")
            return

        self.TC.SetZoomFactor(val)
        
        event.Skip()


    def OnSelChanged(self, event):

        self.log.write("OnSelChanged: Thumb Selected: " + str(self.TC.GetSelection()) + "\n")
        event.Skip()


    def OnPointed(self, event):

        self.log.write("OnPointed: Thumb Pointed: " + str(self.TC.GetPointed()) + "\n")
        event.Skip()


    def OnDClick(self, event):

        self.log.write("OnDClick: Thumb Double-Clicked: " + str(self.TC.GetSelection()) + "\n")
        event.Skip()
        

    def OnSetFont(self, event): # wxGlade: MyFrame.<event_handler>

        data = wx.FontData()
        data.EnableEffects(True)
        data.SetInitialFont(self.TC.GetCaptionFont())

        dlg = wx.FontDialog(self, data)
        
        if dlg.ShowModal() == wx.ID_OK:
            data = dlg.GetFontData()
            font = data.GetChosenFont()
            self.TC.SetCaptionFont(font)
            self.TC.Refresh()
            self.log.write("OnSetFont: Caption Font Changed\n")
            
        # Don't destroy the dialog until you get everything you need from the
        # dialog!
        dlg.Destroy()        
        event.Skip()


    def OnSetColour(self, event):

        dlg = wx.ColourDialog(self)

        # Ensure the full colour dialog is displayed, 
        # not the abbreviated version.
        dlg.GetColourData().SetChooseFull(True)

        if dlg.ShowModal() == wx.ID_OK:

            # If the user selected OK, then the dialog's wx.ColourData will
            # contain valid information. Fetch the data ...
            data = dlg.GetColourData()

            # ... then do something with it. The actual colour data will be
            # returned as a three-tuple (r, g, b) in this particular case.
            colour = data.GetColour().Get()
            colour = wx.Colour(colour[0], colour[1], colour[2])
            self.TC.SetSelectionColour(colour)
            self.TC.Refresh()

        # Once the dialog is destroyed, Mr. wx.ColourData is no longer your
        # friend. Don't use it again!
        dlg.Destroy()
        

    def CreatePopups(self):

        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            self.popupID3 = wx.NewId()
            self.popupID4 = wx.NewId()
            self.popupID5 = wx.NewId()
            self.popupID6 = wx.NewId()
            self.popupID7 = wx.NewId()
            self.popupID8 = wx.NewId()
            self.popupID9 = wx.NewId()
            self.popupID10 = wx.NewId()
            self.popupID11 = wx.NewId()
            self.popupID12 = wx.NewId()

            self.Bind(wx.EVT_MENU, self.OnPopupOne, id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnPopupTwo, id=self.popupID2)
            self.Bind(wx.EVT_MENU, self.OnPopupThree, id=self.popupID3)
            self.Bind(wx.EVT_MENU, self.OnPopupFour, id=self.popupID4)
            self.Bind(wx.EVT_MENU, self.OnPopupFive, id=self.popupID5)
            self.Bind(wx.EVT_MENU, self.OnPopupSix, id=self.popupID6)
            self.Bind(wx.EVT_MENU, self.OnPopupSeven, id=self.popupID7)
            self.Bind(wx.EVT_MENU, self.OnPopupEight, id=self.popupID8)
            self.Bind(wx.EVT_MENU, self.OnPopupNine, id=self.popupID9)
            
        menu = wx.Menu()
        item = wx.MenuItem(menu, self.popupID1, "One")
        bmp = GetMondrianImage()
        bmp = bmp.Scale(16, 16)
        bmp = bmp.ConvertToBitmap()
        item.SetBitmap(bmp)
        menu.AppendItem(item)
        
        # add some other items
        menu.Append(self.popupID2, "Two")
        menu.Append(self.popupID3, "Three")
        menu.Append(self.popupID4, "Four")
        menu.Append(self.popupID5, "Five")
        menu.Append(self.popupID6, "Six")
        # make a submenu
        sm = wx.Menu()
        sm.Append(self.popupID8, "Sub Item 1")
        sm.Append(self.popupID9, "Sub Item 1")
        menu.AppendMenu(self.popupID7, "Test Submenu", sm)

        return menu


    def CreateGlobalPopups(self):

        if not hasattr(self, "popupID10"):
            self.popupID10 = wx.NewId()
            self.popupID11 = wx.NewId()
            self.popupID12 = wx.NewId()

        self.Bind(wx.EVT_MENU, self.OnPopupTen, id=self.popupID10)
        self.Bind(wx.EVT_MENU, self.OnPopupEleven, id=self.popupID11)
        self.Bind(wx.EVT_MENU, self.OnPopupTwelve, id=self.popupID12)
        
        menu = wx.Menu()
        item = wx.MenuItem(menu, self.popupID10, "Select All")
        menu.AppendItem(item)
        menu.AppendSeparator()

        item = wx.MenuItem(menu, self.popupID11, "Say Hello!")
        bmp = GetMondrianImage()
        bmp = bmp.Scale(16, 16)
        bmp = bmp.ConvertToBitmap()
        item.SetBitmap(bmp)
        menu.AppendItem(item)
        menu.AppendSeparator()
        
        menu.Append(self.popupID12, "Get Thumbs Count")

        return menu
    

    def OnPopupOne(self, event):
        self.log.write("OnPopupMenu: Popup One\n")


    def OnPopupTwo(self, event):
        self.log.write("OnPopupMenu: Popup Two\n")


    def OnPopupThree(self, event):
        self.log.write("OnPopupMenu: Popup Three\n")


    def OnPopupFour(self, event):
        self.log.write("OnPopupMenu: Popup Four\n")


    def OnPopupFive(self, event):
        self.log.write("OnPopupMenu: Popup Five\n")


    def OnPopupSix(self, event):
        self.log.write("OnPopupMenu: Popup Six\n")


    def OnPopupSeven(self, event):
        self.log.write("OnPopupMenu: Popup Seven\n")


    def OnPopupEight(self, event):
        self.log.write("OnPopupMenu: Popup Eight\n")


    def OnPopupNine(self, event):
        self.log.write("OnPopupMenu: Popup Nine\n")
        

    def OnPopupTen(self, event):

        items = self.TC.GetItemCount()

        for ii in xrange(items):
            self.TC.SetSelection(ii)

        self.log.write("OnGlobalPopupMenu: All Thumbs Selected\n")
        
        event.Skip()


    def OnPopupEleven(self, event):

        self.log.write("OnGlobalPopupMenu: Say Hello Message...\n")
        
        msgstr = "Info: Let's Say Hello To wxPython! "
        dlg = wx.MessageDialog(self, msgstr, "ThumbnailCtrlDemo Info",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        event.Skip()


    def OnPopupTwelve(self, event):

        items = self.TC.GetItemCount()
        self.log.write("OnGlobalPopupMenu: Number Of Thumbs: " + str(items) + "\n")
        
        msgstr = "Info: Number Of Thumbs: " + str(items)
        dlg = wx.MessageDialog(self, msgstr, "ThumbnailCtrlDemo Info",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

        event.Skip()
        
        
if __name__ == "__main__":
    
    app = wx.PySimpleApp()
    frame = ThumbnailCtrlDemo(None, -1, "ThumbnailCtrl Demo ;-)")
    frame.CenterOnScreen()
    frame.Show()

    app.MainLoop()

    
    