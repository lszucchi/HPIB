import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os, csv

Thr=10
PointsMax=36
PointsDer=4

EarlyLimitDraw=-200

Ut=25e-3

prefix=['f','p','n','u','m','','k','M','G','T','P']

font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 16,
        }

path=".\\231024\\IdxVgs-231024 163936.csv"


def CheckMultilevel(path):
    with open(path, newline='') as f:
      reader = csv.reader(f)
      row1 = next(reader)
    return row1[0]==row1[1]

def ReadDF(path):
    if CheckMultilevel(path):
        return pd.read_csv(path, header=[0, 1])
    return pd.read_csv(path)

def Plot(self, path, X, Y):
    
    df=pd.read_csv(path, header=[0, 1])
    
    if not isinstance(Y, list):
        Y=[Y]

    if len(Y)>2:
        return "Too many traces to plot"
    
    fig, ax1=plt.subplots(dpi=85)
    j, i=PlotMatrix(ax1, df, X, Y[0])
    
    if Y[0][0]=='I': unit='A'
    else: unit='V'
    
    ax1.set_ylabel(f"{Y[0]} ({prefix[i]}{unit})")
    if df.columns.levels[1][0] != 'None':
        ax1.legend([np.around(float(x), 2) for x in df.columns.levels[1]])

    if X[0]=='I': unit='A'
    else: unit='V'
    ax1.set_xlabel(f"{X} ({prefix[j]}{unit})")

    if len(Y)==2:
        ax2=ax1.twinx()
        j, i=PlotMatrix(ax2, df, X, Y[1])
        plt.setp(ax2.get_lines()[0], linestyle="--", color='r')
        if Y[1][0]=='I': unit='A'
        else: unit='V'
        ax2.set_ylabel(f"{Y[1]} ({prefix[i]}{unit})", color='r')

    
        
    name, _=path.rsplit('.',1)
    name=name+'.png'
    fig.show()
    plt.savefig(name)
    return name

def PlotMatrix(ax, df, X, Y):
    X=df[X]
    Y=df[Y]
    
    i=5
    j=5

    while np.max(Y) > 100:
        i+=1
        Y=Y*1e-3
    while np.max(Y) < 0.1:
        i-=1
        Y=Y*1e3

    while np.max(X) > 100:
        j+=1
        X=X*1e-3
    while np.max(Y) < 0.1:
        j-=1
        X=X*1e3
    
    ax.plot(X, Y)
    return (j, i)

def PlotDiode(path,draw=False):
    df = pd.read_csv(path)
    VD=df['Vf']
    ID=df['If']
    if (path[len(path)-11] == 'D'):
        path=path[:len(p)-11]+"S"+path[len(p)-10:]
    elif (path[len(path)-11] == 'S'):
        path=path[:len(p)-11]+"D"+path[len(p)-10:]
    df = pd.read_csv (path)
    VS=df['Vf']
    IS=df['If']
    VD=VD.to_numpy()
    ID=ID.to_numpy()
    VS=VS.to_numpy()
    IS=IS.to_numpy()
    

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.grid(True, which='both')

    ax1.plot(VD, ID, 'b')

    ax2.plot(VS, IS, 'r--')
    
    ax1.set_xlabel('V')
    ax1.set_xlim(np.min(VD), np.max(VD))
    ax1.set_ylabel('I_D', color='b')

    
    
##    if(np.abs(np.min(ID))>np.abs(np.max(ID))):
##        ax1.set_ylim(1.1*np.min(ID), -0.05*np.min(ID))
##    else:
##        ax1.set_ylim(-0.05*np.max(ID), 1.1*np.max(ID))
        
    ax2.set_ylabel('IS', color='r')
    
##    if(np.abs(np.min(IS))>np.abs(np.max(IS))):
##        ax1.set_ylim(1.1*np.min(IS), -0.05*np.min(IS))
##    else:
##        ax1.set_ylim(-0.05*np.max(IS), 1.1*np.max(IS))
    if not os.path.isdir(path.rsplit('/',1)[0]+'/fig/'):
        os.mkdir(path.rsplit('/',1)[0]+'/fig/')
    save_path=path.rsplit('/',1)[0]+'/fig/'+path.rsplit('/',1)[1].strip(".csv")+'.png'
    plt.savefig(save_path)
    
    if(draw):
        plt.draw()
        plt.pause(0.001)
    #plt.close()
    return save_path

