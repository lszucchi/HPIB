import sys
sys.path.append("Modules")

from Tab_GP import *
from Tab_IV import *
from Tab_CV import *
from Tab_4P import *

from defaults import *   

                
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
        
        self.notebook = NotebookDemo(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Layout()
        self.SetSize(1535,555)
        self.Move(wx.Point(-8,0))
        self.Maximize(False)
 
        self.Show()

    def OnPageChanged(self, event):
        match event.GetSelection():
            case 0:
                self.SetSize(1535,555)
            case 1:
                self.Maximize(False)
                self.SetSize(1570,555)
                self.Move(wx.Point(-8,0))
            case 2:
                self.Maximize(False)
                self.SetSize(980,555)
            case 3:
                self.SetSize(980,555)
                
        event.Skip()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = DemoFrame()
    app.MainLoop()
