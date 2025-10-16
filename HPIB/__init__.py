import pyvisa, string
import numpy as np
import pandas as pd
from datetime import datetime
from os.path import splitext
from HPIB.HPT import ETF, frange
from time import sleep

########## Tabelas para intruções HPIB ###########

striplc = str.maketrans('', '', string.ascii_lowercase)

Measurements=['0', 'Single', 'Append', 'Stop']
Modelist=['0', 'V', 'I', 'COMM']
Funclist=['0', 'VAR1', 'VAR2', 'CONS', 'VARD']
Varlist=['0', 'R', 'P']
Intlist=['0', 'SHOR', 'MED', 'LONG']
Scalelist=['0', 'LIN', 'LOG']
S="SMU1"
D="SMU2"
G="SMU3"
B="SMU4"

## Classe genérica HP com código compartilhado

class HP:

    def __init__(self, addr, read_termination = '\n', write_termination = '\n', timeout=5000, debug=False):

        self.term=""
        self.read_termination=read_termination
        self.timeout=timeout
        self.debug=debug
        
        self.Stop_flag = False
        self.VarComp=np.array(['','',''])
        self.Var2Name='Var2'
        self.Var2=[None]
        
        if not debug:
            self.rm = pyvisa.ResourceManager()
            self.inst = self.rm.open_resource(addr)
            self.inst.timeout=self.timeout
            self.write(":STAT:MEAS:ENAB 8")
            self.Mode="SWEEP"
            print(self.IDN)

    @property
    def IDN(self):
        return self.ask("*IDN?")
    
    def beep(self):
        if '4155' in self.ask("*IDN?"): 
            return 0
        else:
            return "Comm Lost"
        
    def ask(self, msg):
        if self.debug: 
            print(msg)
            return "HP4155 query response debug"
        return self.inst.query(msg).strip(self.read_termination)
    
    def write(self, msg):
        if self.debug: return print(msg)
        self.inst.write(msg)
        return 1

    def close(self):
        self.inst.close()

    def SingleSave(self, path=None, timeout=2, real=False):
        if self.term=="0": return "Parameters not set"
        
        print(f"Measuring {self.term} ", end='')
        self.measure()
        
        Poll=self.PollDR(1, 1, timeout)

        ######################## Importante
        
        if Poll:
            return "Operation stopped or timeout"
        if real:
            df=self.get_realdata()
        else:
            df=self.get_data()

        #####################################
        
        try:
            _, ext = splitext(path)
            if ext != ".csv":
                path = f"{path}/{self.term}-{datetime.now().strftime('%y%m%d %H%M%S')}.csv"
        except:
            return "Invalid Path"
        
        try: df.to_csv(path, float_format='%+.6E')
        
        except: return "Unable to write CSV"
        
        return path

    ##### Poll DataReady == state, a cada delay em s, no máximo de maxpoll ciclos. Retorna 1 se chegar ao máximo de ciclos.
    def PollDR(self, state, delay=1, maxpoll=2):
        if self.debug:
            sleep(2*delay)
            print("Debug DataReady")
            return 0
        start=datetime.now()  
        for i in range(60*maxpoll):
            delta=datetime.now()-start
            freq=5
            print(f"\rMeasuring {self.term} {str(delta).split('.')[0]} {''.join(['.' if k<=delta.seconds%freq else ' ' for k in range(freq)])}", end='')

            sleep(delay)
            if self.Stop_flag:
                print('')
                return 1
            if self.GetDR()==state:
                print(f"\rDone {self.term}. Duration: {str(delta).split('.')[0]}                                       ")
                return 0
        print('')
        return 1

    ##################### Sweep Mode Setups

    def SetVgs(self, VgStart, VgStop, VgStep, VdValue=0.025, Comp=1e-3, VdSweep=False, ptype=False, sat=False):
        
        if ptype:
                    VdValue=-VdValue
                    VgStart=-VgStart
                    VgStop=-VgStop
                    VgStep=-VgStep

        self.DisableAll()
        
        self.SetSMU('SMU1', 'Vs', 'Is', 'COMM', 'CONS')
        self.SetSMU('SMU3', 'Vg', 'Ig', 'V', 'VAR1')
        self.SetSMU('SMU4', 'Vb', 'Ib', 'COMM', 'CONS')

        if VdSweep:
            self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'VARD')
            self.SetVar('VARD', 1, 0)
        else:
            self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'CONS', Value=VdValue, Comp=Comp)
            self.Var2=[f"{VdValue}"]
            self.Var2Name="Vds"

        self.SetVar('VAR1', 'V', VgStart, VgStop, VgStep, Comp=Comp)

        self.SetAxis('X', 'Vg', 'LIN', VgStart, VgStop)
        self.SetAxis('Y1', 'Id', 'LIN', 0, -1e-5 if ptype else 1e-5)

        self.save_list=['Vg', 'Ig', 'Id', 'Is']
        self.beep()
        
        if sat:
                    self.term='IdxVgs Sat'
        else:
                    self.term='IdxVgs'
                    
        print(f"Set {self.term}")
        print(f"Vg=({VgStart}, {VgStop}, {VgStep}), Vd={VdValue}, Ilim={Comp}")
        
        return 0
    
    def SetVds(self, VdStart, VdStop, VdStep, VgStart, VgStop, VgStep, Comp=1e-3, ptype=False):
        
        if ptype:
                VdStart=-VdStart
                VdStop=-VdStop
                VdStep=-VdStep
                VgStart=-VgStart
                VgStop=-VgStop
                VgStep=-VgStep

        self.DisableAll()
        
        self.SetSMU('SMU1', 'Vs', 'Is', 'COMM', 'CONS')
        self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'VAR1')
        self.SetSMU('SMU3', 'Vg', 'Ig', 'V', 'VAR2')
        self.SetSMU('SMU4', 'Vb', 'Ib', 'COMM', 'CONS')
        self.SetVar('VAR1', 'V', VdStart, VdStop, VdStep, Comp=Comp)
        self.SetVar('VAR2', 'V', VgStart, VgStop, VgStep, Comp=Comp)
        sleep(0.5)
        self.SetAxis('X', 'Vd', 'LIN', VdStart, VdStop)
        self.SetAxis('Y1', 'Id', 'LIN', 0, -1e-3 if ptype else 1e-3)
        self.Var2Name="Vgs"

        self.save_list=['Vd', 'Id', 'Ig', 'Is', 'Ib']
        self.beep()
        
        self.term='IdxVds'
        
        print(f"Set {self.term}")
        print(f"Vd=({VdStart}, {VdStop}, {VdStep}), Vg=({VgStart}, {VgStop}, {VgStep}), Ilim={Comp}")
        
        return 0
        
    def SetVp(self, Is, VgStart, VgStop, VgStep, Comp=1.5, ptype=False):       
        
        if ptype:
            VgStart=-VgStart
            VgStop=-VgStop
            VgStep=-VgStep
        else:
            Is=-Is
            
        self.DisableAll()
        
        self.SetSMU('SMU3', 'Vg', 'Ig', 'V', 'VAR1')
        self.SetSMU('SMU1', 'Vs', 'Is', 'I', 'CONS', Comp=Comp, Value=format(Is, '.3e'))
        self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'VARD')
        self.SetSMU('SMU4', 'Vb', 'Ib')
        
        self.SetVar('VAR1', 'V', VgStart, VgStop, VgStep)
        self.SetVar('VARD', 'V', 1, 0)
        self.Var2=Is
        self.Var2Name='Is'

        self.SetAxis('X', 'Vd', 'LIN', VgStart, VgStop)
        self.SetAxis('Y1', 'Vs', 'LIN', 0, 1)

        self.save_list=['Vg', 'Ig', 'Vs', 'Id']
        self.beep()

        self.term='VpxVgs'
        
        print(f"Set {self.term}")
        print(f"Is={format(Is, '.3e')}, Vg=({VgStart}, {VgStop}, {VgStep}), Vlim={Comp}")
        
        return 0
    
    def SetEx_Is(self, VsStart, VsStop, VsStep, VgStart, VgStop, VgStep, VdValue, Comp=1e-3, ptype=False):
        
        if ptype:
            VsStart=-VsStart
            VsStop=-VsStop
            VsStep=-VsStep
            VgStart=-VgStart
            VgStop=-VgStop
            VgStep=-VgStep
            VdValue=-VdValue

        self.DisableAll()
        
        self.SetSMU('SMU1', 'Vs', 'Is', 'V', 'VAR1', Comp=Comp)
        self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'CONS', Value=VdValue, Comp=Comp)
        self.SetSMU('SMU3', 'Vg', 'Ig', 'V', 'VAR2', Comp=Comp)
        self.SetSMU('SMU4', 'Vb', 'Ib', 'COMM')

        
        self.SetVar('VAR1', 'V', VsStart, VsStop, VsStep)
        self.SetVar('VAR2', 'V', VgStart, VgStop, VgStep)

        self.SetAxis('X', 'Vs', 'LIN', VsStart, VsStop)
        self.SetAxis('Y1', 'Id', 'LIN', 0, 1)

        self.save_list=['Vs', 'Id', 'Ig']
        
        self.beep()

        self.term='Ex_Is'
        
        print(f"Set {self.term}")
        print(f"Vs=({VsStart}, {VsStop}, {VsStep}), Vg=({VgStart}, {VgStop}, {VgStep}), Vd={VdValue}")
        
        return 0

    ############ Diode Measurements

    def SetDiode(self, VfStart, VfStop, VfStep, Comp=1.2e-3):
        self.Var2=None
        self.Var2Name=None
        VfStart=-VfStart
        VfStop=-VfStop
        VfStep=-VfStep
        
        self.DisableAll()
        
        self.SetSMU('SMU4', 'Vb', 'Ib', 'V', 'VAR1', Comp=10e-3)
        self.SetSMU('SMU1', 'Vs', 'Is', 'V', 'CONS', Comp=Comp)
        self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'CONS', Comp=Comp)

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep)
        self.UFUNC("Vf=-Vb")
        
        self.SetAxis('X', 'Vf', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'Is', 'LIN', -1e-3, 1e-3)
        self.SetAxis('Y2', 'Id', 'LIN', -1e-3, 1e-3)

        self.save_list=['Vf', 'Is', 'Id']
        self.beep()

        self.term="Diode"
        
        print(f"Set {self.term}")
        print(f"Vf=({VfStart}, {VfStop})")

        return 0

    def SingleDiode(self, VfStart, VfStop, VfStep, SMUP='SMU2', SMUN='SMU4', Comp=2e-3):
        self.Var2=None
        self.Var2Name=None
        self.DisableAll()
        
        self.SetSMU(SMUN, 'Vb', 'Ib', 'COMM', Comp=Comp)
        self.SetSMU(SMUP, 'Vf', 'If', 'V', 'VAR1', Comp=Comp)

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep, Comp=Comp)
        
        self.SetAxis('X', 'Vf', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'If', 'LIN', -Comp, Comp)

        self.save_list=['Vf', 'If']
        self.beep()

        self.term="Diode"
        
        print(f"Diode=({VfStart}, {VfStop}, {VfStep})")

        return 0

    def Diode4P(self, VfStart, VfStop, VfStep, Im='SMU1', Ip='SMU2', Vm='SMU3', Vp='SMU4', Comp=2e-3):
        self.Var2=None
        self.Var2Name=None
        self.DisableAll()
        
        self.SetSMU(Im, 'Vb', 'Ib', 'COMM', Comp=Comp)
        self.SetSMU(Ip, 'Vf', 'If', 'V', 'VAR1', Comp=Comp)
        self.SetSMU(Vp, 'Vp', 'Ip', 'I', 'CONS', Value=0, Comp=5)
        self.SetSMU(Vm, 'Vm', 'Im', 'I', 'CONS', Value=0, Comp=5)
        self.UFUNC("V=Vp-Vm")

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep, Comp=Comp)
        
        self.SetAxis('X', 'V', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'If', 'LIN', -Comp, Comp)

        self.save_list=['Vf', 'V', 'If']
        self.beep()

        self.term="Diode4P"
        
        print(f"Diode=({VfStart}, {VfStop}, {VfStep})")

        return 0

    ############# 2 point IxV Measurement

    def Set2P(self, Istart, Istop, Points, SMUP='SMU2', SMUN='SMU1', Comp=1.5):
        self.DisableAll()
        
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU(SMUN, 'Vb', 'Ib')
        self.SetSMU(SMUP, 'Vf', 'If', 'I', 'VAR1')
        self.SetVar('VAR1', 'I', Istart, Istop, (Istop-Istart)/(Points), Comp=Comp)
        
        self.SetAxis('Y1', 'If', 1, Istart, Istop)
        self.SetAxis('X', 'Vf', 1, -Comp, Comp)

        self.save_list=['Vf', 'If']
        self.beep()
        
        self.term=f"2P - {SMUN[-1]}{SMUP[-1]}"
        
        print(f"Set {self.term}")
        print(f"I=({Istart}, {Istop}), {Points} Points")

    ############# Current controlled (VxI) 4-point measurements 
    
    def Set4P(self, Istart, Istop, Points, Ip='SMU2', Im='SMU1', Vp='VMU2', Vm='VMU1', Comp=1):        
        self.DisableAll()
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU(Im, 'V1', 'I1')
        self.SetSMU(Ip, 'V2', 'I2', 'I', 'VAR1')
        self.SetVSMU(Vm, 'V3')
        self.SetVSMU(Vp, 'V4')
        Istep=(Istop-Istart)/(Points-1)
        self.SetVar('VAR1', 'I', Istart, Istop, Istep, Comp=Comp)
        
        self.UFUNC('Vf=V3-V4')
        self.UFUNC('If=-I1')

        self.SetAxis('X', 'If', 1, Istart, Istop)
        self.SetAxis('Y1', 'Vf', 1, -1e-2, 1e-2)
        
        self.save_list=['I2', 'If', 'Vf']
        self.beep()
        
        self.term="4P"
        
        print(f"Set {self.term}")
        print(f"I=({Istart}, {Istop}), {Points} Points")

        return 0

    def Set4PSMU(self, Istart, Istop, Points, Im='SMU1', Ip='SMU2', Vm='SMU3', Vp='SMU4', Comp=2, CompI=1e-3):        
        self.DisableAll()
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU(Im, 'V1', 'I1')
        self.SetSMU(Ip, 'V2', 'I2', 'I', 'VAR1', Comp=Comp)
        self.SetSMU(Vm, 'V3', 'I3', 'I', 'CONS', Value=0, Comp=Comp)
        self.SetSMU(Vp, 'V4', 'I4', 'I', 'CONS', Value=0, Comp=Comp)
        self.SetVar('VAR1', 'I', Istart, Istop, (Istop-Istart)/(Points))

        self.UFUNC('Vf=V4-V3')
        self.UFUNC('If=-I1')

        self.SetAxis('X', 'Vf')
        self.SetAxis('Y1', 'If', 'LIN', 0, 10e-3)
        
        self.save_list=['I2', 'If', 'Vf']
        self.beep()
        
        self.term="4P"
        
        print(f"Set {self.term}")
        print(f"{Mode}=({Istart}, {Istop}), {Points} Points")

        return 0
        
    ########### CV Measurement
    
    def SetCV(self, Vstart, Vstop, Vstep, Comp):
        self.Var2=None
        self.Var2Name=None
        self.DisableAll()
        
        self.SetSMU('SMU1', 'V', 'I', 'V', Func='VAR1')
        self.SetVsMU('VMU1', 'C')
        self.SetVar('VAR1', 'V', Vstart, Vstop, Vstep, Comp=ETF(Comp))
        

        self.SetAxis('X', 'V', 'LIN', Vstart, Vstop)
        self.SetAxis('Y1', 'C', 'LIN', 0, 2)
        self.SetAxis('Y2', 'I', 'LIN', 0, 1e-3)

        self.save_list=['V', 'C', 'I']
        self.beep()

        self.term='CV'
        
        print(f"Set {self.term}")
        print(f"V=({Vstart}, {Vstop}, {Vstep}), Ilim={Comp})")
        
        return 0

    ############ Dict Wrappers
    
    def SetVGS(self, dict, ptype):
        self.SetVgs(dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], ETF(dict['Vd']), ETF(dict['Compliance']), ptype=ptype)
        
    def SetVDS(self, dict, ptype):
        self.SetVds(dict['Vdstart'], dict['Vdstop'], dict['Vdstep'], dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], ETF(dict['Compliance']), ptype)

    def SetVP(self, dict, ptype):
        self.SetVp(dict['Is'], dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], dict['Compliance'], ptype)
        
    def SetExIs(self, dict, ptype):
        self.SetEx_Is(dict['Vsstart'], dict['Vsstop'], dict['Vsstep'], dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], dict['Vdvalue'], dict['Compliance'], ptype)

