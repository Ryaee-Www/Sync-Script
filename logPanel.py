import wx

class LogPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent)

        self.log_text = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)

        # Create a sizer for the log text box
        text_sizer = wx.BoxSizer(wx.VERTICAL)
        text_sizer.Add(self.log_text, proportion=1, flag=wx.EXPAND)
        text_sizer.AddSpacer(10)

        # Create a sizer for the overall panel
        panel_sizer = wx.BoxSizer(wx.HORIZONTAL)
        panel_sizer.AddSpacer(10)  # Add a 10-pixel space to the left
        panel_sizer.Add(text_sizer, proportion=1, flag=wx.EXPAND)
        panel_sizer.AddSpacer(10)  # Add a 10-pixel space to the right

        # Set the panel's sizer
        self.SetSizer(panel_sizer)

    def print(self, message):
        self.log_text.AppendText(message + '\n')
        print(message)

class MyFrame(wx.Frame):
    def __init__(self, parent):
        super().__init__(parent, title="Log Text Box Example")
        self.log_panel = LogPanel(self)
        self.Show()

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame(None)

    app.MainLoop()