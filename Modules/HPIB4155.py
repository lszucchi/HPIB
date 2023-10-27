from HPIB import *

class HP4155(HP):

    def reset(self):
        return self.write("*RST")

    def stop(self):
        return self.write(":PAGE:SCON:STOP")

    def SetAxis(self, AXIS, NAME, SCALE="LIN", MIN=0, MAX=1):
        self.write(f":PAGE:DISP:GRAP:{AXIS}:NAME \'{NAME}\'")
        self.write(f":PAGE:DISP:GRAP:{AXIS}:SCAL {SCALE}")
        self.write(f":PAGE:DISP:GRAP:{AXIS}:MIN {MIN}")
        self.write(f":PAGE:DISP:GRAP:{AXIS}:MAX {MAX}")
        
        return 0
        
    def DisableAll(self):
        self.write(":PAGE:CHAN:ALL:DIS")
        
        return 0

    def SetIntTime(self, IntTime="MEDium"):
        IntTime=IntTime.translate(striplc)
        
        if IntTime in Intlist:
            self.write(f":PAGE:MEAS:MSET:ITIM {IntTime}")

            return 0
        
        return 'Invalid Integration Time'

    def UFUNC(self, ufunc):
    
        if ufunc[0]=='V':
            mode='V'
        else:
            mode='A'

        (NAME, UNIT, EXPRESSION) = (ufunc.split('=')[0], mode, ufunc.split('=')[1])
        
        self.write(f":PAGE:CHAN:UFUN:DEF '{NAME}', '{UNIT}', '{EXPRESSION}'")

        return 0

    def measure(self, period="INF", points=100):
            if self.analyzer_mode == "SWEEP":
                self.write(":PAGE:GLIS")
                self.write(":PAGE:SCON:MEAS:SING")
                self.write("*ESE 1")
                self.write("*OPC")
            else:
                self.write(f":PAGE:MEAS:SAMP:PER {period}")
                self.write(f":PAGE:MEAS:SAMP:POIN {points}")
                self.write(":PAGE:SCON:MEAS:SING; *OPC?")

            return 0

    def PollDR(self, state, delay=1, maxpoll=2):
        if self.debug:
            time.sleep(2*delay)
            print("Debug DR")
            return 0
            
        for i in range(60*maxpoll):
            if self.StopFlag:
                return 1
            if int(self.ask("*ESR?"))&1==state:
                return 0
            time.sleep(delay) 
            if i%10==0: print("Still alive")
        return 1

    def save_list(self, trace_list):
        self.data_variables=trace_list
        self.write(":PAGE:DISP:MODE LIST")
        self.write(":PAGE:DISP:LIST:DEL:ALL")
        
        if isinstance(trace_list, list):
            if len(trace_list) > 8:
                raise RuntimeError('Maximum of 8 variables allowed')
            for name in trace_list:
                self.write(f":PAGE:DISP:LIST \'{name}\'")
        else:
            raise TypeError('Invalid trace list')
        self.write(":PAGE:DISP:MODE GRAP")

    def DataOutput(self, trace):
        if self.debug:
            self.out=self.out/10

            return np.column_stack(np.split(self.out, len(self.Var2)))
        
        return np.column_stack(np.split(np.array(self.ask(f":DATA? \'{trace}\'").split(',')), len(self.Var2)))

    def get_data(self):
        if not (isinstance(self.Var2, list) or isinstance(self.Var2, np.ndarray)):
            self.Var2=[self.Var2]
            
        if self.debug:
            self.out=np.arange(0, 100*len(self.Var2))
            header=self.data_variables
            
        elif int(self.ask('*OPC?')):
            header = self.ask(":PAGE:DISP:LIST?").split(',')
            
        self.write(":FORM:DATA ASC")

        lastdata=self.DataOutput(header[0])
        
        # recursively get data for each variable
        for i, listvar in enumerate(header[1:]):

            lastdata = np.column_stack((lastdata, self.DataOutput(listvar)))
        
        header = pd.MultiIndex.from_product([self.data_variables,
                                    [f"{str(x)}" for x in self.Var2]],
                                    names=["Trace", f"{self.Var2Name}"])
        
        df = pd.DataFrame(data=lastdata, columns=header, index=None)
        self.write(":PAGE:DISP:MODE GRAP")
        
        return df

    def SetVSMU(self, SMUno, VNAME, Func='CONS', Value=0, Comp='1e-3'):

        SMUno=SMUno.upper()
        if SMUno not in ['VMU1', 'VMU2','VSU1','VSU2']:

            raise Exception("Invalid VS or VM: <{SMUno}>")
        
        Func=Func.upper()
        if Func not in ['CONS', 'VAR1', 'VAR2', 'VARD']:

            raise Exception(f"Invalid Mode in {SMUno}: <{Mode}>")
        
        if SMUno[1]=='M':
            self.write(f":PAGE:CHAN:{SMUno}:VNAME \'{VNAME}\'")
            self.write(f":PAGE:CHAN:{SMUno}:MODE V")

            return 0
        
        self.write(f":PAGE:CHAN:{SMUno}:FUNC {Func}")
        if Func[len(Func)-1] in ['1', '2', 'D']:
            try: self.VarComp[int(Func[len(Func)-1])]=Comp
            except: self.VarComp[0]=Comp

            return 0
        
        if Func=='CONS':
            self.write(f":PAGE:MEAS:CONS:{SMUno} {Value}")
            self.write(f":PAGE:MEAS:CONS:{SMUno}:COMP {Comp}")
            time.sleep(0.1)

            return 0
        
        return 1
        
    def SetSMU(self, SMUno, VNAME, INAME, Mode="COMM", Func="CONS", Comp="1e-3", SRES="0OHM", Value=0):
 
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
       
        self.beep()
        
        if Mode == "COMM": return 0
        
        self.write(f":PAGE:CHAN:{SMUno}:SRES {SRES}")
        if Func[3] in ['1', '2', 'D']:
            try: self.VarComp[int(Func[len(Func)-1])]=Comp
            except: self.VarComp[0]=Comp

            return 0
            
        if Func == "CONS":
            self.write(f":PAGE:MEAS:CONS:{SMUno} {ETF(Value)}")
            self.write(f":PAGE:MEAS:CONS:{SMUno}:COMP {Comp}")

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
            time.sleep(0.1)
            
            return 0

        if VARno=='VAR2' and Step:
            self.Var2=np.arange(Start, Stop+Step, Step)
            Points=1+(Stop-Start)/Step
            self.write(f":PAGE:MEAS:{VARno}:STAR {Start}")
            self.write(f":PAGE:MEAS:{VARno}:STEP {Step}")
            self.write(f":PAGE:MEAS:{VARno}:POINTS {Points}")
            self.write(f":PAGE:MEAS:{VARno}:COMP {Comp}")
            time.sleep(0.1)

            return 0

        if VARno=='VARD' and not Step:
            """ Start = Ratio, Stop=Offset"""
            self.write(f":PAGE:MEAS:VARD:RAT {Start}")
            self.write(f":PAGE:MEAS:VARD:OFFS {Stop}")
            time.sleep(0.1)

            return 0
        
        return 1
