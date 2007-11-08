# --------------------------------------------------------------------------- #
# THUMBNAILCTRL Control wxPython IMPLEMENTATION
# Python Code By:
#
# Andrea Gavana And Peter Damoc, @ 12 Dec 2005
# Latest Revision: 19 June 2006, 10.00 CET
#
#
# TODO List/Caveats
#
# 1. Thumbnail Creation/Display May Be Somewhat Improved From The Execution
#    Speed Point Of View;
#
# 2. The Implementation For wx.HORIZONTAL Style Is Still To Be Written;
#
# 3. I Have No Idea On How To Implement Thumbnails For Audio And Video Files.
#
# 4. Other Ideas?
#
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To Me At:
#
# andrea.gavana@agip.it
# andrea_gavan@tin.it
#
# Or, Obviously, To The wxPython Mailing List!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------- #


"""Description:

ThumbnailCtrl Is A Widget That Can Be Used To Display A Series Of Images In
A "Thumbnail" Format; It Mimics, For Example, The Windows Explorer Behavior
When You Select The "View Thumbnails" Option.
Basically, By Specifying A Folder That Contains Some Image Files, The Files
In The Folder Are Displayed As Miniature Versions Of The Actual Images In
A wx.ScrolledWindow.

The Code Is Partly Based On wxVillaLib, A wxWidgets Implementation Of This
Control. However, ThumbnailCtrl Wouldn't Have Been So Fast And Complete
Without The Suggestions And Hints From Peter Damoc. So, If He Accepts The
Mention, This Control Is His As Much As Mine.


Usage:

ThumbnailCtrl.__init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                       size = wx.DefaultSize, thumboutline=THUMB_OUTLINE_RECT,
                       thumbfilter=THUMB_FILTER_IMAGES):

For The Full Listing Of The Input Parameters, See The ThumbnailCtrl __init__()
Method.


Methods And Settings:

With ThumbnailCtrl You Can:

- Create Different Thumb Outlines (None, Images Only, Full, etc...);
- Highlight Thumbnails On Mouse Hovering;
- Show/Hide File Names Below Thumbs;
- Change Thumb Caption Font;
- Zoom In/Out Thumbs (Done Via Ctrl Key + Mouse Wheel Or With "+" And "-" Chars,
  With Zoom Factor Value Customizable);
- Rotate Thumbs With These Specifications:
  a) "d" Key Rotates 90 Degrees Clockwise;
  b) "s" Key Rotates 90 Degrees Counter-Clockwise;
  c) "a" Key Rotates 180 Degrees
- Delete Files/Thumbnails (Via The "Del" Key);
- Drag And Drop Thumbs From ThumbnailCtrl To Whatever Application You Want;
- Use Local (When At Least One Thumb Is Selected) Or Global (No Need For
  Thumb Selection) Popup Menus;
- Show/Hide A wx.ComboBox At The Top Of ThumbnailCtrl: This ComboBox Contains
  Working Directory Information And It Has History Entries;
- Possibility To Show ToolTips On Thumbs, Which Display File Information
  (Like File Name, Size, Last Modification Date And Thumb Size).


For More Info On Methods And Initial Styles, Please Refer To The __init__()
Method For ThumbnailCtrl Or To The Specific Functions.

|=========================================================================== |
| NOTE: ThumbnailCtrl *Requires* The PIL (Python Imaging Library) Library To |
|       Be Installed.                                                        |
|=========================================================================== |

Side-Note: Using Highlight Thumbnails On Mouse Hovering May Be Slow On Slower
           Computers.

ThumbnailCtrl Control Is Freeware And Distributed Under The wxPython License. 

Latest Revision: Andrea Gavana @ 19 Jun 2006, 10.00 CET

"""


#----------------------------------------------------------------------
# Beginning Of ThumbnailCtrl wxPython Code
#----------------------------------------------------------------------

import wx
import os
import time

import thread
import cStringIO
import zlib

try:

    import Image
    import ImageEnhance

except ImportError:
    
    errstr = ("\nThumbnailCtrl *Requires* PIL (Python Imaging Library).\n"
             "You Can Get It At:\n\n"
             "http://www.pythonware.com/products/pil/\n\n"
             "ThumbnailCtrl Can Not Continue. Exiting...\n")
    
    raise errstr

from math import pi, ceil


#----------------------------------------------------------------------
# Get Default Icon/Data
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

