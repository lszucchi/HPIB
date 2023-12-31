import wx, datetime, time
import wx.lib.agw.floatspin as FS7

from HPIB4145 import *
from HPIB4155 import *
from INOSerial import *
from HPIB_plot import *

from threading import Thread

from defaults import *

class GenericTab(wx.Panel):

    def OpenHP(self, addr, inst):
        self.Progress.AppendText('\nOpening HP')
        self.debug=False
        
        if inst[len(inst)-1].lower()=='d':
            self.debug=True
            inst=inst.strip('dD')
            print(f"\n\n#####################    {inst}   #####################\n\n") 

        if not addr[0]=='G':
            addr="GPIB0::"+str(addr)
        
        if inst=='HP4155':
            try:
                self.HP = HP4155(addr, read_termination = '\n', write_termination = '\n', timeout=None, debug=self.debug)
            except Exception as error:
                if self.ShowMessage('Communication error:\nInstrument not found', True): raise error
                return 1
        elif inst=='HP4145':
            try:
                self.HP = HP4145(addr, read_termination = '\n', write_termination = '\n', timeout=None, debug=self.debug)
            except Exception as error:
                if self.ShowMessage('Communication error:\nInstrument not found', True): raise error
                return 1            
        else:
            if self.ShowMessage('Input error:\nInvalid Instrument', True): raise RuntimeError('Invalid Instrument')
            return 1
            
        self.HP.reset()
        
    def DrawSaveBox(self, X, Y, length):
        Bx0=wx.StaticBox(self, pos=(X,Y), size=(length+115,70),label='Save:')
        Bx0.SetFont(wx.Font(15, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Dir_Select = wx.Button(self, label='Save dir', pos=(X+10,Y+25),size=(80,30))
        self.Dir_Select.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Dir_Select.Bind(wx.EVT_BUTTON, self.OnSaveButton)
        self.SaveFilePath=wx.TextCtrl(self, pos=(X+100, Y+25), size=(length, 30),style=wx.TE_LEFT)
        
    
    def DrawConfigBox(self, X, Y):
 
        #========  Config Box ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        self.Box1=[[X, Y],[225,280]]
        self.Bx1=wx.StaticBox(self,label='Port and SM Config', pos=(self.Box1[0][0], self.Box1[0][1]),size=(self.Box1[1][0], self.Box1[1][1]))
        self.Sizer1=wx.BoxSizer()
        self.Sizer2=wx.BoxSizer()

        #Instr Select
        self.InstTx = wx.StaticText(self, label='Instrument', pos=(self.Box1[0][0]+Margin+5, self.Box1[0][1]+2*Margin))
        self.Inst = wx.ComboBox(self, value='HP4155d', pos=(self.Box1[0][0]+Margin+5, self.Box1[0][1]+4*Margin), choices=['HP4145','HP4155'])
##        self.Inst.Bind(wx.EVT_TEXT, self.EnableTraces)

        #GPIB address selection box
        self.GPIBTXT = wx.StaticText(self, label='GBIP Address', pos=(self.Box1[0][0]+105, self.Box1[0][1]+2*Margin))
        self.GPIBCH = wx.ComboBox(self, value='17', pos=(self.Box1[0][0]+105, self.Box1[0][1]+4*Margin), size=(40,40), choices=['15','16','17'])
        self.Sizer2.Add(self.GPIBCH)

        
        #COM port selection box
        self.COMEnable = wx.CheckBox(self, label='SM Port', pos=(self.Box1[0][0]+Margin+5, self.Box1[0][1]+2*Margin+50))
        self.COMEnable.SetValue(0)
        self.COM = wx.ComboBox(self, value='COM3', pos=(self.Box1[0][0]+Margin+5, self.Box1[0][1]+4*Margin+50), choices=['COM3','COM4'])
        self.Sizer1.Add(self.COM)



        #Checkboxes
        cbpos=(self.Box1[0][0]+Margin, self.Box1[0][1]+125)
        self.cb1 = wx.CheckBox(self, label='Channel 1', pos=(cbpos[0], cbpos[1]))
        self.cb2 = wx.CheckBox(self, label='Channel 2', pos=(cbpos[0], cbpos[1]+25))
        self.cb3 = wx.CheckBox(self, label='Channel 3', pos=(cbpos[0], cbpos[1]+50))
        self.cb4 = wx.CheckBox(self, label='Channel 4', pos=(cbpos[0], cbpos[1]+75))
        self.cb5 = wx.CheckBox(self, label='Channel 5', pos=(cbpos[0], cbpos[1]+100))
        self.cb6 = wx.CheckBox(self, label='Channel 6', pos=(cbpos[0], cbpos[1]+125))
        self.cb1.SetValue(1)
        self.cb2.SetValue(1)
        self.cb3.SetValue(1)
        self.cb4.SetValue(1)
        self.cb5.SetValue(1)
        self.cb6.SetValue(1)
        self.Sizer1.Add(self.cb1)
        self.Sizer1.Add(self.cb2)
        self.Sizer1.Add(self.cb3)
        self.Sizer1.Add(self.cb4)
        self.Sizer1.Add(self.cb5)
        self.Sizer1.Add(self.cb6)

        def ToggleSizer(evt):
            children = self.Sizer1.GetChildren()
            for child in children:
                try:
                    child.GetWindow().Enable(self.COMEnable.GetValue())
                except:
                    print('ERROR')
                    
        ToggleSizer(1)
        self.COMEnable.Bind(wx.EVT_CHECKBOX, ToggleSizer)

        #Send HP config
        self.Config_Btn = wx.Button(self, label='Send HP\nConfig', pos=(self.Box1[0][0]+110, cbpos[1]+10-40), size=(80, 40))
        self.Sizer2.Add(self.Config_Btn)
        self.Config_Btn.Bind(wx.EVT_BUTTON, self.OnConfig)

        #Start button
        self.Btn_Start = wx.Button(self, label='Start', pos=(self.Box1[0][0]+100, cbpos[1]+10+2*Margin),size=(100,60))
        self.Sizer2.Add(self.Btn_Start)
        self.Btn_Start.Bind(wx.EVT_BUTTON, self.OnButton)
        

        #Stop button
        Btn_Stop = wx.Button(self, label='Stop', pos=(self.Box1[0][0]+100+25, cbpos[1]+10+60+4*Margin),size=(50,30))
        Btn_Stop.Bind(wx.EVT_BUTTON, self.Stop)

    def DrawSMUConfig(self, X, Y):
        
        self.Box1a=[[X, Y],[225,93]]
        self.Bx1a=wx.StaticBox(self,label='SMU Config', pos=(self.Box1a[0][0], self.Box1a[0][1]),size=(self.Box1a[1][0], self.Box1a[1][1]))
        self.Sizer1a=wx.StaticBoxSizer(self.Bx1a)

        self.DBoxTx = wx.StaticText(self, label='S:', pos=(X+1*Margin, Y+2*Margin+3))
        self.DBox  = wx.ComboBox(self, value='SMU1', pos=(X+3*Margin+5, Y+2*Margin), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.DBox)

        self.SBoxTx  = wx.StaticText(self, label='D:', pos=(X+2*Margin+SMU_MarginX, Y+2*Margin+3))
        self.SBox = wx.ComboBox(self, value='SMU2', pos=(X+4*Margin+5+SMU_MarginX, Y+2*Margin), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.SBox)

        self.BBoxTx = wx.StaticText(self, label='B:', pos=(X+1*Margin, Y+2*Margin+3+SMU_MarginY))
        self.BBox = wx.ComboBox(self, value='SMU4', pos=(X+3*Margin+5, Y+2*Margin+SMU_MarginY), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.BBox)

        self.GBoxTx = wx.StaticText(self, label='G:', pos=(X+2*Margin+SMU_MarginX,  Y+2*Margin+3+SMU_MarginY))
        self.GBox = wx.ComboBox(self, value='SMU3', pos=(X+4*Margin+5+SMU_MarginX, Y+2*Margin+SMU_MarginY), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.GBox)

        
    def Measure(self):
        self.Progress.AppendText('\nMeasurement started!\n...')
        try:
            self.HP.SetIntTime(self.IntTimeBox.GetValue())
            ReturnFlag = self.HP.SingleSave(self.SaveFilePath.GetValue(), timeout=180)
        except:
            ReturnFlag="No instrument\nSend config to open connection"
            if self.ShowMessage(f'Error: {ReturnFlag}', True): raise Exception(ReturnFlag)

        self.Progress.AppendText('\nMeasurement Done!')
        
        if os.path.isfile(ReturnFlag):
            self.img_path.SetLabel(ReturnFlag)
            Plot(self, ReturnFlag)
            return ReturnFlag
        
        if self.ShowMessage(f'Error: {ReturnFlag}', True): raise Exception(ReturnFlag)

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
            # check if current path is a file
            if os.path.isfile(path):
                img = wx.Image(path, wx.BITMAP_TYPE_ANY)
                # scale the image, preserving the aspect ratio
                W = img.GetWidth()
                H = img.GetHeight()
                if W > H:
                    NewW = PhotoMaxSizeX
                    NewH = PhotoMaxSizeX * H / W
                else:
                    NewH = PhotoMaxSizeY
                    NewW = PhotoMaxSizeY * W / H
                img = img.Scale(int(NewW),int(NewH))
                self.imageCtrl.SetBitmap(wx.Bitmap(img))
                self.Refresh()
