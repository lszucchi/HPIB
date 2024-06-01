from .Tab_Generic import *

class IVTab(GenericTab):
    """
    This will be the first notebook tab
    """
    #----------------------------------------------------------------------

    def Measure(self):
        
        self.OpenHP(self.GPIBCH.GetValue(), self.Inst.GetValue())

        self.HP.SMU=[self.SBox.GetValue(), self.DBox.GetValue(),self.GBox.GetValue(),self.BBox.GetValue()]
        self.HP.SetIntTime(self.IntTimeBox.GetValue())
        
        ChSelect=[self.cb1.GetValue(),self.cb2.GetValue(),self.cb3.GetValue(),self.cb4.GetValue(),self.cb5.GetValue(),self.cb6.GetValue()]
        
        self.Progress.SetValue('Arduino Opened on: '+ self.COM.GetValue()+'\n')    
        MeasureList=['ChnOpen', 'Diode', 'Id_Vgs', 'Id_VgsSat', 'Id_Vds', 'Vp_Vgs']

        path=self.SaveFilePath.GetValue()
        
        if not os.path.isdir(path):
            self.ShowMessage('Invalid path\nEnter a folder')
        path=self.SaveFilePath.GetValue()
        if not path.endswith('\\'):
            path=path+'\\'
            
        for Chn in range(6):
            if not ChSelect[Chn]:
                continue