def getDataSH():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2_A\x98\x83\rHvl\
\xdc\x9c\n\xa4X\x8a\x9d<C8\x80\xa0\x86#\xa5\x83\x81\x81y\x96\xa7\x8bcH\xc5\
\x9c\xb7\xd7\xd7\xf6\x85D2\xb4^\xbc\x1b\xd0\xd0p\xa6\x85\x9d\xa1\xf1\xc0\xc7\
\x7f\xef\x8d\x98\xf89_:p]\xaew\x0c\xe9\x16[\xbc\x8bSt\xdf\x9aT\xad\xef\xcb\
\x8e\x98\xc5\xbf\xb3\x94\x9ePT\xf8\xff\xf7\xfbm\xf5\xdb\xfeZ<\x16{\xf01o[l\
\xee\xee\xbd7\xbe\x95\xdd\xde\x9d+\xbf\xfdo\xf9\xb9\xd0\x03\x8be\xb7\xc7\xe6\
Y\xcb\xbd\x8b\xdfs\xe3[\xd6\xed\xe5\x9b}\x99\xe6=:\xbd\xed\xfc\xedu|\xfcq\
\xfb\xec/K<\xf8\xfec\xd7\xdb\xdb\x87W\xec\xcf\xfd]\xb0\xcc\xf0\xc0\xe5=\xf7^\
\x1e\xf9\xfb\xe6\xe6\xce\xe9\x0c\xfb\xa7\xafPt\xbb"\xa0\x9c\xd5!hz\xa4C*\xc9\
\x85\xd7pQ\x9bD\xa0s\xcf\xa8\xf0\xa8\xf0\x00\x0b\x9fyX\x7fo\xef\xdf\xc7\xda\
\r\xcbw\xd4\xfcx\xe0\xcdk\xd8\x9e[~{\xdd\xf6\xbfw\xbe\xfd\xddS\xdc\xe0\xfec_\
\xf0\xfe\xeb\xb7\xdf\xf1\xdd\xce\xdb&\xbb\xbdv\xe7\xff\xc3\xaf\x8dy\x99\xe5\
\x9e?\xf7\xfb+\xb7\xfdnLN\xf5\xc6\xb7g\xfd\xca_\x9a\x7f?\x7f\xe0\xfe\xe3\xaa\
\xe5\x0b\xf4\xb7\xcb\xea\x97\xed\n\xb7\xbf\xff\xadh\xf9\xe3\x1d\xd5f\x7fb\
\xdf\x95Y\x15\xc6\xe7\xee\xfe\xcbz7Y\xbd\xde[\xf3y\x1f0\xd72x\xba\xfa\xb9\
\xacsJh\x02\x00\xc4i\x8dN' )

def getDataBL():
    return zlib.decompress(
"x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xac \xcc\xc1\
\x06${\xf3\xd5\x9e\x02)\x96b'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2\xed=]\x1cC8f\
\xea\x9e\xde\xcb\xd9` \xc2\xf0P\xdf~\xc9y\xaeu\x0f\xfe1\xdf\xcc\x14\x1482A\
\xe9\xfd\x83\x1d\xaf\x84\xac\xf8\xe6\\\x8c3\xfc\x98\xf8\xa0\xb1\xa9K\xec\x9f\
\xc4\xd1\xb4GG{\xb5\x15\x8f_|t\x8a[a\x1fWzG\xa9\xc4,\xa0Q\x0c\x9e\xae~.\xeb\
\x9c\x12\x9a\x00\x7f1,7" )

def getDataTR():
    return zlib.decompress(
'x\xda\xeb\x0c\xf0s\xe7\xe5\x92\xe2b``\xe0\xf5\xf4p\t\x02\xd2\xac \xcc\xc1\
\x06${\xf3\xd5\x9e\x02)\x96b\'\xcf\x10\x0e \xa8\xe1H\xe9\x00\xf2m=]\x1cC8f\
\xe6\x9e\xd9\xc8\xd9` \xc2p\x91\xbd\xaei\xeeL\x85\xdcUo\xf6\xf7\xd6\xb2\x88\
\x0bp\x9a\x89i\x16=-\x94\xe16\x93\xb9!\xb8y\xcd\t\x0f\x89\n\xe6\xb7\xfcV~6\
\x8dFo\xf5\xee\xc8\x1fOaw\xc9\x88\x0c\x16\x05\x1a\xc4\xe0\xe9\xea\xe7\xb2\
\xce)\xa1\t\x00"\xf9$\x83' )

def getShadow():
    sh_tr = wx.ImageFromStream(cStringIO.StringIO(getDataTR())).ConvertToBitmap()
    sh_bl = wx.ImageFromStream(cStringIO.StringIO(getDataBL())).ConvertToBitmap()
    sh_sh = wx.ImageFromStream(cStringIO.StringIO(getDataSH())).ConvertToBitmap()    
    return (sh_tr, sh_bl, sh_sh)

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

# Different Outline On Thumb Selection:
# THUMB_OUTLINE_NONE: No Outline Drawn On Selection
# THUMB_OUTLINE_FULL: Full Outline Drawn On Selection
# THUMB_OUTLINE_RECT: Only Maximum Image Rect Outlined On Selection
# THUMB_OUTLINE_IMAGE: Only Image Rect Outlined On Selection

THUMB_OUTLINE_NONE = 0
THUMB_OUTLINE_FULL = 1
THUMB_OUTLINE_RECT = 2
THUMB_OUTLINE_IMAGE = 4

# Options For Filtering Files
THUMB_FILTER_IMAGES = 1
# THUMB_FILTER_VIDEOS = 2  Don't Know How To Create Thumbnails For Videos!!!

# ThumbnailCtrl Orientation: Not Fully Implemented Till Now
THUMB_HORIZONTAL = wx.HORIZONTAL
THUMB_VERTICAL = wx.VERTICAL

# Image File Name Extensions: Am I Missing Some Extensions Here?
extensions = [".jpeg", ".jpg", ".bmp", ".png", ".ico", ".tiff", ".ani", ".cur", ".gif",
              ".iff", ".icon", ".pcx", ".tif", ".xpm", ".xbm", ".mpeg", ".mpg", ".mov"]
extensions = extensions + [l.upper() for l in extensions]

# ThumbnailCtrl Events:
# wxEVT_THUMBNAILS_SEL_CHANGED: Event Fired When You Change Thumb Selection
# wxEVT_THUMBNAILS_POINTED: Event Fired When You Point A Thumb
# wxEVT_THUMBNAILS_DCLICK: Event Fired When You Double-Click A Thumb
# wxEVT_THUMBNAILS_CAPTION_CHANGED: Not Used At Present
# wxEVT_THUMBNAILS_THUMB_CHANGED: Used Internally

wxEVT_THUMBNAILS_SEL_CHANGED = wx.NewEventType()
wxEVT_THUMBNAILS_POINTED = wx.NewEventType()
wxEVT_THUMBNAILS_DCLICK = wx.NewEventType()
wxEVT_THUMBNAILS_CAPTION_CHANGED = wx.NewEventType()
wxEVT_THUMBNAILS_THUMB_CHANGED = wx.NewEventType()

#-----------------------------------#
#        ThumbnailCtrlEvent
#-----------------------------------#

EVT_THUMBNAILS_SEL_CHANGED = wx.PyEventBinder(wxEVT_THUMBNAILS_SEL_CHANGED, 1)
EVT_THUMBNAILS_POINTED = wx.PyEventBinder(wxEVT_THUMBNAILS_POINTED, 1)
EVT_THUMBNAILS_DCLICK = wx.PyEventBinder(wxEVT_THUMBNAILS_DCLICK, 1)
EVT_THUMBNAILS_CAPTION_CHANGED = wx.PyEventBinder(wxEVT_THUMBNAILS_CAPTION_CHANGED, 1)
EVT_THUMBNAILS_THUMB_CHANGED = wx.PyEventBinder(wxEVT_THUMBNAILS_THUMB_CHANGED, 1)

TN_USE_PIL = 0

TIME_FMT = '%d %b %Y, %H:%M:%S'


def CmpThumb(first, second):
    """ Compares Two Thumbs In Terms Of File Names And Ids. """
    
    if first.GetFileName() < second.GetFileName():
        return -1
    elif first.GetFileName() == second.GetFileName():
        return first.GetId() - second.GetId()
    
    return 1


def SortFiles(items, sorteditems, filenames):
    """ Sort Files In Alphabetical Order. """
    
    newfiles = []
    for item in sorteditems:
        newfiles.append(filenames[items.index(item)])
        
    return newfiles


# ---------------------------------------------------------------------------- #
# Class ThumbnailEvent
# ---------------------------------------------------------------------------- #

class ThumbnailEvent(wx.PyCommandEvent):
    
    def __init__(self, evtType, id=-1):
        """ Default Constructor For This Class."""
        
        wx.PyCommandEvent.__init__(self, evtType, id)
        self._eventType = evtType


# ---------------------------------------------------------------------------- #
# Class Thumb
# Auxiliary Class, To Handle Single Thumb Information For Every Thumb.
# Used Internally.
# ---------------------------------------------------------------------------- #

class Thumb:

    def __init__(self, parent, dir, filename, caption="", size=0, lastmod=0):
        """ Default Class Constructor. """
        
        self._filename = filename
        self.SetCaption(caption)
        self._id = 0
        self._dir = dir
        self._filesize = size
        self._lastmod = lastmod
        self._parent = parent
        self._captionbreaks = []
        self._bitmap = wx.EmptyBitmap(-1, -1)
        self._image = wx.EmptyImage(-1, -1)
        self._rotation = 0


    def SetCaption(self, caption=""):
        """ Sets Thumb Caption. """
        
        self._caption = caption
        self._captionbreaks = []
    

    def GetImage(self):
        """ Gets Thumb Image. """
        
        return self._image

    
    def SetImage(self, image):
        """ Sets Thumb Image. """
        
        self._image = image        


    def SetBitmap(self, bmp):
        """ Sets Thumb Bitmap. """
        
        self._bitmap = bmp
        

    def GetFileName(self):
        """ Gets Thumb File Name. """
        
        return self._filename


    def SetFileName(self, filename):
        """ Sets Thumb File Name. """
        
        self._filename = filename
        self._bitmap = wx.EmptyBitmap(-1, -1)
        

    def GetId(self):
        """ Returns Thumb Id. """
        
        return self._id


    def SetId(self, id=-1):
        """ Sets Thumb Id. """

        self._id = id
        

    def SetRotatedImage(self, image):
        """ Sets The Image As Rotated (Faster). """
        
        self._rotatedimage = image


    def GetRotatedImage(self):
        """ Gets A Rotated Image. """
        
        return self._rotatedimage
    

    def GetBitmap(self, width, height):
        """ Returns The Bitmap Associated To A Thumb. """
        
        if self.GetRotation() % (2*pi) < 1e-6:
            if not self._bitmap.Ok():
                if not hasattr(self, "_threadedimage"):
                    img = GetMondrianImage()
                else:
                    img = self._threadedimage
                
            else:
                
                img = self._threadedimage
                
        else:

            img = self.GetRotatedImage()

        if hasattr(self, "_originalsize"):
            imgwidth, imgheight = self._originalsize
        else:
            imgwidth, imgheight = (img.GetWidth(), img.GetHeight())
            
        if width < imgwidth or height < imgheight:
            scale = float(width)/imgwidth

            if scale > float(height)/imgheight:
                scale = float(height)/imgheight

            img = img.Scale(int(imgwidth*scale), int(imgheight*scale))
            
        bmp = img.ConvertToBitmap()
                        
        self._image = img

        return bmp


    def GetOriginalImage(self):
        """ Returns The Bitmap Associated To A Thumb. """

        original = opj((self._dir + "/" + self._filename))

        return original
    
##        pil = Image.open(opj(self._dir + "/" + self._filename))
##        originalsize = pil.size
##        return originalsize

                
    def GetCaption(self, line):
        """ Gets The Caption Associated To A Thumb. """
        
        if line + 1 >= len(self._captionbreaks):
            return ""
        
        strs = self._caption

        return strs        


    def GetFileSize(self):
        """ Returns The File Size Associated To A Thumb. """
        
        return self._filesize


    def GetCreationDate(self):
        """ Returns The File Last Modification Date Associated To A Thumb. """
        
        return self._lastmod        


    def GetCaptionLinesCount(self, width):
        """ Returns The Number Of Lines For The Caption. """
        
        self.BreakCaption(width)
        return len(self._captionbreaks) - 1


    def BreakCaption(self, width):
        """ Breaks The Caption Into Several Lines Of Text. """
        
        if len(self._captionbreaks) > 0 or  width < 16:
            return
        
        self._captionbreaks.append(0)

        if len(self._caption) == 0:
            return

        pos = width/16
        beg = 0
        end = 0

        dc = wx.MemoryDC()
        bmp = wx.EmptyBitmap(10,10)
        dc.SelectObject(bmp)
        
        while 1:
  
            if pos >= len(self._caption):

                self._captionbreaks.append(len(self._caption))
                break

            sw, sh = dc.GetTextExtent(self._caption[beg:pos-beg])
            
            if  sw > width:

                if end > 0:
              
                    self._captionbreaks.append(end)
                    beg = end
              
                else:
              
                    self._captionbreaks.append(pos)
                    beg = pos
              
                pos = beg + width/16
                end = 0

            if pos < len(self._caption) and self._caption[pos] in [" ", "-", ",", ".", "_"]:
                end = pos + 1

            pos = pos + 1


        dc.SelectObject(wx.NullBitmap)
        

    def SetRotation(self, angle=0):
        """ Sets Thumb Rotation. """
        
        self._rotation = angle


    def GetRotation(self):
        """ Gets Thumb Rotation. """
        
        return self._rotation
    

# ---------------------------------------------------------------------------- #
# Class ThumbnailCtrl
# Auxiliary Class, All Useful Methods Are Defined On ScrolledThumbnail Class.
# ---------------------------------------------------------------------------- #        

class ThumbnailCtrl(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, thumboutline=THUMB_OUTLINE_IMAGE,
                 thumbfilter=THUMB_FILTER_IMAGES):
        """
        Default Class Constructor. Non-Default Parameters Are:
        - thumboutline: Outline Style For The ThumbnailCtrl, Which May Be:
          a) THUMB_OUTLINE_NONE: No Outline Is Drawn On Selection;
          b) THUMB_OUTLINE_FULL: Full Outline (Image + Caption) Is Drawn On
             Selection;
          c) THUMB_OUTLINE_RECT: Only Thumb Bounding Rect Is Drawn On Selection
             (Default);
          d) THUMB_OUTLINE_IMAGE: Inly Image Bounding Rect Is Drawn.

        - thumbfilter: Filter For Image/Video/Audio Files. Actually Only
          THUMB_FILTER_IMAGES Is Implemented.
        """
        
        wx.Panel.__init__(self, parent, id, pos, size)     

        self._sizer = wx.BoxSizer(wx.VERTICAL)

        self._combo = wx.ComboBox(self, -1, style=wx.CB_DROPDOWN | wx.CB_READONLY)
        self._scrolled = ScrolledThumbnail(self, -1, thumboutline=thumboutline,
                                           thumbfilter=thumbfilter)

        subsizer = wx.BoxSizer(wx.HORIZONTAL)
        subsizer.Add((3, 0), 0)
        subsizer.Add(self._combo, 0, wx.EXPAND | wx.TOP, 3)
        subsizer.Add((3, 0), 0)
        self._sizer.Add(subsizer, 0, wx.EXPAND | wx.ALL, 3)
        self._sizer.Add(self._scrolled, 1, wx.EXPAND)

        self.SetSizer(self._sizer)

        self._sizer.Show(0, False)        
        self._sizer.Layout()

        methods = ["GetSelectedItem", "GetPointed", "GetHighlightPointed", "SetHighlightPointed",
                   "SetThumbOutline", "GetThumbOutline", "GetPointedItem", "GetItem",
                   "GetItemCount", "GetThumbWidth", "GetThumbHeight", "GetThumbBorder",
                   "ShowFileNames", "SetPopupMenu", "GetPopupMenu", "SetGlobalPopupMenu",
                   "GetGlobalPopupMenu", "SetSelectionColour", "GetSelectionColour",
                   "EnableDragging", "SetThumbSize", "GetThumbSize", "ShowDir",
                   "GetShowDir", "SetSelection", "GetSelection", "SetZoomFactor",
                   "GetZoomFactor", "SetCaptionFont", "GetCaptionFont", "GetItemIndex",
                   "InsertItem", "RemoveItemAt", "IsSelected", "Rotate", "ZoomIn", "ZoomOut",
                   "EnableToolTips", "GetThumbInfo", "GetOriginalImage"]

        for method in methods:
            setattr(self, method, getattr(self._scrolled, method))

        self._combochoices = []
        self._showcombo = False
        self._subsizer = subsizer
        
        self._combo.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        

    def ShowComboBox(self, show=True):
        """ Shows Or Hide The Top Folder ComboBox. """
        
        if show:
            self._showcombo = True
            self._sizer.Show(0, True)
            self._sizer.Layout()
        else:
            self._showcombo = False
            self._sizer.Show(0, False)
            self._sizer.Layout()

        self._scrolled.Refresh()


    def GetShowComboBox(self):
        """ Returns Whether The Folder ComboBox Is Shown Or Not. """
        
        return self._showcombo
    

    def OnComboBox(self, event):
        """ Handles The wx.EVT_COMBOBOX For The Folder ComboBox. """
        
        dirs = self._combo.GetValue()

        if os.path.isdir(opj(dirs)):
            self._scrolled.ShowDir(opj(dirs))
            
        event.Skip()


    def RecreateComboBox(self, newdir):
        """ Recreates The Folder ComboBox Every Time A New Directory Is Explored. """
        
        newdir = newdir.strip()
        
        if opj(newdir) in self._combochoices:
            return

        self.Freeze()

        self._sizer.Detach(0)
        self._subsizer.Detach(1)
        self._subsizer.Destroy()
        self._combo.Destroy()

        subsizer = wx.BoxSizer(wx.HORIZONTAL)
        
        self._combochoices.insert(0, opj(newdir))
        
        self._combo = wx.ComboBox(self, -1, value=newdir, choices=self._combochoices,
                                  style=wx.CB_DROPDOWN | wx.CB_READONLY)

        subsizer.Add((3, 0), 0)
        subsizer.Add(self._combo, 1, wx.EXPAND | wx.TOP, 3)
        subsizer.Add((3, 0), 0)
        self._sizer.Insert(0, subsizer, 0, wx.EXPAND | wx.ALL, 3)

        self._subsizer = subsizer
    
        self._subsizer.Layout()

        if not self.GetShowComboBox():
            self._sizer.Show(0, False)
            
        self._sizer.Layout()

        self._combo.Bind(wx.EVT_COMBOBOX, self.OnComboBox)
        
        self.Thaw()
        
        
# ---------------------------------------------------------------------------- #
# Class ScrolledThumbnail
# This Is The Main Class Implementation
# ---------------------------------------------------------------------------- #        

class ScrolledThumbnail(wx.ScrolledWindow):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size = wx.DefaultSize, thumboutline=THUMB_OUTLINE_RECT,
                 thumbfilter=THUMB_FILTER_IMAGES):
        """
        Default Class Constructor. Non-Default Parameters Are:
        - thumboutline: Outline Style For The ThumbnailCtrl, Which May Be:
          a) THUMB_OUTLINE_NONE: No Outline Is Drawn On Selection;
          b) THUMB_OUTLINE_FULL: Full Outline (Image + Caption) Is Drawn On
             Selection;
          c) THUMB_OUTLINE_RECT: Only Thumb Bounding Rect Is Drawn On Selection
             (Default);
          d) THUMB_OUTLINE_IMAGE: Inly Image Bounding Rect Is Drawn.

        - thumbfilter: Filter For Image/Video/Audio Files. Actually Only
          THUMB_FILTER_IMAGES Is Implemented.
        """
        
        wx.ScrolledWindow.__init__(self, parent, id, pos, size)

        self.SetThumbSize(96, 80)
        self._tOutline = thumboutline
        self._filter = thumbfilter
        self._selected = -1
        self._pointed = -1
        self._labelcontrol = None
        self._pmenu = None
        self._gpmenu = None
        self._dragging = False
        self._checktext = False
        self._orient = THUMB_VERTICAL

        self._tCaptionHeight = []
        self._selectedarray = []
        self._tTextHeight = 16
        self._tCaptionBorder = 8
        self._tOutlineNotSelected = True
        self._mouseeventhandled = False
        self._highlight = False
        self._zoomfactor = 1.4
        self.SetCaptionFont()
        self._items = []

        self._enabletooltip = False
        
        self._parent = parent
        
        self._selectioncolour = "#009EFF"
        self.grayPen = wx.Pen("#A2A2D2", 1, wx.SHORT_DASH)
        self.grayPen.SetJoin(wx.JOIN_MITER)
        self.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOX))

        t, b, s = getShadow()
        self.shadow = wx.MemoryDC()
        self.shadow.SelectObject(s)        
        
        self.ShowFileNames(True)

        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_LEFT_DCLICK, self.OnMouseDClick)
        self.Bind(wx.EVT_RIGHT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_RIGHT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)
        self.Bind(EVT_THUMBNAILS_THUMB_CHANGED, self.OnThumbChanged)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_PAINT, self.OnPaint)


    def GetSelectedItem(self, index):
        """ Returns The Selected Thumb. """

        return self.GetItem(self.GetSelection(index))


    def GetPointed(self):
        """ Returns The Pointed Thumb Index. """
        
        return self._pointed


    def GetHighlightPointed(self):
        """
        Returns Whether The Thumb Pointed Should Be Highlighted Or Not.
        Please Be Aware That This Functionality May Be Slow On Slower
        Computers.
        """
        
        return self._highlight


    def SetHighlightPointed(self, highlight=True):
        """
        Sets Whether The Thumb Pointed Should Be Highlighted Or Not.
        Please Be Aware That This Functionality May Be Slow On Slower
        Computers.
        """
        
        self._highlight = highlight


    def SetThumbOutline(self, outline):
        """ Sets The Thumb Outline Style On Selection. """

        if outline not in [THUMB_OUTLINE_NONE, THUMB_OUTLINE_FULL, THUMB_OUTLINE_RECT,
                           THUMB_OUTLINE_IMAGE]:
            raise "\nERROR: Outline Style Should Be One Of THUMB_OUTLINE_NONE, " \
                  "THUMB_OUTLINE_FULL, THUMB_OUTLINE_RECT, THUMB_OUTLINE_IMAGE"
        
        self._tOutline = outline        


    def GetThumbOutline(self):
        """ Returns The Thumb Outline Style On Selection. """
        
        return self._tOutline
    

    def GetPointedItem(self):
        """ Returns The Pointed Thumb. """
        
        return self.GetItem(self._pointed)
        

    def GetItem(self, index):
        """ Returns The Item At Position "index". """

        return index >= 0 and (index < len(self._items) and [self._items[index]] or [None])[0]


    def GetItemCount(self):
        """ Returns The Number Of Thumbs. """

        return len(self._items)


    def SortItems(self):
        """ Sorts The Items Accordingly To The CmpThumb Function. """

        self._items.sort(CmpThumb)        


    def GetThumbWidth(self):
        """ Returns The Thumb Width. """

        return self._tWidth


    def GetThumbHeight(self):
        """ Returns The Thumb Height. """

        return self._tHeight


    def GetThumbBorder(self):
        """ Returns The Thumb Border. """

        return self._tBorder
    
 
    def GetCaption(self):
        """ Not Used At Present. """

        return self._caption

    
    def SetLabelControl(self, statictext):
        """ Not Used At Present. """
        
        self._labelcontrol = statictext
        

    def ShowFileNames(self, show=True):
        """ Sets Whether The User Wants To Show File Names Under The Thumbs Or Not. """
        
        self._showfilenames = show
        

    def SetOrientation(self, orient=THUMB_VERTICAL):
        """ Not Used At Present. """
        
        self._orient = orient


    def SetPopupMenu(self, menu):
        """ Sets Thumbs Popup Menu When At Least One Thumb Is Selected. """
        
        self._pmenu = menu


    def GetPopupMenu(self):
        """ Returns Thumbs Popup Menu When At Least One Thumb Is Selected. """
        
        return self._pmenu        


    def SetGlobalPopupMenu(self, gpmenu):
        """ Sets Global Thumbs Popup Menu (No Need Of Thumb Selection). """
        
        self._gpmenu = gpmenu


    def GetGlobalPopupMenu(self):
        """ Returns Global Thumbs Popup Menu (No Need Of Thumb Selection). """
        
        return self._gpmenu
    

    def GetSelectionColour(self):
        """ Returns The Colour Used To Indicate A Selected Thumb. """
        
        return self._selectioncolour


    def SetSelectionColour(self, colour=None):
        """ Sets The Colour Used To Indicate A Selected Thumb. """
        
        if colour is None:
            colour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)

        self._selectioncolour = colour
        

    def EnableDragging(self, enable=True):
        """ Enables/Disables Thumbs Drag And Drop. """
        
        self._dragging = enable


    def EnableToolTips(self, enable=True):
        """ Globally Enables/Disables Thumb File Information. """

        self._enabletooltip = enable
        
        if not enable and hasattr(self, "_tipwindow"):
            self._tipwindow.Enable(False)
        

    def GetThumbInfo(self, thumb=-1):
        """ Returns Thumbs Information. """
        
        thumbinfo = None
        
        if thumb >= 0:
            thumbinfo = "Name: " + self._items[thumb].GetFileName() + "\n" \
                        "Size: " + self._items[thumb].GetFileSize() + "\n" \
                        "Modified: " + self._items[thumb].GetCreationDate() + "\n" \
                        "Thumb: " + str(self.GetThumbSize()[0:2])

        return thumbinfo
    

    def SetThumbSize(self, width, height, border=15):
        """ Sets The Thumb Size As Width, Height And Border. """
        
        if width > 350 or height > 280:
            return
        
        self._tWidth = width 
        self._tHeight = height
        self._tBorder = border
        self.SetScrollRate((self._tWidth + self._tBorder)/4,
                           (self._tHeight + self._tBorder)/4)
        self.SetSizeHints(self._tWidth + self._tBorder*2 + 16,
                          self._tHeight + self._tBorder*2 + 8)


    def GetThumbSize(self):
        """ Returns The Thumb Size As Width, Height And Border. """
        
        return self._tWidth, self._tHeight, self._tBorder


    def Clear(self):
        """ Clears ThumbnailCtrl. """
        
        self._items = []
        self._selected = -1
        self._selectedarray = []
        self.UpdateProp()
        self.Refresh()


    def ListDirectory(self, directory, fileExtList):
        "Gets List Of File Info Objects For Files Of Particular Extensions. "
        
        fileList = [os.path.normcase(f) for f in os.listdir(directory)]               
        fileList = [f for f in fileList \
                    if os.path.splitext(f)[1] in fileExtList]                          

        return fileList


    def EventGen1(self, filenames):
        """ Threaded Method To Load Images. Used Internally. """
        
        count = 0
        
        while count < len(filenames):

            if not self._isrunning:
                self._isrunning = False
                thread.exit()
                return
            
            self.LoadImages(filenames[count], count)
            if count < 4:
                self.Refresh()
            elif count%4 == 0:
                self.Refresh()
                
            count = count + 1

        self._isrunning = False            
        thread.exit()
        

    def LoadImages(self, newfile, imagecount):
        """ Methods That Load Images On ThumbnailCtrl. Used Internally. """

        if not self._isrunning:
            thread.exit()
            return
        
        pil = Image.open(newfile)
        originalsize = pil.size
        
        pil.thumbnail((300, 240))
        img = wx.EmptyImage(pil.size[0], pil.size[1])

        img.SetData(pil.convert("RGB").tostring())
        try:
            self._items[imagecount]._threadedimage = img
            self._items[imagecount]._originalsize = originalsize
            self._items[imagecount]._bitmap = img
        except:
            return
        

    def ShowDir(self, dir, filter=THUMB_FILTER_IMAGES):
        """ Shows Thumbnails For A Particular Folder. """
        
        self._dir = dir
        if filter >= 0:
            self._filter = filter
            
        self.SetCaption(self._dir)
        
        self._isrunning = False

        self._parent.RecreateComboBox(dir)
        
        # update items
        self._items = []

        filenames = self.ListDirectory(self._dir, extensions)
        myfiles = []

        for files in filenames:

            caption = (self._showfilenames and [files] or [""])[0]
            fullfile = opj(self._dir + "/" + files)
            myfiles.append(fullfile)
            stats = os.stat(fullfile)
            size = stats[6]
            
            if size < 1000:
                size = str(size) + " bytes"
            else:
                size = str(int(round(size/1000.0))) + " Kb"

            lastmod = time.strftime(TIME_FMT, time.localtime(stats[8]))
            
            if self._filter & THUMB_FILTER_IMAGES:
                self._items.append(Thumb(self, dir, files, caption, size, lastmod))

        items = self._items[:]
        self._items.sort(CmpThumb)

        newfiles = SortFiles(items, self._items, myfiles)
        self._locked = [0]*len(newfiles)

        self._isrunning = True
        
        thread.start_new_thread(self.EventGen1, (newfiles,))
        wx.MilliSleep(20)

        self._selectedarray = []
        self.UpdateProp()
        self.Refresh()


    def GetShowDir(self):
        """ Returns The Working Directory With Images. """
        
        return self._dir
    

    def SetSelection(self, value=-1):
        """ Sets Thumb Selection. """
        
        self._selected = value

        if value != -1:
            self._selectedarray = [value]
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)
            self.ScrollToSelected()
            self.Refresh()
            
        
    def SetZoomFactor(self, zoom=1.4):
        """ Sets The Zoom Factor. """
        
        if zoom <= 1.0:
            raise "\nERROR: Zoom Factor Must Be Greater Than 1.0"
        
        self._zoomfactor = zoom        


    def GetZoomFactor(self):
        """ Returns The Zoom Factor. """
        
        return self._zoomfactor
    

    def IsAudioVideo(self, fname):
        """ Not Used At Present. """

        return os.path.splitext(fname)[1].lower() in \
               [".mpg", ".mpeg", ".vob"]


    def IsVideo(self, fname):
        """ Not Used At Present. """

        return os.path.splitext(fname)[1].lower() in \
               [".m1v", ".m2v"]


    def IsAudio(self, fname):
        """ Not Used At Present. """

        return os.path.splitext(fname)[1].lower() in \
               [".mpa", ".mp2", ".mp3", ".ac3", ".dts", ".pcm"]
    

    def UpdateItems(self):
        """ Updates Thumb Items. """
        
        selected = self._selectedarray
        selectedfname = []
        selecteditemid = []
        
        for ii in xrange(len(self._selectedarray)):
            selectedfname.append(self.GetSelectedItem(ii).GetFileName())
            selecteditemid.append(self.GetSelectedItem(ii).GetId())
            
        self.UpdateShow()
        
        if len(selected) > 0:
            self._selectedarray = []            
            for ii in xrange(len(self._items)):
                for jj in xrange(len(selected)):
                    if self._items[ii].GetFileName() == selectedfname[jj] and \
                       self._items[ii].GetId() == selecteditemid[jj]:
                  
                        self._selectedarray.append(ii)
                        if len(self._selectedarray) == 1:
                            self.ScrollToSelected()

            if len(self._selectedarray) > 0:
                self.Refresh()
                eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
                self.GetEventHandler().ProcessEvent(eventOut)
  

    def SetCaption(self, caption=""):
        """ Not Used At Present. """
        
        self._caption = caption
        if self._labelcontrol:

            maxWidth = self._labelcontrol.GetSize().GetWidth()/8
            if len(caption) > maxWidth:
                caption = "..." + caption[len(caption) + 3 - maxWidth]

            self._labelcontrol.SetLabel(caption)

        eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_CAPTION_CHANGED, self.GetId())
        self.GetEventHandler().ProcessEvent(eventOut)


    def SetCaptionFont(self, font=None):
        """ Sets The Font For All The Thumb Captions. """
        
        if font is None:
            font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False)

        self._captionfont = font


    def GetCaptionFont(self):
        """ Returns The Font For All The Thumb Captions. """
        
        return self._captionfont
    

    def UpdateShow(self):
        """ Updates Thumb Items. """
        
        self.ShowDir(self._dir)


    def GetCaptionHeight(self, begRow, count=1):
        """ Returns The Height For The File Name Caption. """
        
        capHeight = 0
        for ii in xrange(begRow, begRow + count):
            if ii < len(self._tCaptionHeight):
                capHeight = capHeight + self._tCaptionHeight[ii]

        return capHeight*self._tTextHeight 


    def GetItemIndex(self, x, y):
        """ Returns The Thumb Index At Position (x, y). """
        
        col = (x - self._tBorder)/(self._tWidth + self._tBorder)

        if col >= self._cols:
            col = self._cols - 1
        
        row = -1
        y = y - self._tBorder
        
        while y > 0:

            row = row + 1
            y = y - (self._tHeight + self._tBorder + self.GetCaptionHeight(row))

        if row < 0:
            row = 0

        index = row*self._cols + col
        
        if index >= len(self._items):
            index = -1

        return index


    def UpdateProp(self, checkSize=True):
        """ Updates ThumbnailCtrl wx.ScrolledWindow And Visible Thumbs. """

        width = self.GetClientSize().GetWidth()
        self._cols = (width - self._tBorder)/(self._tWidth + self._tBorder)
        
        if self._cols == 0:
            self._cols = 1

        tmpvar = (len(self._items)%self._cols and [1] or [0])[0]
        self._rows = len(self._items)/self._cols + tmpvar
        
        self._tCaptionHeight = []

        for row in xrange(self._rows):

            capHeight = 0
            
            for col in xrange(self._cols):

                ii = row*self._cols + col
                
                if len(self._items) > ii and \
                   self._items[ii].GetCaptionLinesCount(self._tWidth - self._tCaptionBorder) > capHeight:
                    
                    capHeight = self._items[ii].GetCaptionLinesCount(self._tWidth - self._tCaptionBorder)

            self._tCaptionHeight.append(capHeight)

        self.SetVirtualSize((self._cols*(self._tWidth + self._tBorder) + self._tBorder,
                            self._rows*(self._tHeight + self._tBorder) + \
                            self.GetCaptionHeight(0, self._rows) + self._tBorder))
        
        self.SetSizeHints(self._tWidth + 2*self._tBorder + 16,
                          self._tHeight + 2*self._tBorder + 8 + \
                          (self._rows and [self.GetCaptionHeight(0)] or [0])[0])
        
        if checkSize and width != self.GetClientSize().GetWidth():
            self.UpdateProp(False)


    def InsertItem(self, thumb, pos):
        """ Inserts Thumb In A Specified Position "pos". """
        
        if pos < 0 or pos > len(self._items):
            self._items.append(thumb)
        else:
            self._items.insert(pos, thumb)
            
        self.UpdateProp()


    def RemoveItemAt(self, pos, count):
        """ Removes A Thumb In A Specified Position "pos". """

