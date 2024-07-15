import pyvisa, string, datetime
from IPython.display import clear_output, display
from time import sleep
try:
    from .HPIB_plot import *
except:
    from HPIB_plot import *

########## Tabelas para intruções HPIb ###########

striplc = str.maketrans('', '', string.ascii_lowercase)

Measurements=['0', 'Single', 'Append', 'Stop']
Modelist=['0', 'V', 'I', 'COMM']
Funclist=['0', 'VAR1', 'VAR2', 'CONS', 'VARD']
Varlist=['0', 'R', 'P']
Intlist=['0', 'SHOR', 'MED', 'LONG']
Scalelist=['0', 'LIN', 'LOG']


## Classe genérica HP com código compartilhado

class HP:

    def __init__(self, addr, read_termination = '\n', write_termination = '\n', timeout=5000, debug=False):

        self.analyzer_mode="SWEEP"
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
            print(self.ask("*IDN?"))

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

    def close(self):
        self.inst.close()

    def SingleSave(self, path=".", timeout=2, real=False):
        if self.term=="0": return "Parameters not set"
        
        print(self.term)
        self.measure()
        
        Poll=self.PollDR(1, 1, timeout)
        
        if Poll:
            return "Operation stopped or timeout"
        if real:
            df=self.get_realdata()
        else:
            df=self.get_data()
        
        try:
            _, ext = os.path.splitext(path)
            if ext != ".csv":
                path = f"{path}/{self.term}-{datetime.datetime.now().strftime('%y%m%d %H%M%S')}.csv"
        except:
            return "Invalid Path"
        try: df.to_csv(path, float_format='%+.6E')
        except: return "Unable to write CSV"
        
        return path

    ##### Poll DataReady == state, a cada delay em ms, no máximo de maxpoll ciclos. Retorna 1 se chegar ao máximo de ciclos.
    def PollDR(self, state, delay=1, maxpoll=2):
        if self.debug:
            sleep(2*delay)
            print("Debug DR")
            return 0
        minute=False
        progress=''
        #prog_bar=display(progress, display_id=True)
        
        for i in range(60*maxpoll):
            progress+='+'
            if len(progress)>=30:
                progress="+"
                print("30s", end=' ')
                if minute:
                    print("|", end=' ')
                minute=not minute
            #prog_bar.update(progress)
            
            sleep(delay)
            if self.Stop_flag:
                print('')
                return 1
            if self.GetDR()==state:
                print('')
                return 0
        print('')
        return 1
    
    def SetVgS(self, dict, ptype):
        self.SetVgs(dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], ETF(dict['Vd']), ETF(dict['Compliance']), ptype=ptype)

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
        self.SetAxis('Y1', 'Id', 'LIN', 0, VgStop*1e-3)

        self.save_list(['Vg', 'Ig', 'Id', 'Is'])
        self.beep()
        
        if sat:
                    self.term='IdxVgs Sat'
        else:
                    self.term='IdxVgs'
                    
        print(f"Set {self.term}")
        print(f"Vg=({VgStart}, {VgStop}, {VgStep}), Vd={VdValue}, Ilim={Comp}")
        
        return 0
    
    def SetVdS(self, dict, ptype):
        self.SetVds(dict['Vdstart'], dict['Vdstop'], dict['Vdstep'], dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], ETF(dict['Compliance']), ptype)
    
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
        self.SetAxis('Y1', 'Id', 'LIN', 0, 1e-3)
        self.Var2Name="Vgs"

        self.save_list(['Vd', 'Id', 'Ig', 'Is', 'Ib'])
        self.beep()
        
        self.term='IdxVds'
        
        print(f"Set {self.term}")
        print(f"Vd=({VdStart}, {VdStop}, {VdStep}), Vg=({VgStart}, {VgStop}, {VgStep}), Ilim={Comp}")
        
        return 0

    def SetVP(self, dict, ptype):
        self.SetVp(dict['Is'], dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], dict['Compliance'], ptype)
        
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

        self.save_list(['Vg', 'Ig', 'Vs', 'Id'])
        self.beep()

        self.term='VpxVgs'
        
        print(f"Set {self.term}")
        print(f"Is={format(Is, '.3e')}, Vg=({VgStart}, {VgStop}, {VgStep}), Vlim={Comp}")
        
        return 0

    def SetExIs(self, dict, ptype):
        self.SetEx_Is(dict['Vsstart'], dict['Vsstop'], dict['Vsstep'], dict['Vgstart'], dict['Vgstop'], dict['Vgstep'], dict['Vdvalue'], dict['Compliance'], ptype)
    
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

        self.save_list(['Vs', 'Id', 'Ig'])
        
        self.beep()

        self.term='Ex_Is'
        
        print(f"Set {self.term}")
        print(f"Vs=({VsStart}, {VsStop}, {VsStep}), Vg=({VgStart}, {VgStop}, {VgStep}), Vd={VdValue}")
        
        return 0

    def SetDiode(self, VfStart, VfStop, VfStep):
        self.Var2=None
        self.Var2Name=None
        VfStart=-VfStart
        VfStop=-VfStop
        VfStep=-VfStep
        
        self.DisableAll()
        
        self.SetSMU('SMU4', 'Vb', 'Ib', 'V', 'VAR1', Comp=2.4e-3)
        self.SetSMU('SMU1', 'Vs', 'Is', 'V', 'CONS', Comp=1.2e-3)
        self.SetSMU('SMU2', 'Vd', 'Id', 'V', 'CONS', Comp=1.2e-3)

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep)
        self.UFUNC("Vf=-Vb")
        
        self.SetAxis('X', 'Vf', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'Is', 'LIN', -1e-3, 1e-3)
        self.SetAxis('Y2', 'Id', 'LIN', -1e-3, 1e-3)

        self.save_list(['Vf', 'Is', 'Id'])
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

        self.save_list(['Vf', 'If'])
        self.beep()

        self.term="Diode"
        
        print(f"Set {self.term}")
        print(f"Vf=({VfStart}, {VfStop})")

        return 0

    def SetCap(self, Vstart, Vstop, Vstep, Comp):
        self.Var2=None
        self.Var2Name=None
        self.DisableAll()
        
        self.SetSMU('SMU1', 'V', 'I', 'V', Func='VAR1')
        self.SetVsMU('VMU1', 'C')
        self.SetVar('VAR1', 'V', Vstart, Vstop, Vstep, Comp=ETF(Comp))
        

        self.SetAxis('X', 'V', 'LIN', Vstart, Vstop)
        self.SetAxis('Y1', 'C', 'LIN', 0, 2)
        self.SetAxis('Y2', 'I', 'LIN', 0, 1e-3)

        self.save_list(['V', 'C', 'I'])
        self.beep()

        self.term='CV'
        
        print(f"Set {self.term}")
        print(f"V=({Vstart}, {Vstop}, {Vstep}), Ilim={Comp})")
        
        return 0

    def Set2P(self, Istart, Istop, Points, SMUP='SMU2', SMUN='SMU4', Comp=1.5):
        self.DisableAll()
        
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU(SMUN, 'Vb', 'Ib')
        self.SetSMU(SMUP, 'Vf', 'If', 'I', 'VAR1')
        self.SetVar('VAR1', 'I', Istart, Istop, (Istop-Istart)/(Points-1), Comp=Comp)
        
        self.SetAxis('Y1', 'If')
        self.SetAxis('X', 'Vf')

        self.save_list(['Vf', 'If'])
        self.beep()
        
        self.term=f"2P - {SMUN[-1]}{SMUP[-1]}"
        
        print(f"Set {self.term}")
        print(f"I=({Istart}, {Istop}), {Points} Points")
    
    def Set4P(self, Istart, Istop, Points, Ip='SMU2', Im='SMU1', Vp='VMU2', Vm='VMU1', Comp=1):        
        self.DisableAll()
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU(Im, 'V1', 'I')
        self.SetSMU(Ip, 'V2', 'I2', 'I', 'VAR1')
        self.SetVSMU(Vm, 'V3')
        self.SetVSMU(Vp, 'V4')
        self.SetVar('VAR1', 'I', Istart, Istop, (Istop-Istart)/(Points-1), Comp=Comp)
        
        self.UFUNC('V=V3-V4')

        self.SetAxis('X', 'V', 1, -1e-2, 1e-2)
        self.SetAxis('Y1', 'I', 1, Istart, Istop)
        
        self.save_list(['I', 'V'])
        self.beep()
        
        self.term="4P"
        
        print(f"Set {self.term}")
        print(f"I=({Istart}, {Istop}), {Points} Points")

        return 0
    
    def Set4PV(self, Vstart, Vstop, Points, R=None):
        self.DisableAll()
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU('SMU1', 'V1', 'I')
        self.SetSMU('SMU2', 'V2', 'I2', 'V', 'VAR1')
        self.SetVSMU('VMU1', 'V3')
        self.SetVSMU('VMU2', 'V4')
        self.SetVar('VAR1', 'I', Vstart, Vstop, (Vstop-Vstart)/(Points-1))
        self.UFUNC('V=V4-V3')

        self.SetAxis('X', 'V')
        self.SetAxis('Y1', 'I')
        
        self.save_list(['I', 'V'])
        self.beep()
        
        self.term="4PV"
        
        print(f"Set {self.term}")
        print(f"Vsource=({Vstart}, {Vstop}), {Points} Points")

        return 0

    def Set4PSMU(self, Istart, Istop, Points):        
        self.DisableAll()
        self.Var2=None
        self.Var2Name=None
        
        self.SetSMU('SMU1', 'V1', 'I1')
        self.SetSMU('SMU4', 'V4', 'I4', 'I', 'VAR1')
        self.SetSMU('SMU2', 'V2', 'I2', 'I', 'CONS', Value=0, Comp=1)
        self.SetSMU('SMU3', 'V3', 'I3', 'I', 'CONS', Value=0, Comp=1)
        self.SetVar('VAR1', 'I', Istart, Istop, (Istop-Istart)/(Points-1))

        self.SetAxis('X', 'V3')
        self.SetAxis('Y1', 'I1')
        
        self.save_list(['I1', 'V3'])
        self.beep()
        
        self.term="4P"
        
        print(f"Set {self.term}")
        print(f"I=({Istart}, {Istop}), {Points} Points")

        return 0

def DebugOut(inst, varlist, Var2):
    inst.Var2=Var2
    inst.data_variables=varlist
    inst.Var2Name='Var2'
    return inst.get_data()