##            opench(Chn)
            self.Progress.AppendText(str('ChnOpen')+ '  ')
            self.Progress.AppendText('Channel: ' +str(Chn+1) + ' Measurements:\n')                                                
                       
            if self.EnableIdVgs.GetValue():
                    self.Progress.AppendText(str('Id_Vgs')+ '  ')
                    self.HP.SetVgs(self.VgVgsStart.GetValue(),self.VgVgsStop.GetValue(),self.VgVgsStep.GetValue(),self.VdVgsStart.GetValue(),self.VdVgsSweep.GetValue(),ptype=self.ptype.GetValue())

                    save_path=path+'Ch ' + str(Chn+1) + '-' + self.HP.term + '-' + datetime.datetime.now().strftime("%y%m%d %H%M%S") + '.csv'
                    self.HP.SingleSave(save_path)
                    self.RefreshImg(Plot(save_path, 'ID', 'VG'))
                    
            if self.EnableVgsSat.GetValue():
                    self.Progress.AppendText(str('Id_VgsSat')+ '  ')
                    self.HP.SetVgs(self.VgVgsStart.GetValue(),self.VgVgsStop.GetValue(),self.VgVgsStep.GetValue(),self.VdVgsSat.GetValue(),ptype=self.ptype.GetValue(), sat=True)

                    save_path=path+'Ch ' + str(Chn+1) + '-' + self.HP.term + '-' + datetime.datetime.now().strftime("%y%m%d %H%M%S") + '.csv'
                    self.HP.SingleSave(save_path)
                    self.RefreshImg(PlotVgs(save_path))
                    
            if self.EnableIdVds.GetValue():
                    self.Progress.AppendText(str('Id_Vds')+ '  ')
                    self.HP.SetVds(self.VdVdsStart.GetValue(),self.VdVdsStop.GetValue(),self.VdVdsStep.GetValue(),self.VgVdsStart.GetValue(),self.VgVdsStop.GetValue(),self.VgVdsStep.GetValue(),ptype=self.ptype.GetValue())                                                

                    save_path=path+'Ch ' + str(Chn+1) + '-' + self.HP.term + '-' + datetime.datetime.now().strftime("%y%m%d %H%M%S") + '.csv'
                    self.HP.SingleSave(save_path)
                    self.RefreshImg(PlotVgs(save_path))
                    
            if self.EnableVp.GetValue():
                    if not self.IsImport.GetValue():
                            Ispec=self.IsDef.GetValue()
                    else:
                            self.HP.SetEx_Ib(-0.5,self.VgVpStop.GetValue(),self.VgVpStep.GetValue(),ptype=self.ptype.GetValue())
                            save_path=self.SaveFilePath.GetValue()+'/Ch ' + str(Chn+1) + '-Ex_Ib-' + datetime.datetime.now().strftime("%y%m%d %H%M%S") + '.csv'
                            self.HP.get_data(save_path)
                            Ispec=self.HP.Ex_Ib(save_path, ptype=ptype.GetValue()) # type: ignore
                            
                    self.Progress.AppendText(str('Vp_Vgs')+ '  ')
                    self.HP.SetVp(Ispec,self.VgVpStart.GetValue(),self.VgVpStop.GetValue(),self.VgVpStep.GetValue(),ptype=self.ptype.GetValue())

                    save_path=path+'Ch ' + str(Chn+1) + '-' + self.HP.term + '-' + datetime.datetime.now().strftime("%y%m%d %H%M%S") + '.csv'
                    self.HP.SingleSave(save_path)
                    self.RefreshImg(PlotVgs(save_path))
                    
            self.Progress.AppendText('\n')
                
        self.Progress.AppendText('End!\n')
        self.Current.SetValue('Finished')
        return 0

        
    def __init__(self, parent):
        
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.timer = wx.Timer(self)
        
        self.DrawSaveBox(10, 0, 820)
 
        self.DrawConfigBox(10, 80)
        self.Config_Btn.Destroy()
        self.ptype = wx.CheckBox(self, label="p-type", pos=(130, 180), name='sv_ptype')
        
        self.DrawSMUConfig(int(config['Window']['Margin']), self.Box1[0][1]+self.Box1[1][1]+int(config['Window']['Margin']))

        #========  Id x Vgs ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
                         
        BoxVgs=[[self.Box1[0][0]+int(config['Window']['Margin'])+self.Box1[1][0]     ,self.Box1[0][1]]     ,       [225        ,280]]
        self.Bx2=wx.StaticBox(self,label='Id x Vgs', pos=(BoxVgs[0][0], BoxVgs[0][1]),size=(BoxVgs[1][0], BoxVgs[1][1]))
        self.Sizer2=wx.StaticBoxSizer(self.Bx2)
        
        self.EnableIdVgs = wx.CheckBox(self, label='Enable', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+2*int(config['Window']['Margin'])), name='sv_EnIdVgs')
        self.EnableIdVgs.SetValue(True)
        self.Sizer2.Add(self.EnableIdVgs)
 
        self.EnableVgsSat = wx.CheckBox(self, label='Measure Vd Sat', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+110, BoxVgs[0][1]+2*int(config['Window']['Margin'])), name='sv_EnIdVgsSat')
        self.EnableVgsSat.SetValue(True)
        self.Sizer2.Add(self.EnableVgsSat)
        self.EnableVgsSat.Bind(wx.EVT_CHECKBOX, self.DrawVgsVdSat)
        
        self.VdVgsSweep = wx.CheckBox(self, label='Sweep Vd=Vg', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+50+int(config['Window']['SMUMY'])), name='sv_IdVgsSweep')
        self.Sizer2.Add(self.VdVgsSweep)
        self.VdVgsSweep.Bind(wx.EVT_CHECKBOX, self.DrawVgsVd)

        ### Draw VGS SWEEP
        self.VdVgsStartTx = wx.StaticText(self, label='Vd', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+50))
        self.VdVgsStart = wx.SpinCtrlDouble(self, value=str (DefaultVd), pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+70), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VdVgsStart')
        self.VdVgsStart.SetIncrement(0.1)
        #self.Sizer2.Add(self.VdVgsStart)

        ### Draw VGS sat SWEEP
        self.VdVgsSatTx = wx.StaticText(self, label='Vd Sat', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+50))
        self.VdVgsSat= wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+70), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VdVgsSat')
        self.VdVgsSat.SetIncrement(0.1)
        #self.Sizer2.Add(self.VdVgsSat)

        # Vg Step
        self.VgVgsStartTx = wx.StaticText(self, label='Vg Initial Value', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+180))
        self.VgVgsStart = wx.SpinCtrlDouble(self, value='0', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+200), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVgsStart')
        self.VgVgsStart.SetIncrement(0.1)
        self.Sizer2.Add(self.VgVgsStart)

        self.VgVgsStepTx = wx.StaticText(self, label='Vg Step Size', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+180))
        self.VgVgsStep = wx.SpinCtrlDouble(self, value=str(DefaultStep/StepScale), pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+200), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVgsStep')
        self.VgVgsStep.SetIncrement(0.01)
        self.Sizer2.Add(self.VgVgsStep)

        self.VgVgsStopTx = wx.StaticText(self, label='Vg Stop Value', pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+180+int(config['Window']['SMUMY'])))
        self.VgVgsStop = wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVgs[0][0]+int(config['Window']['Margin']), BoxVgs[0][1]+200+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVgsStop')
        self.VgVgsStop.SetIncrement(0.1)
        self.Sizer2.Add(self.VgVgsStop)

        #self.VgVgsPointsTx = wx.StaticText(self, label='Vg Step Number', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+180+int(config['Window']['SMUMY'])))
        #self.VgVgsPoints = wx.SpinCtrl(self, value='40', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVgs[0][1]+200+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS)



        #========  Id x Vds ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        BoxVds=[[BoxVgs[0][0]+int(config['Window']['Margin'])+BoxVgs[1][0]        ,self.Box1[0][1]],        [225        ,280]]
        self.Bx3=wx.StaticBox(self,label='Id x Vds', pos=(BoxVds[0][0], BoxVds[0][1]),size=(BoxVds[1][0], BoxVds[1][1]))
        self.Sizer3=wx.StaticBoxSizer(self.Bx3)
        
        # Enable
        self.EnableIdVds = wx.CheckBox(self, label='Enable Id x Vds', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+2*int(config['Window']['Margin'])), name='sv_EnIdVds')
        self.EnableIdVds.SetValue(True)
        self.Sizer3.Add(self.EnableIdVds)

        #Value Config

        #Vd Sweep
        self.VdVdsStartTx = wx.StaticText(self, label='Vd Initial Value', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+50))
        self.VdVdsStart = wx.SpinCtrlDouble(self, value='0', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+70), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VdVdsStart')
        self.VdVdsStart.SetIncrement(0.1)
        self.Sizer3.Add(self.VdVdsStart)

        self.VdVdsStepTx = wx.StaticText(self, label='Vd Step Size', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+50))
        self.VdVdsStep = wx.SpinCtrlDouble(self, value=str(DefaultStep/StepScale), pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+70), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VdVdsStep')
        self.VdVdsStep.SetIncrement(0.01)
        self.Sizer3.Add(self.VdVdsStep)

        self.VdVdsStopTx = wx.StaticText(self, label='Vd Stop Value', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+50+int(config['Window']['SMUMY'])))
        self.VdVdsStop = wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+70+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VdVdsStop')
        self.VdVdsStop.SetIncrement(0.1)
        self.Sizer3.Add(self.VdVdsStop)

        #self.VdVdsPointsTx = wx.StaticText(self, label='Vd Step Number', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+50+int(config['Window']['SMUMY'])))
        #self.VdVdsPoints = wx.SpinCtrl(self, value='40', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+70+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS)

        # Vg Step
        self.VgVdsStartTx = wx.StaticText(self, label='Vg Initial Value', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+180))
        self.VgVdsStart = wx.SpinCtrlDouble(self, value='0', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+200), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVdsStart')
        self.VgVdsStart.SetIncrement(0.1)
        self.Sizer3.Add(self.VgVdsStart)

        self.VgVdsStepTx = wx.StaticText(self, label='Vg Step Size', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+180))
        self.VgVdsStep = wx.SpinCtrlDouble(self, value=str(DefaultStep), pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+200), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVdsStep')
        self.VgVdsStep.SetIncrement(0.1)
        self.Sizer3.Add(self.VgVdsStep)

        self.VgVdsStopTx = wx.StaticText(self, label='Vg Stop Value', pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+180+int(config['Window']['SMUMY'])))
        self.VgVdsStop = wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVds[0][0]+int(config['Window']['Margin']), BoxVds[0][1]+200+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVdsStop')
        self.VgVdsStop.SetIncrement(0.1)
        self.Sizer3.Add(self.VgVdsStop)

        #self.VgVdsPointsTx = wx.StaticText(self, label='Vg Step Number', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+180+int(config['Window']['SMUMY'])))
        #self.VgVdsPoints = wx.SpinCtrl(self, value='5', pos=(BoxVds[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVds[0][1]+200+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS)



        #========  Vp x Vg ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        global BoxVp
        BoxVp=[[BoxVds[0][0]+int(config['Window']['Margin'])+BoxVds[1][0]       ,self.Box1[0][1]]        ,[225        ,280]]
        self.Bx4=wx.StaticBox(self,label='Vp x Vgs', pos=(BoxVp[0][0],BoxVp[0][1]),size=(BoxVp[1][0], BoxVp[1][1]))
        self.Sizer4=wx.StaticBoxSizer(self.Bx4)
        
        self.EnableVp = wx.CheckBox(self, label='Enable Vp', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+2*int(config['Window']['Margin'])), name='sv_EnVp')
        self.EnableVp.SetValue(True)
        self.Sizer4.Add(self.EnableVp)

        #Value Config

        #Vd Sweep
        self.IsImport = wx.CheckBox(self, label='Import Ispec', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+50+20), name='sv_IsImport')
        
        self.IsDefTx = wx.StaticText(self, label='Ispec', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX'])-10, BoxVp[0][1]+50))
        self.IsDef = wx.TextCtrl(self, value='1e-6', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX'])-10, BoxVp[0][1]+70), size=(60,20), name='sv_IsDef')
        self.IsDef.SetValue(" ")
        #self.Sizer4.Add(self.IsDef)
        
        self.IsDef.Disable()
        self.IsDefTx.Disable()
        self.IsImport.SetValue(True)
        self.IsImport.Bind(wx.EVT_CHECKBOX, self.DrawIspecDef)
        self.Sizer4.Add(self.IsImport)

        # Vg Step
        self.VgVpStartTx = wx.StaticText(self, label='Vg Initial Value', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+180))
        self.VgVpStart = wx.SpinCtrlDouble(self, value='0', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+200), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVpStart')
        self.VgVpStart.SetIncrement(0.1)
        self.Sizer4.Add(self.VgVpStart)

        self.VgVpStepTx = wx.StaticText(self, label='Vg Step Size', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+180))
        self.VgVpStep = wx.SpinCtrlDouble(self, value=str (DefaultStep/StepScale), pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+200), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVpStep')
        self.VgVpStep.SetIncrement(0.01)
        self.Sizer4.Add(self.VgVpStep)

        self.VgVpStopTx = wx.StaticText(self, label='Vg Stop Value', pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+180+int(config['Window']['SMUMY'])))
        self.VgVpStop = wx.SpinCtrlDouble(self, value=str (DefaultMax), pos=(BoxVp[0][0]+int(config['Window']['Margin']), BoxVp[0][1]+200+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS, name='sv_VgVpstop')
        self.VgVpStop.SetIncrement(0.1)
        self.Sizer4.Add(self.VgVpStop)

        #self.VgVpPointsTx = wx.StaticText(self, label='Vg Step Number', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+180+int(config['Window']['SMUMY'])))
        #self.VgVpPoints = wx.SpinCtrl(self, value='40', pos=(BoxVp[0][0]+int(config['Window']['Margin'])+int(config['Window']['SMUMX']), BoxVp[0][1]+200+int(config['Window']['SMUMY'])), size=(60,20),style=wx.SP_ARROW_KEYS)

        self.Progress=wx.TextCtrl(self, pos=(BoxVgs[0][0],BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])), size=(400, 90),style=wx.TE_MULTILINE)

        self.CurrentTx = wx.StaticText(self, label='Current Step:', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+400,BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+3))
        self.Current = wx.TextCtrl(self, pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+400+80,BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])),size=(150,20))

        self.IntTimeTx = wx.StaticText(self, label='Integration Time:', pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+400,BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+33))
        self.IntTimeBox = wx.ComboBox(self, value=DefaultIntTime, pos=(BoxVgs[0][0]+int(config['Window']['Margin'])+400,BoxVgs[0][1]+BoxVgs[1][1]+int(config['Window']['Margin'])+53), size=(80,40), choices=['SHORt','MEDium','LONG'], style=wx.CB_READONLY, name='sv_IntTime')                
        self.Sizer4.Add(self.IntTimeBox)


        #======== Image preview =========#
        img = wx.Image((PhotoMaxSizeX,int(PhotoMaxSizeX*480/640)))
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img),pos=(960, 30), size=(PhotoMaxSizeX,int(PhotoMaxSizeX*480/640)))
        self.img_path = wx.StaticText(self, label="No measurements to show", pos=(960,10),size=(400,20))

            

        #========  End ========#
        self.Show()
       # self.Maximize()

    def DrawVgsVd(self, event):
        if not self.VdVgsSweep.GetValue():
            self.VdVgsStart.SetValue(DefaultVd)
            self.VdVgsStart.Enable()
            self.VdVgsStartTx.Enable()
        else:
            self.VdVgsStart.SetValue(" ")
            self.VdVgsStart.Disable()
            self.VdVgsStartTx.Disable() 

    def DrawVgsVdSat(self, event):
        if self.EnableVgsSat.GetValue():
            self.VdVgsSat.SetValue(DefaultMax)
            self.VdVgsSat.Enable()
            self.VdVgsSatTx.Enable()
        else:
            self.VdVgsSat.SetValue(" ")
            self.VdVgsSat.Disable()
            self.VdVgsSatTx.Disable() 
            
    def DrawIspecDef(self,event):
        if not self.IsImport.GetValue():
            self.IsDef.Enable()
            self.IsDefTx.Enable()
        else:
            self.IsDef.SetValue(" ")
            self.IsDef.Disable()
            self.IsDefTx.Disable()

    def OnButton(self, event):
        self.Stop_flag=False
        print(self.SaveFilePath.GetValue())
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
        self.VdVgsStart.Disable()
        self.VdVgsStart.Enable(State and not self.VdVgsSweep.GetValue())
   