##        for ii in xrange(count):
##            if ii < len(self._items):
##                del self._items[pos+ii]

        del self._items[pos:]
        
        self.UpdateProp()


    def GetPaintRect(self):
        """ Returns The Paint Bounding Rect For The OnPaint() Method. """
        
        size = self.GetClientSize()
        paintRect = wx.Rect(0, 0, size.GetWidth(), size.GetHeight())
        paintRect.x, paintRect.y = self.GetViewStart()
        xu, yu = self.GetScrollPixelsPerUnit()
        paintRect.x = paintRect.x*xu
        paintRect.y = paintRect.y*yu
        
        return paintRect


    def IsSelected(self, indx):
        """ Returns Whether A Thumb Is Selected Or Not. """

        return self._selectedarray.count(indx) != 0
    

    def GetSelection(self, selIndex=-1):
        """ Returns The Selected Thumb. """
        
        return (selIndex == -1 and [self._selected] or \
                [self._selectedarray[selIndex]])[0]


    def GetOriginalImage(self, index=None):
        """ Returns The Bitmap Associated To A Thumb. """

        if index is None:
            index = self.GetSelection()
            
        return self._items[index].GetOriginalImage()


    def ScrollToSelected(self):
        """ Scrolls The wx.ScrolledWindow To The Thumb Selected. """
        
        if self.GetSelection() == -1:
            return

        # get row
        row = self.GetSelection()/self._cols
        # calc position to scroll view
        
        paintRect = self.GetPaintRect()
        y1 = row*(self._tHeight + self._tBorder) + self.GetCaptionHeight(0, row)
        y2 = y1 + self._tBorder + self._tHeight + self.GetCaptionHeight(row)

        if y1 < paintRect.GetTop():
            sy = y1 # scroll top
        elif y2 > paintRect.GetBottom():
            sy = y2 - paintRect.height # scroll bottom
        else:
            return

        # scroll view
        xu, yu = self.GetScrollPixelsPerUnit()
        sy = sy/yu + (sy%yu and [1] or [0])[0] # convert sy to scroll units
        x, y = self.GetViewStart()
        
        self.Scroll(x,sy)


    def CalculateBestCaption(self, dc, caption, sw, width):
        """ Calculate The Best Caption Based On Actual Zoom. """

        caption = caption + "..."
        
        while sw > width:
            caption = caption[1:]
            sw, sh = dc.GetTextExtent(caption)
            
        return "..." + caption[0:-3]
  

    def DrawThumbnail(self, bmp, thumb, index):
        """ Draws The Visible Thumbnails. """

        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.BeginDrawing()
        
        x = self._tBorder/2
        y = self._tBorder/2

        # background
        dc.SetPen(wx.Pen(wx.BLACK, 0, wx.TRANSPARENT))
        dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.SOLID))
        dc.DrawRectangle(0, 0, bmp.GetWidth(), bmp.GetHeight())

        # image
        img = thumb.GetBitmap(self._tWidth, self._tHeight)
        ww = img.GetWidth()
        hh = img.GetHeight()

        if index == self.GetPointed() and self.GetHighlightPointed():
            
            img = img.ConvertToImage()
            pil = Image.new('RGB', (img.GetWidth(), img.GetHeight()))
            pil.fromstring(img.GetData())
            enh = ImageEnhance.Brightness(pil)
            enh = enh.enhance(1.5)
            img.SetData(enh.convert('RGB').tostring())
            img = img.ConvertToBitmap()
        
        imgRect = wx.Rect(x + (self._tWidth - img.GetWidth())/2,
                          y + (self._tHeight - img.GetHeight())/2,
                          img.GetWidth(), img.GetHeight())

        dc.Blit(imgRect.x+5, imgRect.y+5, imgRect.width, imgRect.height, self.shadow, 245-ww, 245-hh)        
        dc.DrawBitmap(img, imgRect.x, imgRect.y, True)

        colour = self.GetSelectionColour()
        selected = self.IsSelected(index)

        # outline
        if self._tOutline != THUMB_OUTLINE_NONE and (self._tOutlineNotSelected or self.IsSelected(index)):

            dotrect = wx.Rect()
            dotrect.x = x - 2
            dotrect.y = y - 2
            dotrect.width = bmp.GetWidth() - self._tBorder + 4
            dotrect.height = bmp.GetHeight() - 2*self._tBorder + 4
        
            dc.SetPen(wx.Pen((self.IsSelected(index) and [colour] or [wx.LIGHT_GREY])[0],
                             0, wx.SOLID))       
            dc.SetBrush(wx.Brush(wx.BLACK, wx.TRANSPARENT))
        
            if self._tOutline == THUMB_OUTLINE_FULL or self._tOutline == THUMB_OUTLINE_RECT:

                imgRect.x = x
                imgRect.y = y
                imgRect.width = bmp.GetWidth() - self._tBorder
                imgRect.height = bmp.GetHeight() - self._tBorder

                if self._tOutline == THUMB_OUTLINE_RECT:
                    imgRect.height = self._tHeight             

            dc.SetBrush(wx.TRANSPARENT_BRUSH)

            if selected:

                dc.SetPen(self.grayPen)
                dc.DrawRectangleRect(dotrect)
                
                dc.SetPen(wx.Pen(wx.WHITE))
                dc.DrawRectangle(imgRect.x, imgRect.y,
                                 imgRect.width, imgRect.height)

                pen = wx.Pen((selected and [colour] or [wx.LIGHT_GREY])[0], 2)
                pen.SetJoin(wx.JOIN_MITER)
                dc.SetPen(pen)
                dc.DrawRectangle(imgRect.x - 1, imgRect.y - 1,
                                 imgRect.width + 3, imgRect.height + 3)
            else:
                dc.SetPen(wx.Pen(wx.LIGHT_GREY))
                dc.DrawRectangle(imgRect.x - 1, imgRect.y - 1,
                             imgRect.width + 2, imgRect.height + 2)            
            
        # draw caption

        if self._showfilenames:
            textWidth = 0
            dc.SetFont(self.GetCaptionFont())
            mycaption = thumb.GetCaption(0)
            sw, sh = dc.GetTextExtent(mycaption)   

            if sw > self._tWidth:
                mycaption = self.CalculateBestCaption(dc, mycaption, sw, self._tWidth)
                sw = self._tWidth
            
            textWidth = sw + 8                
            tx = x + (self._tWidth - textWidth)/2
            ty = y + self._tHeight
            txtcolour = "#7D7D7D"
            dc.SetTextForeground(txtcolour) 

            tx = x + (self._tWidth - sw)/2
            if hh >= self._tHeight:
                ty = y + self._tHeight + (self._tTextHeight - sh)/2 + 3
            else:
                ty = y + hh + (self._tHeight-hh)/2 + (self._tTextHeight - sh)/2 + 3
                
            dc.DrawText(mycaption, tx, ty)
  
        dc.EndDrawing()
        dc.SelectObject(wx.NullBitmap)


    def OnPaint(self, event):
        """ Handles The wx.EVT_PAINT Event For ThumbnailCtrl. """
        
        paintRect = self.GetPaintRect()
        
        dc = wx.PaintDC(self)
        self.PrepareDC(dc)
        dc.BeginDrawing()

        dc.SetPen(wx.Pen(wx.BLACK, 0, wx.TRANSPARENT))
        dc.SetBrush(wx.Brush(self.GetBackgroundColour(), wx.SOLID))

        w, h = self.GetClientSize()        

        # items
        row = -1
        xwhite = self._tBorder
        
        for ii in xrange(len(self._items)):

            col = ii%self._cols

            if col == 0:
                row = row + 1

            xwhite = ((w - self._cols*(self._tWidth + self._tBorder)))/(self._cols+1)
            tx = xwhite + col*(self._tWidth + self._tBorder)

            ty = self._tBorder/2 + row*(self._tHeight + self._tBorder) + \
                 self.GetCaptionHeight(0, row)
            tw = self._tWidth + self._tBorder
            th = self._tHeight + self.GetCaptionHeight(row) + self._tBorder
            # visible?
            if not paintRect.Intersects(wx.Rect(tx, ty, tw, th)):
                continue
          
            thmb = wx.EmptyBitmap(tw, th)
            self.DrawThumbnail(thmb, self._items[ii], ii)
            dc.DrawBitmap(thmb, tx, ty)
  
        rect = wx.Rect(xwhite, self._tBorder/2,
                       self._cols*(self._tWidth + self._tBorder),
                       self._rows*(self._tHeight + self._tBorder) + \
                       self.GetCaptionHeight(0, self._rows))
        
        w = max(self.GetClientSize().GetWidth(), rect.width)
        h = max(self.GetClientSize().GetHeight(), rect.height)
        dc.DrawRectangle(0, 0, w, rect.y)
        dc.DrawRectangle(0, 0, rect.x, h)
        dc.DrawRectangle(rect.GetRight(), 0, w - rect.GetRight(), h + 50)
        dc.DrawRectangle(0, rect.GetBottom(), w, h - rect.GetBottom() + 50)
       
        col = len(self._items)%self._cols

        if col > 0:
            rect.x = rect.x + col*(self._tWidth + self._tBorder)
            rect.y = rect.y + (self._rows - 1)*(self._tHeight + self._tBorder) + \
                     self.GetCaptionHeight(0, self._rows - 1)
            dc.DrawRectangleRect(rect)

        dc.EndDrawing()


    def OnResize(self, event):
        """ Handles The wx.EVT_SIZE Event For ThumbnailCtrl. """

        self.UpdateProp()
        self.ScrollToSelected()
        self.Refresh()


    def OnMouseDown(self, event):
        """ Handles The wx.EVT_LEFT_DOWN And wx.EVT_RIGHT_DOWN Events For ThumbnailCtrl. """
        
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)
        # get item number to select
        lastselected = self._selected
        self._selected = self.GetItemIndex(x, y)
        
        self._mouseeventhandled = False
        update = False

        if event.ControlDown():
            if self._selected == -1:
                self._mouseeventhandled = True
            elif not self.IsSelected(self._selected):
                self._selectedarray.append(self._selected)
                update = True
                self._mouseeventhandled = True

        elif event.ShiftDown():
            if self._selected != -1:
                begindex = self._selected
                endindex = lastselected
                if lastselected < self._selected:
                    begindex = lastselected
                    endindex = self._selected
                self._selectedarray = []

                for ii in xrange(begindex, endindex+1):
                    self._selectedarray.append(ii)

                update = True
                
            self._selected = lastselected
            self._mouseeventhandled = True
                    
        else:

            if self._selected == -1:
                update = len(self._selectedarray) > 0
                self._selectedarray = []
                self._mouseeventhandled = True
            elif len(self._selectedarray) <= 1:
                try:
                    update = len(self._selectedarray)== 0 or self._selectedarray[0] != self._selected
                except:
                    update = True
                self._selectedarray = []
                self._selectedarray.append(self._selected)
                self._mouseeventhandled = True
        
        if update:
            self.ScrollToSelected()
            self.Refresh()
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)

        self.SetFocus()
        

    def OnMouseUp(self, event):
        """ Handles The wx.EVT_LEFT_UP And wx.EVT_RIGHT_UP Events For ThumbnailCtrl. """
        
        # get item number to select
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)
        lastselected = self._selected
        self._selected = self.GetItemIndex(x,y)

        if not self._mouseeventhandled:
            # set new selection
            if event.ControlDown():
                if self._selected in self._selectedarray:
                    self._selectedarray.remove(self._selected)
                    
                self._selected = -1
            else:
                self._selectedarray = []
                self._selectedarray.append(self._selected)

            self.ScrollToSelected()
            self.Refresh()
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_SEL_CHANGED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)

        # Popup menu
        if event.RightUp():
            if self._selected >= 0 and self._pmenu:
                self.PopupMenu(self._pmenu, event.GetPosition())
            elif self._selected >= 0 and not self._pmenu and self._gpmenu:
                self.PopupMenu(self._gpmenu, event.GetPosition())
            elif self._selected == -1 and self._gpmenu:
                self.PopupMenu(self._gpmenu, event.GetPosition())

        if event.ShiftDown():
            self._selected = lastselected


    def OnMouseDClick(self, event):
        """ Handles The wx.EVT_LEFT_DCLICK Event For ThumbnailCtrl. """
        
        eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_DCLICK, self.GetId())
        self.GetEventHandler().ProcessEvent(eventOut)


    def OnMouseMove(self, event):
        """ Handles The wx.EVT_MOTION Event For ThumbnailCtrl. """
        
        # -- drag & drop --
        if self._dragging and event.Dragging() and len(self._selectedarray) > 0:

            files = wx.FileDataObject()
            for ii in xrange(len(self._selectedarray)):
                files.AddFile(self.GetSelectedItem(ii).GetFileName())
                
            source = wx.DropSource(self)
            source.SetData(files)
            source.DoDragDrop(wx.Drag_DefaultMove)

        # -- light-effect --
        x = event.GetX()
        y = event.GetY()
        x, y = self.CalcUnscrolledPosition(x, y)

        # get item number
        sel = self.GetItemIndex(x, y)

        if sel == self._pointed:
            if self._enabletooltip and sel >= 0:
                if not hasattr(self, "_tipwindow"):
                    self._tipwindow = wx.ToolTip(self.GetThumbInfo(sel))
                    self._tipwindow.SetDelay(1000)
                    self.SetToolTip(self._tipwindow)
                else:
                    self._tipwindow.SetDelay(1000)
                    self._tipwindow.SetTip(self.GetThumbInfo(sel))
                    
            event.Skip()
            return

        if self._enabletooltip:
            if hasattr(self, "_tipwindow"):
                self._tipwindow.Enable(False)
                
        # update thumbnail
        self._pointed = sel

        if self._enabletooltip and sel >= 0:
            if not hasattr(self, "_tipwindow"):
                self._tipwindow = wx.ToolTip(self.GetThumbInfo(sel))
                self._tipwindow.SetDelay(1000)
                self._tipwindow.Enable(True)
                self.SetToolTip(self._tipwindow)
            else:
                self._tipwindow.SetDelay(1000)
                self._tipwindow.Enable(True)
                self._tipwindow.SetTip(self.GetThumbInfo(sel))
            
        self.Refresh()
        eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_POINTED, self.GetId())
        self.GetEventHandler().ProcessEvent(eventOut)
        event.Skip()
        

    def OnMouseLeave(self, event):
        """ Handles The wx.EVT_LEAVE_WINDOW Event For ThumbnailCtrl. """

        if self._pointed != -1:

            self._pointed = -1
            self.Refresh()
            eventOut = ThumbnailEvent(wxEVT_THUMBNAILS_POINTED, self.GetId())
            self.GetEventHandler().ProcessEvent(eventOut)
  

    def OnThumbChanged(self, event):
        """ Handles The wxEVT_THUMBNAILS_THUMB_CHANGED Event For ThumbnailCtrl. """
        
        for ii in xrange(len(self._items)):
            if self._items[ii].GetFileName() == event.GetString():

                self._items[ii].SetFilename(self._items[ii].GetFileName())
                if event.GetClientData():

                    img = wx.Image(event.GetClientData())
                    self._items[ii].SetImage(img)
