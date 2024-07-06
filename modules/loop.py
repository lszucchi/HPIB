from INOSerial import *
from HPIB4155 import *
from HPIB_plot import*
from IPython.display import clear_output, display

def printf(msg, path, output=True):
    os.makedirs(path, exist_ok=True)

    path+=f"/log.txt"
    
    with open(path, 'a') as the_file:
        the_file.write(f'{msg}\n')
    if output:
        print(msg)

def loop(HP, prefix, ptype, start):    
    timeout=10  
    VGS = {
        'enable' : True,
        'VGstart' : 0, 'VGstop' : 1.5, 'VGstep' : 0.01,
        'VD' : '25m', 'Compliance' : '1.5m'
        }
    
    # SubVt = {
    #     'enable' : True,
    #     'VGstart' : Vt-0.2, 'VGstop' : Vt+0.2, 'VGstep' : '1m',
    #     'VD' : '10m', 'Compliance' : '10m'
    #     }
        
    VGS_sat = {
        'enable' : False,
        'VGstart' : 0, 'VGstop' : 1.5, 'VGstep' : 0.01,
        'VD' : 1.5, 'Compliance' : '1.5m'
        }
    
    VDS = {
        'enable' : False,
        'VDstart' : 0, 'VDstop' : 1.5, 'VDstep' : 0.01,
        'VGstart' : 0.6, 'VGstop' : 1.5, 'VGstep' : 0.15,
        'Compliance' : '1.5m'
        }
    
    Ex_Ib = {
        'enable' : False,
        'VSstart' : 0, 'VSstop' : 1.5, 'VSstep' : 0.01,
        'VGstart' : 1.3, 'VGstop' : 1.6, 'VGstep' : 0.1,
        'Compliance' : '1.5m'
        }
    
    VP = {
        'enable' : False,
        'VGstart' : -1.5, 'VGstop' : 1.5, 'VGstep' : 0.01,
        'Ib' : '1e-6', 'Compliance' : 1.5
        }
    
    
    # In[3]:
    
    HP.StopFlag=False
    
    HP.reset()
    
    HP.beep()
    
    # In[ ]:
    
    # prefix=input()
    
    now=datetime.datetime.now().strftime('%y%m%d')
    
    os.makedirs(path, exist_ok=True) 
        
    HP.SetIntTime("LONG")
    HP.ask(":PAGE:MEAS:MSET:ITIM?")
    
    # In[ ]:
    
    if VGS['enable']:
        HP.SetVGS(VGS, ptype)
        
        now=datetime.datetime.now().strftime("%y%m%d %H%M%S")
        plotp=f"{path}{prefix}-{HP.term}-{now}.csv"
        
        now=datetime.datetime.now().strftime("%H%M")
        printf(f"{now} : Parameters VGS\n{VGS}\n", start)
    
        HP.SingleSave(plotp, timeout)
        Vth=PlotVgs(plotp)
        plt.close()
        
        printf(f"Vth={Vth}\n", start, True)
    
    if VGS_sat['enable']:
        HP.SetVGS(VGS_sat, ptype)
    
        now=datetime.datetime.now().strftime("%y%m%d %H%M%S")
        plotp=f"{path}{prefix}-{HP.term}-{now}.csv"

        now=datetime.datetime.now().strftime("%H%M")
        printf(f"{now} : Parameters VGS_sat \n{VGS_sat}\n", start)
        
        HP.SingleSave(plotp, timeout*60)
        PlotVgs(plotp)
        plt.close()

    HP.SetIntTime("MED")
    HP.ask(":PAGE:MEAS:MSET:ITIM?")
   
    if VDS['enable']:
        HP.SetVDS(VDS, ptype)
    
        now=datetime.datetime.now().strftime("%y%m%d %H%M%S")
        plotp=f"{path}{prefix}-{HP.term}-{now}.csv"

        now=datetime.datetime.now().strftime("%H%M")
        printf(f"{now} : Parameters VDS\n{VDS}\n", start)
    
        HP.SingleSave(plotp, timeout*60*7)
        Plot(plotp, 'VD', 'ID')
        plt.close()    
    
    if Ex_Ib['enable']:
        HP.SetEXIB(Ex_Ib, ptype)
    
        now=datetime.datetime.now().strftime("%y%m%d %H%M%S")
        plotp=f"{path}{prefix}-{HP.term}-{now}.csv"

        now=datetime.datetime.now().strftime("%H%M")
        printf(f"{now} : Parameters Is\n{Ex_Ib}\n", start)
       
        HP.SingleSave(plotp, timeout*60*7)
        ibcalc=plotp
        VP['Ib']=-CalcIs(ibcalc, ptype)
        if not ptype: VP['Ib']=-VP['Ib']
        plt.close()
    
    HP.SetIntTime("LONG")
    HP.ask(":PAGE:MEAS:MSET:ITIM?")
    
    if VP['enable']:
        # VP['Ib']=CalcIb(ibcalc, ptype)
        HP.SetVP(VP, ptype)
    
        now=datetime.datetime.now().strftime("%y%m%d %H%M%S")
        plotp=f"{path}{prefix}-{HP.term}-{now}.csv"

        now=datetime.datetime.now().strftime("%H%M")
        printf(f"{now} : Parameters VP\n{VP}\n", start)
        
        HP.SingleSave(plotp, timeout*60)
        Plot(plotp, 'VG', 'VS')
        plt.close()

    if ptype:
        HP.SetDiode(0, 1.5, 0.02)
    else:
        HP.SetDiode(0, -1.5, 0.02)
    HP.SetIntTime("SHOR")
    
    now=datetime.datetime.now().strftime("%y%m%d %H%M%S")
    plotp=f"{path}{prefix}-{HP.term}-{now}.csv"

    HP.SingleSave(plotp, timeout)
    Plot(plotp, "V", ["ID", "IS"])




