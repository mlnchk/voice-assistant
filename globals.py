import wx
import json
import os.path

AppIconBitmap = None
Content = None

Settings = {
    'lang' : 'en',
    'pathname_regexp' : (True, r'.*/(.*)_assignsubmission_file_/.*', 1),
    'rendering_quality' : 0
}

def CheckExisting(filePath):
    if filePath == None:
        return False
    if not os.path.isfile(filePath):
        return False
    return True

def OpenFile(filePath):
    if not CheckExisting(filePath):
        return None
    mode = {
        'mode' : 'r',
        'encoding' : 'utf8'
    }
    with open(filePath, **mode) as content:
        data = content.read()
    return data

def LoadResources():
    loadIcon()
    loadContent()

def loadIcon():
    global AppIconBitmap
    AppIconBitmap = wx.Bitmap('gui_resources/icon.ico')

def loadContent():
    global Content
    contentFile = OpenFile('gui_resources/content.json')
    if contentFile != None:
        Content = json.loads(contentFile)

def Get(what):
    if Content == None:
        return 'n/a'
    return Content[what]

def GetVersion():
    return Get('version')

def GetAvailableLanguages():
    return Get('langs')

def GetText(element, lang):
    if Content == None:
        return 'n/a'
    if element not in Content['text']:
        return 'n/a'
    if lang not in Content['text'][element]:
        return 'n/a'
    return Content['text'][element][lang]