##                    delete img

        self.Refresh()


    def OnChar(self, event):
        """
        Handles The wx.EVT_CHAR Event For ThumbnailCtrl. You Have These Choices:

        (1) "d" Key Rotates 90 Degrees Clockwise The Selected Thumbs;
        (2) "s" Key Rotates 90 Degrees Counter-Clockwise The Selected Thumbs;
        (3) "a" Key Rotates 180 Degrees The Selected Thumbs;
        (4) "Del" Key Deletes The Selected Thumbs;
        (5) "+" Key Zooms In;
        (6) "-" Key Zooms Out.
        """

        if event.m_keyCode == 115:
            self.Rotate()
        elif event.m_keyCode == 100:
            self.Rotate(270)
        elif event.m_keyCode == 97:
            self.Rotate(180)
        elif event.m_keyCode == wx.WXK_DELETE:
            self.DeleteFiles()
        elif event.m_keyCode == 43:
            self.ZoomIn()
        elif event.m_keyCode == 45:
            self.ZoomOut()
            
        event.Skip()
                            

    def Rotate(self, angle=90):
        """ Rotates The Selected Thumbs By The Angle Specified By "angle" (In Degrees!!!). """
        
        wx.BeginBusyCursor()

        count = 0
        selected = []
        
        for ii in xrange(len(self._items)):
            if self.IsSelected(ii):
                selected.append(self._items[ii])

        dlg = wx.ProgressDialog("Thumbnail Rotation",
                                "Rotating Thumbnail... Please Wait",
                                maximum = len(selected)+1,
                                parent=None)

        for thumb in selected:
            count = count + 1
            if TN_USE_PIL:
                newangle = thumb.GetRotation()*180/pi + angle
                fil = opj(self._dir + "/" + thumb.GetFileName())
                pil = Image.open(fil).rotate(newangle)
                img = wx.EmptyImage(pil.size[0], pil.size[1])
                img.SetData(pil.convert('RGB').tostring())
                thumb.SetRotation(newangle*pi/180)
            else:
                img = thumb._threadedimage
                newangle = thumb.GetRotation() + angle*pi/180
                thumb.SetRotation(newangle)
                img = img.Rotate(newangle, (img.GetWidth()/2, img.GetHeight()/2), True)
                
            thumb.SetRotatedImage(img)
            dlg.Update(count)

        wx.EndBusyCursor()
        dlg.Destroy()
        
        if self.GetSelection() != -1:
            self.Refresh()                


    def DeleteFiles(self):
        """ Deletes The Selected Thumbs And Their Associated Files. Be Careful!!! """

        dlg = wx.MessageDialog(self, 'Are You Sure You Want To Delete The Files?',
                               'Confirmation',
                               wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        
        if dlg.ShowModal() == wx.ID_YES:
            errordelete = []
            count = 0

            dlg.Destroy()
            
            wx.BeginBusyCursor()
            
            for ii in xrange(len(self._items)):
                if self.IsSelected(ii):
                    thumb = self._items[ii]
                    files = self._items[ii].GetFileName()
                    filename = opj(self._dir + "/" + files)
                    try:
                        os.remove(filename)
                        count = count + 1
                    except:
                        errordelete.append(files)                        

            wx.EndBusyCursor()

            if errordelete:
                strs = "Unable To Remove The Following Files:\n\n"
                for fil in errordelete:
                    strs = strs + fil + "\n"
                strs = strs + "\n"
                strs = strs + "Please Check Your Privileges And File Permission."
                dlg = wx.MessageDialog(self, strs,
                               'Error In File Deletion',
                               wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()

            if count:
                self.UpdateShow()


    def OnMouseWheel(self, event):
        """
        Handles The wx.EVT_MOUSEWHEEL Event For ThumbnailCtrl.
        If You Hold Down The Ctrl Key, You Can Zoom In/Out With The Mouse Wheel.
        """
        
        if event.ControlDown():
            if event.GetWheelRotation() > 0:
                self.ZoomIn()
            else:
                self.ZoomOut()
        else:
            event.Skip()


    def ZoomOut(self):
        """ Zooms The Thumbs Out. """
        
        w, h, b = self.GetThumbSize()

        if w < 40 or h < 40:
            return
        
        zoom = self.GetZoomFactor()
        neww = float(w)/zoom
        newh = float(h)/zoom

        self.SetThumbSize(int(neww), int(newh))
        self.OnResize(None)
        self._checktext = True
        
        self.Refresh()


    def ZoomIn(self):
        """ Zooms The Thumbs In. """
        
        size = self.GetClientSize()
        w, h, b = self.GetThumbSize()
        zoom = self.GetZoomFactor()
        
        if w*zoom + b > size.GetWidth() or h*zoom + b > size.GetHeight():
            if w*zoom + b > size.GetWidth():
                neww = size.GetWidth() - 2*self._tBorder
                newh = (float(h)/w)*neww
            else:
                newh = size.GetHeight() - 2*self._tBorder
                neww = (float(w)/h)*newh

        else:
            neww = float(w)*zoom
            newh = float(h)*zoom

        self.SetThumbSize(int(neww), int(newh))
        self.OnResize(None)
        self._checktext = True

        self.Refresh()
