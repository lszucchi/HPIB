import pyvisa
import string
import datetime

from IPython.display import clear_output, display
from HPIB_plot import *
from time import sleep

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
        
        print(self.term)
        self.measure()
        
        Poll=self.PollDR(1, 1, timeout)
        
        if Poll:
            return "Operation stopped or timeout"
        
        df=self.get_data()
        
        try:
            _, ext = os.path.splitext(path)
            if ext != ".csv":
                path = f"{path}/{self.term}-{datetime.datetime.now().strftime('%y%m%d %H%M%S')}.csv"
        except:
            return "Invalid Path"
        try: df.to_csv(path)
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
                return 1
            if self.GetDR()==state:
                return 0

        return 1
    
    def SetVGS(self, dict, ptype):
        self.SetVgs(dict['VGstart'], dict['VGstop'], dict['VGstep'], ETF(dict['VD']), ETF(dict['Compliance']), ptype=ptype)

    def SetVgs(self, VgStart, VgStop, VgStep, VdValue=0.1, Comp=1e-3, VdSweep=False, ptype=False, sat=False):
        
        if ptype:
                    VdValue=-VdValue
                    VgStart=-VgStart
                    VgStop=-VgStop
                    VgStep=-VgStep

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
            self.Var2Name="VDS"

        self.SetVar('VAR1', 'V', VgStart, VgStop, VgStep, 1e-3)

        self.SetAxis('X', 'VG', 'LIN', VgStart, VgStop)
        self.SetAxis('Y1', 'ID', 'LIN', 0, VgStop*1e-3)

        self.save_list(['VG', 'IG', 'ID', 'IS'])
        self.beep()
        
        if sat or (np.abs(VgStop)-np.abs(VdValue)<0.5):
                    self.term='IdxVgs Sat'
        else:
                    self.term='IdxVgs'
                    
        print("Set " + self.term)
        print(f" Vg=({VgStart}, {VgStop}, {VgStep}), Vd={VdValue}, Ilim={Comp}")
        
        return 0
    
    def SetVDS(self, dict, ptype):
        self.SetVds(dict['VDstart'], dict['VDstop'], dict['VDstep'], dict['VGstart'], dict['VGstop'], dict['VGstep'], ETF(dict['Compliance']), ptype)
    
    def SetVds(self, VdStart, VdStop, VdStep, VgStart, VgStop, VgStep, Comp=1e-3, ptype=False):
        
        if ptype:
                VdStart=-VdStart
                VdStop=-VdStop
                VdStep=-VdStep
                VgStart=-VgStart
                VgStop=-VgStop
                VgStep=-VgStep

        self.DisableAll()
        
        self.SetSMU('SMU1', 'VS', 'IS', 'COMM', 'CONS')
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'VAR1', Comp=Comp)
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR2', Comp=Comp)
        self.SetSMU('SMU4', 'VB', 'IB', 'COMM', 'CONS')
        self.SetVar('VAR1', 'V', VdStart, VdStop, VdStep)
        self.SetVar('VAR2', 'V', VgStart, VgStop, VgStep)
        sleep(0.5)
        self.SetAxis('X', 'VD', 'LIN', VdStart, VdStop)
        self.SetAxis('Y1', 'ID', 'LIN', 0, 1e-3)
        self.Var2Name="VGS"

        self.save_list(['VD', 'ID', 'IG', 'IS'])
        self.beep()
        
        self.term='IdxVds'
        
        print("Set " + self.term)
        print(f"Vd=({VdStart}, {VdStop}, {VdStep}), Vg=({VgStart}, {VgStop}, {VgStep}), Ilim={Comp}")
        
        return 0

    def SetVP(self, dict, ptype):
        self.SetVp(dict['Is'], dict['VGstart'], dict['VGstop'], dict['VGstep'], dict['Compliance'], ptype)
        
    def SetVp(self, Is, VgStart, VgStop, VgStep, Comp=1.5, ptype=False):       
        
        if ptype:
                Is=-Is
                VgStart=-VgStart
                VgStop=-VgStop
                VgStep=-VgStep
            
        self.DisableAll()
        
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR1')
        self.SetSMU('SMU1', 'VS', 'IS', 'I', 'CONS', Comp=Comp, Value=format(Is, '.2e'))
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'VARD')
        self.SetSMU('SMU4', 'VB', 'IB')
        
        self.SetVar('VAR1', 'V', VgStart, VgStop, VgStep)
        self.SetVar('VARD', 'V', 1, 0)
        self.Var2=Is
        self.Var2Name='Is'

        self.SetAxis('X', 'VD', 'LIN', VgStart, VgStop)
        self.SetAxis('Y1', 'VS', 'LIN', 0, 1)

        self.save_list(['VG', 'IG', 'VS', 'ID'])
        self.beep()

        self.term='VpxVgs'
        
        print("Set " + self.term)
        print(f"Is={Is}, Vg=({VgStart}, {VgStop}, {VgStep}), Vlim={Comp}")
        
        return 0

    def SetEXIS(self, dict, ptype):
        self.SetEx_Is(dict['VSstart'], dict['VSstop'], dict['VSstep'], dict['VGstart'], dict['VGstop'], dict['VGstep'], dict['VDvalue'], dict['Compliance'], ptype)
    
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
        
        self.SetSMU('SMU1', 'VS', 'IS', 'V', 'VAR1', Comp=Comp)
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'CONS', Value=VdValue, Comp=Comp)
        self.SetSMU('SMU3', 'VG', 'IG', 'V', 'VAR2', Comp=Comp)
        self.SetSMU('SMU4', 'VB', 'IB', 'COMM')

        
        self.SetVar('VAR1', 'V', VsStart, VsStop, VsStep)
        self.SetVar('VAR2', 'V', VgStart, VgStop, VgStep)

        self.SetAxis('X', 'VS', 'LIN', VsStart, VsStop)
        self.SetAxis('Y1', 'ID', 'LIN', 0, 1)

        self.save_list(['VS', 'ID', 'IG'])
        
        self.beep()

        self.term='Ex_Is'
        
        print("Set " + self.term)
        print(f" Vs=({VsStart}, {VsStop}, {VsStep}), Vg=({VgStart}, {VgStop}, {VgStep}), Vd={VdValue}")
        
        return 0

    def SetDiode(self, VfStart, VfStop, VfStep):
        VfStart=-VfStart
        VfStop=-VfStop
        VfStep=-VfStep
        
        self.DisableAll()
        
        self.SetSMU('SMU4', 'VB', 'IF', 'V', 'VAR1', Comp=2.4e-3)
        self.SetSMU('SMU1', 'VS', 'IS', 'V', 'CONS', Comp=1.2e-3)
        self.SetSMU('SMU2', 'VD', 'ID', 'V', 'CONS', Comp=1.2e-3)

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep)
        self.UFUNC("V=-VB")
        
        self.SetAxis('X', 'V', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'IS', 'LIN', -1e-3, 1e-3)
        self.SetAxis('Y2', 'ID', 'LIN', -1e-3, 1e-3)

        self.save_list(['V', 'IS', 'ID'])
        self.beep()

        self.term="Diode"
        
        print("Set " + self.term)
        print(f"Vf=({VfStart}, {VfStop})")

        return 0

    def SingleDiode(self, VfStart, VfStop, VfStep, SMUP='SMU2', SMUN='SMU4'):
        
        self.DisableAll()
        
        self.SetSMU(SMUN, 'VB', 'IB', 'V', Comp=2e-3)
        self.SetSMU(SMUP, 'VF', 'IF', 'V', 'VAR1', Comp=2e-3)

        self.SetVar('VAR1', 'V', VfStart, VfStop, VfStep)
        
        self.SetAxis('X', 'VF', 'LIN', VfStart, VfStop)
        self.SetAxis('Y1', 'IF', 'LIN', -2e-3, 2e-3)

        self.save_list(['VF', 'IF'])
        self.beep()

        self.term="Diode"
        
        print("Set " + self.term)
        print(f"Vf=({VfStart}, {VfStop})")

        return 0

    def SetCap(self, VStart, VStop, VStep, Comp):
        self.DisableAll()
        
        self.SetSMU('SMU1', 'V', 'I', 'V', Func='VAR1')
        self.SetVSMU('VMU1', 'C')
        self.SetVar('VAR1', 'V', VStart, VStop, VStep, Comp=ETF(Comp))
        

        self.SetAxis('X', 'V', 'LIN', VStart, VStop)
        self.SetAxis('Y1', 'C', 'LIN', 0, 2)
        self.SetAxis('Y2', 'I', 'LIN', 0, 1e-3)

        self.save_list(['V', 'C', 'I'])
        self.beep()

        self.term='CV'
        
        print("Set " + self.term)
        print(f"V=({VStart}, {VStop}, {VStep}), Ilim={Comp})")
        
        return 0

    def Set2P(self, IStart, IStop, Points):
        self.DisableAll()
        
        self.SetSMU('SMU4', 'V1', 'I1')
        self.SetSMU('SMU1', 'V2', 'I2', 'I', 'VAR1')
        self.SetVar('VAR1', 'I', IStart, IStop, (IStop-IStart)/(Points-1), 1)
        
        self.UFUNC('V=-V1')
        
        self.SetAxis('Y1', 'I2')
        self.SetAxis('X', 'V2')

        self.save_list(['V2', 'I2'])
        self.beep()
        
        self.term="2P"
        
        print("Set " + self.term)
        print(f"I=({IStart}, {IStop}), {Points} Points")

    def Set2PD(self, VStart, VStop, Points):
        self.DisableAll()
        
        self.SetSMU('SMU4', 'V1', 'I1')
        self.SetSMU('SMU2', 'V2', 'I2', 'V', 'VAR1')
        self.SetVar('VAR1', 'V', VStart, VStop, (VStop-VStart)/(Points-1), 1.5e-3)
        
        self.UFUNC('V=-V1')
        
        self.SetAxis('Y1', 'I2', 0, 1e-3)
        self.SetAxis('X', 'V2')

        self.save_list(['V2', 'I2'])
        self.beep()
        
        self.term="2PD"
        
        print("Set " + self.term)
        print(f"I=({VStart}, {VStop}), {Points} Points")
    
    def Set4P(self, IStart, IStop, Points):        
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
        print(f"I=({IStart}, {IStop}), {Points} Points")

        return 0

    def Set4PV(self, VStart, VStop, Points):
        self.DisableAll()
        
        self.SetSMU('SMU1', 'V1', 'I1')
        self.SetSMU('SMU2', 'V2', 'I2', 'V', 'VAR1')
        self.SetVSMU('VMU1', 'V3')
        self.SetVSMU('VMU2', 'V4')
        self.SetVar('VAR1', 'I', VStart, VStop, (VStop-VStart)/(Points-1))
        self.UFUNC('V=VMU2-VMU1')

        self.SetAxis('X', 'V')
        self.SetAxis('Y1', 'I1')
        
        self.save_list(['I2', 'V'])
        self.beep()
        
        self.term="4PV"
        
        print("Set " + self.term)
        print(f"Vsource=({VStart}, {VStop}), {Points} Points")
        
        return 0

def DebugOut(inst, varlist, Var2):
    inst.Var2=Var2
    inst.data_variables=varlist
    inst.Var2Name='Var2'
    return inst.get_data()
