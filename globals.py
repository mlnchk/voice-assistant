import wx

AppIconBitmap = None
Content = None

Settings = {
    'locale' : 'en'
}

def LoadResources():
    loadIcon()

def loadIcon():
    global AppIconBitmap
    AppIconBitmap = wx.Bitmap('gui_resources/icon.ico')