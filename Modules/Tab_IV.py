from .Tab_Generic import *

class IVTab(GenericTab):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------

    def __init__(self, parent):
        
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.timer = wx.Timer(self)
        
        self.DrawSaveBox(10, 0, 655)
 
        self.DrawConfigBox(10, 80)

        self.CreateFonts()

        self.Config_Btn.Destroy()
        self.ptype = wx.CheckBox(self, label="p-type", pos=(130, 180), name='sv_enptype')
        
        self.DrawSMUConfig(int(config['Window']['Margin']), self.Box1[0][1]+self.Box1[1][1]+int(config['Window']['Margin']))

        #========  Id x Vgs ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
                         
        BoxVgs=[[self.Box1[0][0]+int(config['Window']['Margin'])+self.Box1[1][0]     ,self.Box1[0][1]]     ,       [180        ,280]]
        self.Bx2=wx.StaticBox(self,label='Id x Vgs', pos=(BoxVgs[0][0], BoxVgs[0][1]),size=(BoxVgs[1][0], BoxVgs[1][1]))
        self.Sizer2=wx.StaticBoxSizer(self.Bx2)
        
        self.EnableIdVgs = wx.CheckBox(self, label='Enable', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+2*int(config['Window']['Margin'])), name='sv_enIdVgs')
        self.EnableIdVgs.SetValue(True)
        self.Sizer2.Add(self.EnableIdVgs)
 
        self.EnableVgsSat = wx.CheckBox(self, label='Vgs Sat', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+2*int(config['Window']['Margin'])), name='sv_enIdVgsSat')
        self.EnableVgsSat.SetValue(False)
        self.Sizer2.Add(self.EnableVgsSat)
        self.EnableVgsSat.Bind(wx.EVT_CHECKBOX, self.DrawVgsVdSat)
        
        self.VdVgsSweep = wx.CheckBox(self, label='Sweep Vd=Vg', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+2*int(config['Window']['SMUMY'])+2*int(config['Window']['Margin'])), name='sv_enIdVgsSweep')
        self.Sizer2.Add(self.VdVgsSweep)
        self.VdVgsSweep.Bind(wx.EVT_CHECKBOX, self.DrawVgsVd)

        ### Draw VGS SWEEP
        self.VdVgsTx = wx.StaticText(self, label='Vd (mV)', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+40))
        self.VdVgs = wx.SpinCtrlDouble(self, value='50', min=-1000, max=1000, pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+60), size=self.MdSize, inc=5, style=wx.SP_ARROW_KEYS, name='sv_VdVgs')
        self.VdVgs.SetFont(self.MdFont)
        #self.Sizer2.Add(self.VdVgs)

        ### Draw VGS sat SWEEP
        self.VdVgsSatTx = wx.StaticText(self, label='Vd Sat', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+40))
        self.VdVgsSat= wx.SpinCtrlDouble(self, value='1', min=-100, max=100, pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+60), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VdVgsSat')
        self.VdVgsSat.SetFont(self.MdFont)
        #self.Sizer2.Add(self.VdVgsSat)

        # Vg Step
        self.VgVgsStartTx = wx.StaticText(self, label='Vg Start', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+160))
        self.VgVgsStart = wx.SpinCtrlDouble(self, value='0', min=-100, max=100, pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+180), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVgsStart')
        self.VgVgsStart.SetFont(self.MdFont)
        self.Sizer2.Add(self.VgVgsStart)

        self.VgVgsStopTx = wx.StaticText(self, label='Vg Stop', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+160))
        self.VgVgsStop = wx.SpinCtrlDouble(self, value='1', min=-100, max=100, pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+180), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVgsStep')
        self.VgVgsStop.SetFont(self.MdFont)
        self.Sizer2.Add(self.VgVgsStop)

        self.VgVgsStepTx = wx.StaticText(self, label='Vg Step', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+210))
        self.VgVgsStep = wx.SpinCtrlDouble(self, value='0.05', min=-100, max=100, pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+230), size=(80, 30), inc=0.01, style=wx.SP_ARROW_KEYS, name='sv_VgVgsStop')
        self.VgVgsStep.SetFont(self.MdFont)
        self.Sizer2.Add(self.VgVgsStep)


        #self.VgVgsPointsTx = wx.StaticText(self, label='Vg Step Number', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+180+int(config['Window']['SMUMY'])))
        #self.VgVgsPoints = wx.SpinCtrl(self, value='40', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+200+int(config['Window']['SMUMY'])), size=self.MdSize,style=wx.SP_ARROW_KEYS)

        #========  Id x Vds ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        BoxVds=[[BoxVgs[0][0]+int(config['Window']['Margin'])+BoxVgs[1][0]        ,self.Box1[0][1]],        [180        ,280]]
        self.Bx3=wx.StaticBox(self,label='Id x Vds', pos=(BoxVds[0][0], BoxVds[0][1]),size=(BoxVds[1][0], BoxVds[1][1]))
        self.Sizer3=wx.StaticBoxSizer(self.Bx3)
        
        # Enable
        self.EnableIdVds = wx.CheckBox(self, label='Enable Id x Vds', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+2*int(config['Window']['Margin'])), name='sv_enIdVds')
        self.EnableIdVds.SetValue(True)
        self.Sizer3.Add(self.EnableIdVds)

        #Value Config

        #Vd Sweep
        self.VdVdsStartTx = wx.StaticText(self, label='Vd Start', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+40))
        self.VdVdsStart = wx.SpinCtrlDouble(self, value='0', min=-100, max=100, pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+60), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VdVdsStart')
        self.VdVdsStart.SetFont(self.MdFont)
        self.Sizer3.Add(self.VdVdsStart)

        self.VdVdsStopTx = wx.StaticText(self, label='Vd Stop', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+40))
        self.VdVdsStop = wx.SpinCtrlDouble(self, value='1', min=-100, max=100, pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+60), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VdVdsStep')
        self.VdVdsStop.SetFont(self.MdFont)
        self.Sizer3.Add(self.VdVdsStop)

        self.VdVdsStepTx = wx.StaticText(self, label='Vd Step', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+50+int(config['Window']['SMUMY'])))
        self.VdVdsStep = wx.SpinCtrlDouble(self, value='0.05', min=-100, max=100, pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+70+int(config['Window']['SMUMY'])), size=(80, 30), inc=0.01, style=wx.SP_ARROW_KEYS, name='sv_VdVdsStop')
        self.VdVdsStep.SetFont(self.MdFont)
        self.Sizer3.Add(self.VdVdsStep)

        #self.VdVdsPointsTx = wx.StaticText(self, label='Vd Step Number', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+50+int(config['Window']['SMUMY'])))
        #self.VdVdsPoints = wx.SpinCtrl(self, value='40', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+70+int(config['Window']['SMUMY'])), size=self.MdSize,style=wx.SP_ARROW_KEYS)

        # Vg Step
        self.VgVdsStartTx = wx.StaticText(self, label='Vg Start', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+160))
        self.VgVdsStart = wx.SpinCtrlDouble(self, value='0', min=-100, max=100, pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+180), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVdsStart')
        self.VgVdsStart.SetFont(self.MdFont)
        self.Sizer3.Add(self.VgVdsStart)

        self.VgVdsStopTx = wx.StaticText(self, label='Vg Stop', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+160))
        self.VgVdsStop = wx.SpinCtrlDouble(self, value='1', min=-100, max=100, pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+180), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVdsStep')
        self.VgVdsStop.SetFont(self.MdFont)
        self.Sizer3.Add(self.VgVdsStop)

        self.VgVdsStepTx = wx.StaticText(self, label='Vg Step', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+210))
        self.VgVdsStep = wx.SpinCtrlDouble(self, value='0.2', min=-100, max=100, pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+230), size=(80, 30), inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVdsStop')
        self.VgVdsStep.SetFont(self.MdFont)
        self.Sizer3.Add(self.VgVdsStep)

        #self.VgVdsPointsTx = wx.StaticText(self, label='Vg Step Number', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+180+int(config['Window']['SMUMY'])))
        #self.VgVdsPoints = wx.SpinCtrl(self, value='5', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+200+int(config['Window']['SMUMY'])), size=self.MdSize,style=wx.SP_ARROW_KEYS)

        #========  Vp x Vg ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        global BoxVp
        BoxVp=[[BoxVds[0][0]+int(config['Window']['Margin'])+BoxVds[1][0]       ,self.Box1[0][1]]        ,[180        ,280]]
        self.Bx4=wx.StaticBox(self,label='Vp x Vgs', pos=(BoxVp[0][0],BoxVp[0][1]),size=(BoxVp[1][0], BoxVp[1][1]))
        self.Sizer4=wx.StaticBoxSizer(self.Bx4)
        
        self.EnableVp = wx.CheckBox(self, label='Enable Vp', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+2*int(config['Window']['Margin'])), name='sv_enVp')
        self.EnableVp.SetValue(False)
        self.Sizer4.Add(self.EnableVp)

        #Value Config

        #Vd Sweep
        self.IsImport = wx.CheckBox(self, label='Extract Ib', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+40+20), name='sv_enIsImport')
        
        self.IsDefTx = wx.StaticText(self, label='Ib', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+40+int(config['Window']['SMUMY'])))
        self.IsDef = wx.TextCtrl(self, value='1e-6', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+60+int(config['Window']['SMUMY'])), size=self.MdSize, name='sv_IsDef')
        self.IsDef.SetFont(self.MdFont)
        self.IsDef.SetValue("")
        #self.Sizer4.Add(self.IsDef)
        
        self.IsDef.Disable()
        self.IsDefTx.Disable()
        self.IsImport.SetValue(True)
        self.IsImport.Bind(wx.EVT_CHECKBOX, self.DrawIspecDef)
        self.Sizer4.Add(self.IsImport)

        # Vg Step
        self.VgVpStartTx = wx.StaticText(self, label='Vg Start', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+160))
        self.VgVpStart = wx.SpinCtrlDouble(self, value='0', min=-100, max=100, pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+180), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVpStart')
        self.VgVpStart.SetFont(self.MdFont)
        self.Sizer4.Add(self.VgVpStart)

        self.VgVpStopTx = wx.StaticText(self, label='Vg Stop', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+160))
        self.VgVpStop = wx.SpinCtrlDouble(self, value='1', min=-100, max=100, pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+180), size=self.MdSize, inc=0.1, style=wx.SP_ARROW_KEYS, name='sv_VgVpStep')
        self.VgVpStop.SetFont(self.MdFont)
        self.Sizer4.Add(self.VgVpStop)

        self.VgVpStepTx = wx.StaticText(self, label='Vg Step', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+220))
        self.VgVpStep = wx.SpinCtrlDouble(self, value='0.05', min=-100, max=100, pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+240), size=(80, 30), inc=0.01, style=wx.SP_ARROW_KEYS, name='sv_VgVpstop')
        self.VgVpStep.SetFont(self.MdFont)
        self.Sizer4.Add(self.VgVpStep)

        #self.VgVpPointsTx = wx.StaticText(self, label='Vg Step Number', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+160+int(config['Window']['SMUMY'])))
        #self.VgVpPoints = wx.SpinCtrl(self, value='40', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+200+int(config['Window']['SMUMY'])), size=self.MdSize,style=wx.SP_ARROW_KEYS)

        self.Progress=wx.TextCtrl(self, pos=(BoxVgs[0][0], BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+3), size=(BoxVds[1][0]+BoxVds[1][0]+int(config['Window']['Margin']), 90),style=wx.TE_MULTILINE)

        self.IntTimeTx = wx.StaticText(self, label='Integration Time:', pos=(BoxVp[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])))
        self.IntTimeBox = wx.ComboBox(self, value='MEDium', pos=(BoxVp[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+20), size=(80,40), choices=['SHORt','MEDium','LONG'], style=wx.CB_READONLY, name='sv_IntTime')                
        self.Sizer4.Add(self.IntTimeBox)

        self.ComplianceTx = wx.StaticText(self, label='Compliance:', pos=(BoxVp[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+50))
        self.CompBox = wx.ComboBox(self, value='10 mA', pos=(BoxVp[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+70), size=(80,40), choices=['1 mA','10 mA'], name='sv_CompBox')                
        self.Sizer4.Add(self.CompBox)

        #======== Image preview =========#
        img = wx.Image((int(config['Window']['PhotoMaxSizeX']),int(int(config['Window']['PhotoMaxSizeX'])*480/640)))
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img),pos=(785, int(config['Window']['Margin'])), size=(int(config['Window']['PhotoMaxSizeX']),int(config['Window']['PhotoMaxSizeX'])*480/640))
        self.img_path = wx.StaticText(self, label="No measurements to show", pos=(785,int(config['Window']['Margin'])),size=(400,20))

        #========  End ========#
        self.Show()
       # self.Maximize()

    def Measure(self):
        
        self.OpenHP(self.GPIBCH.GetValue(), self.Inst.GetValue())

        self.HP.SMU=[self.SBox.GetValue(), self.DBox.GetValue(),self.GBox.GetValue(),self.BBox.GetValue()]
        self.HP.SetIntTime(self.IntTimeBox.GetValue())
            
        MeasureList=['ChnOpen', 'Diode', 'Id_Vgs', 'Id_VgsSat', 'Id_Vds', 'Vp_Vgs']

        path=self.SaveFilePath.GetValue()
        
        if not os.path.isdir(path):
            self.ShowMessage('Invalid path\nEnter a folder')
        if not path.endswith('\\'):
            path=path+'\\'
            
        if not self.COMEnable.GetValue():
            self.SimpleMeas(path, None)
            self.Progress.AppendText('End!\n')
            return 0

        self.Progress.SetValue(f'Arduino Opened on: {self.COM.GetValue()}\n')
        ChSelect=[self.cb1.GetValue(),self.cb2.GetValue(),self.cb3.GetValue(),self.cb4.GetValue(),self.cb5.GetValue(),self.cb6.GetValue()]

        for n, Enable in enumerate(ChSelect):
            if Enable:
                self.Progress.AppendText(str('ChnOpen')+ '  ')
                self.Progress.AppendText(f'Channel: {n+1} Measurements:\n')                                                
                self.SimpleMeas()
        self.Progress.AppendText('End!\n')
        return 0
        
    def SimpleMeas(self, path, Chn=None):
        path_start=''
        if Chn is not None:
             path_start=f'Ch{Chn+1}-'
             
        if self.EnableIdVgs.GetValue():
            self.Progress.AppendText('Id_Vgs  ')
            self.HP.SetVgs(self.VgVgsStart.GetValue(), self.VgVgsStop.GetValue(), self.VgVgsStep.GetValue(), float(self.VdVgs.GetValue())/1000, VdSweep=self.VdVgsSweep.GetValue(), Comp=ETF(self.CompBox.GetValue().strip('A')), ptype=self.ptype.GetValue(), sat=False)

            save_path=f'{path}{path_start}{self.HP.term}-{datetime.datetime.now().strftime("%y%m%d %H%M%S")}.csv'
            self.HP.SingleSave(save_path)
            self.RefreshImg(Plot(save_path, 'VG', 'ID', sizex=int(config['Window']['PhotoMaxSizeX'])))

        if self.EnableVgsSat.GetValue():
            self.Progress.AppendText('Id_VgsSat  ')
            self.HP.SetVgs(self.VgVgsStart.GetValue(), self.VgVgsStop.GetValue(), self.VgVgsStep.GetValue(), self.VdVgsSat.GetValue(), Comp=ETF(self.CompBox.GetValue().strip('A')), ptype=self.ptype.GetValue(), sat=True)

            save_path=f'{path}{path_start}{self.HP.term}-{datetime.datetime.now().strftime("%y%m%d %H%M%S")}.csv'
            self.HP.SingleSave(save_path)
            self.RefreshImg(Plot(save_path, 'VG', 'ID', sizex=int(config['Window']['PhotoMaxSizeX'])))
                    
        if self.EnableIdVds.GetValue():
            self.Progress.AppendText('Id_Vds  ')
            self.HP.SetVds(self.VdVdsStart.GetValue(), self.VdVdsStop.GetValue(), self.VdVdsStep.GetValue(), self.VgVdsStart.GetValue(), self.VgVdsStop.GetValue(), self.VgVdsStep.GetValue(), Comp=ETF(self.CompBox.GetValue().strip('A')), ptype=self.ptype.GetValue())                                                

            save_path=f'{path}{path_start}{self.HP.term}-{datetime.datetime.now().strftime("%y%m%d %H%M%S")}.csv'
            self.HP.SingleSave(save_path)
            self.RefreshImg(Plot(save_path, 'VD', 'ID', sizex=int(config['Window']['PhotoMaxSizeX'])))
                    
        if self.EnableVp.GetValue():
            if not self.IsImport.GetValue():
                    Ispec=ETF(self.IsDef.GetValue())
            else:
                    self.HP.SetEx_Ib(-0.5,self.VgVpStop.GetValue(),self.VgVpStep.GetValue(),ptype=self.ptype.GetValue())
                    save_path=f'{path}{path_start}{self.HP.term}-{datetime.datetime.now().strftime("%y%m%d %H%M%S")}.csv'
                    self.HP.get_data(save_path)
                    Ispec=self.HP.Ex_Ib(save_path, ptype=ptype.GetValue()) # type: ignore
                    
            self.Progress.AppendText('Vp_Vgs  ')
            self.HP.SetVp(Ispec,self.VgVpStart.GetValue(),self.VgVpStop.GetValue(),self.VgVpStep.GetValue(),ptype=self.ptype.GetValue())

            save_path=f'{path}{path_start}{self.HP.term}-{datetime.datetime.now().strftime("%y%m%d %H%M%S")}.csv'
            self.HP.SingleSave(save_path)
            self.RefreshImg(Plot(save_path, 'VG', 'VS', sizex=int(config['Window']['PhotoMaxSizeX'])))
                    
        self.Progress.AppendText('\n')

    def DrawVgsVd(self, event):
        if not self.VdVgsSweep.GetValue():
            self.VdVgs.Enable()
            self.VdVgsTx.Enable()
        else:
            self.VdVgs.Disable()
            self.VdVgsTx.Disable() 

    def DrawVgsVdSat(self, event):
        if self.EnableVgsSat.GetValue():
            self.VdVgsSat.Enable()
            self.VdVgsSatTx.Enable()
        else:
            self.VdVgsSat.Disable()
            self.VdVgsSatTx.Disable() 
            
    def DrawIspecDef(self,event):
        if not self.IsImport.GetValue():
            self.IsDef.Enable()
            self.IsDefTx.Enable()
        else:
            self.IsDef.Disable()
            self.IsDefTx.Disable()

    def OnButton(self, event):
        self.Stop_flag=False
        if self.SaveFilePath.GetValue() == "":
            self.ShowMessage("Select savepath and try again", False)
            self.OnSaveButton(1)
            return 1
        self.testThread = Thread(target=self.Measure)
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
                    self.Stop_flag=False

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
        self.ToggleList([self.Sizer1,self.Sizer1a,self.Sizer2,self.Sizer3,self.Sizer4], State)
        self.IsDef.Disable()
        self.IsDef.Enable(State and not self.IsImport.GetValue())
        self.VdVgsSat.Disable()
        self.VdVgsSat.Enable(State and self.EnableVgsSat.GetValue())
        self.VdVgs.Disable()
        self.VdVgs.Enable(State and not self.VdVgsSweep.GetValue())
   