class HP4155(HP):

    ############# Initial Defs
    
    def reset(self):
        self.write("*RST")
        self.write(":STAT:MEAS:ENAB 8")
        self.write(":PAGE:MEAS:MSET:ITIM MED")
        self.write(":PAGE:MEAS:MSET:ITIM:LONG 4")
        self.write(":PAGE:MEAS:DEL 1e-3")
        self.write(":PAGE:MEAS:HTIM 1e-3")
        return 0


    ############# Properties
        
    @property
    def State(self):
        return self.ask(":PAGE:SCONtrol:STAT?")
    
    @property
    def Mode(self):
        return self.ask(":PAGE:CHAN:MODE?")
    
    @Mode.setter
    def Mode(self, Value):
        if Value.upper() not in ['SWE', 'SWEEP', 'SAMP', 'SAMPLING']:
            raise ValueError("Invalid Mode")
        self.write(f":PAGE:CHAN:MODE {Value.upper()}")
    
    @property
    def IntTime(self):
        return self.ask(":PAGE:MEAS:MSET:ITIM?")
        
    @IntTime.setter
    def IntTime(self, Value="MEDium"):
        Value=Value.translate(striplc)
        
        if Value not in ['SHOR', 'MED', 'LONG']:
            raise ValueError("Invalid IntTime")
            
        self.write(f":PAGE:MEAS:MSET:ITIM {Value}")
    
    @property
    def LongNPLC(self):
        try:
            return float(self.ask(":PAGE:MEAS:MSET:ITIM:LONG?"))
        except:
            raise RuntimeError("Invalid response on Long NPLC query")
    
    @LongNPLC.setter
    def LongNPLC(self, Value=None):
        if type(Value) != int:
            raise ValueError("Long NPLC must be an integer")
        while np.abs(self.LongNPLC - Value) > 0.1:
            self.write(f":PAGE:MEAS:MSET:ITIM:LONG {Value}")
            sleep(1)
    
    @property
    def HoldTime(self):
        if self.Mode=='SAMP':
            return self.ask(":PAGE:MEAS:SAMP:HTIMe?")
        return self.ask(":PAGE:MEAS:HTIM?")
    
    @HoldTime.setter
    def HoldTime(self, Value=1):
        if Value < 0 or Value > 650:
            raise ValueError("Invalid Hold Time")
        if self.Mode=='SWE':
            self.write(f":PAGE:MEAS:HTIM {Value}")
        elif self.Mode=='SAMP':
            self.write(f":PAGE:MEAS:SAMP:HTIM {Value}")
    
    @property
    def DelayTime(self):
        return float(self.ask(":PAGE:MEAS:DEL?"))
    
    @DelayTime.setter
    def DelayTime(self, value):
        self.write(f":PAGE:MEAS:DEL {value}")
    
    @property
    def StopCond(self):
        return self.ask(":PAGE:MEAS:SST?")
        
    @StopCond.setter
    def StopCond(self, Condition="OFF"):
        if Condition not in ['ABN', 'COMP', 'OFF']:
            raise ValueError("Invalid condition")
        self.write(f":PAGE:MEAS:SST {Condition}")
        
    @property
    def Interval(self):
        if self.Mode != "SAMP":
            raise RuntimeError("Must be in sampling mode")
        return self.ask(":PAGE:MEAS:SAMP:IINT:")
    
    @Interval.setter
    def Interval(self, value):
        if self.Mode != "SAMP":
            raise RuntimeError("Must be in sampling mode")
        if value > 60e-6 and value < 65.535:
            self.write(f":PAGE:MEAS:SAMP:IINT {value}")
            return 0
        raise ValueError("Invalid interval (must be between 60e-6 and 65.535 seconds)")
    @property
    def SPoints(self):
        if self.Mode != "SAMP":
            raise RuntimeError("Must be in sampling mode")
        return self.ask(":PAGE:MEAS:SAMP:POIN?") 
    
    @SPoints.setter
    def SPoints(self, value):
        if self.Mode != "SAMP":
            raise RuntimeError("Must be in sampling mode")
        if value >= 1 and value <= 10001:
            self.write(f":PAGE:MEAS:SAMP:POIN {value}")
            return 0
        raise ValueError("Invalid sampling (must be between 1 and 10001)")
    
    @property
    def SPeriod(self):
        if self.Mode != "SAMP":
            raise RuntimeError("Must be in sampling mode")
        return self.ask(":PAGE:MEASure:SAMPling:PER?")
    
    @SPeriod.setter
    def SPeriod(self, value):
        if self.Mode != "SAMP": 
            raise RuntimeError("Must be in sampling mode")
        if value == "INF":
            self.write(f":PAGE:MEAS:SAMP:PER {value}")
            return 0
        if value >= 60e-6 and value <= 1e11:
            self.write(f":PAGE:MEAS:SAMP:PER {value}")
            return 0
        raise ValueError("Invalid period (must be between 60e-6 and 1e11 or 'INF')")
        
    @property
    def save_list(self):
        if self.debug: return self.save_debug
        return self.ask(":PAGE:DISP:LIST?").split(',')
    
    @save_list.setter
    def save_list(self, trace_list):
        if self.debug: 
            self.save_debug=trace_list
            return 0
        self.write(":PAGE:DISP:MODE LIST")
        self.write(":PAGE:DISP:LIST:DEL:ALL")
        
        if not isinstance(trace_list, list):
            raise TypeError('Invalid trace list')
    
        if len(trace_list) > 8:
            raise RuntimeError('Maximum of 8 variables allowed')
            
        for name in trace_list:
                self.write(f":PAGE:DISP:LIST \'{name}\'")
            
        self.write(":PAGE:DISP:MODE GRAP")

    ################ Start\Stop

    def measure(self):
        self.write(":PAGE:SCON:MEAS:SING")
        self.write("*ESE 1")
        self.write("*OPC")
        while(self.GetDR()):
            sleep(0.5)
        return 0

    def stop(self):
        while self.State=="MEAS":
            self.write(":PAGE:SCON:STOP")
        return 0
    
    ################ Measurement Setup
        
    def DisableAll(self):
        self.write(":PAGE:CHAN:ALL:DIS")
        self.beep()
        self.write(":PAGE:DISP:GRAP:Y2:DEL")
        self.beep()
        self.write(":PAGE:CHAN:UFUN:DEL:ALL")
        self.beep()
        return 0

    def SetSMU(self, SMUno, VNAME, INAME, Mode="COMM", Func="CONS", Value=0, Comp="1e-3"):
    
        SMUno=SMUno.upper()
        if SMUno not in ['SMU1', 'SMU2','SMU3','SMU4']:
            raise Exception(f"Invalid SMU: <{SMUno}>")
    
        Mode=Mode.upper()
        if Mode not in ['COMM', 'V', 'I']:
            raise Exception(f"Invalid Mode in {SMUno}: <{Mode}>")
    
        try:
            if Func.upper() not in ['CONS', 'VAR1', 'VAR2', 'VARD']:
                Value=ETF(Func)
                Func='CONS'
        except: raise Exception(f"Invalid Func in {SMUno}: <{Func}>")
                            
        self.write(f":PAGE:CHAN:{SMUno}:VNAME \'{VNAME}\'")
        self.write(f":PAGE:CHAN:{SMUno}:INAME \'{INAME}\'")
        self.write(f":PAGE:CHAN:{SMUno}:MODE {Mode}")
        self.write(f":PAGE:CHAN:{SMUno}:FUNC {Func}")
        
        if Mode == "COMM": return 0
        
        if Func[3] in ['1', '2', 'D']:
            try: self.VarComp[int(Func[len(Func)-1])]=Comp
            except: self.VarComp[0]=Comp
    
            return 0
        
        if Func == "CONS" and self.Mode == "SWE":
            # print(f"{Value}, {Comp}")
            self.write(f":PAGE:MEAS")
            self.beep()
            self.write(f":PAGE:MEAS:CONS:{SMUno} {Value}")
            self.write(f":PAGE:MEAS:CONS:{SMUno}:COMP {Comp}")
            return 0
    
        elif Func == "CONS" and self.Mode == "SAMP":
            self.write(f":PAGE:MEAS:SAMP:CONS:{SMUno} {Value}")
            self.write(f":PAGE:MEAS:SAMP:CONS:{SMUno}:COMP {Comp}")
        return 1
    
    def SetVSMU(self, SMUno, VNAME, Func='CONS', Comp='1e-3'):
        SMUno=SMUno.upper()
        if SMUno not in ['VMU1', 'VMU2','VSU1','VSU2']:
            raise Exception("Invalid VSU or VMU: <{SMUno}>")
            
        self.write(f":PAGE:CHAN:{SMUno}:VNAME \'{VNAME}\'")
        self.write(f":PAGE:CHAN:{SMUno}:MODE V")
        
        Func=Func.upper()
        if Func not in ['CONS', 'VAR1', 'VAR2', 'VARD']:
    
            raise Exception(f"Invalid Func in {SMUno}: <{Func}>")
    
        self.beep()
        
        if "VMU" in SMUno:
            return 0
            
        self.write(f":PAGE:CHAN:{SMUno}:FUNC {Func}")
        if Func[len(Func)-1] in ['1', '2', 'D']:
            try: self.VarComp[int(Func[len(Func)-1])]=Comp
            except: self.VarComp[0]=Comp
    
            return 0
        
        if Func=='CONS':
        #    self.write(f":PAGE:MEAS:CONS:{SMUno} {Value}")
        #    self.write(f":PAGE:MEAS:CONS:{SMUno}:COMP {Comp}")
        #    sleep(0.1)
    
            return 0
        
        return 1
    
    def SetVar(self, VARno, Func, Start, Stop, Step=0, Comp='0.01'):
        Start=float(ETF(Start))
        Stop=float(ETF(Stop))
        Step=float(ETF(Step))
        
        
        VARno=VARno.upper()
        if VARno not in ['VAR1', 'VAR2', 'VARD']:
    
            raise Exception(f"Invalid Var: <{VARno}>")
        
        if VARno=='VAR1' and Step:
            self.write(f":PAGE:MEAS:{VARno}:STAR {Start}")
            self.write(f":PAGE:MEAS:{VARno}:STOP {Stop}")
            self.write(f":PAGE:MEAS:{VARno}:STEP {Step}")
            self.write(f":PAGE:MEAS:{VARno}:COMP {Comp}")
            sleep(0.1)
            self.beep()
            
            return 0
    
        if VARno=='VAR2' and Step:
            self.Var2=frange(Start, Stop, Step)
            Points=1+(Stop-Start)/Step
            self.write(f":PAGE:MEAS:{VARno}:STAR {Start}")
            self.write(f":PAGE:MEAS:{VARno}:STEP {Step}")
            self.write(f":PAGE:MEAS:{VARno}:POINTS {Points}")
            self.write(f":PAGE:MEAS:{VARno}:COMP {Comp}")
            sleep(0.1)
            self.beep()
    
            return 0
    
        if VARno=='VARD' and not Step:
            """ Start = Ratio, Stop=Offset"""
            self.write(f":PAGE:MEAS:VARD:RAT {Start}")
            self.write(f":PAGE:MEAS:VARD:OFFS {Stop}")
            sleep(0.1)
            self.beep()
    
            return 0
        
        return 1
    
    def SetAxis(self, AXIS, NAME, SCALE="LIN", MIN=0, MAX=1):
        self.write(f":PAGE:DISP:GRAP:{AXIS}:NAME \'{NAME}\'")
        self.write(f":PAGE:DISP:GRAP:{AXIS}:SCAL {SCALE}")
        self.write(f":PAGE:DISP:GRAP:{AXIS}:MIN {MIN}")
        self.write(f":PAGE:DISP:GRAP:{AXIS}:MAX {MAX}")
        self.beep()
        return 0
    
    def UFUNC(self, ufunc):
    
        if ufunc[0]=='V':
            mode='V'
        else:
            mode='A'
    
        (NAME, UNIT, EXPRESSION) = (ufunc.split('=')[0], mode, ufunc.split('=')[1])
        
        self.write(f":PAGE:CHAN:UFUN:DEF '{NAME}', '{UNIT}', '{EXPRESSION}'")
        self.beep()
    
        return 0
    
    def DelUFUNC(self):
        self.write(":PAGE:CHANnels:UFUN:DEL:ALL")
    
    def GetDR(self):
        return int(self.ask("*ESR?"))&1
    
    def DataOutput(self, trace):
        if self.debug:
            self.out=self.out/10
    
            return np.column_stack(np.split(self.out, len(self.Var2)))
        
        return np.column_stack(np.split(np.array(self.ask(f":DATA? \'{trace}\'").split(',')), len(self.Var2)))
    
    def RealDataOutput(self, trace, TrigComp):
        if self.debug:
            self.out=self.out/10
    
            return np.column_stack(np.split(self.out, len(self.Var2)))
        out=[x for x in self.inst.query_binary_values(f":DATA? \'{trace}\'", datatype='d', is_big_endian=True) if not np.isnan(x)]
        if TrigComp: out=out[:-1]
        return np.column_stack(np.split(np.array(out), len(self.Var2)))
    
    def get_realdata(self):
        if not (isinstance(self.Var2, list) or isinstance(self.Var2, np.ndarray)):
            self.Var2=[self.Var2]
        TrigComp=0
        
        if self.debug:
            self.out=np.arange(0, 100*len(self.Var2))
            header=self.save_list
            
        elif int(self.ask('*OPC?')):
            header = self.save_list
            
        self.write(":FORM:DATA REAL")
    
        if self.ask(":STAT:MEAS?"):
            TrigComp=1
    
        lastdata=self.RealDataOutput(header[0], TrigComp)
        
        # recursively get data for each variable
        for i, listvar in enumerate(header[1:]):
            lastdata = np.column_stack((lastdata, self.RealDataOutput(listvar, TrigComp)))
        
        header = pd.MultiIndex.from_product([self.save_list,
                                    [f"{str(x)}" for x in self.Var2]],
                                    names=["Trace", f"{self.Var2Name}"])
        
        df = pd.DataFrame(data=lastdata, columns=header)
        self.write(":PAGE:DISP:MODE GRAP")
        self.write(":FORM:DATA ASC")
        
        return df
    
    def get_data(self):
        if not (isinstance(self.Var2, list) or isinstance(self.Var2, np.ndarray)):
            self.Var2=[self.Var2]
            
        if self.debug:
            self.out=np.arange(0, 100*len(self.Var2))
            header=self.save_list
            
        elif int(self.ask('*OPC?')):
            header = self.save_list
            
        self.write(":FORM:DATA ASC")
    
        lastdata=self.DataOutput(header[0])
        
        # recursively get data for each variable
        for i, listvar in enumerate(header[1:]):
            lastdata = np.column_stack((lastdata, self.DataOutput(listvar)))
        
        header = pd.MultiIndex.from_product([self.save_list,
                                    [f"{str(x)}" for x in self.Var2]],
                                    names=["Trace", f"{self.Var2Name}"])
        
        df = pd.DataFrame(data=lastdata, columns=header)
        self.write(":PAGE:DISP:MODE GRAP")
        
        return df


    ##################### Sampling (Static) Mode Setups
    
    def IBias(self, I=10e-6, SMUP='SMU2', SMUN='SMU1', interval=5e-3, points=10, Comp=2):
        self.DisableAll()
    
        self.Mode = "SAMPLING"
        self.HoldTime=100e-3
        
        self.SetSMU(SMUP, 'Vf', 'If', 'I', 'CONS', Value=I, Comp=Comp)
        self.SetSMU(SMUN, 'Vb', 'Ib', 'COMM')
    
        self.write(f":PAGE:MEAS:SAMP:IINT {interval}")
        self.write(f":PAGE:MEAS:SAMP:POIN {points}")
    
        self.save_list=['If', 'Vf']
        self.beep()
        
        self.term='VCC2P'
        
        print(f"Set {self.term}")
        print(f"I={I}, Vlim={Comp},  interval={interval}, points={points}")
    
    def VBias(self, V=0.1, Comp=10e-3, SMUP='SMU2', SMUN='SMU1', interval=10e-3, points=6):
        self.DisableAll()
    
        self.Mode = "SAMPLING"
        self.HoldTime=100e-3
        
        self.SetSMU(SMUP, 'Vf', 'If', 'V', 'CONS', Value=V, Comp=Comp)
        self.SetSMU(SMUN, 'Vb', 'Ib', 'COMM')
    
        self.write(f":PAGE:MEAS:SAMP:IINT {interval}")
        self.write(f":PAGE:MEAS:SAMP:POIN {points}")
    
        self.save_list=['Vf', 'If']
        self.beep()
        
        self.term='ICV2P'
        
        print(f"Set {self.term}")
        print(f"V={V}, Ilim={Comp},  interval={interval}, points={points}")
    
    def Samp4P(self, I=10e-6, Ip='SMU2', Im='SMU1', Vp='SMU3', Vm='SMU4',  Comp=2, interval=10e-3, points=20):
        self.DisableAll()
    
        self.Mode = "SAMPLING"
        self.HoldTime=100e-3
        
        self.SetSMU(Ip, 'VIp', 'Ip', 'I', 'CONS', Value=I, Comp=Comp)
        self.SetSMU(Im, 'VIm', 'Im', 'COMM')
        self.SetSMU(Vp, 'Vp', 'IVp', 'I', 'CONS', Value=0, Comp=Comp)
        self.SetSMU(Vm, 'Vm', 'IVm', 'I', 'CONS', Value=0, Comp=Comp)
    
        self.write(f":PAGE:MEAS:SAMP:IINT {interval}")
        self.write(f":PAGE:MEAS:SAMP:POIN {points}")
    
        self.UFUNC('Vf=Vp-Vm')
        self.UFUNC('If=-Im')
        
        self.save_list=['If', 'Vf', 'Ip', 'Im', 'Vp', 'Vm', 'IVp', 'IVm']
        self.beep()
        
        self.term='4P SMU'
        
        print(f"Set {self.term}")
        print(f"I={I}, Vlim={Comp},  interval={interval}, points={points}")
        return 0
    
    def VSource(self, port_p, value, port_m="SMU1", Vname="V", Iname="I", Comp=3e-3):
        self.DisableAll()
        self.Mode="SAMP"
        self.SetSMU(port_p, Vname, Iname, "V", Value=value, Comp=Comp)
        self.SetSMU(port_m, "Vm", "Im")
        self.SetSMU("SMU3", "V3", "I3")
        self.SetSMU("SMU4", "V4", "I4")
        self.SetVSMU("VSU1", "GND1")
        self.SetVSMU("VSU2", "GND2")
        self.Interval=0.1
        self.SPoints=100
        self.save_list=[Vname, Iname]
        self.SPeriod="INF"
    
    def SetBiasVCO(self, Vt, Vcc=2.75, Vcc_port="SMU2", Vt_port="SMU3", GND_port="SMU1", Comp=30e-3):
        self.DisableAll()
        self.Mode="SAMP"
        self.SetSMU(GND_port, "V1", "I1")
        self.SetSMU(Vcc_port, "Vcc", "I2", "V", Value=Vcc, Comp=Comp)
        self.SetSMU(Vt_port, "Vt", "I3", "V", Value=Vt, Comp=Comp)
        self.SetSMU("SMU4", "V4", "I4")
        self.SetVSMU("VSU1", "GND1")
        self.SetVSMU("VSU2", "GND2")
        self.Interval=1
        self.SPoints=10
        self.save_list=['Vcc', 'I2', 'I3']
        self.beep()
        self.SPeriod="INF"
    
    def SetRampVCO(self, VtStart, VtStop, VtStep, Vcc=3, Vcc_port="SMU2", Vt_port="SMU3", GND_port="SMU1", HTime=1, DTime=0.5, Comp=30e-3):
        self.DisableAll()
        self.Mode="SWE"
        self.SetSMU(GND_port, "V1", "I1")
        self.SetSMU("SMU4", "V4", "I4")
        self.SetSMU(Vt_port, "Vt", "I3", "V", Func="VAR1")
        self.SetVar('VAR1', 'V', VtStart, VtStop, VtStep, Comp=Comp)
    
        self.SetSMU(Vcc_port, "Vcc", "I2", "V", Value=Vcc, Comp=Comp)
        
        self.SetVSMU("VSU1", "GND1")
        self.SetVSMU("VSU2", "GND2")
        
        self.SetAxis('X', 'Vcc', 'LIN', Vcc-0.5, Vcc+0.5)
        self.SetAxis('Y1', 'I2', 'LIN', 0, 30e-3)
    
        self.save_list=['Vcc', 'I2', 'I3']
        self.beep()
        
        self.term='RampVCO'
        self.HoldTime=HTime
        self.DelayTime=DTime
                    
        print(f"Set {self.term}")
        print(f"Vg=({VtStart}, {VtStop}, {VtStep}), Ilim={Comp}")
        
        return 0
        
    def AdjustVCOtune(self, Vt, Vt_port="SMU3"):
        self.write(f":PAGE:MEAS:SAMP:CONS:{Vt_port} {Vt}")


def DebugOut(inst, varlist, Var2):
    inst.Var2=Var2
    inst.data_variables=varlist
    inst.Var2Name='Var2'
    return inst.get_data()
