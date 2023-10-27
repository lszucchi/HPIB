import pyvisa
import time
import string
import numpy as np
import pandas as pd
import os
import datetime
import matplotlib.pyplot as plt

#from INOSerial import *

########## Tabelas para intruções HPIB ###########

striplc = str.maketrans('', '', string.ascii_lowercase)

Measurements=['0', 'Single', 'Append', 'Stop']
Modelist=['0', 'V', 'I', 'COMM']
Funclist=['0', 'VAR1', 'VAR2', 'CONS', 'VARD']
Varlist=['0', 'R', 'P']
Intlist=['0', 'SHOR', 'MED', 'LONG']
Scalelist=['0', 'LIN', 'LOG']

ID='ID'
VD='VD'
VS='VS'
VG='VG'
VB='VB'

current='I'
voltage='V'


## Classe genérica HP com código compartilhado

class HP:

    def __init__(self, addr, read_termination = '\n', write_termination = '\n', timeout=None, debug=False):

        self.analyzer_mode="SWEEP"
        self.term="0"
        self.read_termination=read_termination
        self.timeout=timeout
        self.debug=debug
        
        self.Stop_flag = False
        self.VarComp=np.array(['','',''])
        self.Var2Name='Var2'
        self.Var2=None
        
        if not debug:
            self.rm = pyvisa.ResourceManager()
            self.inst = self.rm.open_resource(addr)
            self.inst.timeout=self.timeout


    def beep(self):
        if '4155' in self.ask("*IDN?"): 
            return 0
        else: raise Exception("Comm lost")
        
    def ask(self, msg):
        if self.debug: 
            print(msg)
            return "HP4155 query response debug"
        return self.inst.query(msg).strip(self.read_termination)
    
    def write(self, msg):
        if self.debug: return print(msg)
        return self.inst.write(msg)

    def SingleSave(self, path=".", timeout=2):
        if self.term=="0": return "Parameters not set"
        
        self.measure()
        
        Poll=self.PollDR(1, 1, timeout)
        
        if Poll:
            return "Operation stopped or timeout"
        
        df=self.get_data()
        
        try:
            _, ext = os.path.splitext(path)
            if ext != ".csv":
                path = path +'/'+ self.term + '-' + datetime.datetime.now().strftime("%y%m%d %H%M%S") + ".csv"
        except:
            return "Invalid Path"
        try: df.to_csv(path, index=False)
        except: return "Unable to write CSV"
        
        return path
    
    def SetCap(self, VStart, VStop, VStep, Compliance):
        self.DisableAll()
        
        self.SetSMU('SMU1', 'V', 'I', 'V', Func='VAR1')
        self.SetVSMU('VMU1', 'C')
        self.SetVar('VAR1', 'V', VStart, VStop, VStep, Comp=ETF(Compliance))
        

        self.SetAxis('X', 'V', 'LIN', VStart, VStop)
        self.SetAxis('Y1', 'C', 'LIN', 0, 2)
        self.SetAxis('Y2', 'I', 'LIN', 0, 1e-3)

        self.save_list(['V', 'C', 'I'])
        self.beep()

        self.term='CV'
        
        print("Set " + self.term)
        return 0

    def SetVDS(self, dict):
        self.SetVds(dict['VDstart'], dict['VDstop'], dict['VDstep'], dict['VGstart'], dict['VGstop'], dict['VGstep'], dict['Compliance'])
    
    def SetVds(self, VdStart, VdStop, VdStep, VgStart, VgStop, VgStep, Comp=1e-3, ptype=False):
        
        if ptype:
                VdStart=-VdStart
                VdStop=-VdStop
                VdStep=-VdStep
                VgStart=-VgStart
                VgStop=-VgStop
                VgStep=-VgStep

        print(VdStart, VdStop, VdStep, VgStart, VgStop, VgStep)

        self.DisableAll()
        
        self.SetSMU('SMU1', 'VS', 'IS', 'COMM', 'CONS')
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'VAR1', Comp=Comp)
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR2', Comp=Comp)
        self.SetSMU('SMU4', 'VB', 'IB', 'COMM', 'CONS')
        self.SetVar('VAR1', 'V', VdStart, VdStop, VdStep)
        self.SetVar('VAR2', 'V', VgStart, VgStop, VgStep)
        time.sleep(0.5)
        self.SetAxis('X', 'VD', 'LIN', VdStart, VdStop)
        self.SetAxis('Y1', 'ID', 'LIN', 0, 1e-3)

        self.save_list(['VD', 'ID'])
        self.beep()
        
        self.term='IdxVds'
        
        print("Set " + self.term)
        return 0

    def SetVGS(self, dict):
        self.SetVgs(dict['VGstart'], dict['VGstop'], dict['VGstep'], dict['VD'], dict['Compliance'])

    def SetVgs(self, VgStart, VgStop, VgStep, VdValue=0.1, Comp=1e-3, VdSweep=False, ptype=False, sat=False):
        
        if ptype:
                    VdValue=-VdValue
                    VgStart=-VgStart
                    VgStop=-VgStop
                    VgStep=-VgStep
        print(VgStart, VgStop, VgStep, VdValue, Comp)

        self.DisableAll()
        
        self.SetSMU('SMU1', 'VS', 'IS', 'COMM', 'CONS')
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR1', Comp=Comp)
        self.SetSMU('SMU4', 'VB', 'IB', 'COMM', 'CONS')

        if VdSweep:
            self.SetSMU('SMU2', 'VD', 'ID', 'V', 'VARD')
            self.SetVar('VARD', 1, 0)
        else:
            self.SetSMU('SMU2', 'VD', 'ID', 'V', 'CONS', Value=VdValue, Comp=Comp)
            self.Var2=[f"{VdValue}"]

        self.SetVar('VAR1', 'V', VgStart, VgStop, VgStep, 1e-3)

        self.SetAxis('X', 'VG', 'LIN', VgStart, VgStop)
        self.SetAxis('Y1', 'ID', 'LIN', 0, 1e-3)

        self.save_list(['VG', 'ID'])
        self.beep()
        
        if sat:
                    self.term='IdxVgs Sat'
        else:
                    self.term='IdxVgs'
                    
        print("Set " + self.term)
        
        return 0

    def SetVP(self, dict):
        self.SetVp(dict['Ib'], dict['VGstart'], dict['VGstop'], dict['VGstep'], dict['Compliance'])
        
    def SetVp(self, Ib, VgStart, VgStop, VgStep, Comp=1.5, ptype=False):
        Ib=ETF(Ib)
        Comp=ETF(Comp)
        
        if ptype:
                VgStart=-VgStart
                VgStop=-VgStop
                VgStep=-VgStep
                
        print(Ib, VgStart, VgStop, VgStep)

        self.DisableAll()
        
        self.SetSMU('SMU1', 'VS', 'IS', 'I', 'CONS', Comp=Comp, Value=Ib)
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'VARD')
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR1')
        self.SetSMU('SMU4', 'VB', 'IB')
        
        self.SetVar('VAR1', 'V', VgStart, VgStop, VgStep)
        self.SetVar('VARD', 'V', 1, 0)
        self.Var2=Ib

        self.SetAxis('X', 'VD', 'LIN', VgStart, VgStop)
        self.SetAxis('Y1', 'VS', 'LIN', 0, 1)

        self.save_list(['VG', 'VS'])
        self.beep()

        self.term='VpxVgs'
        
        print("Set " + self.term)
        return 0

    def SetEXIB(self, dict):
        self.SetEx_Ib(dict['VSstart'], dict['VSstop'], dict['VSstep'], dict['VGstart'], dict['VGstop'], dict['VGstep'],  dict['Compliance'])
    
    def SetEx_Ib(self, VsStart, VsStop, VsStep, VgStart, VgStop, VgStep, Comp=1e-3, ptype=False):
        Comp=ETF(Comp)
        
        if ptype:
                VsStart=-VsStart
                VsStop=-VsStop
                VsStep=-VsStep

        print(VsStart, VsStop, VsStep)

        self.DisableAll()
        
        self.SetSMU('SMU1', 'VS', 'IS', 'V', 'VAR1', Comp=Comp)
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'CONS', Value=VsStop)
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR2', Comp=Comp)
        self.SetSMU('SMU4', 'VB', 'IB', 'COMM')

        
        self.SetVar('VAR1', 'V', VsStart, VsStop, VsStep)
        self.SetVar('VAR2', 'V', VgStart, VgStop, VgStep)

        self.SetAxis('X', 'VS', 'LIN', VsStart, VsStop)
        self.SetAxis('Y1', 'ID', 'LIN', 0, 1)

        self.save_list(['VS', 'ID'])
        self.beep()

        self.term='Ex_Ib'
        
        print("Set " + self.term)
        return 0

    def SetDiode(self, VfStart, VfStop, VfStep):
        
        self.DisableAll()
        
        self.SetSMU('SMU4', 'VB', 'IF', 'V', 'VAR1', Comp=2e-3)
        self.SetSMU('SMU1', 'VS', 'IS', 'V', 'CONS', Comp=1e-3)
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'CONS', Comp=1e-3)

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep)
        self.UFUNC("VF=-VB")
        
        self.SetAxis('X', 'VF', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'IS', 'LIN', 0, 1e-4)
        self.SetAxis('Y2', 'ID', 'LIN', 0, 1e-4)

        self.save_list(['VF', 'IS', 'ID'])
        self.beep()

        self.term="Diode"
        print("Set " + self.term)

        return 0

    def Set4P(self, IStart, IStop, Points):

        print(IStart, IStop, Points)
        
        self.DisableAll()
        
        self.SetSMU('SMU1', 'V1', 'I1')
        self.SetSMU('SMU2', 'V2', 'I2', 'I', 'VAR1')
        self.SetVSMU('VMU1', 'V3')
        self.SetVSMU('VMU2', 'V4')
        self.SetVar('VAR1', 'I', IStart, IStop, (IStop-IStart)/(Points-1))
        self.UFUNC('V=VMU1-VMU2')

        self.SetAxis('X', 'V')
        self.SetAxis('Y1', 'I1')
        
        self.save_list(['I1', 'V'])
        self.beep()
        
        self.term="4P"
        
        print("Set " + self.term)

        return 0

def ETF(value):
    try: return float(value)
    except:
        pass
    exp=value[len(value)-1]
    try: value=np.around(float(value[:len(value)-1]), 1)
    except:
        return "Invalid mantissa"

    match exp:
        case 'P':
            return str(value)+'e15'
        case 'T':
            return str(value)+'e12'
        case 'G':
            return str(value)+'e9'
        case 'M':
            return str(value)+'e6'
        case 'k':
            return str(value)+'e3'
        
        #0#
        
        case 'm':
            return str(value)+'e-3'
        case 'u':
            return str(value)+'e-6'
        case 'n':
            return str(value)+'e-9'
        case 'p':
            return str(value)+'e-12'
        case 'f':
            return str(value)+'e-15'
        
    return "Invalid expoent"

def DebugOut(inst, varlist, Var2):
    inst.Var2=Var2
    inst.data_variables=varlist
    inst.Var2Name='Var2'
    return inst.get_data()
