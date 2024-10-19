from .Tab_Generic import *

scripts=configparser.ConfigParser()
scripts.read('./scripts/MainScripts.ini')

class General(GenericTab):
    
    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
        self.timer = wx.Timer(self)
        
        self.DrawSaveBox(5, 0, 680)

        self.DrawConfigBox(5, 80)

        self.CreateFonts()

        #========  Channel Config ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        SizeSMUcol=50
        SizeIVcol=40
        SizeFMcol=70
        SizeRow=23
        SpacingRow=40
        
        self.Box2=[[self.Box1[0][0]+5+self.Box1[1][0],self.Box1[0][1]]     ,       [395       , 7*SpacingRow]]
        self.Bx2=wx.StaticBox(self,label='Port Configuration', pos=(self.Box2[0][0], self.Box2[0][1]),size=(self.Box2[1][0], self.Box2[1][1]))

        self.VTx = wx.StaticText(self, label='V', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol, self.Box2[0][1]+2*int(config['Window']['Margin'])))
        self.ITx = wx.StaticText(self, label='I', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+2*int(config['Window']['Margin'])))
        self.MTx = wx.StaticText(self, label='Mode', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+2*int(config['Window']['Margin'])))
        self.FTx = wx.StaticText(self, label='Func/Value', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+2*int(config['Window']['Margin'])))
        self.CTx = wx.StaticText(self, label='Comp', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+2*int(config['Window']['Margin'])))
        
        ########################## SMU1 ##########################
        self.SizerSMU1=wx.BoxSizer()
        self.SMU1Tx = wx.StaticText(self, label='SMU1', pos=(self.Box2[0][0]+int(config['Window']['Margin']), self.Box2[0][1]+SpacingRow+4))
        

        ### Draw SMU1 Names
        self.SMU1V = wx.TextCtrl(self, value='V1', pos=(self.Box2[0][0]+SizeSMUcol, self.Box2[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU1V')
        self.SizerSMU1.Add(self.SMU1V)
        self.SMU1I = wx.TextCtrl(self, value='I1', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU1I')
        self.SizerSMU1.Add(self.SMU1I)
        
        ### Draw SMU1 Mode/Func/Comp
        self.SMU1M = wx.ComboBox(self, value='COMM', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+SpacingRow), size=(SizeFMcol,SpacingRow),choices=['COMM','V','I'], name='sv_SMU1M')
        self.SizerSMU1.Add(self.SMU1M)
        self.SMU1F = wx.ComboBox(self, value='CONS', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+SpacingRow), size=(SizeFMcol,SizeRow), choices=['CONS','VAR1','VAR2','VARD'], name='sv_SMU1F')
    
        self.SizerSMU1.Add(self.SMU1F)
        self.SMU1C = wx.TextCtrl(self, value='1e-3', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+SpacingRow), size=(SizeSMUcol,SizeRow), name='sv_SMU1C')
        self.SizerSMU1.Add(self.SMU1C)

        ## Enable
        self.EnableSMU1 = wx.CheckBox(self, label='', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+2*SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+SpacingRow+4), name='sv_enSMU1')
        self.EnableSMU1.SetValue(True)
        self.SizerSMU1.Add(self.EnableSMU1)
        self.EnableSMU1.Bind(wx.EVT_CHECKBOX, self.SetSizers)     


        ########################## SMU2 ##########################
        self.SizerSMU2=wx.BoxSizer()
        self.SMU2Tx = wx.StaticText(self, label='SMU2', pos=(self.Box2[0][0]+int(config['Window']['Margin']), self.Box2[0][1]+2*SpacingRow+4))
        

        ### Draw SMU2 Names
        self.SMU2V = wx.TextCtrl(self, value='V2', pos=(self.Box2[0][0]+SizeSMUcol, self.Box2[0][1]+2*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU2V')
        self.SizerSMU2.Add(self.SMU2V)
        self.SMU2I = wx.TextCtrl(self, value='I2', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+2*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU2I')
        self.SizerSMU2.Add(self.SMU2I)
        
        ### Draw SMU2 Mode/Func/Comp
        self.SMU2M = wx.ComboBox(self, value='V', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+2*SpacingRow), size=(SizeFMcol,SpacingRow),choices=['COMM','V','I'], name='sv_SMU2M')
        self.SizerSMU2.Add(self.SMU2M)
        self.SMU2F = wx.ComboBox(self, value='VAR1', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+2*SpacingRow), size=(SizeFMcol,SizeRow), choices=['CONS','VAR1','VAR2','VARD'], name='sv_SMU2F')
        self.SizerSMU2.Add(self.SMU2F)
        self.SMU2C = wx.TextCtrl(self, value='1e-3', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+2*SpacingRow), size=(SizeSMUcol,SizeRow), name='sv_SMU2C')
        self.SizerSMU2.Add(self.SMU2C)

        ## Enable
        self.EnableSMU2 = wx.CheckBox(self, label='', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+2*SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+2*SpacingRow+4), name='sv_enSMU2')
        self.EnableSMU2.SetValue(True)
        self.SizerSMU2.Add(self.EnableSMU2)        
        self.EnableSMU2.Bind(wx.EVT_CHECKBOX, self.SetSizers)

        ########################## SMU3 ##########################
        self.SizerSMU3=wx.BoxSizer()
        self.SMU3Tx = wx.StaticText(self, label='SMU3', pos=(self.Box2[0][0]+int(config['Window']['Margin']), self.Box2[0][1]+3*SpacingRow+4))
        

        ### Draw SMU3 Names
        self.SMU3V = wx.TextCtrl(self, value='V3', pos=(self.Box2[0][0]+SizeSMUcol, self.Box2[0][1]+3*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU3V')
        self.SizerSMU3.Add(self.SMU3V)
        self.SMU3I = wx.TextCtrl(self, value='I3', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+3*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU3I')
        self.SizerSMU3.Add(self.SMU3I)
        
        ### Draw SMU3 Mode/Func/Comp
        self.SMU3M = wx.ComboBox(self, value='V', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+3*SpacingRow), size=(SizeFMcol,SpacingRow),choices=['COMM','V','I'], name='sv_SMU3M')
        self.SizerSMU3.Add(self.SMU3M)
        self.SMU3F = wx.ComboBox(self, value='VAR2', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+3*SpacingRow), size=(SizeFMcol,SizeRow), choices=['CONS','VAR1','VAR2','VARD'], name='sv_SMU3F')
        self.SizerSMU3.Add(self.SMU3F)
        self.SMU3C = wx.TextCtrl(self, value='1e-3', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+3*SpacingRow), size=(SizeSMUcol,SizeRow), name='sv_SMU3C')
        self.SizerSMU3.Add(self.SMU3C)

        ## Enable
        self.EnableSMU3 = wx.CheckBox(self, label='', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+2*SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+3*SpacingRow+4), name='sv_enSMU3')
        self.EnableSMU3.SetValue(True)
        self.SizerSMU3.Add(self.EnableSMU3)            
        self.EnableSMU3.Bind(wx.EVT_CHECKBOX, self.SetSizers)
        
        ########################## SMU4 ##########################
        self.SizerSMU4=wx.BoxSizer()
        self.SMU4Tx = wx.StaticText(self, label='SMU4', pos=(self.Box2[0][0]+int(config['Window']['Margin']), self.Box2[0][1]+4*SpacingRow+4))
        

        ### Draw SMU4 Names
        self.SMU4V = wx.TextCtrl(self, value='V4', pos=(self.Box2[0][0]+SizeSMUcol, self.Box2[0][1]+4*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU4V')
        self.SizerSMU4.Add(self.SMU4V)
        self.SMU4I = wx.TextCtrl(self, value='I4', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+4*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_SMU4I')
        self.SizerSMU4.Add(self.SMU4I)
        
        ### Draw SMU4 Mode/Func/Comp
        self.SMU4M = wx.ComboBox(self, value='COMM', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+4*SpacingRow), size=(SizeFMcol,SpacingRow),choices=['COMM','V','I'], name='sv_SMU4M')
        self.SizerSMU4.Add(self.SMU4M)
        self.SMU4F = wx.ComboBox(self, value='CONS', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+4*SpacingRow), size=(SizeFMcol,SizeRow), choices=['CONS','VAR1','VAR2','VARD'], name='sv_SMU4F')
        self.SizerSMU4.Add(self.SMU4F)
        self.SMU4C = wx.TextCtrl(self, value='1e-3', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+4*SpacingRow), size=(SizeSMUcol,SizeRow), name='sv_SMU4C')
        self.SizerSMU4.Add(self.SMU4C)

        ## Enable
        self.EnableSMU4 = wx.CheckBox(self, label='', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+2*SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+4*SpacingRow+4), name='sv_enSMU4')
        self.EnableSMU4.SetValue(True)
        self.SizerSMU4.Add(self.EnableSMU4)        
        self.EnableSMU4.Bind(wx.EVT_CHECKBOX, self.SetSizers)

        ########################## VS1 ##########################
        self.SizerVS1=wx.BoxSizer()
        self.VS1Tx = wx.StaticText(self, label='VSU1', pos=(self.Box2[0][0]+int(config['Window']['Margin']), self.Box2[0][1]+5*SpacingRow+4))
        

        ### Draw VS1 Names
        self.VS1V = wx.TextCtrl(self, value='VSU1', pos=(self.Box2[0][0]+SizeSMUcol, self.Box2[0][1]+5*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VS1V')
        self.SizerVS1.Add(self.VS1V)
        self.VS1I = wx.TextCtrl(self, value='', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+5*SpacingRow), size=(SizeIVcol,SizeRow))
        self.SizerVS1.Add(self.VS1I)
        self.VS1I.Disable()
        
        ### Draw VS1 Mode/Func/Comp
        self.VS1M = wx.ComboBox(self, value='V', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+5*SpacingRow), size=(SizeFMcol,SpacingRow),choices=['COMM','V','I'])
        self.SizerVS1.Add(self.VS1M)
        self.VS1M.Disable()
        self.VS1F = wx.ComboBox(self, value='CONS', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+5*SpacingRow), size=(SizeFMcol,SizeRow), choices=['CONS','VAR1','VAR2','VARD'], name='sv_VS1F')
        self.SizerVS1.Add(self.VS1F)
        self.VS1C = wx.TextCtrl(self, value='1e-3', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+5*SpacingRow), size=(SizeSMUcol,SizeRow), name='sv_VS1C')
        self.SizerVS1.Add(self.VS1C)

        ## Enable
        self.EnableVS1 = wx.CheckBox(self, label='', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+2*SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+5*SpacingRow+4), name='sv_enVS1')
        self.EnableVS1.SetValue(False)
        self.SizerVS1.Add(self.EnableVS1)       
        self.EnableVS1.Bind(wx.EVT_CHECKBOX, self.SetSizers)

        ########################## VS2 ##########################
        self.SizerVS2=wx.BoxSizer()
        self.VS2Tx = wx.StaticText(self, label='VSU2', pos=(self.Box2[0][0]+int(config['Window']['Margin']), self.Box2[0][1]+6*SpacingRow+4))
        

        ### Draw VS2 Names
        self.VS2V = wx.TextCtrl(self, value='VSU2', pos=(self.Box2[0][0]+SizeSMUcol, self.Box2[0][1]+6*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VS2V')
        self.SizerVS2.Add(self.VS2V)
        self.VS2I = wx.TextCtrl(self, value='', pos=(self.Box2[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, self.Box2[0][1]+6*SpacingRow), size=(SizeIVcol,SizeRow))
        self.SizerVS2.Add(self.VS2I)
        self.VS2I.Disable()
        
        ### Draw VS2 Mode/Func/Comp
        self.VS2M = wx.ComboBox(self, value='V', pos=(self.Box2[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, self.Box2[0][1]+6*SpacingRow), size=(SizeFMcol,SpacingRow),choices=['COMM','V','I'])
        self.SizerVS2.Add(self.VS2M)
        self.VS2M.Disable()
        self.VS2F = wx.ComboBox(self, value='CONS', pos=(self.Box2[0][0]+3*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+SizeFMcol, self.Box2[0][1]+6*SpacingRow), size=(SizeFMcol,SizeRow), choices=['CONS','VAR1','VAR2','VARD'], name='sv_VS2F')
        self.SizerVS2.Add(self.VS2F)
        self.VS2C = wx.TextCtrl(self, value='1e-3', pos=(self.Box2[0][0]+4*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+6*SpacingRow), size=(SizeSMUcol,SizeRow), name='sv_VS2C')
        self.SizerVS2.Add(self.VS2C)

        ## Enable
        self.EnableVS2 = wx.CheckBox(self, label='', pos=(self.Box2[0][0]+5*int(config['Window']['Margin'])+2*SizeSMUcol+2*SizeIVcol+2*SizeFMcol, self.Box2[0][1]+6*SpacingRow+4), name='sv_enVS2')
        self.EnableVS2.SetValue(False)
        self.SizerVS2.Add(self.EnableVS2)           
        self.EnableVS2.Bind(wx.EVT_CHECKBOX, self.SetSizers)

        self.sizers=[self.SizerSMU1, self.SizerSMU2, self.SizerSMU3, self.SizerSMU4, self.SizerVS1, self.SizerVS2]
        
        #========  Var Config ========#
        # BoxN = [[PosX, PoxY],[SizeX,SizeY]]
        Box3=[[self.Box2[0][0]+5+self.Box2[1][0]       ,self.Box1[0][1]]        ,[190        , int(config['Window']['Margin'])+4*SpacingRow+int(config['Window']['Margin'])]]
        self.Bx3=wx.StaticBox(self,label='Var Config', pos=(Box3[0][0],Box3[0][1]),size=(Box3[1][0], Box3[1][1]))
        self.VTx = wx.StaticText(self, label='Start', pos=(Box3[0][0]+SizeSMUcol, Box3[0][1]+2*int(config['Window']['Margin'])))
        self.ITx = wx.StaticText(self, label='Stop', pos=(Box3[0][0]+int(config['Window']['Margin'])+SizeSMUcol+SizeIVcol, Box3[0][1]+2*int(config['Window']['Margin'])))
        self.MTx = wx.StaticText(self, label='Step', pos=(Box3[0][0]+2*int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, Box3[0][1]+2*int(config['Window']['Margin'])))

        
        ########################## VAR1 ##########################
        self.SizerVAR1=wx.BoxSizer()
        self.VAR1Tx = wx.StaticText(self, label='VAR1', pos=(Box3[0][0]+int(config['Window']['Margin']), Box3[0][1]+SpacingRow+4))
        
        self.VAR1Start = wx.TextCtrl(self, value='0', pos=(Box3[0][0]+SizeSMUcol-10, Box3[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VAR1Start')
        self.VAR1Start.Bind(wx.EVT_TEXT, self.AxisSet)
        self.SizerVAR1.Add(self.VAR1Start)
        self.VAR1Stop = wx.TextCtrl(self, value='1', pos=(Box3[0][0]+SizeSMUcol+SizeIVcol, Box3[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VAR1Stop')
        self.VAR1Stop.Bind(wx.EVT_TEXT, self.AxisSet)
        self.SizerVAR1.Add(self.VAR1Stop)
        self.VAR1Step = wx.TextCtrl(self, value='0.01', pos=(Box3[0][0]+int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, Box3[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VAR1Step')
        self.SizerVAR1.Add(self.VAR1Step)

        ########################## VAR2 ##########################
        self.SizerVAR2=wx.BoxSizer()
        self.VAR2Tx = wx.StaticText(self, label='VAR2', pos=(Box3[0][0]+int(config['Window']['Margin']), Box3[0][1]+2*SpacingRow+4))
        
        self.VAR2Start = wx.TextCtrl(self, value='0', pos=(Box3[0][0]+SizeSMUcol-10, Box3[0][1]+2*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VAR2Start')
        self.SizerVAR2.Add(self.VAR2Start)
        self.VAR2Stop = wx.TextCtrl(self, value='1', pos=(Box3[0][0]+SizeSMUcol+SizeIVcol, Box3[0][1]+2*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VAR2Stop')
        self.SizerVAR2.Add(self.VAR2Stop)
        self.VAR2Step = wx.TextCtrl(self, value='0.2', pos=(Box3[0][0]+int(config['Window']['Margin'])+SizeSMUcol+2*SizeIVcol, Box3[0][1]+2*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VAR2Step')
        self.SizerVAR2.Add(self.VAR2Step)

        ########################## VARD ##########################
        self.SizerVARD=wx.BoxSizer()
        self.VARDTx = wx.StaticText(self, label='VARD', pos=(Box3[0][0]+int(config['Window']['Margin']), Box3[0][1]+2*int(config['Window']['Margin'])+3*SpacingRow+4))
        
        self.VARDOffTx = wx.StaticText(self, label='Offset', pos=(Box3[0][0]+SizeSMUcol-10, Box3[0][1]+2*int(config['Window']['Margin'])+2*SpacingRow+2*int(config['Window']['Margin'])))       
        self.VARDOff = wx.TextCtrl(self, value='0', pos=(Box3[0][0]+SizeSMUcol-10, Box3[0][1]+2*int(config['Window']['Margin'])+3*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VARDOff')
        self.SizerVARD.Add(self.VARDOff)
        self.VARDRatTx = wx.StaticText(self, label='Ratio', pos=(Box3[0][0]+SizeSMUcol+SizeIVcol, Box3[0][1]+2*int(config['Window']['Margin'])+2*SpacingRow+2*int(config['Window']['Margin'])))
        self.VARDRat = wx.TextCtrl(self, value='1', pos=(Box3[0][0]+SizeSMUcol+SizeIVcol, Box3[0][1]+2*int(config['Window']['Margin'])+3*SpacingRow), size=(SizeIVcol,SizeRow), name='sv_VARDRat')
        self.SizerVARD.Add(self.VARDRat)                     



        #======== Axis Config =========#
        Box4=[[Box3[0][0]         , Box3[0][1]+int(config['Window']['Margin'])+Box3[1][1]]        ,[190        , 5*SpacingRow]]
        self.Bx4=wx.StaticBox(self,label='Axis Config', pos=(Box4[0][0],Box4[0][1]),size=(Box4[1][0], Box4[1][1]))

        self.SizerAxis=wx.BoxSizer()
        
        self.XTx = wx.StaticText(self, label='X', pos=(Box4[0][0]+39, Box4[0][1]+2*int(config['Window']['Margin'])))       
        self.Y1Tx = wx.StaticText(self, label='Y1', pos=(Box4[0][0]+92+12, Box4[0][1]+2*int(config['Window']['Margin'])))
        self.Y2Tx = wx.StaticText(self, label='Y2', pos=(Box4[0][0]+140+12, Box4[0][1]+2*int(config['Window']['Margin'])))
        self.X1 = wx.TextCtrl(self, value='V2', pos=(Box4[0][0]+39, Box4[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_X1')
        
        self.Y1 = wx.TextCtrl(self, value='I2', pos=(Box4[0][0]+92, Box4[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_Y1')
        self.Y2 = wx.TextCtrl(self, value='', pos=(Box4[0][0]+140, Box4[0][1]+SpacingRow), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_Y2')
        self.SizerAxis.Add(self.X1)

        self.MinTx = wx.StaticText(self, label='Min', pos=(Box4[0][0]+int(config['Window']['Margin']), Box4[0][1]+2*SpacingRow-5))
        self.X1Min = wx.TextCtrl(self, value='0', pos=(Box4[0][0]+39, Box4[0][1]+2*SpacingRow-int(config['Window']['Margin'])), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_X1Min')
        self.Y1Min = wx.TextCtrl(self, value='0', pos=(Box4[0][0]+92, Box4[0][1]+2*SpacingRow-int(config['Window']['Margin'])), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_Y1Min')
        self.Y2Min = wx.TextCtrl(self, value='', pos=(Box4[0][0]+140, Box4[0][1]+2*SpacingRow-int(config['Window']['Margin'])), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_Y2Min')

        self.MaxTx = wx.StaticText(self, label='Max', pos=(Box4[0][0]+int(config['Window']['Margin']), Box4[0][1]+3*SpacingRow-15))
        self.X1Max = wx.TextCtrl(self, value='1', pos=(Box4[0][0]+39, Box4[0][1]+3*SpacingRow-2*int(config['Window']['Margin'])), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_X1Max')
        self.Y1Max = wx.TextCtrl(self, value='1m', pos=(Box4[0][0]+92, Box4[0][1]+3*SpacingRow-2*int(config['Window']['Margin'])), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_Y1Max')
        self.Y2Max = wx.TextCtrl(self, value='', pos=(Box4[0][0]+140, Box4[0][1]+3*SpacingRow-2*int(config['Window']['Margin'])), size=(SizeIVcol,SizeRow), style=wx.TE_CENTRE, name='sv_Y2Max')

        self.Traces = wx.TextCtrl(self, value='I1, I3, I4', pos=(Box4[0][0]+int(config['Window']['Margin']), Box4[0][1]+4*SpacingRow-3*int(config['Window']['Margin'])+5), size=(Box4[1][0]-2*int(config['Window']['Margin']),SizeRow), name='sv_Traces')
        self.ufunc = wx.TextCtrl(self, value='VM=VMU2-VMU1', pos=(Box4[0][0]+int(config['Window']['Margin']), Box4[0][1]+5*SpacingRow-4*int(config['Window']['Margin'])+5), size=(Box4[1][0]-2*int(config['Window']['Margin']),SizeRow), name='sv_ufunc')

        ## Misc Configs
        
        self.IntTimeTx = wx.StaticText(self, label='Integration:', pos=(self.Box1[0][0],self.Box2[0][1]+self.Box2[1][1]+int(config['Window']['Margin'])))
        self.IntTimeBox = wx.ComboBox(self, value='MEDium', pos=(self.Box1[0][0],self.Box2[0][1]+self.Box2[1][1]+3*int(config['Window']['Margin'])), size=(70,40), choices=['SHORt','MEDium','LONG'], name='sv_IntTimeBox', style=wx.CB_READONLY)

        self.ScriptBox = wx.ComboBox(self, value='Script:', pos=(self.Box1[0][0],self.Box2[0][1]+self.Box2[1][1]+3*int(config['Window']['Margin'])+int(config['Window']['SMUMY'])), size=(70,20), choices=['Script:']+scripts.sections()+['Open', 'Save'] , style=wx.CB_READONLY)
        self.NameBox = wx.TextCtrl(self, value='New', pos=(self.Box1[0][0]+80,self.Box2[0][1]+self.Box2[1][1]+3*int(config['Window']['Margin'])+int(config['Window']['SMUMY'])), size=(120,20))
        self.ScriptBox.Bind(wx.EVT_COMBOBOX, self.ScriptMenu)

        self.TimeoutTx = wx.StaticText(self, label='Timeout (min/trace):', pos=(self.Box1[0][0]+80,self.Box2[0][1]+self.Box2[1][1]+int(config['Window']['Margin'])))
        self.Timeout = wx.SpinCtrlDouble(self, value='1', pos=(self.Box1[0][0]+80,self.Box2[0][1]+self.Box2[1][1]+3*int(config['Window']['Margin'])), inc=0.5, size=(50,23), name='sv_Timeout')

        self.Progress=wx.TextCtrl(self, pos=(self.Box2[0][0],self.Box2[0][1]+self.Box2[1][1]+int(config['Window']['Margin'])), size=(self.Box2[1][0], 100),style=wx.TE_MULTILINE) 
        
        #======== Image preview =========#
        img = wx.Image((int(config['Window']['PhotoMaxSizeX']),int(int(config['Window']['PhotoMaxSizeX'])*480/640)))
        self.imageCtrl = wx.StaticBitmap(self, wx.ID_ANY, wx.Bitmap(img),pos=(805, 2+int(config['Window']['Margin'])), size=(int(config['Window']['PhotoMaxSizeX']),int(config['Window']['PhotoMaxSizeX'])*480/640))
        self.img_path = wx.StaticText(self, label="No measurements to show", pos=(805,int(config['Window']['Margin'])),size=(400,20))

        #========  End ========#
        self.Show()
        self.SetSizers(1)
       # self.Maximize()

    def Configure(self):

        self.OpenHP(self.GPIBCH.GetValue(), self.Inst.GetValue())

        SMUfuncs=[self.SMU1F.GetValue(), self.SMU2F.GetValue(), self.SMU3F.GetValue(), self.SMU4F.GetValue(), self.VS1F.GetValue(), self.VS2F.GetValue()]
        self.EnableChan=[self.EnableSMU1.GetValue(),self.EnableSMU2.GetValue(),self.EnableSMU3.GetValue(),self.EnableSMU4.GetValue(),self.EnableVS1.GetValue(),self.EnableVS2.GetValue()]

        Funcs=[val for n, val in enumerate(SMUfuncs) if self.EnableChan[n]]

        if Funcs.count('VAR1') != 1:
            self.ShowMessage('Invalid Var1', True)
            return 1

        self.Progress.AppendText('\nSetting Channels, ')

        Comps=[self.SMU1C.GetValue(), self.SMU2C.GetValue(), self.SMU3C.GetValue(), self.SMU4C.GetValue(), self.VS1C.GetValue(), self.VS2C.GetValue()]
        
        self.HP.DisableAll()
        if self.EnableSMU1.GetValue(): self.HP.SetSMU("SMU1", self.SMU1V.GetValue(), self.SMU1I.GetValue(), self.SMU1M.GetValue(), self.SMU1F.GetValue(), self.SMU1C.GetValue())
        if self.EnableSMU2.GetValue(): self.HP.SetSMU("SMU2", self.SMU2V.GetValue(), self.SMU2I.GetValue(), self.SMU2M.GetValue(), self.SMU2F.GetValue(), self.SMU2C.GetValue())
        if self.EnableSMU3.GetValue(): self.HP.SetSMU("SMU3", self.SMU3V.GetValue(), self.SMU3I.GetValue(), self.SMU3M.GetValue(), self.SMU3F.GetValue(), self.SMU3C.GetValue())
        if self.EnableSMU4.GetValue(): self.HP.SetSMU("SMU4", self.SMU4V.GetValue(), self.SMU4I.GetValue(), self.SMU4M.GetValue(), self.SMU4F.GetValue(), self.SMU4C.GetValue())
        if self.EnableVS1.GetValue(): self.HP.SetVSMU("VSU1", self.VS1V.GetValue(), self.VS1F.GetValue(), self.VS1C.GetValue())
        if self.EnableVS2.GetValue(): self.HP.SetVSMU("VSU2", self.VS2V.GetValue(), self.VS2F.GetValue(), self.VS2C.GetValue())
        self.HP.SetVSMU("VMU1", "VMU1")
        self.HP.SetVSMU("VMU2", "VMU2")
        time.sleep(0.5)
        
        ########### Setting Vars
        
        self.Progress.AppendText('Vars, ')
        
        if self.CheckVar1() != 1:
            data_variables=self.CheckVar1()
            
        else:
            self.ShowMessage("Invalid Var1", True)
            return 1
        
        self.HP.SetVar("VAR1", "V", ETF(self.VAR1Start.GetValue()), ETF(self.VAR1Stop.GetValue()), ETF(self.VAR1Step.GetValue()), ETF(Comps[Funcs.index('VAR1')]))
        
        if "VAR2" in Funcs:
            self.HP.SetVar("VAR2", "V", ETF(self.VAR2Start.GetValue()), ETF(self.VAR2Stop.GetValue()), ETF(self.VAR2Step.GetValue()))

        if "VARD" in Funcs:
            self.HP.SetVar("VARD", "V", ETF(self.VARDRat.GetValue()), ETF(self.VARDOff.GetValue()))

        ########### Setting Axis
        self.Progress.AppendText('Axis')

        self.HP.SetAxis("X", self.X1.GetValue(), 'LIN', ETF(self.VAR1Start.GetValue()), ETF(self.VAR1Stop.GetValue()))
        
        self.YAxis=[self.Y1.GetValue()]
        scale='LIN'
        if 'log' in self.YAxis[0]:
            scale='LOG'
            self.YAxis[0]=YAxis[0].split('log')[1].strip('( )') # type: ignore
        
        self.HP.SetAxis("Y1", self.YAxis[0], scale, ETF(self.Y1Min.GetValue()), ETF(self.Y1Max.GetValue()))

        if self.Y1.GetValue() not in data_variables:
            data_variables += [self.Y1.GetValue()]
        
        if self.Y2.GetValue():
            self.YAxis+=[self.Y2.GetValue()]
            scale='LIN'
            if 'log' in self.YAxis[1]:
                scale='LOG'
                self.YAxis[1]=YAxis[1].split('log')[1].strip('( )') # type: ignore
                
            if not (self.Y2Min.GetValue() and self.Y2Max.GetValue()):
                self.Y2Min.SetValue('0')
                self.Y2Max.SetValue('1')
            
            self.HP.SetAxis("Y2", self.YAxis[1], scale, ETF(self.Y2Min.GetValue()), ETF(self.Y2Max.GetValue()))
            if self.Y2.GetValue() not in data_variables:
                data_variables += [self.Y2.GetValue()]
        
        if self.Traces.GetValue() and 'Unavailable' not in self.Traces.GetValue():
            for trace in self.Traces.GetValue().split(','):
                trace=trace.strip(' ')
                if trace not in data_variables:
                    data_variables+=[trace]
        print(data_variables)
        data_variables=data_variables[:2]+sorted(data_variables[2:])
        print(data_variables)

        self.HP.save_list(data_variables)

        if self.ufunc.GetValue():
            for function in self.ufunc.GetValue().split(','):
                self.HP.UFUNC(function.strip(' '))
        
        if config['Window'].getboolean('Debug'):
            print("\nTraces: ["+','.join(data_variables)+']')
            print(self.HP.Var2)
        self.Progress.AppendText('\nConfig done')
        
        self.HP.term='GP'
        
        return 0
        
    def Measure(self):
        self.Progress.AppendText('\nMeasurement started!\n...')
        try:
            self.HP.SetIntTime(self.IntTimeBox.GetValue())
            print('a')
            ReturnFlag = self.HP.SingleSave(self.SaveFilePath.GetValue(), timeout=1800)
        except:
            #ReturnFlag="No instrument\nSend config to open connection"
            if self.ShowMessage(f'Error: {ReturnFlag}', True): raise Exception(ReturnFlag)

        self.Progress.AppendText('\nMeasurement Done!')
        
        if os.path.isfile(ReturnFlag):
            self.img_path.SetLabel(ReturnFlag)
            self.RefreshImg(Plot(ReturnFlag, self.X1.GetValue(), self.YAxis, sizex=550))
            return ReturnFlag
        
        if self.ShowMessage(f'Error: {ReturnFlag}', True): raise Exception(ReturnFlag)
        
    def AxisSet(self, event):
        self.X1Min.SetValue(self.VAR1Start.GetValue())
        self.X1Max.SetValue(self.VAR1Stop.GetValue())
        
    def SetSizers(self, event):
        for sizer in self.sizers:
            children=sizer.GetChildren()
            state=children[len(children)-1].GetWindow().GetValue()
            for n, child in enumerate(children):
                if n==5:break
                child.GetWindow().Enable(state)
        self.VS1I.Disable()
        self.VS2I.Disable()
        self.VS1M.Disable()
        self.VS2M.Disable()

    def CheckVar1(self):
        
        for n, SMU in enumerate(self.sizers):
            if SMU.GetChildren()[3].GetWindow().GetValue()=='VAR1' and self.EnableChan[n]:
                if SMU.GetChildren()[2].GetWindow().GetValue()=='V':
                    return [SMU.GetChildren()[0].GetWindow().GetValue(), SMU.GetChildren()[1].GetWindow().GetValue()]
                elif SMU.GetChildren()[2].GetWindow().GetValue()=='I':
                    return [SMU.GetChildren()[1].GetWindow().GetValue(), SMU.GetChildren()[0].GetWindow().GetValue()]
                else:
                    return 1
    
    def ScriptMenu(self, event):
        CurrScr=configparser.ConfigParser()
        if self.ScriptBox.GetValue() == 'Script:':
            return 0
            ############### Saving Subroutine #################
        if self.ScriptBox.GetValue() == 'Save':
            CurrScr[self.NameBox.GetValue()]={}
            for child in self.GetChildren():
                if 'sv_' in child.GetName():
                    CurrScr[self.NameBox.GetValue()][child.GetName()]=str(child.GetValue())
            dialog = wx.FileDialog(None, "Choose a script:", defaultDir="./scripts", wildcard = "Scripts (*.ini)|*.ini", style=wx.DD_DEFAULT_STYLE)
            if dialog.ShowModal() == wx.ID_OK:
                with open(dialog.GetPath(), 'w') as configfile:
                    CurrScr.write(configfile)
            return 0
            ############### Loading Subroutine #################
        if self.ScriptBox.GetValue() == 'Open':
            
            dialog = wx.FileDialog(None, "Choose a script:", defaultDir="./scripts", style=wx.DD_DEFAULT_STYLE)
            if dialog.ShowModal() == wx.ID_OK:
                CurrScr.read(dialog.GetPath())
                CurrScr=CurrScr[CurrScr.sections()[0]]
        else:
            CurrScr=scripts[self.ScriptBox.GetValue()]
            self.NameBox.SetValue(self.ScriptBox.GetValue())

            ############### Placing Subroutine #################
        for child in self.GetChildren():
            if 'sv_' in child.GetName():
                if 'en' in child.GetName() or 'cb' in child.GetName():
                    child.SetValue(CurrScr.getboolean(child.GetName()))
                else:
                    child.SetValue(CurrScr[child.GetName()])
            self.SetSizers(True)
        self.ScriptBox.SetValue('Script:')
