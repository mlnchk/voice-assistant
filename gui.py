import wx

import globals as glo
import AudioRecorder as arec

PUBSUB_STOP_MESSAGE = 'stop_record'

def process_path(pathname):
    return pathname

class AppCore(wx.App):

    def OnInit(self):
        glo.LoadResources()
        mf = MainFrame()
        self.SetTopWindow(mf)
        mf.Show()
        return True

class AutoID :

    def __init__(self):
        self.id = 0

    def GetID(self):
        self.id += 1
        return self.id

class MainFrame (wx.Frame):

    class element :

        def __init__ (self, obj, style = None, child = None):
            self.obj = obj
            self.style = style
            self.child = child

        def Compose(self, parent = None):
            if self.style == None:
                self.style = parent.style
            if self.child != None:
                for c in self.child:
                    c.Compose(self)
            if parent != None:
                parent.obj.Add(self.obj, **self.style)

    def __init__ (self):
        self.recorder = arec.AudioRecorder('default')
        wx.Frame.__init__(self,
                          parent = None,
                          style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.icon = wx.Icon(glo.AppIconBitmap)
        self.autoID = AutoID()
        self.aboutDialog = self.AboutDialog(self)
        self.__InitStateFields()
        self.__InitUI()
        self.UpdateContent()
        self.__SetState(self.STATE_RESET)

    def __InitStateFields(self):
        self.STATE_RESET = self.autoID.GetID()
        self.STATE_RECORD = self.autoID.GetID()
        self.STATE_STOP = self.autoID.GetID()
        self.STATE_LOADING = self.autoID.GetID()

        self.availableLangs = glo.GetAvailableLanguages()

        self.fileOpened = False
        self.fileChanged = False
        self.fileSaved = False
        self.state = self.STATE_RESET

        def state_reset():
            self.state = self.STATE_RESET
            self.fileOpened = False
            self.fileChanged = False
            self.fileSaved = False
            self.panel.FindWindow('input_device_choice').Enable()
            self.panel.FindWindow('record_button').Enable()
            self.panel.FindWindow('stop_button').Disable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(True)

        def state_record():
            self.state = self.STATE_RECORD
            self.fileOpened = True
            self.fileChanged = True
            self.fileSaved = False
            self.panel.FindWindow('input_device_choice').Disable()
            self.panel.FindWindow('record_button').Disable()
            self.panel.FindWindow('stop_button').Enable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(False)

        def state_stop():
            self.state = self.STATE_STOP
            self.panel.FindWindow('input_device_choice').Enable()
            self.panel.FindWindow('record_button').Enable()
            self.panel.FindWindow('stop_button').Disable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(True)

        def state_loading():
            self.state = self.STATE_LOADING
            self.panel.FindWindow('input_device_choice').Disable()
            self.panel.FindWindow('record_button').Disable()
            self.panel.FindWindow('stop_button').Disable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(False)

        self.statesHandlers = {
            self.STATE_RESET   : state_reset,
            self.STATE_RECORD  : state_record,
            self.STATE_STOP    : state_stop,
            self.STATE_LOADING : state_loading
        }

    def __InitUI (self):
        self.panel = wx.Panel(self)
        self.__SetLayout()
        self.__Bind()

    def __SetLayout (self):
        panel = self.panel
        self.__ComposeWidgets(panel)
        self.__ComposeMenuBar(panel)
        self.__ComposeStatusBar(panel)

    def __ComposeWidgets (self, panel):
        element = self.element
        self.elements = element(
            wx.BoxSizer(wx.VERTICAL),
            { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
            [
                element(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        element(wx.StaticText(panel, name = 'session_name_label')),
                        element(wx.TextCtrl(panel, name = 'session_name_text_control'))
                    ]
                ),
                element(
                    wx.StaticLine(panel),
                    { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                ),
                element(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        element(wx.StaticText(panel, name = 'input_device_label')),
                        element(wx.Choice(panel, name = 'input_device_choice'))
                    ]
                ),
                element(
                    wx.StaticLine(panel),
                    { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                ),
                element(
                    wx.BoxSizer(wx.HORIZONTAL),
                    { 'proportion' : 1, 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        element(wx.Button(panel, name = 'record_button')),
                        element(wx.Button(panel, name = 'stop_button'))
                    ]
                ),
            ]
        )
        self.elements.Compose()
        panel.SetSizer(self.elements.obj)

    def __ComposeMenuBar (self, panel):
        mb = self.menuBar = wx.MenuBar()

        self.MENU_BAR_NEW = self.autoID.GetID()
        self.MENU_BAR_OPEN = self.autoID.GetID()
        self.MENU_BAR_SAVE = self.autoID.GetID()
        self.MENU_BAR_SAVE_AS = self.autoID.GetID()
        self.MENU_BAR_EXIT = self.autoID.GetID()
        self.MENU_BAR_LANGUAGE = self.autoID.GetID()
        self.MENU_BAR_ABOUT = self.autoID.GetID()

        self.MENU_BAR_LANGS = {}
        LanguageSubmenu = wx.Menu()

        menus = self.menus = [
            (wx.Menu(), 'menu_file'),
            (wx.Menu(), 'menu_settings'),
            (wx.Menu(), 'menu_help')
        ]

        self.menuItems = [
            {
                'menu' : menus[0][0],
                'name' : 'menu_bar_new',
                'params' : {
                    'id' : self.MENU_BAR_NEW
                }
            },
            {
                'menu' : menus[0][0],
                'name' : 'menu_bar_open',
                'params' : {
                    'id' : self.MENU_BAR_OPEN
                }
            },
            {
                'menu' : menus[0][0],
                'name' : 'menu_bar_save',
                'params' : {
                    'id' : self.MENU_BAR_SAVE
                }
            },
            {
                'menu' : menus[0][0],
                'name' : 'menu_bar_save_as',
                'params' : {
                    'id' : self.MENU_BAR_SAVE_AS
                }
            },
            {
                'menu' : menus[0][0],
                'params' : {
                    'id' : wx.ID_SEPARATOR,
                    'kind' : wx.ITEM_SEPARATOR
                }
            },
            {
                'menu' : menus[0][0],
                'name' : 'menu_bar_exit',
                'params' : {
                    'id' : self.MENU_BAR_EXIT
                }
            },
            {
                'menu' : menus[1][0],
                'name' : 'menu_bar_language',
                'params' : {
                    'id' : self.MENU_BAR_LANGUAGE,
                    'subMenu' : LanguageSubmenu
                }
            },
            {
                'menu' : menus[2][0],
                'name' : 'menu_bar_about',
                'params' : {
                    'id' : self.MENU_BAR_ABOUT
                }
            }
        ]

        for lang in self.availableLangs:
            langID = self.autoID.GetID()
            self.MENU_BAR_LANGS[langID] = lang[0]
            self.menuItems.append(
                {
                    'menu' : LanguageSubmenu,
                    'params' : {
                        'id' : langID,
                        'item' : lang[0],
                        'helpString' : lang[1]
                    }
                }
            )

        for menuItem in self.menuItems:
            params = menuItem['params']
            if 'item' not in params:
                params['item'] = 'default'
            menuItem['object'] = menuItem['menu'].Append(**params)

        self.SetMenuBar(mb)

    def __ComposeStatusBar (self, panel):
        sb = self.statusBar = wx.StatusBar(panel)
        sb.SetFieldsCount(2)
        sb.SetStatusWidths([-3, -1])
        sb.SetStatusText('', 0)
        sb.SetStatusText('', 1)
        self.SetStatusBar(sb)

    def __SetContent (self):
        self.SetIcon(self.icon)
        lang = glo.Settings['lang']
        self.SetTitle(glo.GetText('main_frame_title', lang))
        self.__SetWidgetsContent(lang)
        self.__SetMenuBarContent(lang)

    def __SetWidgetsContent(self, lang):
        self.__SetDevicesList(self.panel.FindWindow('input_device_choice'))
        for element in self.panel.GetChildren():
            name = element.GetName()
            text = glo.GetText(name, lang)
            if text != 'n/a':
                element.SetLabel(text)

    def __SetDevicesList(self, element):
        # self.devices = audio.get_devices()
        # devices = [x['name'] for x in self.devices]
        # element.SetItems(devices)
        # default = audio.get_devices('input')
        # n = element.FindString(default['name'], True)
        # element.SetSelection(n)
        return

    def __SetMenuBarContent(self, lang):
        menus = []
        for menu in self.menus:
            menus.append((menu[0], glo.GetText(menu[1], lang)))
        for menuItem in self.menuItems:
            if 'name' in menuItem:
                name = menuItem['name']
                text = glo.GetText(name, lang)
                obj = menuItem['object']
                obj.SetItemLabel(text[0])
                obj.SetHelp(text[1])
        self.menuBar.SetMenus(menus)

    def __Bind(self):
        panel = self.panel
        self.__BindWidgets(panel)
        self.__BindMenus(panel)
        self.Bind(wx.EVT_PAINT, self.__OnRepaint)
        self.Bind(wx.EVT_CLOSE, self.__OnClose)

    def __BindWidgets(self, panel):
        panel.FindWindow('input_device_choice').Bind(wx.EVT_CHOICE, self.__SetDevice)
        panel.FindWindow('record_button').Bind(wx.EVT_BUTTON, self.__RecordBtn)
        panel.FindWindow('stop_button').Bind(wx.EVT_BUTTON, self.__StopBtn)

    def __SetDevice(self, event):
        self.device = event.GetInt()

    def __RecordBtn(self, event):
        self.__SetState(self.STATE_RECORD)
        self.recorder.start()

    def __StopBtn(self, event):
        self.recorder.stop()
        self.__SetState(self.STATE_STOP)

    def __BindMenus(self, panel):
        menuHandlers = {
            self.MENU_BAR_NEW  : self.__Reset,
            self.MENU_BAR_OPEN : self.__Open,
            self.MENU_BAR_EXIT : self.__Exit,
            self.MENU_BAR_ABOUT: self.__InvokeAboutWindow
        }
        for lang in self.MENU_BAR_LANGS:
            menuHandlers[lang] = self.__ChangeLanguage(lang)

        for menuItem in self.menuItems:
            obj = menuItem['object']
            id = obj.GetId()
            if id in menuHandlers:
                self.Bind(wx.EVT_MENU, menuHandlers[id], obj)

    def __ChangeLanguage(self, langID):
        lang = self.MENU_BAR_LANGS[langID]
        def cl(event):
            glo.Settings['lang'] = lang
            self.UpdateContent()
        return cl

    def __Reset(self, event):
        self.__SetState(self.STATE_RESET)

    def __Open(self, event):
        lang = glo.Settings['lang']
        with wx.FileDialog(
            self,
            glo.GetText('file_open_dialog_title', lang),
            wildcard = glo.GetText('file_open_dialog_wildcard', lang) + '(*.*)|*.*',
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = process_path(fileDialog.GetPath())
            self.panel.FindWindow('session_name_text_control').SetValue(pathname)

    def __Exit(self, event):
        self.Close()

    def __InvokeAboutWindow(self, event):
        self.aboutDialog.ShowModal()

    def UpdateContent(self):
        self.__SetContent()
        self.Refresh()
        self.Update()
        self.aboutDialog.UpdateContent()

    def __SetState(self, state):
        if state in self.statesHandlers:
            self.statesHandlers[state]()

    def __OnRepaint (self, event):
        sizer = self.panel.GetSizer()
        sizer.Layout()
        sizer.Fit(self)

    def __OnClose(self, event):
        if self.state == self.STATE_RECORD:
            self.__StopBtn(event)
        if event.CanVeto() and (self.fileChanged and not self.fileSaved):
            if wx.MessageBox("The file has not been saved... continue closing?",
                             "Please confirm",
                             wx.ICON_QUESTION | wx.YES_NO) != wx.YES:
                event.Veto()
                return

        self.Destroy()

    class AboutDialog(wx.Dialog):

        def __init__(self, parent):
            super().__init__(parent = parent,
                             style = wx.CAPTION)
            self.__InitUI()
            self.__Bind()
            self.UpdateContent()

        def __InitUI(self):
            panel = self.panel = wx.Panel(self)
            element = MainFrame.element
            elements = element(
                wx.BoxSizer(wx.VERTICAL),
                { 'flag' : wx.ALL, 'border' : 3 },
                [
                    element(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.CENTER, 'border' : 3 },
                        [
                            element(
                                wx.StaticBitmap(panel, bitmap = glo.AppIconBitmap)
                            ),
                            element(
                                wx.StaticText(panel, name = 'about_dialog_text')
                            ),
                            element(
                                wx.Button(panel, name = 'about_dialog_close_button')
                            )
                        ]
                    )
                ]
            )
            elements.Compose()
            panel.SetSizer(elements.obj)

        def __SetContent(self):
            lang = glo.Settings['lang']
            self.SetTitle(glo.GetText('about_frame_title', lang))
            for element in self.panel.GetChildren():
                name = element.GetName()
                text = glo.GetText(name, lang)
                variable = glo.GetText(name, 'var')
                varstr = ''
                if variable != 'n/a':
                    varstr = glo.Get(variable)
                if text != 'n/a':
                    element.SetLabel(text + varstr)

        def __Bind(self):
            self.Bind(wx.EVT_PAINT, self.__OnRepaint)
            self.Bind(wx.EVT_BUTTON, self.__CloseBtnClick)

        def UpdateContent(self):
            self.__SetContent()
            self.Refresh()
            self.Update()

        def __OnRepaint(self, event):
            sizer = self.panel.GetSizer()
            sizer.Layout()
            sizer.Fit(self)

        def __CloseBtnClick(self, event):
            self.EndModal(wx.ID_OK)
