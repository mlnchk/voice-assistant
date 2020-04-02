import wx

class AppCore(wx.App):
    
    def OnInit(self):
        mf = MainFrame()
        mf.Show()
        self.SetTopWindow(mf)
        return True

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

        sizers = [
            {
                'object' : wx.BoxSizer(wx.VERTICAL),
                'style' : { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 }
            },
            {
                'object' : wx.BoxSizer(wx.VERTICAL),
                'style' : { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 }
            },
            {
                'object' : wx.BoxSizer(wx.HORIZONTAL),
                'separator' : {
                    'object' : wx.StaticLine(panel),
                    'style'  : { 'flag' : wx.LEFT | wx.RIGHT | wx.EXPAND, 'border' : 6 }
                },
                'style' : { 'proportion' : 1, 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 }
            }
        ]
        widgets = [
            {
                'object' : wx.StaticText(panel, name = 'SessionNameLabel', label = 'Session name:'),
                'sizer' : 1
            },
            {
                'object' : wx.TextCtrl(panel, name = 'SessionNameTextControl'),
                'sizer' : 1
            },
            {
                'object' : wx.Button(panel, name = 'recBtn'),
                'sizer'  : 2
            },
            {
                'object' : wx.Button(panel, name = 'stopBtn'),
                'sizer'  : 2
            },
            {
                'object' : wx.Button(panel, name = 'playBtn'),
                'sizer'  : 2
            }
        ]

        for widget in widgets:
            if 'style' not in widget.keys():
                widget['style'] = sizers[widget['sizer']]['style']
            sizers[widget['sizer']]['object'].Add(widget['object'], **widget['style'])
        
        for sizer in sizers[1:]:
            if 'separator' in sizer.keys():
                sizers[0]['object'].Add(sizer['separator']['object'], **sizer['separator']['style'])
            sizers[0]['object'].Add(sizer['object'], **sizers[0]['style'])

        panel.SetSizer(sizers[0]['object'])

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