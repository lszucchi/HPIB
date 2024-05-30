from Modules.Tab_Generic import *
from Modules.Tab_4P import FourPoint
from Modules.Tab_CV import CVTab
from Modules.Tab_GP import General
from Modules.Tab_IV import IVTab
                
####### COMMIT TEST
                
########################################################################
class NotebookDemo(wx.Notebook):
    """
    Notebook class
    """
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=
                             wx.BK_DEFAULT
                             #wx.BK_TOP 
                             #wx.BK_BOTTOM
                             #wx.BK_LEFT
                             #wx.BK_RIGHT
                             )

        self.AddPage(General(self), "General")
        
        # Create the first tab and add it to the notebook
        self.AddPage(IVTab(self), "I-V Measurements")
 
        # Create and add the second tab
        self.AddPage(CVTab(self), "C-V Mesurements")
 
        # Create and add the third tab
        self.AddPage(FourPoint(self), "4-Point Measurements")        
 
 
########################################################################
class DemoFrame(wx.Frame):
    """
    Frame that holds all other widgets
    """
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Measure CryoCMOS"
                          )
        panel = wx.Panel(self)
        
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        
        menubar.Append(fileMenu, "Tools")
        
        self.SetDebug = fileMenu.AppendCheckItem(wx.NewIdRef(), 'Enable Debug')
        self.Bind (wx.EVT_MENU, self.OnSetDebug, self.SetDebug)
        reinit = fileMenu.Append(wx.NewIdRef(), 'REINIT')
        self.Bind(wx.EVT_MENU, self.OnReinit, reinit)

        self.SetMenuBar ( menubar )

        self.notebook = NotebookDemo(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)
        self.notebook.debug=False

        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Layout()
        self.SetSize(1535,570)
        self.Move(wx.Point(-8,0))
        self.Maximize(False)
 
        self.Show()

        
    def OnSetDebug(self, event):
        self.SetDebug.Check(self.SetDebug.IsChecked())
        self.notebook.debug = self.SetDebug.IsChecked()
        print(self.notebook.debug)
            
        return 0

    def OnReinit(self, event):
        for child in self.notebook.GetChildren()[0].GetChildren():
            if 'sv_' in child.Name:
                print(child.GetName())
        print(self.notebook.GetPageText(0))
        return 0
		

    def OnPageChanged(self, event):
        match event.GetSelection():
            case 0:
                self.SetSize(1535,570)
            case 1:
                self.Maximize(False)
                self.SetSize(1570,570)
                self.Move(wx.Point(-8,0))
            case 2:
                self.Maximize(False)
                self.SetSize(980,570)
            case 3:
                self.SetSize(980,570)
                
        event.Skip()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = DemoFrame()
    app.MainLoop()