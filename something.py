import wx
from wx import *

class ButtonColumn ( wx.Panel ):
    '''Create aligned column of equal-sized buttons with distinct labels and OnClick destinations.

    Illustrates use of nested classes for creating a collection of controls.
    Also illustrates use of mouse over and mouse leave events.
    '''
    class aButton ( wx.Button ):
        '''Nested button class for use by ButtonColumn class.'''
        def __init__ ( self, parent, label, whotocall, whotonotify, msg ):
            """Expects reference to 'ButtonColumn', list of labels for buttons and list of functions to be called for OnClick events"""
            id = wx.NewId ( )
            wx.Button . __init__ ( self, parent, id, label, wx.DefaultPosition, wx.DefaultSize, 1 )
            self . whotocall = whotocall
            self . whotonotify = whotonotify
            self . msg = msg
            EVT_BUTTON ( self, id, self.OnClick )
            EVT_ENTER_WINDOW ( self, self . OnEnter )
            EVT_LEAVE_WINDOW ( self, self . OnLeave )

        def OnClick ( self, event ):
            if self . whotocall: self . whotocall ( )
            
        def OnEnter ( self, event ) :
            if self . whotonotify : self . whotonotify ( 1, self . msg )
        
        def OnLeave ( self, event ) :
            if self . whotonotify : self . whotonotify ( 0, self . msg )

    def __init__ ( self, parent, width, buttons, Bottom = 0 ):
        """Expects reference to 'parent' of 'ButtonColumn', button column 'width', list of button descriptor tuples, and number of buttons to be displayed at the bottom of the column.

        Each button descriptor consists of a label for the button and a reference to the function to be called when the button is clicked.
        """
        wx.Panel . __init__ ( self, parent, -1, wx.DefaultPosition, ( 100, 200 ) )
        self . parent = parent

        """Create the upper collection of buttons"""
        previous = None
        for button in buttons [ 0 : len ( buttons ) -Bottom ]:
            oneButton = self . aButton ( self, button [ 0 ], button [ 1 ], button [ 2 ], button [ 3 ] )
            lc = wx.LayoutConstraints ( )
            lc . left . SameAs ( self, wx.Left, 5 )
            lc . right . SameAs ( self, wx.Right, 5 )
            lc . height . AsIs ( )
            if previous: lc . top . SameAs ( previous, wx.Bottom, 5 )
            else: lc . top . SameAs ( self, wx.Top, 5 )
            oneButton . SetConstraints ( lc )
            previous = oneButton

        """Create the lower collection of buttons"""
        buttons . reverse ( )
        previous = None
        for button in buttons [ 0 : Bottom ]:
            oneButton = self . aButton ( self, button [ 0 ], button [ 1 ], button [ 2 ], button [ 3 ] )
            lc = wx.LayoutConstraints ( )
            lc . left . SameAs ( self, wx.Left, 5 )
            lc . right . SameAs ( self, wx.Right, 5 )
            lc . height . AsIs ( )
            if previous: lc . bottom . SameAs ( previous, wx.Top, 5 )
            else: lc . bottom . SameAs ( self, wx.Bottom, 5 )
            oneButton . SetConstraints ( lc )
            previous = oneButton
class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame . __init__ (
            self, None, -1, "Button Column Test",
            size = ( 450, 300 ),
            style = wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE
            )
        self . SetAutoLayout ( True )
        buttons = [
            ( 'OK', self . OKClicked, self . OnMessage, 'OK button text', ),
            ( 'Cancel', self . CancelClicked, self . OnMessage, 'Cancel button text', ),
            ( 'Re-invert', self . ReinvertClicked, self . OnMessage, 'Re-invert button text', ),
            ( 'Exit', self . ExitClicked, self . OnMessage, 'Exit button text', ),
            ]

        self . tp = ButtonColumn ( self, 45, buttons, 2 )

        lc = wx.LayoutConstraints ( )
        lc . right . SameAs ( self, wx.Right)
        lc . width . AsIs ( )
        lc . top . SameAs ( self, wx.Top )
        lc . bottom . SameAs ( self, wx.Bottom )
        self . tp . SetConstraints ( lc )

        self . CreateStatusBar ( )
        
    def OnMessage ( self, on, msg ) :
        if not on : msg = ""
        self . SetStatusText ( msg )

    def OKClicked ( self ):
        print ("OKClicked")

    def CancelClicked ( self ):
        print ("CancelClicked")

    def ReinvertClicked ( self ):
        print ("ReInvertClicked")

    def ExitClicked ( self ):
        print ("ExitClicked")
        self . Close ( )
if __name__ == '__main__':


    app = wx.PySimpleApp()
    frame = TestFrame()
    frame . Show(True)
    app . MainLoop()