import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from HPIB.HPT import Plot, PlotVgs, PlotVp, CalcIsSat, SecDer, Plot2P

from HPIB.DevParams import UMC

from YFunc import YFuncExtraction

from os import makedirs, rename
from time import sleep
from datetime import datetime, timedelta

def WriteLog(msg, path, mode='a', end='\n', output=True):
    with open(path, mode) as logfile:
        logfile.write(msg+end)
    if output:
        print(f"{msg}{end}", end='')

def TestDevice(device, chn, path, params, HiPot=False):
    global HP, INO, Elsa, prog_bar
    INO.opench(chn+1)

    if not device:
        INO.opench(0)
        sleep(2)
        return 0

    if device[:2].upper() not in ['CA', 'CB', 'CG', 'TP', 'TN', 'DP', 'DN']:
        return "Invalid device"

    WriteLog(f"## Ch {chn+1} {device}", path + 'log.txt')
    pathp=path+device
    makedirs(pathp, exist_ok=True)
    
    ####################### Measure Diode
    #
    #
    if 'D' in device.upper():
        
        HP.SetStop("COMP")
        HP.SetIntTime("MED")
        HP.SingleDiode(params['Vfmin'], params['Vfmax'], params['Vfstep'], 'SMU2', 'SMU1', Comp=params['IComp'])
            
        now=datetime.now().strftime('%y%m%d %H%M%S')
        Plot(HP.SingleSave(f"{pathp}/{now}.csv", timeout=30, real=True), 'Vf', 'If')
        try:
            temp=format(Elsa.GetT('t4k'), '07.3f')
            rename(f"{pathp}/{now}.csv", f"{pathp}/{temp} - {now}.csv")
            rename(f"{pathp}/{now}.png", f"{pathp}/{temp} - {now}.png")
        except Exception as e:
            print (">>> Error:", e)
        
        now=datetime.now()

        # with open(f"{pathp}/V100uA.log", 'a') as DiodeParam:
        #     DiodeParam.write(f"{temp},{format(RCB, '.2e')}\n")
            
        while (datetime.now()-now).seconds < params['min_wait']:
            prog_bar.update(f"Waiting: {params['min_wait']-(datetime.now()-start).seconds} s")
            sleep(0.5)
            
        HP.SetStop("OFF")
        HP.SetIntTime("LONG")
        
        INO.opench(0)
        WriteLog('', path + 'log.txt')
        return 0
    #
    #
    #######################

    ####################### Measure Transistor
    #
    #

    if 'T' in device.upper():
        
        ptype='P' in device.upper()
        
        HP.SetVgs(params['Vmin'], params['Vmax'], params['Vstep'], params['Vd'], ptype=ptype)
  
        now=datetime.now().strftime('%y%m%d %H%M')
        LIN = PlotVgs(HP.SingleSave(f"{pathp}/IdVgs - {now}.csv", timeout=30))
        
        try:
            temp=format(Elsa.GetT('t4k'), '07.3f')
            newname=f"{pathp}/IdVgs - {temp} - {now}"
            rename(f"{pathp}/IdVgs - {now}.csv", f"{newname}.csv")
            rename(f"{pathp}/IdVgs - {now}.png", f"{newname}.png")
        except Exception as e:
            print (">>> Error:", e)
        now=datetime.now()

        try:
            LIN, Vth, SS, migm, miyf, theta1, theta2, errmax = YFuncExtraction(f"{newname}.csv", UMC[int(device[2:])], 4.2, 3.9, params['Vd'])
            WriteLog(f"LIN={format(LIN, '.3f')}, Vth={format(Vth, '.3f')} V, SS={format(SS, '.2f')} mV/dec, miyf={format(migm, '.1f')}, miyf={format(miyf, '.1f')}, theta1={format(theta1, '.3e')}, theta2={format(theta2, '.3e')}", path + 'log.txt')
            WriteLog(f"{temp},{format(LIN, '.3f')},{format(Vth, '.3f')},{format(SS, '.2f')},{format(migm, '.1f')},{format(miyf, '.1f')},{format(theta1, '.3e')},{format(theta2, '.3e')}", pathp + '/params.txt')
        except Exception as e:
            print (">>> Error:", e)
            WriteLog(f"Vth={LIN} V", path + 'log.txt')
        
        while (datetime.now()-now).seconds < params['min_wait']:
            prog_bar.update(f"Waiting: {params['min_wait']-(datetime.now()-start).seconds} s")
            sleep(0.5)
            
        if HiPot:
            now=datetime.now().strftime('%y%m%d %H%M')
            HP.SetVgs(params['Vmin'], params['Vmax'], params['Vstep'], params['Vmax'], ptype=ptype, sat=True)
            HP.SingleSave(f"{pathp}/IdVgsSat - {now}.csv", timeout=30)
            try:
                temp=format(Elsa.GetT('t4k'), '07.3f')
                rename(f"{pathp}/IdVgsSat - {now}.csv", f"{pathp}/IdVgsSat - {temp} - {now}.csv")
            except Exception as e:
                print(">>> Error:", e)
            n, Ispec = CalcIsSat(f"{pathp}/IdVgsSat - {temp} - {now}.csv",temp)
            WriteLog(f"n={format(n, '.3f')}, Ispec={format(Ispec, '.3e')} A", path + 'log.txt')

            now=datetime.now()
            while (datetime.now()-now).seconds < 4*params['min_wait']:
                prog_bar.update(f"Waiting: {4*params['min_wait']-(datetime.now()-start).seconds} s")
                sleep(0.5)
            
            if Ispec != 0:
                now=datetime.now().strftime('%y%m%d %H%M')
                HP.SetVp(Ispec, params['Vmin'], params['Vmax'], 0.05, ptype=ptype)
                HP.SingleSave(f"{pathp}/VpVg - {now}.csv", timeout=30)
                try:
                    temp=format(Elsa.GetT('t4k'), '07.3f')
                    rename(f"{pathp}/VpVg - {now}.csv", f"{pathp}/VpVg - {temp} - {now}.csv")
                except Exception as e:
                    print (">>> Error:", e)
                VTO=PlotVp(f"{pathp}/VpVg - {temp} - {now}.csv")
                WriteLog(f"VTO={VTO} V", path + 'log.txt')

                now=datetime.now()
                while (datetime.now()-now).seconds < 4*params['min_wait']:
                    prog_bar.update(f"Waiting: {4*params['min_wait']-(datetime.now()-start).seconds} s")
                    sleep(0.5)

            now=datetime.now().strftime('%y%m%d %H%M')
            HP.SetVds(params['Vmin'], params['Vmax'], params['Vstep'], params['Vgmin'], params['Vgmax'], params['Vgstep'], ptype=ptype)
            HP.SingleSave(f"{pathp}/IdVds - {now}.csv", timeout=30)
            try:
                temp=format(Elsa.GetT('t4k'), '07.3f')
                rename(f"{pathp}/IdVds - {now}.csv", f"{pathp}/IdVds - {temp} - {now}.csv")
            except Exception as e:
                print (">>> Error:", e)
            Plot(f"{pathp}/IdVds - {temp} - {now}.csv", 'Vd', 'Id')
            
            now=datetime.now()
            while (datetime.now()-now).seconds < 4*params['min_wait']:
                prog_bar.update(f"Waiting: {4*params['min_wait']-(datetime.now()-start).seconds} s")
                sleep(0.5)
            
        INO.opench(0)
        WriteLog('', path + 'log.txt')
        return 0
    #
    #
    #######################
        
    ####################### Measure CrossBridge
    #
    #
    if 'CG' in device.upper():
           
        now=datetime.now().strftime('%y%m%d %H%M')
        V10u=HP.MeasV10u(f"{pathp}/2P - {now}.csv", timeout=0.5)
        try:
            temp=format(Elsa.GetT('t4k'), '07.3f')
            rename(f"{pathp}/2P - {now}.csv", f"{pathp}/2P - {temp} - {now}.csv")
            rename(f"{pathp}/2P - {now}.png", f"{pathp}/2P - {temp} - {now}.png")
        except Exception as e:
            print (">>> Error:", e)
        WriteLog(f"V_10u={format(V10u, '.2f')}", path + 'log.txt')
        with open(f"{pathp}/VxT 10uA.log", 'a') as VxT:
            VxT.write(f"{temp},{format(V10u, '.4e')}\n")

    if 'CA' in device.upper():

        HP.Set2P(params['Ifmin']/params['Iffactor'], params['Ifmax']/params['Iffactor'], params['Ifpoints'], SMUN='SMU1', SMUP='SMU2', Comp=params['VComp'])
            
        now=datetime.now().strftime('%y%m%d %H%M')
        Rshort=Plot2P(HP.SingleSave(f"{pathp}/2P - {now}.csv", timeout=30))
        try:
            temp=format(Elsa.GetT('t4k'), '07.3f')
            rename(f"{pathp}/2P - {now}.csv", f"{pathp}/2P - {temp} - {now}.csv")
            rename(f"{pathp}/2P - {now}.png", f"{pathp}/2P - {temp} - {now}.png")
        except Exception as e:
            print (">>> Error:", e)
        WriteLog(f"Rshort={format(Rshort, '.2f')}", path + 'log.txt')
        with open(f"{pathp}/RxT 2P.log", 'a') as RxT2p:
            RxT2p.write(f"{temp},{format(Rshort, '.2f')}\n")

    if 'CB' in device.upper():
    
        HP.Set4P(params['Ifmin'], params['Ifmax'], params['Ifpoints'], Im='SMU1', Ip='SMU2', Comp=params['VComp'])
        
        now=datetime.now().strftime('%y%m%d %H%M')
        RCB=Plot2P(HP.SingleSave(f"{pathp}/4P - {now}.csv", timeout=30))
        try:
            temp=format(Elsa.GetT('t4k'), '07.3f')
            rename(f"{pathp}/4P - {now}.csv", f"{pathp}/4P - {temp} - {now}.csv")
            rename(f"{pathp}/4P - {now}.png", f"{pathp}/4P - {temp} - {now}.png")
        except Exception as e:
            print (">>> Error:", e)
        WriteLog(f"RCB={format(RCB, '.2e')}", path + 'log.txt')
        with open(f"{pathp}/RxT 4P.log", 'a') as RxT4p:
            RxT4p.write(f"{temp},{format(RCB, '.2e')}\n")

    now=datetime.now()
    while (datetime.now()-now).seconds < params['min_wait']:
        prog_bar.update(f"Waiting: {params['min_wait']-(datetime.now()-start).seconds} s")
        sleep(0.5)
            
    INO.opench(0)
    WriteLog('', path + 'log.txt')
    return 0
    #
    #
    #######################