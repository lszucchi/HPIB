import os, wx, datetime, time, configparser
import wx.lib.agw.floatspin as FS7
from threading import Thread

config=configparser.ConfigParser()
config.read("config.ini")

from .HP4145 import HP4145
from .HP4155 import HP4155
from .HPT import *
from .INOSerial import *

class GenericTab(wx.Panel):

    def OpenHP(self, addr, inst):
        
        if config['Window'].getboolean('Debug'):
            print('\n\n\n ################# HP4155 Debug #################\n\n\n')

        if 'GPIB' not in addr:
            addr="GPIB0::"+str(addr)
        
        if inst=='HP4155':
            try:
                self.HP = HP4155(addr, read_termination = '\n', write_termination = '\n', timeout=None, debug=config['Window'].getboolean('Debug'))
            except Exception as error:
                if self.ShowMessage('Communication error:\nInstrument not found', True): raise error
                return 1
        elif inst=='HP4145':
            try:
                self.HP = HP4145(addr, read_termination = '\n', write_termination = '\n', timeout=None, debug=config['Window'].getboolean('Debug'))
            except Exception as error:
                if self.ShowMessage('Communication error:\nInstrument not found', True): raise error
                return 1            
        else:
            if self.ShowMessage('Input error:\nInvalid Instrument', True): raise RuntimeError('Invalid Instrument')
            return 1
        
    def DrawSaveBox(self, X, Y, length):
        Bx0=wx.StaticBox(self, pos=(X,Y), size=(length+115,70),label='Save:')
        Bx0.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Dir_Select = wx.Button(self, label='Save dir', pos=(X+10,Y+25),size=(80,30))
        self.Dir_Select.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Dir_Select.Bind(wx.EVT_BUTTON, self.OnSaveButton)
        self.SaveFilePath=wx.TextCtrl(self, pos=(X+100, Y+25), size=(length, 30), style=wx.TE_LEFT)
        
    
    def DrawConfigBox(self, X, Y):
 
        #========  Config Box ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        self.Box1=[[X, Y],[200,280]]
        self.Bx1=wx.StaticBox(self,label='Port and SM Config', pos=(self.Box1[0][0], self.Box1[0][1]),size=(self.Box1[1][0], self.Box1[1][1]))
        self.Sizer1=wx.BoxSizer()
        self.Sizer2=wx.BoxSizer()

        #Instr Select
        self.InstTx = wx.StaticText(self, label='Instrument', pos=(self.Box1[0][0]+int(config['Window']['Margin'])+5, self.Box1[0][1]+2*int(config['Window']['Margin'])))
        self.Inst = wx.ComboBox(self, value='HP4155', pos=(self.Box1[0][0]+int(config['Window']['Margin'])+5, self.Box1[0][1]+4*int(config['Window']['Margin'])), choices=['HP4145','HP4155'], name='sv_Inst')

        #GPIB address selection box
        self.GPIBTXT = wx.StaticText(self, label='GBIP Address', pos=(self.Box1[0][0]+105, self.Box1[0][1]+2*int(config['Window']['Margin'])))
        self.GPIBCH = wx.ComboBox(self, value='17', pos=(self.Box1[0][0]+105, self.Box1[0][1]+4*int(config['Window']['Margin'])), size=(40,40), choices=['15','16','17'], name='sv_GPIBCH')
        self.Sizer2.Add(self.GPIBCH)

        
        #COM port selection box
        self.COMEnable = wx.CheckBox(self, label='SM Port', pos=(self.Box1[0][0]+int(config['Window']['Margin'])+5, self.Box1[0][1]+2*int(config['Window']['Margin'])+50))
        self.COMEnable.SetValue(0)
        self.COM = wx.ComboBox(self, value='COM3', pos=(self.Box1[0][0]+int(config['Window']['Margin'])+5, self.Box1[0][1]+4*int(config['Window']['Margin'])+50), choices=['COM3','COM4'], name='sv_COM')
        self.Sizer1.Add(self.COM)

        #Checkboxes
        cbpos=(self.Box1[0][0]+int(config['Window']['Margin']), self.Box1[0][1]+125)
        self.cb1 = wx.CheckBox(self, label='Channel 1', pos=(cbpos[0], cbpos[1]))
        self.cb2 = wx.CheckBox(self, label='Channel 2', pos=(cbpos[0], cbpos[1]+25))
        self.cb3 = wx.CheckBox(self, label='Channel 3', pos=(cbpos[0], cbpos[1]+50))
        self.cb4 = wx.CheckBox(self, label='Channel 4', pos=(cbpos[0], cbpos[1]+75))
        self.cb5 = wx.CheckBox(self, label='Channel 5', pos=(cbpos[0], cbpos[1]+100))
        self.cb6 = wx.CheckBox(self, label='Channel 6', pos=(cbpos[0], cbpos[1]+125))
        self.Sizer1.Add(self.cb1)
        self.Sizer1.Add(self.cb2)
        self.Sizer1.Add(self.cb3)
        self.Sizer1.Add(self.cb4)
        self.Sizer1.Add(self.cb5)
        self.Sizer1.Add(self.cb6)
        
        def ToggleSizer(evt):
            for child in self.Sizer1.GetChildren():
                try:
                    child.GetWindow().Enable(self.COMEnable.GetValue())
                except:
                    print('ERROR')
                    
        ToggleSizer(1)
        self.COMEnable.Bind(wx.EVT_CHECKBOX, ToggleSizer)

        #Send HP config
        self.Config_Btn = wx.Button(self, label='Send HP\nConfig', pos=(self.Box1[0][0]+100, cbpos[1]+10-40), size=(80, 40))
        self.Sizer2.Add(self.Config_Btn)
        self.Config_Btn.Bind(wx.EVT_BUTTON, self.OnConfig)

        #Start button
        self.Btn_Start = wx.Button(self, label='Start', pos=(self.Box1[0][0]+90, cbpos[1]+10+2*int(config['Window']['Margin'])),size=(100,60))
        self.Sizer2.Add(self.Btn_Start)
        self.Btn_Start.Bind(wx.EVT_BUTTON, self.OnButton)
        

        #Stop button
        Btn_Stop = wx.Button(self, label='Stop', pos=(self.Box1[0][0]+100+25, cbpos[1]+10+60+4*int(config['Window']['Margin'])),size=(50,30))
        Btn_Stop.Bind(wx.EVT_BUTTON, self.Stop)

    def DrawSMUConfig(self, X, Y):
        
        self.Box1a=[[X, Y],[200,93]]
        self.Bx1a=wx.StaticBox(self,label='SMU Config', pos=(self.Box1a[0][0], self.Box1a[0][1]),size=(self.Box1a[1][0], self.Box1a[1][1]))
        self.Sizer1a=wx.StaticBoxSizer(self.Bx1a)

        self.SBoxTx = wx.StaticText(self, label='S:', pos=(X+int(config['Window']['Margin']), Y+2*int(config['Window']['Margin'])+3))
        self.SBox  = wx.ComboBox(self, value='SMU1', pos=(X+2*int(config['Window']['Margin'])+5, Y+2*int(config['Window']['Margin'])), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'], name='sv_SBox')
        self.Sizer1a.Add(self.SBox)

        self.DBoxTx  = wx.StaticText(self, label='D:', pos=(X+2*int(config['Window']['Margin'])+int(config['Window']['SMUMX']), Y+2*int(config['Window']['Margin'])+3))
        self.DBox = wx.ComboBox(self, value='SMU2', pos=(X+3*int(config['Window']['Margin'])+5+int(config['Window']['SMUMX']), Y+2*int(config['Window']['Margin'])), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'], name='sv_DBox')
        self.Sizer1a.Add(self.DBox)

        self.BBoxTx = wx.StaticText(self, label='B:', pos=(X+int(config['Window']['Margin']), Y+2*int(config['Window']['Margin'])+3+int(config['Window']['SMUMY'])))
        self.BBox = wx.ComboBox(self, value='SMU4', pos=(X+2*int(config['Window']['Margin'])+5, Y+2*int(config['Window']['Margin'])+int(config['Window']['SMUMY'])), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'], name='sv_BBox')
        self.Sizer1a.Add(self.BBox)

        self.GBoxTx = wx.StaticText(self, label='G:', pos=(X+2*int(config['Window']['Margin'])+int(config['Window']['SMUMX']),  Y+2*int(config['Window']['Margin'])+3+int(config['Window']['SMUMY'])))
        self.GBox = wx.ComboBox(self, value='SMU3', pos=(X+3*int(config['Window']['Margin'])+5+int(config['Window']['SMUMX']), Y+2*int(config['Window']['Margin'])+int(config['Window']['SMUMY'])), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'], name='sv_GBox')
        self.Sizer1a.Add(self.GBox)

    def Stop(self, event):
        self.Stop_flag = True
        self.HP.stop()
    
    def OnConfig(self, event):
        self.Config_Btn.Disable()
        self.Config_Btn.SetLabel("Sending\nconfig")
        self.testThread = Thread(target=self.Configure)
        self.testThread.start()
        self.Btn_Start.SetLabel("Running\n.")
        self.Btn_Start.Disable()
        self.Bind(wx.EVT_TIMER, self.PollThread)
        self.timer.Start(20, oneShot=True)
        event.Skip()
        
    def OnButton(self, event):
        self.Stop_flag=False
        if not hasattr(self, 'HP'):
            if self.ShowMessage("No config sent", False):
                return 1
        if self.SaveFilePath.GetValue() == "":
            if self.ShowMessage("Select savepath and try again", False):
                self.OnSaveButton(1)
            return 1
        self.testThread = Thread(target=self.Measure)
        self.testThread.start()
        self.Btn_Start.SetLabel("Running\n.")
        self.Btn_Start.Disable()
        self.Config_Btn.Disable()
        self.Bind(wx.EVT_TIMER, self.PollThread)
        self.timer.Start(20, oneShot=True)
        event.Skip()

    def ShowMessage(self, Msg, Error):
        MsgBox=wx.MessageDialog(self, Msg, 'Info', wx.OK | wx.ICON_INFORMATION | wx.CANCEL)
        if Error:
           MsgBox.SetOKCancelLabels('OK', 'Verbose')
           return (MsgBox.ShowModal()&1)
        return not (MsgBox.ShowModal()&1)

    def PollThread(self, event):
            if self.testThread.is_alive():
                    self.Bind(wx.EVT_TIMER, self.PollThread)
                    self.timer.Start(200, oneShot=True)
                    self.Btn_Start.Disable()
                    self.Btn_Start.SetLabel(self.Btn_Start.GetLabel() + ".")
                    if(len(self.Btn_Start.GetLabel())>25):
                            self.Btn_Start.SetLabel("Running\n.")
            else:
                    self.Config_Btn.Enable()
                    self.Config_Btn.SetLabel('Send HP\nConfig')
                    self.Btn_Start.Enable()
                    self.Btn_Start.SetLabel("Start")
                    self.Stop_flag=False

    def OnSaveButton(self, event):
        dialog = wx.DirDialog(None, "Choose a directory:",style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dialog.ShowModal() == wx.ID_OK:
            self.SaveFilePath.SetValue(dialog.GetPath())

    def RefreshImg(self, path):
        if os.path.isfile(path):
            img = wx.Image(path, wx.BITMAP_TYPE_ANY)
            # scale the image, preserving the aspect ratio
            W = img.GetWidth()
            H = img.GetHeight()
            if W > H:
                NewW = int(config['Window']['PhotoMaxSizeX'])
                NewH = int(config['Window']['PhotoMaxSizeX']) * H / W
            else:
                NewH = int(config['Window']['PhotoMaxSizeX'])
                NewW = int(config['Window']['PhotoMaxSizeX']) * W / H
            img = img.Scale(int(NewW),int(NewH))
            self.imageCtrl.SetBitmap(wx.Bitmap(img))
            self.Refresh()                  
            return 0
        
    def CreateFonts(self):
        self.SmFont=wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.MdFont=wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        self.MdSize=(70,30)
        self.LgFont=wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False)
        
    
