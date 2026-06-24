import wx, configparser

config=configparser.ConfigParser()
config.read("./config.ini")

from mainpanel import General

########################################################################
class MainFrame(wx.Frame):
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Measure CryoCMOS"
                          )
        self.MainPanel = General(self)
        
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        
        menubar.Append(fileMenu, "Tools")
        
        self.SetDebug = fileMenu.AppendCheckItem(wx.NewIdRef(), 'Enable Debug')
        self.Bind (wx.EVT_MENU, self.OnSetDebug, self.SetDebug)
        self.reinit = fileMenu.Append(wx.NewIdRef(), 'Restore defaults')
        self.Bind(wx.EVT_MENU, self.OnReinit, self.reinit)

        self.SetMenuBar ( menubar )

        try:
            config.read("config.ini")
            self.SetDebug.Check(config['Window'].getboolean('Debug'))
        except:
            config['Window']={}
            config['Window']['Debug']='False'
            config['Window']['Margin']='10'
            config['Window']['SMUMY']='40'
            config['Window']['SMUMX']='90'
            config['Window']['PhotoMaxSizeX']='610'

        try:
            for child in self.MainPanel.GetChildren():
                if 'sv_' in child.GetName():
                    if 'en' in child.GetName() or 'cb' in child.GetName():
                        child.SetValue(config['General'.__class__.__name__].getboolean(child.GetName()))
                    else:
                        child.SetValue(config['General'.__class__.__name__][child.GetName()])
        except: pass

        self.Layout()
        self.SetSize(1366,475)
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
        for child in self.MainPanel.GetChildren():
            if 'sv_' in child.GetName():
                if 'en' in child.GetName() or 'cb' in child.GetName():
                    child.SetValue(config['General'].getboolean(child.GetName()))
                else:
                    child.SetValue(config['General'][child.GetName()])
        return 0
    
    def OnClose(self, event):
        for child in self.MainPanel.GetChildren():
            if 'sv_' in child.GetName():
                config['General'][child.GetName()]=str(child.GetValue())
        
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            
        event.Skip()
 
#----------------------------------------------------------------------
if __name__ == "__main__":
    app = wx.App()
    frame = MainFrame()
    app.MainLoop()
