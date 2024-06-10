from .Tab_Generic import *

class FourPoint(GenericTab):
    
    def __init__(self, parent):
        
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.timer = wx.Timer(self) 
 
        self.DrawSaveBox(10, 0, 255)

        self.DrawConfigBox(10, 80)

        self.CreateFonts()
        
        #SMU config
    
        X=self.Box1[0][0]
        Y=self.Box1[0][1]+self.Box1[1][1]+int(config['Window']['Margin'])
        
        self.Box1a=[[X, Y],[225,93]]
        self.Bx1a=wx.StaticBox(self,label='SMU Config', pos=(X, Y),size=(self.Box1a[1][0], self.Box1a[1][1]))
        self.Sizer1a=wx.StaticBoxSizer(self.Bx1a)

        self.ImBoxTx = wx.StaticText(self, label='I-:', pos=(X+1*int(config['Window']['Margin']), Y+2*int(config['Window']['Margin'])+3))
        self.ImBox  = wx.ComboBox(self, value='SMU1', pos=(X+3*int(config['Window']['Margin'])+5, Y+2*int(config['Window']['Margin'])), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'], name='sv_ImBox')
        self.Sizer1a.Add(self.ImBox)

        self.IpBoxTx  = wx.StaticText(self, label='I+:', pos=(X+2*int(config['Window']['Margin'])+int(config['Window']['SMUMX']), Y+2*int(config['Window']['Margin'])+3))
        self.IpBox = wx.ComboBox(self, value='SMU2', pos=(X+4*int(config['Window']['Margin'])+5+int(config['Window']['SMUMX']), Y+2*int(config['Window']['Margin'])), size=(60,40), choices=['SMU1','SMU2','SMU3','SMU4'], name='sv_IpBox')
        self.Sizer1a.Add(self.IpBox)

        self.VmBoxTx = wx.StaticText(self, label='V-:', pos=(X+1*int(config['Window']['Margin']), Y+2*int(config['Window']['Margin'])+3+int(config['Window']['SMUMY'])))
        self.VmBox = wx.ComboBox(self, value='VMU1', pos=(X+3*int(config['Window']['Margin'])+5, Y+2*int(config['Window']['Margin'])+int(config['Window']['SMUMY'])), size=(60,40), choices=['VMU1','VMU2','SMU1','SMU2','SMU3','SMU4'], name='sv_VmBox')
        self.Sizer1a.Add(self.VmBox)

        self.VpBoxTx = wx.StaticText(self, label='V+:', pos=(X+2*int(config['Window']['Margin'])+int(config['Window']['SMUMX']),  Y+2*int(config['Window']['Margin'])+3+int(config['Window']['SMUMY'])))
        self.VpBox = wx.ComboBox(self, value='VMU2', pos=(X+4*int(config['Window']['Margin'])+5+int(config['Window']['SMUMX']), Y+2*int(config['Window']['Margin'])+int(config['Window']['SMUMY'])), size=(60,40), choices=['VMU1','VMU2','SMU1','SMU2','SMU3','SMU4'], name='sv_VpBox')
        self.Sizer1a.Add(self.VpBox)

        ######################## V Config ###########################

        BoxVgs=[[self.Box1[0][0]+int(config['Window']['Margin'])+self.Box1[1][0]     ,self.Box1[0][1]]     ,       [130        ,250]]
        self.Bx2=wx.StaticBox(self,label='4-P Config', pos=(BoxVgs[0][0], BoxVgs[0][1]),size=(BoxVgs[1][0], BoxVgs[1][1]))
        self.Sizer2=wx.StaticBoxSizer(self.Bx2)

        self.IStopTx = wx.StaticText(self, label='I Stop', pos=(BoxVgs[0][0]+2*int(config['Window']['Margin']), BoxVgs[0][1]+30+70))
        self.IStopTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.IStop= wx.TextCtrl(self, value='1m', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+10, BoxVgs[0][1]+50+70), size=(80,36), style=wx.TE_CENTRE, name='sv_IStop')
        self.IStop.SetFont(self.LgFont)
        self.Sizer2.Add(self.IStop)

        self.IStartTx = wx.StaticText(self, label='I Start', pos=(BoxVgs[0][0]+2*int(config['Window']['Margin']), BoxVgs[0][1]+30))
        self.IStartTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.IStart= wx.TextCtrl(self, value='-1m', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+10, BoxVgs[0][1]+50), size=(80,35), style=wx.TE_CENTRE, name='sv_IStart')
        self.IStart.SetFont(self.LgFont)
        self.Sizer2.Add(self.IStart)

        self.IStepTx = wx.StaticText(self, label='I Points', pos=(BoxVgs[0][0]+2*int(config['Window']['Margin']), BoxVgs[0][1]+30+140))
        self.IStepTx.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False))
        self.IPoints= wx.SpinCtrlDouble(self, value='200', pos=(BoxVgs[0][0]+2*int(config['Window']['Margin']), BoxVgs[0][1]+50+140), min=10, max=2000, inc=10, size=(80,35), style=wx.SP_ARROW_KEYS|wx.TE_CENTRE, name='sv_IPoints')
        self.IPoints.SetFont(self.LgFont)
        self.Sizer2.Add(self.IPoints)
        
        ############################# Progress #############################
        

        self.CurrentTx = wx.StaticText(self, label='Current Step:', pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+3))
        self.Current = wx.TextCtrl(self, pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+23),size=(130,20))

        self.IntTimeTx = wx.StaticText(self, label='Integration Time:', pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+53))
        self.IntTimeBox = wx.ComboBox(self, value='MEDium', pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+73), size=(80,40), choices=['SHORt','MEDium','LONG'], style=wx.CB_READONLY, name='sv_IntTime')
        self.Sizer2.Add(self.IntTimeBox)

        #======== Image preview =========#
        img = wx.Image((int(config['Window']['PhotoMaxSizeX']),int(int(config['Window']['PhotoMaxSizeX'])*480/640)))
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img),pos=(385, int(config['Window']['Margin'])), size=(int(config['Window']['PhotoMaxSizeX']),int(config['Window']['PhotoMaxSizeX'])*480/640))
        self.img_path = wx.StaticText(self, label="No measurements to show", pos=(385,int(config['Window']['Margin'])),size=(400,20))

    def Measure(self):

        if not self.COMEnable.GetValue():
            self.HP.SetIntTime(self.IntTimeBox.GetValue())
            last_path=self.HP.SingleSave(self.SaveFilePath.GetValue())
            self.RefreshImg(Plot(last_path, "V", "I", sizex=550))
            return 0

        ChSelect=[self.cb1.GetValue(),self.cb2.GetValue(),self.cb3.GetValue(),self.cb4.GetValue(),self.cb5.GetValue(),self.cb6.GetValue()]

        #print('Opening Arduino on: '+ self.COM.GetValue())
        #INO=pyfirmata.Arduino(self.COM.GetValue())
        
        for Chn in range(6):      
            if ChSelect[Chn]:
                INO.opench(Chn-1)
                last_path=self.HP.SingleSave(self.SaveFilePath.GetValue())
                self.RefreshImg(Plot(last_path, "V", "I", sizex=550))
                
        return 0                          

    def Configure(self):
        self.OpenHP(self.GPIBCH.GetValue(), self.Inst.GetValue())
        self.HP.beep()
        self.HP.DisableAll()
        self.HP.Set4P(ETF(self.IStart.GetValue()),ETF(self.IStop.GetValue()),int(self.IPoints.GetValue())+1,self.IpBox.GetValue(), self.ImBox.GetValue(),self.VpBox.GetValue(),self.VmBox.GetValue())

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
