from HPIB import *

class HP4145(HP):

    def stop(self):
        self.write("ME4")

        return 0

    def reset(self):

        return 0

    ##### Eixos, X=XN, Y1 e Y2. Mode 1=linear, 2=log.
    def SetAxis(self, AXIS, NAME, Scale=1, Min=0, Max=1):
        if AXIS not in ['X', 'Y1','Y2']:
            raise Exception("Invalid axis: <{AXIS}>")
        self.write("SM")
        self.write("DM1")
        time.sleep(0.5)
        if AXIS=='X':
            AXIS='XN'        
        elif AXIS[0].upper()=='Y':
            AXIS=AXIS[0]+chr(ord(AXIS[1])+16)
        
        self.write(f"{AXIS}\'{NAME}\',{Scale},{Min},{Max}")
        
        return 0

    def DisableAll(self):
        self.write("DE")
        for i in range(1, 7):
            self.write(f"CH{i}")
            time.sleep(0.01)
        for i in range(1, 3):
            self.write(f"VS{i}")
            time.sleep(0.01)
            
        return 0
    
    def Disable(self, VSMU):
        chtype=VSMU[:len(VSMU)-1]
        no=VSMU[len(VSMU)-1]
        
        if chtype.upper()=='SMU':
            self.write(f'CH{no}')
        if chtype[0].upper()=='V':
            self.write(VSMU)

        return 0
    
    def save_list(self, trace_list):
        self.data_variables=trace_list

        
    ##### Configura IntTime
    def SetIntTime(self, IntTime="MED"):
        
        IntTime=Intlist.index(IntTime.translate(striplc))
        self.write(f"IT{IntTime}")
        
        return 0

    ##### Lê Data Ready (OPC)
    def GetDR(self):
        return int(self.inst.read_stb()&0b1)

    ##### Medida, padrão single  >>>> self.measure() <<<<<
    def measure(self, meas='Single', maxpoll=60):
        try: meas=Measurements.index(meas)
        except: return "Invalid measurement command"
        ## Buffer Clear + DataReady 0
        self.write("BC\nDR0")
        ## Espera DataReady == 0
        if self.PollDR(0, maxpoll=maxpoll):
            return 'Timeout'
        self.write("SM\nDR1\nDM1")
        self.write(f"MD\nME{meas}")
        
        return 0

    ##### Lê uma varíavel
    def DataOutput(self, name):
        ## Lê a string, remove o terminador "\r", split em valores, remove o indicador de compliance C ou N e casta em uma lista numpy de floats
        if self.debug:
            
            if hasattr(self, 'Var2'):
                return np.column_stack(tuple([self.Var1*0.1**n for n in range(1, len(self.Var2)+1)]))
            return self.Var1*0.1
        print(name)
        out=np.array([float(x.strip('CNX')) for x in self.ask(f"DO '{name}'").strip('N \r').split(',')])
        return np.column_stack(np.split(out, len(out)/len(self.Var1)))
        
    def MakeHeader(self, trace_list):
        if hasattr(self, 'Var2Name'):
            return pd.MultiIndex.from_product([trace_list[1:],
                                    [trace_list[0]]+[f"{self.Var2Name}={str(np.around(x, 1))}" for x in self.Var2]],
                                    names=["Trace", "Parameter"])

        hgen=[[],[]]
              
        for x in trace_list[1:]:
              hgen[1]+=[trace_list[0], x]
              hgen[0]+=[x, x]

              
        return pd.MultiIndex.from_tuples(list(zip(*hgen)), names=["Trace", "Parameter"])
        
    
    def get_data(self):
##        if self.PollDR(1,maxpoll=10):
##            return 1
        self.write("DL1\nDP1")
        ## Output em lista numpy 
        lastdata=self.Var1
        
        for n, trace in enumerate(self.data_variables[1:]):
            data=np.column_stack((self.Var1, self.DataOutput(trace)))
            if n==0:
                lastdata=data
                continue
            lastdata=np.column_stack((lastdata, data))          
        header=self.MakeHeader(self.data_variables)
        print(header)
        print(lastdata)
            
        #Retorna em forma de pandas dataframe 
        df = pd.DataFrame(data=lastdata, columns=header, index=None)
        
        return(df)

    ##### Configura VM ou VS    
    def SetVSMU(self, SMUno, VNAME, Func='CONS', Value=0, Comp='1e-3'):

        SMUno=SMUno.upper()
        if SMUno not in ['VMU1', 'VMU2','VSU1','VSU2']:
            raise Exception("Invalid VS or VM: <{SMUno}>")

        Func=Funclist.index(Func)
        self.write("DE")

        ## Para VMU
        if SMUno[len(SMUno)-1].upper()=='M':
            self.write(f"V{t}{no},\'{VNAME}\'")
            return 0
            
        ##para VSU
        self.write(f"V{t}{no},\'{VNAME}\',{Func}")
        if Func[len(Func)-1] in ['1', '2', 'D']:
            try: self.VarComp[int(Func[len(Func)-1])]=Comp
            except: self.VarComp[0]=Comp

            return 0
        
        if Func=='CONS':
            self.write("SS")
            time.sleep(0.05)
            self.write(f"SC{no},{Value}")

            return 0
        
        return 1

    ##### Configura SMUs
    def SetSMU(self, SMUno, VNAME, INAME, Mode='COMM', Func='CONS', Comp='1e-3', SRES='0OHM', Value=0):
        #Value=ETF(Value)
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
##        if Func not in ['CONS', 'VAR1', 'VAR2', 'VARD']:
##            raise Exception(f"Invalid Func in {SMUno}: <{Func}>")
        
        no=SMUno[3]
        self.write("DE")
        self.write(f"CH{no},\'{VNAME}\',\'{INAME}\',{Modelist.index(Mode)},{Funclist.index(Func)}")
        
        if Mode=="COMM": return 0

        if Func=='CONS':
            self.write("SS")
            time.sleep(0.05)
            self.write(f"{Mode}C{no},{Value},{Comp}")

            return 0
        
        if Func[3]=='2' and Mode.upper()=='V':
            self.Var2Name=VNAME

        if Func[3]=='2' and Mode.upper()=='I':
            self.Var2Name=INAME
        
        if Func[3] in ['1', '2', 'D']:
            try: self.VarComp[int(Func[len(Func)-1])]=Comp
            except: self.VarComp[0]=Comp

            return 0

        return 1

    ##### Configura VARs
    def SetVar(self, VARno, Func, Start, Stop, Step=0, Comp='1e-3'):
        
        no=VARno[len(VARno)-1]
        self.write("SS")
        Start=ETF(Start)
        Step=ETF(Step)
        Stop=ETF(Stop)

        ##### VARD = Var1*Ratio+Offset -- Start = Ratio, Stop=Offset
        if no=='D' and Step==0:
            self.write(f"RT {Start}")
            self.write(f"FS {Stop}")
            self.VarD=Stop+Start*self.Var1

            return 0
        ##### Var1 - Start, Stop, Step
        if no=='1':
            self.write(f"{Func}{Varlist[int(no)]}1,{Start},{Stop},{Step},{self.VarComp[1]}")
            self.Var1=np.arange(Start, Stop+Step, Step)

            return 0
        ##### Var2 - Start, Stop, StepNo
        if no=='2':
            self.write(f"{Func}{Varlist[int(no)]}{Start},{Step},{Stop/Step+1},{self.VarComp[2]}")
            self.Var2=np.arange(Start, Stop+Step, Step)

            return 0

        return 1
