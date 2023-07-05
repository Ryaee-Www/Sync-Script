import threading
import wx
import wx.lib.agw.flatnotebook as fnb
import string
import os
import json
from wx.core import BoxSizer, EXPAND, HORIZONTAL, LEFT, NB_FIXEDWIDTH, Right, Size, StaticText
import Sync
import paramiko
import socket
import time
import programThread
import logPanel

allTags = ["Space Engineer", "SE Blue Prints", "Stellaris", "ST MOD", "Skyrim", "Civ V", "Banished"]
MEMORY_INDEX_NAME = 0
MEMORY_INDEX_REMOTE = 1
MEMORY_INDEX_LOCAL = 2
CURRENT_DIRECTORY = os.getcwd()
TEMP_WINDOW_SIZE = (455, 385)


class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)

    write = WriteText


class TestGUIFrame(wx.Frame):
    def __init__(self):  # TODO notice change not applied
        super().__init__(parent=None, title='test GUI')

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)
        self.currentDirectory = CURRENT_DIRECTORY
        if os.path.exists(f"{self.currentDirectory}\\config.json"):
            with open(f"{self.currentDirectory}\\config.json") as SSHRaw:
                jsonData = json.load(SSHRaw)
                self.allDef = jsonData
        else:
            content = {
                {
                    "host": "host",
                    "port": 0,
                    "username": "username",
                    "password": "password",
                    "directory": [
                        {"name": "name", "remote": "/home/ubuntu/", "local": "C:\\desktop"}
                    ]
                }
            }
            with open(f"{self.currentDirectory}\\config.json") as SSHRaw:
                json.dump(content, SSHRaw)

        # # start initialize window

        # Major Panel, entire window
        archPanel = wx.Panel(self)
        # Major sizer, entire page
        panelSizer = wx.BoxSizer(wx.VERTICAL)

        # Top toolbar
        self.toolbar, self.syncPage, self.logPage = self._createToolBar_(archPanel)
        # toolbar goes in Major sizer
        panelSizer.Add(self.toolbar)

        # Major sizer for Sync page
        syncPageSizer = wx.BoxSizer(wx.VERTICAL)

        # First sub-sizer init, respond to Sync page panel (ssh connect)
        FirstMajorSizer = self._createFirstSizer_(self.syncPage, font)
        # First sub-sizer, goes in syncPage
        syncPageSizer.Add(FirstMajorSizer)

        # Second sub-sizer init, respond to syncPage (menu book for all preset, warped sizer)
        SecondMajorSizer = self._createSecondSizer_(self.syncPage)
        # choiceBook init, respond to syncPage
        self.mainChoiceBook = menuChoiceBook(self.syncPage, log, jsonData)
        # choiceBook goes in second sizer
        SecondMajorSizer.Add(self.mainChoiceBook)
        # Second sub-sizer goes in sync page
        syncPageSizer.Add(SecondMajorSizer, flag=wx.EXPAND | wx.RIGHT | wx.LEFT | wx.TOP, border=10)

        # Third sub-sizer init, respond to main panel (application control, connect, push pull etc)
        ThirdMajorSizer = self._createThirdSizer_(archPanel)
        # Third sub-sizer goes in Main Panel
        panelSizer.Add(ThirdMajorSizer, flag=wx.ALIGN_LEFT | wx.BOTTOM | wx.LEFT, border=10)

        syncPageSizer.SetSizeHints(self)
        self.SetInitialSize(TEMP_WINDOW_SIZE)
        self.syncPage.SetSizerAndFit(syncPageSizer)
        archPanel.SetSizerAndFit(panelSizer)
        self.readFromJson(jsonData)

        self.mainChoiceBook.win.Show()
        self.Show()
        self.Center()
        # finished initialize window

        # deal with connection
        self.sshClient = Sync.Synchronizer(self.allDef)
        self.Bind(wx.EVT_CLOSE, self.onClose)
        self.sshThread = None

    def _createToolBar_(self, panel):
        toolbar = fnb.FlatNotebook(panel, agwStyle=fnb.FNB_NO_X_BUTTON)
        # Sync page panel
        syncPage = wx.Panel(toolbar)
        # Log page panel
        logPage = logPanel.LogPanel(toolbar)
        #self.log = log
        # add page to toolbar
        toolbar.AddPage(syncPage, "Sync")
        toolbar.AddPage(logPage, "Log")
        return toolbar, syncPage, logPage

    def _createFirstSizer_(self, panel, font):
        FirstMajorSizer = wx.BoxSizer(wx.HORIZONTAL)

        ##ServerIp, userName, timeOut instruction:
        FirstRowColumn1 = wx.BoxSizer(wx.VERTICAL)
        # serverIP Instruction
        serverIPInst = wx.StaticText(panel, -1, "Server IP: ")
        serverIPInst.SetFont(font)
        # userName Instruction
        userNameInst = wx.StaticText(panel, -1, "Username: ")
        userNameInst.SetFont(font)

        FirstRowColumn1.Add(serverIPInst, flag=wx.TOP, border=3)
        FirstRowColumn1.Add(userNameInst, flag=wx.TOP, border=16)

        ##ServerIP, userName, timeOut EntryBox:
        FirstRowColumn2 = wx.BoxSizer(wx.VERTICAL)
        self.serverIPEntry = wx.TextCtrl(panel)
        self.userNameEntry = wx.TextCtrl(panel)
        self.serverIPEntry.SetSize(120, -1)
        self.userNameEntry.SetSize(120, -1)
        FirstRowColumn2.Add(self.serverIPEntry, flag=wx.TOP | wx.BOTTOM, border=10)
        FirstRowColumn2.Add(self.userNameEntry, flag=wx.BOTTOM, border=10)

        ##Port, password instruction:
        FirstRowColumn3 = wx.BoxSizer(wx.VERTICAL)
        # Port Instruction
        portInst = wx.StaticText(panel, -1, "Server port: ")
        portInst.SetFont(font)
        # password Instruction
        passwordInst = wx.StaticText(panel, -1, "Password: ")
        passwordInst.SetFont(font)

        FirstRowColumn3.Add(portInst, flag=wx.TOP, border=3)
        FirstRowColumn3.Add(passwordInst, flag=wx.TOP, border=16)

        ##Port, password EntryBox:
        FirstRowColumn4 = wx.BoxSizer(wx.VERTICAL)
        self.portEntry = wx.TextCtrl(panel)
        self.passwordEntry = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.portEntry.SetSize((120, -1))
        self.passwordEntry.SetSize((120, -1))
        FirstRowColumn4.Add(self.portEntry, flag=wx.TOP | wx.BOTTOM, border=10)
        FirstRowColumn4.Add(self.passwordEntry, flag=wx.BOTTOM, border=10)

        FirstMajorSizer.Add(FirstRowColumn1, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        FirstMajorSizer.Add(FirstRowColumn2, flag=wx.RIGHT, border=10)
        FirstMajorSizer.Add(FirstRowColumn3, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        FirstMajorSizer.Add(FirstRowColumn4, flag=wx.RIGHT, border=10)
        return FirstMajorSizer

    def _createSecondSizer_(self, panel):

        warpStaticBox = wx.StaticBox(panel, label="preset", style=wx.BORDER_STATIC)
        warpStaticSizer = wx.StaticBoxSizer(warpStaticBox, wx.VERTICAL)
        #warpStaticSizer.Add(self.mainChoiceBook)

        return warpStaticSizer

    def _createThirdSizer_(self, panel):
        ThridMajorSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.saveBtn = wx.Button(panel, label="Apply")
        self.pushBtn = wx.Button(panel, label="push")
        self.pullBtn = wx.Button(panel, label="pull")
        self.connectBtn = wx.Button(panel, label="connect")
        self.disconnectBtn = wx.Button(panel, label="disconnect")
        # cancelBtn = wx.Button(panel, label = "Cancel")
        # cancelBtn.Bind(wx.EVT_BUTTON,self.closeWindow)

        ThridMajorSizer.Add(self.saveBtn, flag=wx.RIGHT, border=5)
        ThridMajorSizer.Add(self.pushBtn, flag=wx.RIGHT, border=5)
        ThridMajorSizer.Add(self.pullBtn, flag=wx.RIGHT, border=5)
        ThridMajorSizer.Add(self.connectBtn, flag=wx.RIGHT, border=5)
        ThridMajorSizer.Add(self.disconnectBtn, flag=wx.RIGHT, border=5)

        # ThridMajorSizer.Add(cancelBtn)
        self.pushBtn.Bind(wx.EVT_BUTTON, self.doPush)
        self.pullBtn.Bind(wx.EVT_BUTTON, self.doPull)
        self.pushBtn.Disable()
        self.pullBtn.Disable()
        self.saveBtn.Bind(wx.EVT_BUTTON, self.applyChange)
        self.connectBtn.Bind(wx.EVT_BUTTON, self.connectSSH)
        self.disconnectBtn.Bind(wx.EVT_BUTTON, self.disconnectSSH)
        self.disconnectBtn.Disable()
        return ThridMajorSizer

    def readFromJson(self, SSHDetail):
        host = SSHDetail['host']  # Server ip address
        port = SSHDetail['port']  # port
        username = SSHDetail['username']  # ssh userID
        password = SSHDetail['password']  # password

        self.serverIPEntry.write(host)
        self.portEntry.write(str(port))
        self.userNameEntry.write(username)
        self.passwordEntry.write(password)

    def getServerIP(self):
        return self.serverIPEntry.GetValue()

    def getUserName(self):
        return self.userNameEntry.GetValue()

    def getPort(self):
        return int(self.portEntry.GetValue())

    def getPassword(self):
        return self.passwordEntry.GetValue()

    def applyChange(self, event):
        dlg = wx.MessageDialog(self, f'Confirm update?\nNotice that this will not change save files path',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        if (dlg.ShowModal() == wx.ID_YES):
            self.allDef["host"] = self.getServerIP()
            self.allDef["username"] = self.getUserName()
            self.allDef["port"] = int(self.getPort())
            self.allDef["password"] = self.getPassword()
            with open(f"{CURRENT_DIRECTORY}\\config.json", 'w') as SSHRaw:
                SSHRaw.write(json.dumps(self.allDef, indent=2))
            self.disconnectSSH(self)
            self.sshClient = Sync.Synchronizer(self.allDef)

    def onClose(self, event):
        if (self.sshThread is not None):
            if self.sshThread.is_alive():
                self.sshThread.stop()  # Stop the SSH thread gracefully
                self.sshThread.join()  # Wait for the thread to finish
            else:
                self.sshThread = None
        self.Destroy()

    def doPush(self, event):

        dlg = wx.MessageDialog(self, 'working in progress, do test',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        if (dlg.ShowModal() == wx.ID_YES):
            (numDir, numFile) = self.sshClient.doUpload(self.mainChoiceBook.LocalEntry.GetValue(),
                                                        self.mainChoiceBook.RemoteEntry.GetValue())
            self.logPage.print(f"Upload complete. From {numDir} directories pulled {numFile} files.")

    def doPull(self, event):

        dlg = wx.MessageDialog(self, f'working in progress, do test',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        if (dlg.ShowModal() == wx.ID_YES):
            (numDir, numFile) = self.sshClient.doDownload(self.mainChoiceBook.RemoteEntry.GetValue(),
                                                          self.mainChoiceBook.LocalEntry.GetValue())
            self.logPage.print(f"Download Complete. From {numDir} directories pulled {numFile} files.")

    def connectSSH(self, event):
        self.sshThread = programThread.SSHThread(self, self.logPage)
        self.sshThread.start()
        self.pullBtn.Enable()
        self.pushBtn.Enable()
        self.connectBtn.Disable()
        self.disconnectBtn.Enable()
        self.saveBtn.Disable()

    def disconnectSSH(self, event):
        self.logPage.print("Attempt shutting down ssh connection...")
        if self.sshThread is not None:
            self.logPage.print("Attempt stopping thread...")
            self.sshThread.stop()
            self.sshThread.join()
            if not (self.sshClient.isActive()):
                self.logPage.print("Successfully closed connection")

                self.connectBtn.Enable()
                self.pullBtn.Disable()
                self.pushBtn.Disable()
                self.disconnectBtn.Disable()
                self.saveBtn.Enable()

            else:
                self.logPage.print("Error closing connection, the connection may not be closed")
                # self.sshThread.join()
        else:
            self.logPage.print("No thread running.")
        # self.sshThread.join()

    def _unExpectedDisconnect_(self):
        self.connectBtn.Enable()
        self.pullBtn.Disable()
        self.pushBtn.Disable()
        self.disconnectBtn.Disable()
        self.saveBtn.Enable()


class menuChoiceBook(wx.Choicebook):
    def __init__(self, parent, log, JsonData):
        wx.Choicebook.__init__(self, parent)
        self.optionCount = 0  # how many presets present in the menu
        self.log = log
        self.JsonData = JsonData  # Json Data
        self.currentSelection = 0  # record current index choosen, int
        self.initFromJson(self.JsonData)
        self.win = wx.Panel(self)

        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)

        PanelSizer = BoxSizer(wx.HORIZONTAL)
        LeftSizer = BoxSizer(wx.VERTICAL)

        NameInst = wx.StaticText(self.win, -1, label="Preset Name: ")
        NameInst.SetFont(font)

        RemoteInst = wx.StaticText(self.win, -1, label="Remote Directory: ")
        RemoteInst.SetFont(font)

        LocalInst = wx.StaticText(self.win, -1, label="Local Directory: ")
        LocalInst.SetFont(font)

        LeftSizer.Add(NameInst, flag=wx.TOP, border=5)
        LeftSizer.Add(RemoteInst, flag=wx.TOP, border=15)
        LeftSizer.Add(LocalInst, flag=wx.TOP, border=15)


        RightSizer = BoxSizer(wx.VERTICAL)
        self.NameEntry = wx.TextCtrl(self.win)
        self.RemoteEntry = wx.TextCtrl(self.win)
        self.LocalEntry = wx.TextCtrl(self.win)


        RightSizer.Add(self.NameEntry, flag=wx.EXPAND)
        RightSizer.Add(self.RemoteEntry, flag=wx.TOP | wx.EXPAND, border=10)
        RightSizer.Add(self.LocalEntry, flag=wx.TOP | wx.EXPAND, border=10)

        TwinBtnSizer = BoxSizer(wx.HORIZONTAL)
        # Create and bind buttons
        fileBrowserBtn = wx.Button(self.win, label="Browse")
        fileBrowserBtn.Bind(wx.EVT_BUTTON, self.browseFile)
        fileSaveBtn = wx.Button(self.win, label="Save")
        fileSaveBtn.Bind(wx.EVT_BUTTON, self.saveFile)
        fileSaveAllBtn = wx.Button(self.win, label="Save All")
        fileSaveAllBtn.Bind(wx.EVT_BUTTON, self.saveAllFile)
        # fileSaveAllBtn.Bind(wx.EVT_BUTTON,self.saveAllFile())

        TwinBtnSizer.AddMany([(fileBrowserBtn, 0, wx.LEFT, 10), (fileSaveBtn, 0, wx.RIGHT | wx.LEFT, 5),
                              (fileSaveAllBtn, 0, wx.RIGHT, 10)])
        RightSizer.Add(TwinBtnSizer, flag=wx.TOP | wx.BOTTOM | wx.EXPAND, border=10)
        PanelSizer.Add(LeftSizer, flag=wx.LEFT | wx.RIGHT, border=10)
        PanelSizer.Add(RightSizer, flag=wx.EXPAND | wx.RIGHT, border=10)
        self.win.SetSizer(PanelSizer)

        self.RemoteEntry.write(JsonData['directory'][0]['remote'])
        self.LocalEntry.write(JsonData['directory'][0]['local'])
        # Now make a bunch of panels for the choice book
        for name in JsonData['directory']:
            self.optionCount += 1
            self.AddPage(self.win, name['name'])
        self.AddPage(self.win, "create New Preset")

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)

    def initFromJson(self, JsonData):
        self.memoryData = []
        for addr in JsonData['directory']:
            self.memoryData.append([addr["name"], addr['remote'], addr['local']])
        '''
        self.SERemote = JsonData['directory'][0]['remote']#SPACE ENGINEER
        self.SELocal = JsonData['directory'][0]['local']

        self.SEBRemote = JsonData['directory'][1]['remote']#SPACE ENGINEER BLUEPRINT
        self.SEBLocal = JsonData['directory'][1]['local']

        self.STRemote = JsonData['directory'][2]['remote']#STELLARIS
        self.STLocal = JsonData['directory'][2]['local']

        self.STMRemote = JsonData['directory'][3]['remote']#STELLARIS MODLIST
        self.STMLocal = JsonData['directory'][3]['local']

        self.SKRemote = JsonData['directory'][4]['remote']#SKYRIM
        self.SKLocal = JsonData['directory'][4]['local']

        self.C5Remote = JsonData['directory'][5]['remote']#CIVILIZATION V
        self.C5Local = JsonData['directory'][5]['local']

        self.BNRemote = JsonData['directory'][6]['remote']#BANISHED
        self.BNLocal = JsonData['directory'][6]['local']

        #memoryData must be saved upon onpress or pagechanging
        self.memoryData = [[self.SERemote,self.SELocal],
                    [self.SEBRemote,self.SEBLocal],
                    [self.STRemote,self.STLocal],
                    [self.STMRemote,self.STMLocal],
                    [self.SKRemote,self.SKLocal],
                    [self.C5Remote,self.C5Local],
                    [self.BNRemote,self.BNLocal]]
        '''

    # update menu book
    def OnPageChanged(self, event):
        self.currentSelection = event.GetSelection()
        # print(f"IDonPageChange: {event.GetSelection()}")
        if (self.currentSelection == self.optionCount):  # if create new
            self.RemoteEntry.Clear()
            self.LocalEntry.Clear()
        else:
            self.RemoteEntry.Clear()
            self.RemoteEntry.write(self.JsonData['directory'][self.currentSelection]['remote'])
            self.LocalEntry.Clear()
            self.LocalEntry.write(self.JsonData['directory'][self.currentSelection]['local'])

    # update menu book changing...
    def OnPageChanging(self, event):

        if (event.GetSelection() >= self.optionCount):  # newpage
            # TODO now this if always trigger modify popup, change memdata to have dummy page
            dlg = wx.MessageDialog(self,
                                   'Do you want to save the new preset?\nNotice that this will not modify the config file.',
                                   'Notice',
                                   wx.YES_NO | wx.ICON_INFORMATION)
            if (dlg.ShowModal() == wx.ID_YES):
                self.memoryData.append(["name", self.RemoteEntry.GetValue(), self.LocalEntry.GetValue()])
                self.saveFileNoPop(None)

        elif (self.memoryData[event.GetOldSelection()][MEMORY_INDEX_REMOTE] != self.RemoteEntry.GetValue() or
              self.memoryData[event.GetOldSelection()][MEMORY_INDEX_LOCAL] != self.LocalEntry.GetValue()):
            # page changed

            dlg = wx.MessageDialog(self,
                                   'Do you want to save the modification?\nNotice that this will not modify the config file.',
                                   'Notice',
                                   wx.YES_NO | wx.ICON_INFORMATION)
            if (dlg.ShowModal() == wx.ID_YES):
                self.saveFileNoPop(None)

        else:  # memory == textbox

            self.memoryData[event.GetOldSelection()][MEMORY_INDEX_REMOTE] = self.RemoteEntry.GetValue()
            self.memoryData[event.GetOldSelection()][MEMORY_INDEX_LOCAL] = self.LocalEntry.GetValue()

        # self.log.WriteText("Saved: %s and %s" %(self.memoryData[event.GetSelection()][MEMORY_INDEX_REMOTE],
        # self.memoryData[event.GetSelection()][1]))

    def browseFile(self, event):
        dlg = wx.DirDialog(None, "Choose input directory", "",
                           wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.log.WriteText('You selected: %s.\n' % dlg.GetPath())
            self.LocalEntry.Clear()
            self.LocalEntry.write(dlg.GetPath())  # write to entry box

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()

    # save browsed file
    def saveFile(self, event):
        dlg = wx.MessageDialog(self,
                               'Do you want to save the modification?\nNotice that this will modify the configs.',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        # print(self.currentSelection, self.optionCount)

        if (dlg.ShowModal() == wx.ID_YES):
            if (self.currentSelection == self.optionCount):
                newPreset = {
                    'name': "name",
                    "remote": self.RemoteEntry.GetValue(),
                    "local": self.LocalEntry.GetValue()
                }
                self.JsonData['directory'].append(newPreset)
                self.saveChange()
                self.updateMemory()
                self.log.WriteText(f"Saved: {self.RemoteEntry.GetValue()} and {self.LocalEntry.GetValue()}")
                # update memory data


            else:
                try:

                    self.JsonData['directory'][self.currentSelection]['remote'] = self.RemoteEntry.GetValue()
                    self.JsonData['directory'][self.currentSelection]['local'] = self.LocalEntry.GetValue()
                    self.saveChange()
                    self.updateMemory()
                    self.log.WriteText("Saved: %s and %s" % (
                        self.memoryData[self.currentSelection][MEMORY_INDEX_REMOTE],
                        self.memoryData[self.currentSelection][MEMORY_INDEX_LOCAL]))

                except Exception:  # upon first run#TODO try understand this shitty code
                    self.JsonData['directory'][0]['remote'] = self.memoryData[0][MEMORY_INDEX_REMOTE]
                    self.JsonData['directory'][0]['local'] = self.memoryData[0][MEMORY_INDEX_LOCAL]
                    self.log.WriteText("Saved: %s and %s" % (self.memoryData[0][MEMORY_INDEX_REMOTE],
                                                             self.memoryData[0][MEMORY_INDEX_LOCAL]))

    def saveFileNoPop(self, event):
        if (self.currentSelection == self.optionCount):
            newPreset = {
                'name': "name",
                "remote": self.RemoteEntry.GetValue(),
                "local": self.LocalEntry.GetValue()
            }
            self.JsonData['directory'].append(newPreset)
            self.saveChange()
            self.updateMemory()
            self.log.WriteText(f"Saved: {self.RemoteEntry.GetValue()} and {self.LocalEntry.GetValue()}")
            # update memory data


        else:
            try:
                self.JsonData['directory'][self.currentSelection]['remote'] = self.memoryData[self.currentSelection][
                    MEMORY_INDEX_REMOTE]
                self.JsonData['directory'][self.currentSelection]['local'] = self.memoryData[self.currentSelection][
                    MEMORY_INDEX_LOCAL]
                self.log.WriteText("Saved: %s and %s" % (
                    self.memoryData[self.currentSelection][MEMORY_INDEX_REMOTE],
                    self.memoryData[self.currentSelection][MEMORY_INDEX_LOCAL]))

            except Exception:  # upon first run#TODO try understand this shitty code
                self.JsonData['directory'][0]['remote'] = self.memoryData[0][MEMORY_INDEX_REMOTE]
                self.JsonData['directory'][0]['local'] = self.memoryData[0][MEMORY_INDEX_LOCAL]
                self.log.WriteText("Saved: %s and %s" % (self.memoryData[0][MEMORY_INDEX_REMOTE],
                                                         self.memoryData[0][MEMORY_INDEX_LOCAL]))

    def saveAllFile(self, event):
        dlg = wx.MessageDialog(self,
                               'Do you want to save the modification?\nNotice that this will not modify the config file.',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        if (dlg.ShowModal() == wx.ID_YES):
            for i in range(0, len(self.memoryData)):
                self.JsonData['directory'][i]['remote'] = self.memoryData[i][MEMORY_INDEX_REMOTE]
                self.JsonData['directory'][i]['local'] = self.memoryData[i][MEMORY_INDEX_LOCAL]
                self.log.WriteText("Saved: %s and %s" % (self.memoryData[i][MEMORY_INDEX_REMOTE],
                                                         self.memoryData[i][MEMORY_INDEX_LOCAL]))
            self.log.WriteText("All modification has been saved")

    def saveChange(self):
        with open(f"{CURRENT_DIRECTORY}\\config.json", 'w') as SSHRaw:
            SSHRaw.write(json.dumps(self.JsonData, indent=2))

    def updateMemory(self):
        with open(f"{CURRENT_DIRECTORY}\\config.json") as jsonFile:
            jsonData = json.load(jsonFile)
            self.JsonData = jsonData
        self.initFromJson(self.JsonData)
        self.SetPageText(self.optionCount, self.JsonData['directory'][self.optionCount]['name'])
        self.optionCount += 1
        self.AddPage(self.win, "create New Preset")


if __name__ == '__main__':
    app = wx.App()
    log = Log()
    frame = TestGUIFrame()

    app.MainLoop()
