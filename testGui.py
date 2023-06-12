import wx
import string
import os
import json
from wx.core import BoxSizer, EXPAND, HORIZONTAL, LEFT, NB_FIXEDWIDTH, Right, Size, StaticText
import Sync

allTags = ["Space Engineer","SE Blue Prints","Stellaris","ST MOD","Skyrim","Civ V", "Banished"]

class Log:
    def WriteText(self, text):
        if text[-1:] == '\n':
            text = text[:-1]
        wx.LogMessage(text)
    write = WriteText


class TestGUIFrame(wx.Frame):
    def __init__(self):
        super().__init__(parent=None, title='test GUI')
        #self.SetSize((460,250))
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)
        self.currentDirectory = os.getcwd()
        with open(f"{self.currentDirectory}\\config.json") as SSHRaw:
            allConfig = json.load(SSHRaw)
            self.allDef = allConfig
        panel = wx.Panel(self)
        self.log = log
        
        ArchSizer = wx.BoxSizer(wx.VERTICAL)
        
        FirstMajorSizer = wx.BoxSizer(wx.HORIZONTAL)
        ##ServerIp, userName, timeOut instruction:
        FirstRowColumn1 = wx.BoxSizer(wx.VERTICAL)
        #serverIP Instruction
        serverIPInst = wx.StaticText(panel, -1, "Server IP: ")
        serverIPInst.SetFont(font)
        #userName Instruction
        userNameInst = wx.StaticText(panel, -1, "Username: ")
        userNameInst.SetFont(font)

        FirstRowColumn1.Add(serverIPInst,flag = wx.TOP,border = 3)
        FirstRowColumn1.Add(userNameInst,flag = wx.TOP,border = 16)

        ##ServerIP, userName, timeOut EntryBox:
        FirstRowColumn2 = wx.BoxSizer(wx.VERTICAL)
        self.serverIPEntry = wx.TextCtrl(panel)
        self.userNameEntry = wx.TextCtrl(panel)
        self.serverIPEntry.SetSize(120,-1)
        self.userNameEntry.SetSize(120,-1)
        FirstRowColumn2.Add(self.serverIPEntry,flag = wx.TOP|wx.BOTTOM,border = 10)
        FirstRowColumn2.Add(self.userNameEntry,flag = wx.BOTTOM,border = 10)

        ##Port, password instruction:
        FirstRowColumn3 = wx.BoxSizer(wx.VERTICAL)
        #Port Instruction
        portInst = wx.StaticText(panel, -1, "Server port: ")
        portInst.SetFont(font)
        #password Instruction
        passwordInst = wx.StaticText(panel, -1, "Password: ")
        passwordInst.SetFont(font)

        FirstRowColumn3.Add(portInst,flag = wx.TOP,border = 3)
        FirstRowColumn3.Add(passwordInst,flag = wx.TOP,border = 16)

        ##Port, password EntryBox:
        FirstRowColumn4 = wx.BoxSizer(wx.VERTICAL)
        self.portEntry = wx.TextCtrl(panel)
        self.passwordEntry = wx.TextCtrl(panel,style = wx.TE_PASSWORD)
        self.portEntry.SetSize((120,-1))
        self.passwordEntry.SetSize((120,-1))
        FirstRowColumn4.Add(self.portEntry,flag = wx.TOP|wx.BOTTOM,border = 10)
        FirstRowColumn4.Add(self.passwordEntry,flag = wx.BOTTOM,border = 10)

        FirstMajorSizer.Add(FirstRowColumn1,flag = wx.LEFT | wx.RIGHT |wx.TOP, border = 10)
        FirstMajorSizer.Add(FirstRowColumn2,flag = wx.RIGHT, border = 10)
        FirstMajorSizer.Add(FirstRowColumn3,flag = wx.LEFT|wx.RIGHT|wx.TOP, border = 10)
        FirstMajorSizer.Add(FirstRowColumn4,flag = wx.RIGHT, border = 10)

        #TODO choice book class init
        #SecondMajorSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.mainChocieBook = menuChoiceBook(panel,log,allConfig)
        #SecondMajorSizer.Add(mainChocieBook,flag = wx.EXPAND)
        #confirm reject sizer
        ThridMajorSizer = wx.BoxSizer(wx.HORIZONTAL)
        saveBtn = wx.Button(panel, label = "Apply")
        saveBtn.Bind(wx.EVT_BUTTON,self.applyChange)
        pushBtn = wx.Button(panel, label = "push")
        pullBtn = wx.Button(panel, label = "pull")
        #cancelBtn = wx.Button(panel, label = "Cancel")
        #cancelBtn.Bind(wx.EVT_BUTTON,self.closeWindow)

        ThridMajorSizer.Add(saveBtn,flag = wx.RIGHT, border = 5)
        ThridMajorSizer.Add(pushBtn,flag = wx.RIGHT,border = 5)
        ThridMajorSizer.Add(pullBtn,flag = wx.RIGHT,border = 5)
        #ThridMajorSizer.Add(cancelBtn)

        #pushBtn.Bind(wx.EVT_BUTTON,TODO: push to remote)
        #pullBtn.Bind(wx.EVT_BUTTON,TODO: pull from remote)
        #saveBtn.Bind(wx.EVT_BUTTON,TODO: write to json)
        
        ArchSizer.Add(FirstMajorSizer)
        ArchSizer.Add(self.mainChocieBook,flag = wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP,border = 10)
        ArchSizer.Add(ThridMajorSizer, flag = wx.ALIGN_LEFT|wx.BOTTOM|wx.LEFT,border = 10)
        
        panel.SetSizer(ArchSizer)
        ArchSizer.SetSizeHints(self)
        self.readFromJson(allConfig)
        self.mainChocieBook.win.Show()
        self.Show()

    def readFromJson(self,SSHDetail):
        
        host = SSHDetail['host']  # Server ip address
        port = SSHDetail['port']  # port
        username = SSHDetail['username']  # ssh userID
        password = SSHDetail['password']  # password

        self.serverIPEntry.write(host)
        self.portEntry.write(str(port))
        self.userNameEntry.write(username)
        self.passwordEntry.write(password)

    def closeWindow(self,event):
        self.Close(True)

    def applyChange(self,event):
        self.allDef = self.mainChocieBook.JsonData
        with open(f"{self.currentDirectory}\\config.json",'w') as SSHRaw:
            SSHRaw.write(json.dumps(self.allDef, indent=2))
        


