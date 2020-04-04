import wx
import globals as glo

class AppCore(wx.App):
    
    def OnInit(self):
        glo.LoadResources()
        mf = MainFrame()
        self.SetTopWindow(mf)
        mf.Show()
        return True

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

class MainFrame (wx.Frame):

    def __init__ (self):
        wx.Frame.__init__(self,
                          parent = None,
                          style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.icon = wx.Icon(glo.AppIconBitmap)
        self.SetIcon(self.icon)
        self.aboutDialog = self.AboutDialog(self)
        self.__InitStateFields()
        self.__InitUI()
        self.__Update()

    def __InitStateFields(self):
        self.fileOpened = False
        self.fileChanged = False
        self.fileSaved = False
        self.state = 0

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
                        element(wx.Button(panel, name = 'stop_button')),
                        element(wx.Button(panel, name = 'play_button'))
                    ]
                ),
            ]
        )
        self.elements.Compose()
        panel.SetSizer(self.elements.obj)

    def __ComposeMenuBar (self, panel):
        mb = self.menuBar = wx.MenuBar()
        
        self.MENU_BAR_NEW = 0
        self.MENU_BAR_OPEN = 1
        self.MENU_BAR_SAVE = 2
        self.MENU_BAR_SAVE_AS = 3
        self.MENU_BAR_EXIT = 4
        self.MENU_BAR_LANGUAGE = 5
        self.MENU_BAR_ABOUT = 6

        self.MENU_BAR_LANG_EN = 7

        menus = self.menus = [
            (wx.Menu(), 'menu_file'),
            (wx.Menu(), 'menu_settings'),
            (wx.Menu(), 'menu_help')
        ]

        LanguageSubmenu = wx.Menu()

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
                'menu' : LanguageSubmenu,
                'name' : 'menu_bar_language_submenu_en',
                'params' : {
                    'id' : self.MENU_BAR_LANG_EN
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

        for menuItem in self.menuItems:
            menuItem['object'] = menuItem['menu'].Append(item = 'default', **menuItem['params'])

        self.SetMenuBar(mb)
    
    def __ComposeStatusBar (self, panel):
        sb = self.statusBar = wx.StatusBar(panel, name = 'statusBar')
        sb.SetFieldsCount(2)
        sb.SetStatusWidths([-3, -1])
        sb.SetStatusText('state', 0)
        sb.SetStatusText('0:00', 1)
        self.SetStatusBar(sb)

    def __SetContent (self):
        lang = glo.Settings['lang']
        self.SetTitle(glo.GetText('main_frame_title', lang))
        self.__SetWidgetsContent(lang)
        self.__SetMenuBarContent(lang)

    def __SetWidgetsContent(self, lang):
        for element in self.panel.GetChildren():
            name = element.GetName()
            text = glo.GetText(name, lang)
            if text != 'n/a':
                element.SetLabel(text)

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
        return

    def __BindMenus(self, panel):
        menuHandlers = {
            self.MENU_BAR_EXIT : self.__Exit,
            self.MENU_BAR_ABOUT: self.__InvokeAboutWindow
        }

        for menuItem in self.menuItems:
            obj = menuItem['object']
            id = obj.GetId()
            if id in menuHandlers:
                self.Bind(wx.EVT_MENU, menuHandlers[id], obj)

    def __Exit(self, event):
        self.Close()

    def __InvokeAboutWindow(self, event):
        self.aboutDialog.ShowModal()

    def __Update(self):
        self.__SetContent()
        self.Refresh()
        self.Update()

    def __OnRepaint (self, event):
        sizer = self.panel.GetSizer()
        sizer.Layout()
        sizer.Fit(self)

    def __OnClose(self, event):
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
                             title = 'About',
                             style = wx.CAPTION)
            self.__InitUI()
            self.__Bind()

        def __InitUI(self):
            panel = self.panel = wx.Panel(self)
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
                                wx.StaticText(panel, label = 'The Voice Assistant v'+glo.GetVersion(), name = 'AboutDialogText')
                            ),
                            element(
                                wx.Button(panel, label = 'Close', name = 'AboutDialogCloseButton')
                            )
                    ]   
                    )
                ]
            )
            elements.Compose()
            panel.SetSizer(elements.obj)

        def __Bind(self):
            self.Bind(wx.EVT_PAINT, self.__OnRepaint)
            self.Bind(wx.EVT_BUTTON, self.__CloseBtnClick)

        def __OnRepaint(self, event):
            sizer = self.panel.GetSizer()
            sizer.Layout()
            sizer.Fit(self)

        def __CloseBtnClick(self, event):
            self.EndModal(wx.ID_OK)

# test part

core = AppCore()
core.MainLoop()