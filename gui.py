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
        self.pan = wx.Panel(self)

# test part

core = AppCore()
core.MainLoop()