def PlotVgs(path,draw=False):

    try: df=pd.read_csv(path, header=[0, 1])
    except: print("Error opening VGS\n")
    VG=df['VG']
    ID=df['ID']
    VG=VG.to_numpy()[0]
    ID=ID.to_numpy()[0]
    
    gm=np.diff(ID)/np.diff(VG)

    VGfit=VG[np.argmax(gm)-1:np.argmax(gm)+1]
    IDfit=ID[np.argmax(gm)-1:np.argmax(gm)+1]

    m, b= np.polyfit(VGfit, IDfit, 1)
    VTO=-b/m
    fitID=m*VG[:np.argmax(gm)]+b

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.grid(True, which='both')
    ax1.axhline(y=0, color='k', linewidth=.5)
    ax1.plot(VG, ID, 'b-', VG[:np.argmax(gm)], fitID,'r--')

    ax2.plot(VG[1:], gm, 'r-')
    ax1.set_xlabel('V_GS')
    ax1.set_xlim(np.min(VG), np.max(VG))
    ax1.set_ylabel('I_D', color='b')
    
    if(np.abs(np.min(ID))>np.abs(np.max(ID))):
        ax1.set_ylim(1.1*np.min(ID), -0.05*np.min(ID))
    else:
        ax1.set_ylim(-0.05*np.max(ID), 1.1*np.max(ID))
        
    ax2.set_ylabel('g_m', color='r')
    ax2.set_ylim(-0.05*np.max(gm), 1.1*np.max(gm))
    
    if not os.path.isdir(path.rsplit('/',1)[0]+'/fig/'):
        os.mkdir(path.rsplit('/',1)[0]+'/fig/')
    save_path=path.rsplit('/',1)[0]+'/fig/'+path.rsplit('/',1)[1].rsplit('.',1)[0]+'.png'
    plt.savefig(save_path)    

    if(draw):
        plt.draw()
        plt.pause(0.001)
    #plt.close()
    return save_path

def PlotVds(path,draw=False):
    try: df = pd.read_csv (path)
    except: print("Error opening Vds\n")
    VG=df['VG']
    VD=df['VD']
    ID=df['ID']
    VG=VG.to_numpy()
    VD=VD.to_numpy()
    ID=ID.to_numpy()

    for i in range(len(VD)):
        if(abs(Thr*VD[i+1])<abs(VD[i])):
            IDS=np.split(ID, len(ID)/(i+1))
            VDS=VD[:i+1]
            VGS=np.empty(int(len(VG)/(i+1)))
            for j in range(int(len(VG)/(i+1))):
                VGS[j]=VG[(i+1)*j]
            break

    if np.max(IDS) < 1e-3:
        IDS=np.multiply(IDS, 1e6)
        ILabel=ILabel="$I_D$ (uA)"
    elif np.max(IDS) < 1:
        IDS=np.multiply(IDS, 1e3)
        ILabel="$I_D$ (mA)"
    else:
        ILabel="$I_D$ (A)"

    fig2, ax1 = plt.subplots()
    for i in range(len(VGS)):
        plt.plot(VDS,IDS[i])
    
    plt.grid(True, which='both')

    plt.xlabel("$V_D$ (V)", fontdict=font)
    plt.ylabel(ILabel, fontdict=font)
    
    if(np.abs(np.min(ID))>np.abs(np.max(ID))):
        plt.ylim(1.1*np.min(IDS), -0.05*np.min(IDS))
    else:
        plt.ylim(-0.05*np.max(IDS), 1.1*np.max(IDS))
    plt.xlim(np.min(VD), np.max(VD))
    
    if not os.path.isdir(path.rsplit('/',1)[0]+'/fig/'):
        os.mkdir(path.rsplit('/',1)[0]+'/fig/')
    save_path=path.rsplit('/',1)[0]+'/fig/'+path.rsplit('/',1)[1].rsplit('.',1)[0]+'.png'
    plt.savefig(save_path)    
    
    if(draw):
        plt.draw()
        plt.pause(0.001)
    #plt.close()
    return save_path

