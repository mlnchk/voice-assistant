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
        self.SetTitle('Voice Assistant')
        self.icon = wx.Icon(glo.AppIconBitmap)
        self.SetIcon(self.icon)
        self.aboutDialog = self.AboutDialog(self)
        self.__InitStateFields()
        self.__InitUI()

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
                        element(wx.StaticText(panel, name = 'SessionNameLabel', label = 'Session name:')),
                        element(wx.TextCtrl(panel, name = 'SessionNameTextControl'))
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
                        element(wx.StaticText(panel, name = 'InputDeviceLabel', label = 'Input device:')),
                        element(wx.Choice(panel, name = 'InputDeviceChoice'))
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
                        element(wx.Button(panel, name = 'recBtn', label = 'record')),
                        element(wx.Button(panel, name = 'stopBtn', label = 'stop')),
                        element(wx.Button(panel, name = 'playBtn', label = 'play'))
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

        menus = [
            (wx.Menu(), 'File'),
            (wx.Menu(), 'Settings'),
            (wx.Menu(), 'Help')
        ]
        LanguageSubmenu = wx.Menu()

        self.menuItems = [
            {
                'menu' : menus[0][0],
                'params' : {
                    'id' : self.MENU_BAR_NEW,
                    'item' : 'New',
                    'helpString' : 'Resets for new session'
                }
            },
            {
                'menu' : menus[0][0],
                'params' : {
                    'id' : self.MENU_BAR_OPEN,
                    'item' : 'Open',
                    'helpString' : 'Opens file for the new session'
                }
            },
            {
                'menu' : menus[0][0],
                'params' : {
                    'id' : self.MENU_BAR_SAVE,
                    'item' : 'Save',
                    'helpString' : 'Saves current session'
                }
            },
            {
                'menu' : menus[0][0],
                'params' : {
                    'id' : self.MENU_BAR_SAVE_AS,
                    'item' : 'Save As...',
                    'helpString' : 'Saves current session'
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
                'params' : {
                    'id' : self.MENU_BAR_EXIT,
                    'item' : 'Exit',
                    'helpString' : 'Closes the application'
                }
            },
            {
                'menu' : LanguageSubmenu,
                'params' : {
                    'id' : self.MENU_BAR_LANG_EN,
                    'item' : 'EN',
                    'helpString' : 'English (UK)'
                }
            },
            {
                'menu' : menus[1][0],
                'params' : {
                    'id' : self.MENU_BAR_LANGUAGE,
                    'item' : 'Language',
                    'helpString' : 'Localization',
                    'subMenu' : LanguageSubmenu
                }
            },
            {
                'menu' : menus[2][0],
                'params' : {
                    'id' : self.MENU_BAR_ABOUT,
                    'item' : 'About',
                    'helpString' : 'About the application'
                }
            }
        ]

        for menuItem in self.menuItems:
            menuItem['object'] = menuItem['menu'].Append(**menuItem['params'])

        mb.SetMenus(menus)

        self.SetMenuBar(mb)
    
    def __ComposeStatusBar (self, panel):
        sb = self.statusBar = wx.StatusBar(panel, name = 'statusBar')
        sb.SetFieldsCount(2)
        sb.SetStatusWidths([-3, -1])
        sb.SetStatusText('state', 0)
        sb.SetStatusText('0:00', 1)
        self.SetStatusBar(sb)

    def __SetContent (self):
        panel = self.panel

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

    def __OnRepaint (self, event):
        #self.__SetContent(self.panel)
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