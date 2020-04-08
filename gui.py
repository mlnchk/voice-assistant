import wx
import os.path
import re
import subprocess, os, platform
from shutil import copy
import numpy as np

import matplotlib
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wx import NavigationToolbar2Wx
from matplotlib.figure import Figure

import globals as glo
import AudioRecorder as arec
import silence

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

    def __process_path(self, pathname):
        result = os.path.basename(pathname)
        regexp = glo.Settings['pathname_regexp']
        if regexp[0]:
            if self.regexpDialog.compiledRegexp is None:
                self.regexpDialog.compiledRegexp = re.compile(regexp[1])
            search_result = self.regexpDialog.compiledRegexp.search(pathname)
            if search_result is None:
                return result
            return search_result.group(regexp[2])
        return result

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
        self.recorder = arec.AudioRecorder(self.__StatusError)
        wx.Frame.__init__(self,
                          parent = None,
                          style = wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.icon = wx.Icon(glo.AppIconBitmap)
        self.autoID = AutoID()
        self.aboutDialog = self.AboutDialog(self)
        self.regexpDialog = self.RegexpDialog(self)
        self.vcutterDialog = self.VolumeCutterDialog(self)
        self.__InitStateFields()
        self.__InitUI()
        self.UpdateContent()
        self.__SetState(self.STATE_RESET)

    def __InitStateFields(self):
        self.STATE_RESET = self.autoID.GetID()
        self.STATE_RECORD = self.autoID.GetID()
        self.STATE_STOP = self.autoID.GetID()
        self.STATE_LOADING = self.autoID.GetID()
        self.STATE_SAVED = self.autoID.GetID()

        self.statusTexts = {
            self.STATE_RESET : 'status_bar_reset',
            self.STATE_RECORD : 'status_bar_record',
            self.STATE_STOP : 'status_bar_stop',
            self.STATE_LOADING : 'status_bar_loading',
            self.STATE_SAVED : 'status_bar_saved'
        }

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
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_REGEXP).Enable(True)
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
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_REGEXP).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(False)

        def state_stop():
            self.state = self.STATE_STOP
            self.panel.FindWindow('input_device_choice').Enable()
            self.panel.FindWindow('record_button').Enable()
            self.panel.FindWindow('stop_button').Disable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_REGEXP).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(True)

        def state_loading():
            self.state = self.STATE_LOADING
            self.panel.FindWindow('input_device_choice').Disable()
            self.panel.FindWindow('record_button').Disable()
            self.panel.FindWindow('stop_button').Disable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_REGEXP).Enable(False)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(False)

        def state_saved():
            self.state = self.STATE_SAVED
            self.fileOpened = True
            self.fileChanged = False
            self.fileSaved = True
            self.panel.FindWindow('input_device_choice').Enable()
            self.panel.FindWindow('record_button').Enable()
            self.panel.FindWindow('stop_button').Disable()
            self.menuBar.FindItemById(self.MENU_BAR_NEW).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_OPEN).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_SAVE_AS).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_LANGUAGE).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_REGEXP).Enable(True)
            self.menuBar.FindItemById(self.MENU_BAR_ABOUT).Enable(True)

        self.statesHandlers = {
            self.STATE_RESET  : state_reset,
            self.STATE_RECORD : state_record,
            self.STATE_STOP   : state_stop,
            self.STATE_LOADING: state_loading,
            self.STATE_SAVED  : state_saved
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
        self.MENU_BAR_SAVE_AS = self.autoID.GetID()
        self.MENU_BAR_EXIT = self.autoID.GetID()
        self.MENU_BAR_LANGUAGE = self.autoID.GetID()
        self.MENU_BAR_REGEXP = self.autoID.GetID()
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
                'menu' : menus[1][0],
                'name' : 'menu_bar_regexp',
                'params' : {
                    'id' : self.MENU_BAR_REGEXP
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
        sb.SetFieldsCount()
        self.SetStatusBar(sb)

    def __SetContent (self):
        self.SetIcon(self.icon)
        lang = glo.Settings['lang']
        self.SetTitle(glo.GetText('main_frame_title', lang))
        self.__SetWidgetsContent(lang)
        self.__SetMenuBarContent(lang)
        self.__SetStatusBarContent(lang)

    def __SetWidgetsContent(self, lang):
        self.__SetDevicesList(self.panel.FindWindow('input_device_choice'))
        for element in self.panel.GetChildren():
            name = element.GetName()
            text = glo.GetText(name, lang)
            if text != 'n/a':
                element.SetLabel(text)

    def __SetDevicesList(self, element):
        self.devices = self.recorder.get_devices()
        devices = [x['name'] for x in self.devices if x['max_input_channels'] > 0]
        element.SetItems(devices)
        default = self.recorder.get_device()
        n = element.FindString(default['name'], True)
        element.SetSelection(n)

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

    def __SetStatusBarContent(self, lang):
        self.statusBar.SetStatusText(glo.GetText(self.statusTexts[self.state], lang))

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
        self.recorder.set_device(self.devices[self.device])

    def __RecordBtn(self, event):
        if self.__SaveQuestion():
            self.recorder.start()
            self.__SetState(self.STATE_RECORD)

    def __StatusError(self):
        self.__SetState(self.STATE_STOP)

    def __StopBtn(self, event):
        self.recorder.stop()
        self.__SetState(self.STATE_LOADING)
        while not self.recorder.if_fileClosed():
            continue
        self.__InvokeVcutterWindow(event)
        self.__SetState(self.STATE_STOP)

    def __BindMenus(self, panel):
        menuHandlers = {
            self.MENU_BAR_NEW  : self.__Reset,
            self.MENU_BAR_OPEN : self.__Open,
            self.MENU_BAR_SAVE_AS : self.__SaveAs,
            self.MENU_BAR_EXIT : self.__Exit,
            self.MENU_BAR_REGEXP: self.__InvokeRegexpWindow,
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
        if self.__SaveQuestion():
            self.__SetState(self.STATE_RESET)

    def __Open(self, event):
        if not self.__SaveQuestion():
            return
        self.__SetState(self.STATE_RESET)
        lang = glo.Settings['lang']
        with wx.FileDialog(
            self,
            glo.GetText('file_open_dialog_title', lang),
            wildcard = glo.GetText('file_open_dialog_wildcard', lang) + '(*.*)|*.*',
            style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return
            pathname = fileDialog.GetPath()
            self.panel.FindWindow('session_name_text_control').SetValue(self.__process_path(pathname))
            self.__DelegateOpeningFile(pathname)

    def __DelegateOpeningFile(self, pathname):
        #opening error handle
        try:
            if platform.system() == 'Darwin':
                subprocess.call(('open', pathname))
            elif platform.system() == 'Windows':
                os.startfile(os.path.normpath(pathname))
            else:
                subprocess.call(('xdg-open', pathname))
        except:
            lang = glo.Settings['lang']
            wx.MessageDialog(self,
                             message = glo.GetText('file_open_error_dialog_text', lang),
                             caption = glo.GetText('file_open_error_dialog_title', lang),
                             style = wx.OK | wx.CENTRE | wx.ICON_WARNING
            ).ShowModal()

    def __SaveQuestion(self):
        lang = glo.Settings['lang']
        if self.fileChanged and not self.fileSaved:
            if wx.MessageBox(glo.GetText('save_dialog_question_text', lang),
                             glo.GetText('save_dialog_question_title', lang),
                             wx.ICON_QUESTION | wx.YES_NO) == wx.YES:
                return True
            return False
        return True

    def __SaveDialog(self):
        lang = glo.Settings['lang']
        sessionName = self.panel.FindWindow('session_name_text_control').GetValue()
        if sessionName == '':
            sessionName = glo.GetText('default_session_name', lang)
        with wx.FileDialog(self,
                           glo.GetText('save_dialog_title', lang), 
                           wildcard = glo.GetText('save_dialog_wildcard', lang) + ' (*.wav)|*.wav',
                           defaultFile = sessionName + '.wav',
                           style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT
        ) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return False
            try:
                copy(self.recorder.get_filename(), fileDialog.GetPath())
                return True
            except:
                wx.MessageBox(glo.GetText('save_dialog_error_text', lang),
                              glo.GetText('save_dialog_error_title', lang),
                              wx.ICON_ERROR | wx.OK)
                return False

    def __SaveAs(self, event):
        if self.__SaveDialog():
            self.__SetState(self.STATE_SAVED)

    def __Exit(self, event):
        self.Close()

    def __InvokeAboutWindow(self, event):
        self.aboutDialog.ShowModal()

    def __InvokeRegexpWindow(self, event):
        self.regexpDialog.UpdateContent()
        self.regexpDialog.ShowModal()

    def __InvokeVcutterWindow(self, event):
        self.vcutterDialog.UpdateContent(self.recorder.get_filename())
        self.vcutterDialog.ShowModal()

    def UpdateContent(self):
        self.__SetContent()
        self.Refresh()
        self.Update()
        self.aboutDialog.UpdateContent()
        self.regexpDialog.UpdateContent()
        self.vcutterDialog.UpdateContent()

    def __SetState(self, state):
        if state in self.statesHandlers:
            self.statesHandlers[state]()
            self.__SetStatusBarContent(glo.Settings['lang'])

    def __OnRepaint (self, event):
        sizer = self.panel.GetSizer()
        sizer.Layout()
        sizer.Fit(self)

    def __OnClose(self, event):
        if self.state == self.STATE_RECORD:
            self.__StopBtn(event)
        if event.CanVeto() and not self.__SaveQuestion():
            event.Veto()
            return

        self.recorder.flush_last()
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
                            element(wx.StaticBitmap(panel, bitmap = glo.AppIconBitmap)),
                            element(wx.StaticText(panel, name = 'about_dialog_text')),
                            element(wx.Button(panel, name = 'about_dialog_close_button'))
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

    class RegexpDialog(wx.Dialog):

        def __init__(self, parent):
            super().__init__(parent = parent,
                             style = wx.CAPTION)
            self.__InitUI()
            self.__Bind()
            self.UpdateContent()

        def __InitUI(self):
            panel = self.panel = wx.Panel(self)
            self.regexpTextCtrl = wx.TextCtrl(panel, name = 'regexp_dialog_text_control')
            self.regexpSpinCtrl = wx.SpinCtrl(panel, name = 'regexp_dialog_spin_control', min = 0, max = 99)
            element = MainFrame.element
            elements = element(
                wx.BoxSizer(wx.VERTICAL),
                { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                [
                    element(
                        wx.BoxSizer(wx.VERTICAL),
                        { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                        [
                            element(wx.CheckBox(panel, name = 'regexp_dialog_checkbox')),
                            element(self.regexpTextCtrl),
                            element(
                                wx.BoxSizer(wx.HORIZONTAL),
                                { 'flag' : wx.ALL | wx.EXPAND },
                                [
                                    element(
                                        wx.StaticText(panel, name = 'regexp_dialog_group_number'),
                                        { 'flag' : wx.CENTER | wx.ALL, 'border' : 3 }
                                    ),
                                    element(
                                        self.regexpSpinCtrl,
                                        { 'flag' : wx.EXPAND | wx.ALL, 'border' : 3 }
                                    )
                                ]
                            )
                        ]
                    ),
                    element(
                        wx.BoxSizer(wx.HORIZONTAL),
                        { 'proportion' : 1, 'flag' : wx.ALL ^ wx.TOP | wx.EXPAND, 'border' : 3 },
                        [
                            element(wx.Button(panel, name = 'regexp_dialog_save_button')),
                            element(wx.Button(panel, name = 'regexp_dialog_cancel_button'))
                        ]
                    )
                ]
            )
            elements.Compose()

            panel.SetSizer(elements.obj)

        def __SetContent(self):
            lang = glo.Settings['lang']
            self.SetTitle(glo.GetText('regexp_frame_title', lang))

            cb = self.panel.FindWindow('regexp_dialog_checkbox')
            cb.SetValue(glo.Settings['pathname_regexp'][0])
            tc = self.panel.FindWindow('regexp_dialog_text_control')
            tc.SetValue(glo.Settings['pathname_regexp'][1])
            tc.Enable(cb.IsChecked())
            sc = self.panel.FindWindow('regexp_dialog_spin_control')
            sc.SetValue(glo.Settings['pathname_regexp'][2])
            sc.Enable(cb.IsChecked())

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
            self.panel.FindWindow('regexp_dialog_checkbox').Bind(wx.EVT_CHECKBOX, self.__CheckBoxClick)
            self.regexpTextCtrl.Bind(wx.EVT_TEXT, self.__TextCtrlChanged)
            self.panel.FindWindow('regexp_dialog_save_button').Bind(wx.EVT_BUTTON, self.__SaveBtnClick)
            self.panel.FindWindow('regexp_dialog_cancel_button').Bind(wx.EVT_BUTTON, self.__CancelBtnClick)

        def UpdateContent(self):
            self.__SetContent()
            self.Refresh()
            self.Update()

        def __OnRepaint(self, event):
            sizer = self.panel.GetSizer()
            sizer.Layout()
            sizer.Fit(self)

        def __CheckBoxClick(self, event):
            state = event.IsChecked()
            self.panel.FindWindow('regexp_dialog_text_control').Enable(state)
            self.panel.FindWindow('regexp_dialog_spin_control').Enable(state)

        def __TextCtrlChanged(self, event):
            text = self.regexpTextCtrl.GetValue()
            if len(text) > 0:
                try:
                    self.compiledRegexp = re.compile(text)
                except re.error:
                    return
            self.regexpSpinCtrl.SetMax(self.compiledRegexp.groups)

        def __SaveBtnClick(self, event):
            glo.Settings['pathname_regexp'] = (
                self.panel.FindWindow('regexp_dialog_checkbox').IsChecked(),
                self.panel.FindWindow('regexp_dialog_text_control').GetValue(),
                self.panel.FindWindow('regexp_dialog_spin_control').GetValue()
            )
            self.EndModal(wx.ID_OK)

        def __CancelBtnClick(self, event):
            self.EndModal(wx.ID_OK)

    class VolumeCutterDialog(wx.Dialog):

        class CanvasPanel(wx.Panel):

            def __init__(self, parent):
                wx.Panel.__init__(self, parent)

                self.figure = Figure(
                    figsize = (2, 1),
                    dpi = 256,
                    facecolor = '#000000'
                )
                self.ax = self.figure.add_subplot(
                    111,
                    xmargin = 0,
                    ymargin = 0,
                    autoscale_on = True
                )
                self.ax.set_axis_off()
                self.ax.set_yscale('log', nonposy='clip', basey=10.0)

                self.figure.set_tight_layout({'pad' : 0})
                
                defaultData = ([0, 1], [0, 1])

                self.level_line, = self.ax.plot(
                    *defaultData,
                    c = '#ff0000',
                    lw = 0.5
                )

                self.canvas = FigureCanvas(self, -1, self.figure)
            
            def __refresh_background(self):
                self.level_line.set_visible(False)
                self.canvas.draw()
                self.background = self.canvas.copy_from_bbox(self.ax.bbox)
                self.level_line.set_visible(True)

            def set_level_content(self, h):
                self.level_line.set_ydata([h, h])
                self.canvas.restore_region(self.background)
                self.ax.draw_artist(self.level_line)
                self.canvas.blit(self.ax.bbox)

            def set_graph_content(self, y_data):
                datalen = len(y_data)
                fact = 1.0 / datalen
                x_data = [i * fact for i in range(datalen)]
                self.graph_line = self.ax.stackplot(
                    x_data,
                    y_data,
                    colors = ['#00ff00'],
                    lw = 0
                )
                self.__refresh_background()

        def __init__(self, parent):
            self.ap = silence.AudioProcessor()
            super().__init__(parent = parent,
                             style = wx.CAPTION)
            self.__InitUI()
            self.__Bind()
            self.UpdateContent()

        def __InitUI(self):
            panel = self.panel = wx.Panel(self)

            self.canvasPanel = self.CanvasPanel(panel)
            self.MAX_VAL = 512
            self.slider = wx.Slider(panel, style = wx.SL_VERTICAL | wx.SL_INVERSE, minValue = 0, maxValue = self.MAX_VAL)

            element = MainFrame.element
            elements = element(
                wx.BoxSizer(wx.VERTICAL),
                { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                [
                    element(
                        wx.BoxSizer(wx.HORIZONTAL),
                        { 'flag' : wx.ALL | wx.EXPAND, 'border' : 3 },
                        [
                            element(self.slider),
                            element(self.canvasPanel)
                        ]
                    ),
                    element(
                        wx.BoxSizer(wx.HORIZONTAL),
                        { 'proportion' : 1, 'flag' : wx.ALL ^ wx.TOP | wx.EXPAND, 'border' : 3 },
                        [
                            element(wx.Button(panel, name = 'vcutter_dialog_cut_button')),
                            element(wx.Button(panel, name = 'vcutter_dialog_dont_button'))
                        ]
                    )
                ]
            )
            elements.Compose()

            panel.SetSizer(elements.obj)

        def __SetContent(self, filename):
            lang = glo.Settings['lang']
            self.SetTitle(glo.GetText('vcutter_frame_title', lang))
            for element in self.panel.GetChildren():
                name = element.GetName()
                text = glo.GetText(name, lang)
                variable = glo.GetText(name, 'var')
                varstr = ''
                if variable != 'n/a':
                    varstr = glo.Get(variable)
                if text != 'n/a':
                    element.SetLabel(text + varstr)
            
            if filename is not None:
                self.ap.Open(filename)
                self.soundData = self.ap.GetData()
                
                self.canvasPanel.set_graph_content(self.soundData)
                self.canvasPanel.set_level_content(self.scaleFunc(self.slider.GetValue()))

        def __Bind(self):
            self.Bind(wx.EVT_PAINT, self.__OnRepaint)
            self.slider.Bind(wx.EVT_SLIDER, self.__SliderChanged)
            self.panel.FindWindow('vcutter_dialog_cut_button').Bind(wx.EVT_BUTTON, self.__CutBtnClick)
            self.panel.FindWindow('vcutter_dialog_dont_button').Bind(wx.EVT_BUTTON, self.__DontBtnClick)

        def UpdateContent(self, filename = None):
            self.__SetContent(filename)
            self.Refresh()
            self.Update()

        def scaleFunc(self, x, linear = False):
            x = x / self.MAX_VAL
            ymin, ymax = self.canvasPanel.ax.get_ylim()
            if linear:
                return x
            return ymax ** x

        def __SliderChanged(self, event):
            self.canvasPanel.set_level_content(self.scaleFunc(event.GetInt()))

        def __OnRepaint(self, event):
            sizer = self.panel.GetSizer()
            sizer.Layout()
            sizer.Fit(self)

        def __CutBtnClick(self, event):
            # if self.filename is not None:
            #     vl = self.scaleFunc(self.slider.GetValue(), True)
            #     remove_silence(self.filename, vl)
            #     self.filename = None
            self.ap.Close()
            self.EndModal(wx.ID_OK)

        def __DontBtnClick(self, event):
            self.ap.Close()
            self.EndModal(wx.ID_OK)