def Plot4P(path,dop,draw=False):
    df = pd.read_csv(path)
    X=df['V']
    Y=df['I1']
    X=X.to_numpy()
    Y=Y.to_numpy()

    plt.grid(True, which='both')
    plt.xlabel('V')
    plt.ylabel('I')
    plt.ylim(np.min(Y), np.max(Y))
    plt.xlim(np.min(X), np.max(X))
    print("Enter wafer thickness (um):")
    
    fit=np.polyfit(X, Y, 1)

    t=int(input())
    print(f"t={t} um")
    plt.text(0.95*np.min(X), 0.9*np.max(Y), f"t={t} um")
        
    Rs=np.around(1/fit[0], 2)
    print(f"1/grad={Rs} ohm")
    plt.text(0.95*np.min(X), 0.8*np.max(Y), f"1/grad={Rs} ohm")
    
    ro=np.around(Rs*4.53*t*1e-4, 2)
    print(f"ro={ro} ohm.cm\n")
    plt.text(0.95*np.min(X), 0.7*np.max(Y), f"ro={ro} ohm.cm")
    
    conc=GetConc(ro, dop)
    print("C("+ dop +f")={conc} cm-3\n")
    plt.text(0.95*np.min(X), 0.6*np.max(Y), "C("+ dop +f")={conc} cm-3")

    plt.plot(X,Y,'bx')
    plt.plot(X, X*fit[0]+fit[1], 'r')

    if not os.path.isdir(path.rsplit('/',1)[0]+'/fig/'):
        os.mkdir(path.rsplit('/',1)[0]+'/fig/')
    save_path=path.rsplit('/',1)[0]+'/fig/'+path.rsplit('/',1)[1].rsplit('.',1)[0]+'.png'
    plt.savefig(save_path)    
    
    if(draw):
        plt.draw()
        plt.pause(0.001)
    #plt.close()
    return save_path

def PlotArb(nameX,nameY,path,draw=False,params="k"):
    df = pd.read_csv(path)
    X=df[nameX]
    Y=df[nameY]
    X=X.to_numpy()
    Y=Y.to_numpy()

    plt.grid(True, which='both')
    plt.xlabel(nameX)
    plt.ylabel(nameY)
    plt.ylim(np.min(Y), np.max(Y))
    plt.xlim(np.min(X), np.max(X))

    plt.plot(X,Y,params)

    if not os.path.isdir(path.rsplit('/',1)[0]+'/fig/'):
        os.mkdir(path.rsplit('/',1)[0]+'/fig/')
    save_path=path.rsplit('/',1)[0]+'/fig/'+path.rsplit('/',1)[1].rsplit('.',1)[0]+'.png'
    plt.savefig(save_path)    
    
    if(draw):
        plt.draw()
        plt.pause(0.001)
    #plt.close()
    return save_path
    

def PlotAll(no,path='.',save=".",diode=False,draw=False):

    for i in range(1, 7):
        if(diode):
            PlotDiode(i,path,save, draw)
        PlotVgs(i,path,save,draw)
        PlotVds(i,path,save,draw)

def Ex_Ib(path, ptype=False, draw=False):
    df = pd.read_csv (path)
    VS=df['VS']
    #VG=df['VG']
    ID=df['ID']
    print(df[''])
    VS=VS.to_numpy()
    ID=ID.to_numpy()
    if ptype:
        VS=-VS
        ID=-ID
    i=1
    while VS[i-1] < VS[i]:
        i=i+1
    
    X=np.split(VS,len(VS)/i)
    Y=np.split(ID,len(ID)/i)


    m=np.empty(2)
    for i, x in enumerate(X):
        
        plt.plot(x, Y[i])
        if i==2:
            break
        y=Y[i]
        y=y[y>max(y)/1.5]
        x=x[:len(y)]
        plt.plot(x, y, '--')
        m[i], b= np.polyfit(x, y, 1)
        plt.plot(X[i], np.polyval([m[i], b], X[i]))
    print(m)
    if draw:
        plt.draw()
        plt.pause(0.001)

    Is=(np.average(m)*2*Ut)**2

    return Is

