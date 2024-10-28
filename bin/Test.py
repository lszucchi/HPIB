def WriteLog(msg, path, mode='a', end='\n', output=True):
    with open(path, mode) as logfile:
        logfile.write(msg+end)
    if output:
        print(f"{msg}{end}", end='')

def TestDevice(device, chn, path, params):
    global HP, INO, Elsa, prog_bar
    print(INO.opench(chn+1))

    if not device:
        print(INO.opench(0))
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
        except: 
            pass
        
        now=datetime.now()

        # with open(f"{pathp}/V100uA.log", 'a') as DiodeParam:
        #     DiodeParam.write(f"{temp},{format(RCB, '.2e')}\n")
            
        while True:
            if (datetime.now()-now).seconds > params['min_wait']: break
            prog_bar.update(f"{datetime.now().strftime('%H:%M:%S')} Waiting minimum {params['min_wait']}s")
            sleep(0.5)
            
        HP.SetStop("OFF")
        HP.SetIntTime("LONG")
        
        print(INO.opench(0))
        WriteLog('', path + 'log.txt')
        return 0
    #
    #
    #######################

    ####################### Measure Transistor
    #
    #

    if 'T' in device.upper():
        
        ptype='P' in device.upper()()
        
        HP.SetVgs(params['Vmin'], params['Vmax'], params['Vstep'], params['Vd'], ptype=ptype)
  
        now=datetime.now().strftime('%y%m%d %H%M')
        LIN = PlotVgs(HP.SingleSave(f"{pathp}/IdVgs - {now}.csv", timeout=30))
        temp=format(Elsa.GetT('t4k'), '07.3f')
        try:
            newname=f"{pathp}/IdVgs - {temp} - {now}"
            rename(f"{pathp}/IdVgs - {now}.csv", f"{newname}.csv")
            rename(f"{pathp}/IdVgs - {now}.png", f"{newname}.png")
        except:
            pass
        now=datetime.now()
            
        WriteLog(f"Vth={LIN} V", path + 'log.txt')
        try:
            DGM=SecDer(f"{newname}.csv")
            WriteLog(f"SecDer={format(DGM, '.2f')} V", path + 'log.txt')
        except:
            WriteLog(f"SecDer Fail", path + 'log.txt')

        try:
            LIN, Vth, SS, migm, miyf, theta1, theta2, errmax = YFuncExtraction(f"{newname}.csv", UMC[int(device[2:])], 4.2, 3.9, params['Vd'])
            WriteLog(f"LIN={format(LIN, '.2f')}, Vth={format(Vth, '.2f')} V, SS={format(SS, '.1f')} mV/dec, miyf={format(migm, '.1f')}, miyf={format(miyf, '.1f')}, theta1={format(theta1, '.3e')}, theta2={format(theta2, '.3e')}", path + 'log.txt')
            WriteLog(f"{temp},{format(LIN, '.2f')},{format(Vth, '.2f')},{format(SS, '.1f')},{format(migm, '.1f')},{format(miyf, '.1f')},{format(theta1, '.3e')},{format(theta2, '.3e')}", pathp + '/params.txt')
        except:
            WriteLog(f"YFunc Fail", path + 'log.txt')
        
        while True:
            if (datetime.now()-now).seconds > params['min_wait']: break
            prog_bar.update(f"{datetime.now().strftime('%H:%M:%S')} Waiting minimum {params['min_wait']}s")
            sleep(0.5)
            
        if False:
            HP.SetVgs(params['Vmin'], params['Vmax'], params['Vstep'], params['Vmax'], ptype=ptype, sat=True)
            n, Ispec = CalcIsSat(HP.SingleSave(f"{pathp}/IdVgsSat - {now}.csv", timeout=30), Elsa.GetT('t4k'))
            rename(f"{pathp}/IdVgsSat - {now}.csv", f"{pathp}/IdVgsSat - {format(Elsa.GetT('t4k'), '07.3f')} - {now}.csv")
            WriteLog(f"n={format(n, '.3f')}, Ispec={format(Ispec, '.3e')} A", path + 'log.txt')
            sleep(60)
            
            if Ispec != 0:
                HP.SetVp(Ispec, params['Vmin'], params['Vmax'], 0.05, ptype=ptype)
                VTO=PlotVp(HP.SingleSave(f"{pathp}/VpVg - {now}.csv", timeout=30))
                rename(f"{pathp}/VpVg - {now}.csv", f"{pathp}/VpVg - {format(Elsa.GetT('t4k'), '07.3f')} - {now}.csv")
                WriteLog(f"VTO={VTO} V", path + 'log.txt')
                sleep(60)
                
            HP.SetVds(params['Vmin'], params['Vmax'], params['Vstep'], params['Vgmin'], params['Vgmax'], params['Vgstep'], ptype=ptype)
            Plot(HP.SingleSave(f"{pathp}/IdVds - {now}.csv", timeout=30), 'Vd', 'Id')
            rename(f"{pathp}/IdVds - {now}.csv", f"{pathp}/IdVds - {format(Elsa.GetT('t4k'), '07.3f')} - {now}.csv")
            sleep(60)
            
        print(INO.opench(0))
        WriteLog('', path + 'log.txt')
        return 0
    #
    #
    #######################
        
    ####################### Measure CrossBridge
    #
    #
    if 'C' in device.upper():

        HP.Set2P(params['Ifmin']/params['Iffactor'], params['Ifmax']/params['Iffactor'], params['Ifpoints'], SMUN='SMU1', SMUP='SMU2', Comp=params['VComp'])
            
        now=datetime.now().strftime('%y%m%d %H%M')
        Rshort=Plot2P(HP.SingleSave(f"{pathp}/2P - {now}.csv", timeout=30))
        try:
            temp=format(Elsa.GetT('t4k'), '07.3f')
            rename(f"{pathp}/2P - {now}.csv", f"{pathp}/2P - {temp} - {now}.csv")
            rename(f"{pathp}/2P - {now}.png", f"{pathp}/2P - {temp} - {now}.png")
        except:
            pass
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
        except:
            pass
        WriteLog(f"RCB={format(RCB, '.2e')}", path + 'log.txt')
        with open(f"{pathp}/RxT 4P.log", 'a') as RxT4p:
            RxT4p.write(f"{temp},{format(RCB, '.2e')}\n")

    now=datetime.now()
    while True:
        if (datetime.now()-now).seconds > params['min_wait']: break
        prog_bar.update(f"{datetime.now().strftime('%H:%M:%S')} Waiting minimum {params['min_wait']}s")
        sleep(0.5)
            
    print(INO.opench(0))
    WriteLog('', path + 'log.txt')
    return 0
    #
    #
    #######################