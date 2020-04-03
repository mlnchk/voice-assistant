import wx

class AppCore(wx.App):
    
    def OnInit(self):
        mf = MainFrame()
        mf.Show()
        self.SetTopWindow(mf)
        return True

class gui ():
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
        self.panel = wx.Panel(self)
        self.__SetLayout()
        self.__Bind()

    def __SetLayout (self):
        panel = self.panel

        elements = gui(
            wx.BoxSizer(wx.VERTICAL),
            { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
            [
                gui(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        gui(wx.StaticText(panel, name = 'SessionNameLabel', label = 'Session name:')),
                        gui(wx.TextCtrl(panel, name = 'SessionNameTextControl'))
                    ]
                ),
                gui(
                    wx.StaticLine(panel),
                    { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                ),
                gui(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        gui(wx.StaticText(panel, name = 'InputDeviceLabel', label = 'Input device:')),
                        gui(wx.Choice(panel, name = 'InputDeviceChoice'))
                    ]
                ),
                gui(
                    wx.StaticLine(panel),
                    { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                ),
                gui(
                    wx.BoxSizer(wx.HORIZONTAL),
                    { 'proportion' : 1, 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        gui(wx.Button(panel, name = 'recBtn', label = 'record')),
                        gui(wx.Button(panel, name = 'stopBtn', label = 'stop')),
                        gui(wx.Button(panel, name = 'playBtn', label = 'play'))
                    ]
                ),
            ]
        )
        elements.Compose()

        panel.SetSizer(elements.obj)

        sb = self.CreateStatusBar(name = 'statusBar')
        sb.SetStatusText('Sample state')

    def __Bind(self):
        #panel = self.panel

        self.Bind(wx.EVT_PAINT, self.__OnRepaint)

    def __OnRepaint (self, event):
        #self.__SetContent(self.panel)
        sizer = self.panel.GetSizer()
        sizer.Layout()
        sizer.Fit(self)

# test part

core = AppCore()
core.MainLoop()