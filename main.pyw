from modules.Tab_Generic import *
from modules.Tab_4P import FourPoint
from modules.Tab_CV import CVTab
from modules.Tab_GP import General
from modules.Tab_IV import IVTab

########################################################################
class MainNotebook(wx.Notebook):
 
    #----------------------------------------------------------------------
    def __init__(self, parent):
        wx.Notebook.__init__(self, parent, id=wx.ID_ANY, style=wx.BK_DEFAULT)

        self.AddPage(General(self), "General")
        
        self.AddPage(IVTab(self), "I-V Measurements")
 
        self.AddPage(CVTab(self), "C-V Measurements")
 
        self.AddPage(FourPoint(self), "4-Point Measurements")        
 
 
########################################################################
class MainFrame(wx.Frame):
 
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
        
        try:
            config.read("config.ini")
            self.SetDebug.Check(config['Window'].getboolean('Debug'))
            for page in self.notebook.GetChildren():
                for child in page.GetChildren():
                    if 'sv_' in child.GetName():
                        if 'en' in child.GetName() or 'cb' in child.GetName():
                            child.SetValue(config[page.__class__.__name__].getboolean(child.GetName()))
                        else:
                            child.SetValue(config[page.__class__.__name__][child.GetName()])
            self.notebook.GetChildren()[0].SetSizers(True)
            self.notebook.GetChildren()[1].DrawVgsVd(True)
            self.notebook.GetChildren()[1].DrawVgsVdSat(True)
            self.notebook.GetChildren()[1].DrawIspecDef(True)
        except:
            config['Window']={}
            config['Window']['Debug']='False'
            config['Window']['Margin']='10'
            config['Window']['SMUMY']='40'
            config['Window']['SMUMX']='90'
            config['Window']['PhotoMaxSizeX']='610'

        self.SetDebug = fileMenu.AppendCheckItem(wx.NewIdRef(), 'Enable Debug')
        self.Bind (wx.EVT_MENU, self.OnSetDebug, self.SetDebug)
        self.reinit = fileMenu.Append(wx.NewIdRef(), 'Restore defaults')
        self.Bind(wx.EVT_MENU, self.OnReinit, self.reinit)

        self.SetMenuBar ( menubar )

        self.notebook = MainNotebook(panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL|wx.EXPAND, 5)
        panel.SetSizer(sizer)

        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.Layout()
        self.SetSize(1455,570)
        self.Move(wx.Point(-8,0))
        self.Maximize(False)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Show()

        
    def OnSetDebug(self, event):
        self.SetDebug.Check(self.SetDebug.IsChecked())
        config['Window']['Debug'] = str(self.SetDebug.IsChecked())
        if config['Window']['Debug']:
            print('Debug Mode On')
            
        return 0

    def OnReinit(self, event):
        config.read("defaults.ini")
        for page in self.notebook.GetChildren():
            for child in page.GetChildren():
                if 'sv_' in child.GetName():
                    if 'en' in child.GetName() or 'cb' in child.GetName():
                        child.SetValue(config[page.__class__.__name__].getboolean(child.GetName()))
                    else:
                        child.SetValue(config[page.__class__.__name__][child.GetName()])
            self.notebook.GetChildren()[0].SetSizers(True)
            self.notebook.GetChildren()[1].DrawVgsVd(True)
            self.notebook.GetChildren()[1].DrawVgsVdSat(True)
            self.notebook.GetChildren()[1].DrawIspecDef(True)
        return 0
    
    def OnClose(self, event):
        for page in self.notebook.GetChildren():
            config[page.__class__.__name__]={}
            for child in page.GetChildren():
                if 'sv_' in child.GetName():
                    config[page.__class__.__name__][child.GetName()]=str(child.GetValue())
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
        event.Skip()

    def OnPageChanged(self, event):
        match event.GetSelection():
            case 0:
                self.SetSize(1455,570)
            case 1:
                self.Maximize(False)
                self.SetSize(1435,570)
                self.Move(wx.Point(-8,0))
            case 2:
                self.Maximize(False)
                self.SetSize(1040,570)
            case 3:
                self.SetSize(1040,570)
                
        event.Skip()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