def Early():
    fig2 = plt.figure()
    Early=np.empty(len(VGS))
    EarlyFit=np.empty([len(VGS),2])
    for i in range(len(VGS)):
        Xfit=VDS[len(VDS)-(PointsMax-i*PointsDer):]
        Yfit=IDS[i][len(IDS[i])-(PointsMax-i*PointsDer):]
        EarlyFit[i]= np.polyfit(Xfit, Yfit, 1)
        Early[i]=-EarlyFit[i][1]/EarlyFit[i][0]

        #fig1 = plt.figure()
    #for i in range(len(VGS)):
        plt.plot(VDS,IDS[i])

        #fig2 = plt.figure()
    #for i in range(len(VGS)):
        xearly=np.arange(np.max(VDS)+1,step=1)
        if Early[i]<EarlyLimitDraw:   
            fitFunc=EarlyFit[i][0]*xearly+EarlyFit[i][1]
            plt.plot(xearly,fitFunc,'--',color='black')
        
        xearly=np.arange(-1,np.nanmin(Early)*1.1,step=-10)
        if Early[i]<EarlyLimitDraw:
            fitFunc=EarlyFit[i][0]*xearly+EarlyFit[i][1]
            plt.plot(-np.log10(-xearly),fitFunc,'--',color='black')
        plt.plot(-np.log10(-xearly),0*xearly,color='black')

    EarlyClean=Early[Early < EarlyLimitAvg]
    EarlyAvg=np.average(EarlyClean)

    print(Early)
    print(EarlyAvg)


def GetConc(x, dop):
        if dop=='n':
            ans=np.polyval([ 5.61452759e-05, -1.39752440e-03, -5.24350741e-03,  8.44089739e-02,  -1.19024289e+00,  1.57227877e+01], np.log10(x))
        elif dop=='p':
            ans=np.polyval([-1.97255540e-04, -1.21836929e-03,  5.31204434e-03,  5.89486239e-02,  -1.19702991e+00,  1.62610457e+01], np.log10(x))
        else:
            return 'Invalid dopant'
        
        if 10 < ans < 21:
                return '{:.1e}'.format(10**ans)
        else:
            return 'Outside of range'

        
##C=[10,11,12,13,14,15,16,17,18,19,20,21]
##roP=np.log10([2.47610e5, 43606.3,4415.312387249216,442.0453159585842,44.4686935514397,4.582406466927884,0.527248940805391,0.08652951931265407,0.022535571622752913,0.005437594960591998, 8.48506e-4, 3.12902e-4])
##roB=np.log10([3.95729e5, 1.27926e5, 14667.262500697669,1467.6130226932708,147.2256168021463,14.965676972314505,1.6238443702134566,0.21496536080345086,0.04191163444675014,0.00886221011340648, 0.00126728, 2.55205e-4])
##order=5
##plt.plot(roP, C, 'xr', roP, np.polyval(np.polyfit(roP, C, order), roP), 'r', roB, C, 'xb', roB, np.polyval(np.polyfit(roB, C, order), roB), 'b')
##plt.grid(True, linestyle=':')
##plt.text(0.75*np.max(roP), 0.92*np.max(C), "n-type", fontdict=font, color='red')
##plt.text(0.75*np.max(roP), 0.87*np.max(C), "p-type", fontdict=font, color='blue')
##plt.xlabel("Resistivity (log)",fontdict=font)
##plt.ylabel("Dopant Concentration (log)",fontdict=font)\
##
##plt.show()

##https://cleanroom.byu.edu/resistivitycal (12~19)
##https://www.pvlighthouse.com.au/resistivity
  
##
##VGfit=VG[np.argmax(gm)-1:np.argmax(gm)+1]
##IDfit=ID[np.argmax(gm)-1:np.argmax(gm)+1]
##
##m, b= np.polyfit(VGfit, IDfit, 1)
##VTO=-b/m
##
##fitID=m*VG[:np.argmax(gm)]+b
##
##fig, ax1 = plt.subplots()
##ax2 = ax1.twinx()
##ax1.plot(VG, ID, 'b-', VG[:np.argmax(gm)], fitID,'g--')
##ax2.plot(VG[1:], gm, 'r-')
##ax1.set_xlabel('V_GS')
##ax1.set_xlim((0, 6))
##ax1.set_ylabel('I_D', color='b')
##ax1.set_ylim((0, 1.5e-5))
##ax2.set_ylabel('g_m', color='r')
##ax2.set_ylim((0, 3.5e-6))
##plt.show()
