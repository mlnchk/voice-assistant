import wx

class AppCore(wx.App):
    
    def OnInit(self):
        mf = MainFrame()
        mf.Show()
        self.SetTopWindow(mf)
        return True

class ElemGUI ():
    def __init__ (self, obj, style = None, child = None):
        self.obj = obj,
        self.style = style,
        self.child = child
    
    def Compose(self, parent = None):
        if self.style == (None,):
            self.style = parent.style
        if self.child != None:
            for c in self.child:
                c.Compose(self)
        if parent != None:
            parent.obj[0].Add(self.obj[0], **self.style[0])

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

        elements = ElemGUI(
            wx.BoxSizer(wx.VERTICAL),
            { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
            [
                ElemGUI(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        ElemGUI(wx.StaticText(panel, name = 'SessionNameLabel', label = 'Session name:')),
                        ElemGUI(wx.TextCtrl(panel, name = 'SessionNameTextControl'))
                    ]
                ),
                ElemGUI(
                    wx.StaticLine(panel),
                    { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                ),
                ElemGUI(
                    wx.BoxSizer(wx.VERTICAL),
                    { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        ElemGUI(wx.StaticText(panel, name = 'InputDeviceLabel', label = 'Input device:')),
                        ElemGUI(wx.Choice(panel, name = 'InputDeviceChoice'))
                    ]
                ),
                ElemGUI(
                    wx.StaticLine(panel),
                    { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                ),
                ElemGUI(
                    wx.BoxSizer(wx.HORIZONTAL),
                    { 'proportion' : 1, 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                    [
                        ElemGUI(wx.Button(panel, name = 'recBtn', label = 'record')),
                        ElemGUI(wx.Button(panel, name = 'stopBtn', label = 'stop')),
                        ElemGUI(wx.Button(panel, name = 'playBtn', label = 'play'))
                    ]
                ),
            ]
        )
        elements.Compose()

        panel.SetSizer(elements.obj[0])

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