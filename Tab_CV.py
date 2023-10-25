from GenericTab import *

class CVTab(GenericTab):

    def __init__(self, parent):
         
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.timer = wx.Timer(self) 
 
        self.DrawSaveBox(10, 0, 255)

        self.DrawConfigBox(10, 80)

        #SMU config

        X=self.Box1[0][0]
        Y=self.Box1[0][1]+self.Box1[1][1]+Margin
        
        self.Box1a=[[X, Y],[225,93]]
        self.Bx1a=wx.StaticBox(self,label='SMU Config', pos=(X, Y),size=(self.Box1a[1][0], self.Box1a[1][1]))
        self.Sizer1a=wx.StaticBoxSizer(self.Bx1a)

        self.DBoxTx = wx.StaticText(self, label='V:', pos=(X+1*Margin, Y+2*Margin+3))
        self.DBox  = wx.ComboBox(self, value='SMU1', pos=(X+3*Margin+5, Y+2*Margin), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.DBox)


        self.BBoxTx = wx.StaticText(self, label='C:', pos=(X+1*Margin, Y+2*Margin+3+SMU_MarginY))
        self.BBox = wx.ComboBox(self, value='VMU1', pos=(X+3*Margin+5, Y+2*Margin+SMU_MarginY), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.BBox)

        self.GBoxTx = wx.StaticText(self, label='S:', pos=(X+2*Margin+SMU_MarginX,  Y+2*Margin+3+SMU_MarginY))
        self.GBox = wx.ComboBox(self, value='VMU2', pos=(X+4*Margin+5+SMU_MarginX, Y+2*Margin+SMU_MarginY), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'])
        self.Sizer1a.Add(self.GBox)

        ######################## V Config ###########################

        BoxVgs=[[self.Box1[0][0]+Margin+self.Box1[1][0]     ,self.Box1[0][1]]     ,       [130        ,250]]
        self.Bx2=wx.StaticBox(self,label='C - V Config', pos=(BoxVgs[0][0], BoxVgs[0][1]),size=(BoxVgs[1][0], BoxVgs[1][1]))
        self.Sizer2=wx.StaticBoxSizer(self.Bx2)

        self.VStartTx = wx.StaticText(self, label='V Start', pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+30))
        self.VStartTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStart = wx.SpinCtrlDouble(self, value=str (0), pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+50), size=(80,35),style=wx.SP_ARROW_KEYS|wx.TE_CENTRE)
        self.VStart.SetFont(wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStart.SetIncrement(0.1)
        self.Sizer2.Add(self.VStart)

        self.VStopTx = wx.StaticText(self, label='V Stop', pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+30+70))
        self.VStopTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStop= wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+50+70), size=(80,35),style=wx.SP_ARROW_KEYS|wx.TE_CENTRE)
        self.VStop.SetFont(wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStop.SetIncrement(0.1)
        self.Sizer2.Add(self.VStop)

        self.VStepTx = wx.StaticText(self, label='V Step', pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+30+140))
        self.VStepTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStep= wx.SpinCtrlDouble(self, value=str (DefaultStep/StepScale), pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+50+140), size=(80,35),style=wx.SP_ARROW_KEYS|wx.TE_CENTRE)
        self.VStep.SetFont(wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStep.SetIncrement(0.01)
        self.Sizer2.Add(self.VStep)

        
        ############################# Progress #############################
        

        self.CurrentTx = wx.StaticText(self, label='Current Step:', pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+Margin+3))
        self.Current = wx.TextCtrl(self, pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+Margin+23),size=(130,20))

        self.IntTimeTx = wx.StaticText(self, label='Integration Time:', pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+Margin+53))
        self.IntTimeBox = wx.ComboBox(self, value=DefaultIntTime, pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+Margin+73), size=(80,40), choices=['SHORt','MEDium','LONG'])
        self.Sizer2.Add(self.IntTimeBox)

        #======== Image preview =========#
        img = wx.Image((PhotoMaxSizeX,int(PhotoMaxSizeX*480/640)))
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img),pos=(385, 30), size=(PhotoMaxSizeX,int(PhotoMaxSizeX*480/640)))
        self.img_path = wx.StaticText(self, label="No measurements to show", pos=(385,10),size=(400,20))

    def Measure(self):
        self.OpenHP()
        
        self.HP.SMU=[self.SBox.GetValue(), self.DBox.GetValue(),self.GBox.GetValue(),self.BBox.GetValue()]

        self.HP.reset()
        
        ChSelect=[self.cb1.GetValue(),self.cb2.GetValue(),self.cb3.GetValue(),self.cb4.GetValue(),self.cb5.GetValue(),self.cb6.GetValue()]
        
        #print('Opening Arduino on: '+ self.COM.GetValue())
        #INO=pyfirmata.Arduino(self.COM.GetValue())
        
        self.Progress.SetValue('Arduino Opened on: '+ self.COM.GetValue()+'\n')

        for Chn in range(6):      
            if ChSelect[Chn]:
                self.Progress.AppendText('Channel: ' +str(Chn+1) + ' Measurements:\n')
                #opench(Chn-1)
                self.Progress.AppendText(str('ChnOpen')+ '  ')

                self.Progress.AppendText(str('C-V')+ '  ')
                self.HP.SetCap(self.VStart.GetValue(),self.VStop.GetValue(),self.VStep.GetValue())
                last_path=self.HP.SingleSave(Chn+1,self.SaveFilePath.GetValue(), IntTime=self.IntTimeBox.GetValue())
                self.RefreshImg(PlotVgs(last_path))
                    
        self.Progress.AppendText('End!\n')
        return 0                                       
    
    def Stop(self, event):
            self.timer.Stop()
            self.Btn_Start.Enable()
            self.ToggleAll(True)
            self.Btn_Start.SetLabel("Start")
            global Stop_flag
            Stop_flag = True
            print("Stop")

    def OnButton(self, event):
        global Stop_flag
        Stop_flag = False
        self.testThread = Thread(target=test1)
        self.testThread.start()
        self.Btn_Start.SetLabel("Running\n.")
        self.Btn_Start.Disable()
        self.ToggleAll(False)
        self.Bind(wx.EVT_TIMER, self.PollThread)
        self.timer.Start(20, oneShot=True)
        event.Skip()

    def PollThread(self, event):
            if self.testThread.is_alive():
                    self.Bind(wx.EVT_TIMER, self.PollThread)
                    self.timer.Start(200, oneShot=True)
                    self.Btn_Start.SetLabel(self.Btn_Start.GetLabel() + ".")
                    if(len(self.Btn_Start.GetLabel())>25):
                            self.Btn_Start.SetLabel("Running\n.")
            else:
                    self.Btn_Start.Enable()
                    self.ToggleAll(True)
                    self.Btn_Start.SetLabel("Start")

    def ToggleSizer(self, Sizer, State):
        children = Sizer.GetChildren()
        for child in children:
            try:
                child.GetWindow().Enable(State)
            except:
                print('ERROR')

    def ToggleList(self, List, State):
        for Sizer in List:
            self.ToggleSizer(Sizer, State)

    def ToggleAll(self, State):
        self.ToggleList([self.Sizer1,self.Sizer1a,self.Sizer2], State)    