class menuChoiceBook(wx.Choicebook):
    def __init__(self, parent, log, JsonData):
        wx.Choicebook.__init__(self, parent)
        self.log = log
        self.JsonData = JsonData
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(9)
        
        self.initFromJson(JsonData)
        self.win = wx.Panel(self)
        PanelSizer = BoxSizer(wx.HORIZONTAL)
        LeftSizer = BoxSizer(wx.VERTICAL)

        RemoteInst = wx.StaticText(self.win, -1, label = "Remote Directory: ")
        RemoteInst.SetFont(font)

        LocalInst = wx.StaticText(self.win, -1, label = "Local Directory: ")
        LocalInst.SetFont(font)
            
        LeftSizer.Add(RemoteInst,flag = wx.TOP, border = 3)
        LeftSizer.Add(LocalInst,flag = wx.TOP, border = 16)

        RightSizer = BoxSizer(wx.VERTICAL)
        self.RemoteEntry = wx.TextCtrl(self.win)
        self.LocalEntry = wx.TextCtrl(self.win)
        
        RightSizer.Add(self.RemoteEntry,flag = wx.EXPAND)
        RightSizer.Add(self.LocalEntry,flag =wx.TOP|wx.EXPAND, border = 10)
        TwinBtnSizer = BoxSizer(wx.HORIZONTAL)
        #Create and bind buttons
        fileBrowserBtn = wx.Button(self.win, label = "Browse")
        fileBrowserBtn.Bind(wx.EVT_BUTTON,self.browseFile)
        fileSaveBtn = wx.Button(self.win,label = "Save")
        fileSaveBtn.Bind(wx.EVT_BUTTON,self.saveFile)
        fileSaveAllBtn = wx.Button(self.win,label = "Save All")
        fileSaveAllBtn.Bind(wx.EVT_BUTTON, self.saveAllFile)
        #fileSaveAllBtn.Bind(wx.EVT_BUTTON,self.saveAllFile())

        TwinBtnSizer.AddMany([(fileBrowserBtn,0,wx.LEFT,10),(fileSaveBtn,0,wx.RIGHT|wx.LEFT,5),(fileSaveAllBtn,0,wx.RIGHT,10)])
        RightSizer.Add(TwinBtnSizer,flag = wx.TOP|wx.BOTTOM|wx.EXPAND,border = 10)
        PanelSizer.Add(LeftSizer,flag = wx.LEFT|wx.RIGHT,border = 10)
        PanelSizer.Add(RightSizer,flag = wx.EXPAND|wx.RIGHT,border = 10)
        self.win.SetSizer(PanelSizer)

        self.CurrentSelection = 0
        self.RemoteEntry.write(JsonData['directory'][0]['remote'])
        self.LocalEntry.write(JsonData['directory'][0]['local'])
        # Now make a bunch of panels for the choice book
        count = 0
        for name in JsonData['directory']:
            count += 1
            self.AddPage(self.win, name['name'])

        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Bind(wx.EVT_CHOICEBOOK_PAGE_CHANGING, self.OnPageChanging)

    def initFromJson(self,JsonData):#TODO - hardcoded
        self.memoryData = []
        for addr in JsonData['directory']:
            self.memoryData.append([addr['remote'],addr['local']])
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
    #update menu book
    def OnPageChanged(self, event):
        self.CurrentSelection = event.GetSelection()
        self.RemoteEntry.Clear()
        self.RemoteEntry.write(self.JsonData['directory'][self.CurrentSelection]['remote'])
        self.LocalEntry.Clear()
        self.LocalEntry.write(self.JsonData['directory'][self.CurrentSelection]['local'])
        
        event.Skip()
        
    #update menu book changing...
    def OnPageChanging(self, event):
        self.memoryData[event.GetSelection()][0] = self.RemoteEntry.GetValue()
        self.memoryData[event.GetSelection()][1] = self.LocalEntry.GetValue()
        dlg = wx.MessageDialog(self,'Do you want to save the modification?\nNotice that this will not modify the config file.',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        #if(dlg.ShowModal ()==wx.ID_YES):
           # self.log.WriteText("Saved: %s and %s" %(self.memoryData[event.GetSelection()][0],self.memoryData[event.GetSelection()][1]))
        event.Skip()

    def browseFile(self,event):
        dlg = wx.DirDialog (None, "Choose input directory", "",
                    wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.log.WriteText('You selected: %s.\n' % dlg.GetPath())
            self.LocalEntry.write(dlg.GetPath())#write to entry box

        # Only destroy a dialog after you're done with it.
        dlg.Destroy()
    #save browsed file
    def saveFile(self,event):
        dlg = wx.MessageDialog(self,'Do you want to save the modification?\nNotice that this will not modify the config file.',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        if(dlg.ShowModal ()==wx.ID_YES):
            try:
                self.JsonData['directory'][self.CurrentSelection]['remote'] = self.memoryData[self.CurrentSelection][0]
                self.JsonData['directory'][self.CurrentSelection]['local'] = self.memoryData[self.CurrentSelection][1]
                self.log.WriteText("Saved: %s and %s" %(self.memoryData[self.CurrentSelection][0],self.memoryData[self.CurrentSelection][1]))
            except Exception: #upon first run
                self.JsonData['directory'][0]['remote'] = self.memoryData[0][0]
                self.JsonData['directory'][0]['local'] = self.memoryData[0][1]
                self.log.WriteText("Saved: %s and %s" %(self.memoryData[0][0],self.memoryData[0][1]))

    
    def saveAllFile(self,event):
        dlg = wx.MessageDialog(self,'Do you want to save the modification?\nNotice that this will not modify the config file.',
                               'Notice',
                               wx.YES_NO | wx.ICON_INFORMATION)
        if(dlg.ShowModal ()==wx.ID_YES):
            for i in range (0,len(self.memoryData)):
                self.JsonData['directory'][i]['remote'] = self.memoryData[i][0]
                self.JsonData['directory'][i]['local'] = self.memoryData[i][1]
                self.log.WriteText("Saved: %s and %s" %(self.memoryData[i][0],self.memoryData[i][1]))
            self.log.WriteText("All modification has been saved")
        
        

if __name__ == '__main__':
    app = wx.App()
    log = Log()
    frame = TestGUIFrame()
    app.MainLoop()
    


    
