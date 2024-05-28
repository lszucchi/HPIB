from Tab_Generic import *

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

        self.VBoxTx = wx.StaticText(self, label='V:', pos=(X+1*Margin, Y+2*Margin+3))
        self.VBox  = wx.ComboBox(self, value='SMU1', pos=(X+3*Margin+5, Y+2*Margin), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4', 'VSU1', 'VSU2'])
        self.Sizer1a.Add(self.VBox)

        self.CompTx = wx.StaticText(self, label='Imax:', pos=(X+1*Margin+SMU_MarginX, Y+2*Margin+3))
        self.Comp  = wx.ComboBox(self, value='10m', pos=(X+4*Margin+5+SMU_MarginX, Y+2*Margin), size=(60,40))

        self.CBoxTx = wx.StaticText(self, label='C:', pos=(X+1*Margin, Y+2*Margin+3+SMU_MarginY))
        self.CBox = wx.ComboBox(self, value='VMU1', pos=(X+3*Margin+5, Y+2*Margin+SMU_MarginY), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4', 'VMU1', 'VMU2'])
        self.Sizer1a.Add(self.CBox)

        self.SBoxTx = wx.StaticText(self, label='S:', pos=(X+2*Margin+SMU_MarginX,  Y+2*Margin+3+SMU_MarginY))
        self.SBox = wx.ComboBox(self, value='VMU2', pos=(X+4*Margin+5+SMU_MarginX, Y+2*Margin+SMU_MarginY), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4', 'VMU1', 'VMU2'])
        self.Sizer1a.Add(self.SBox)

        ######################## V Config ###########################

        BoxVgs=[[self.Box1[0][0]+Margin+self.Box1[1][0]     ,self.Box1[0][1]]     ,       [130        ,250]]
        self.Bx2=wx.StaticBox(self,label='C - V Config', pos=(BoxVgs[0][0], BoxVgs[0][1]),size=(BoxVgs[1][0], BoxVgs[1][1]))
        self.Sizer2=wx.StaticBoxSizer(self.Bx2)

        self.VStartTx = wx.StaticText(self, label='V Start', pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+30+70))
        self.VStartTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStart = wx.SpinCtrlDouble(self, value=str (-DefaultMax), pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+50+70), size=(80,35), min=-100, max=100, inc=0.5, style=wx.SP_ARROW_KEYS|wx.TE_CENTRE)
        self.VStart.SetFont(wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Sizer2.Add(self.VStart)

        self.VStopTx = wx.StaticText(self, label='V Stop', pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+30))
        self.VStopTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VStop= wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+50), size=(80,35), min=-100, max=100, inc=0.5,style=wx.SP_ARROW_KEYS|wx.TE_CENTRE)
        self.VStop.SetFont(wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Sizer2.Add(self.VStop)

        self.VStepTx = wx.StaticText(self, label='V Points', pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+30+140))
        self.VStepTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.VPoints= wx.SpinCtrl(self, value=str (200), pos=(BoxVgs[0][0]+2*Margin, BoxVgs[0][1]+50+140), min=10, max=2000, size=(80,35),style=wx.SP_ARROW_KEYS|wx.TE_CENTRE)
        self.VPoints.SetFont(wx.Font(17, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.Sizer2.Add(self.VPoints)

        
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
        try:
            self.HP.SetIntTime(self.IntTimeBox.GetValue())
            print(self.SaveFilePath.GetValue())
            ReturnFlag = self.HP.SingleSave(self.SaveFilePath.GetValue(), timeout=1800)
        except:
            #ReturnFlag="No instrument\nSend config to open connection"
            if self.ShowMessage(f'Error: {ReturnFlag}', True): raise Exception(ReturnFlag)
        
        if os.path.isfile(ReturnFlag):
            self.img_path.SetLabel(ReturnFlag)
            self.RefreshImg(Plot(ReturnFlag, "Vf", ["C", 'S']))
            return ReturnFlag
        
        if self.ShowMessage(f'Error: {ReturnFlag}', True): raise Exception(ReturnFlag)
    
    def Configure(self):
        self.OpenHP(self.GPIBCH.GetValue(), self.Inst.GetValue())
        time.sleep(0.5)
        self.HP.DisableAll()
        VStep=(self.VStop.GetValue()-self.VStart.GetValue())/(self.VPoints.GetValue())
        print(VStep)

        if  "SMU" in self.VBox.GetValue():
            self.HP.SetSMU("SMU1", "Vf", "If", "V", "VAR1")
            data_variables=["Vf", "If", "C", "S"]

        elif  "VSU" in self.VBox.GetValue():
            self.HP.SetVSMU("VSU1", "Vf", "VAR1")
            data_variables=["Vf", "C", "S"]

        else: return "Invalid Bias Port"

        self.HP.SetVSMU("VMU1", "C")
        self.HP.SetVSMU("VMU2", "S")
        time.sleep(0.5)

        self.HP.SetVar("Var1", "V", self.VStart.GetValue(), self.VStop.GetValue(), VStep, self.Comp.GetValue())

        self.HP.SetAxis("X", "Vf", 'LIN', ETF(self.VStart.GetValue()), ETF(self.VStop.GetValue()))
        self.HP.SetAxis("Y1", "C", 1, 0, 2)
        self.HP.SetAxis("Y2", "S", 1, 0, 2)

        self.HP.save_list(data_variables)

        self.HP.term='CV'

        return 0

    def Stop(self, event):
            self.timer.Stop()
            self.Btn_Start.Enable()
            self.ToggleAll(True)
            self.Btn_Start.SetLabel("Start")
            global Stop_flag
            Stop_flag = True
            print("Stop")

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
