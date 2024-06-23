import os, csv

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.constants import e, k
from scipy.special import lambertw
from scipy.optimize import least_squares

px = 1/plt.rcParams['figure.dpi']

Thr=10
PointsMax=36
PointsDer=4

EarlyLimitDraw=-200

Ut=k*300/e
Ut4=k*4/e

prefix=['f','p','n','u','m','','k','M','G','T','P']

font = {'family': 'serif',
        'color':  'black',
        'weight': 'normal',
        'size': 16,
        }

def getpd(df, trace):
    return df[trace][df[trace].columns[0]].to_numpy()

def Id(p, VG, T):
    I0, theta, K, n = p
    x=(1+theta*VG)
    return (I0/x)*lambertw(K*x*np.exp(VG/(n*k*T/e)))

def Vg(p, ID, T):
    I0, theta, K, n = p
    vth=k*T/e
    
    return (n*vth*np.log(ID)+(n*vth/I0)*ID-n*vth*np.log(K*I0))/(1-((n*vth*theta)/I0)*ID)

def fun(p, ID, VG, T):
    return Vg(p, ID, T)-VG

def getvar2(df, trace):
    df2=pd.DataFrame(df.columns.tolist()[1:], columns=df.columns.tolist()[0])
    try:
        var2=df2[trace].to_numpy(dtype=float)
        if var2[0]==var2[1]:
            return var2[0]
        return var2
    except:
        return None

def Plot(df, X, Y, sizex=640, bar='none'):
    if bar not in ['none', 'hori', 'vert', 'both']:
        return 'Invalid bar'
    
    if isinstance(df, str):
        path=df
        df=pd.read_csv(df, header=[0, 1])
    
    if not isinstance(Y, list):
        Y=[Y]

    if len(Y)>2:
        return "Too many traces to plot"
    
    fig, ax1=plt.subplots(figsize=(sizex*px,(sizex*480/640)*px))
    plt.autoscale(tight=True)
    plt.subplots_adjust(left = 0.125,  # the left side of the subplots of the figure
                            right = 0.95,  # the right side of the subplots of the figure
                            bottom = 0.1,  # the bottom of the subplots of the figure
                            top = 0.9)     # the top of the subplots of the figure)
    
    j, i=PlotMatrix(ax1, df, X, Y[0])

    if bar in ['both', 'hori']:
        ax1.plot([0 for x in getpd(df, Y[0])], getpd(df, Y[0]), 'k')

    if bar in ['both', 'vert']:
        ax1.plot(getpd(df, X), [0 for x in getpd(df, X)], 'k')


    if X[0]=='I': unit='A'
    else: unit='V'
    
    ax1.set_xlabel(f"${X[0]}_"+'{'+X[1:]+'}$'+f" ({prefix[j]}{unit})")

    if Y[0][0]=='I': unit='A'
    elif Y[0][0]=='C': unit='F'
    else: unit='V'
    
    ax1.set_ylabel(f"${Y[0][0]}_"+'{'+Y[0][1:]+'}$'+f" ({prefix[i]}{unit})", color='r')

    ax1.set_title(f"${Y[0][0]}_"+'{'+Y[0][1:]+'}$' + ' vs ' + f"${X[0]}_"+'{'+X[1:]+'}$')
    
    if len(Y)==2:
        ax2=ax1.twinx()
        j, i=PlotMatrix(ax2, df, X, Y[1])
        plt.setp(ax2.get_lines()[0], linestyle="--", color='r')
        
        if Y[1][0]=='I': unit='A'
        elif Y[1][0]=='g': unit='S'
        else: unit='V'
            
        ax2.set_ylabel(f"${Y[1][0]}_"+'{'+Y[1][1:]+'}$'+f" ({prefix[i]}{unit})", color='r')
        plt.subplots_adjust(right = 0.875)
        ax1.set_title(f"${Y[0][0]}_"+'{'+Y[0][1:]+'}$, ' + f"${Y[1][0]}_"+'{'+Y[1][1:]+'}$' + ' vs ' + f"${X[0]}_"+'{'+X[1:]+'}$')


    #################################### Legend ######################################
    if df.columns.levels[1][0] != 'None':
        title=df.columns[0][1]
    
        if title=='I': unit='A'
        else: unit='V'
        
        title=f"${title[0]}_"+'{'+title[1:]+'}$' + f" ({unit})"
        try:
            lege=[np.around(float(ETF(x)), 3) 
                for x in df.columns.levels[1][:-1]]
        except:
            lege=[np.around(float(ETF(x)), 3) 
                for x in df.columns.levels[1][1:]]
            
        ax1.legend(lege,
            title=title,
            loc='upper left', bbox_to_anchor=(0, 1)) 
            # fancybox=True, shadow=True)    
    try:
        name, _=path.rsplit('.',1)
        name+=".png"
        
        if '/csv/' in name:
            name=name.replace('csv/', '')
            
        plt.savefig(name)
        
        return name
    except:
        pass
        

def PlotMatrix(ax, df, X, Y):
    X=df[X]
    Y=df[Y]
    
    i=5
    j=5

    while np.max(np.abs(Y)) > 300:
        i+=1
        Y=Y*1e-3
    while np.max(np.abs(Y)) < 0.3:
        i-=1
        Y=Y*1e3

    while np.max(np.abs(X)) > 300:
        j+=1
        X=X*1e-3
    while np.max(np.abs(X)) < 0.3:
        j-=1
        X=X*1e3
    
    ax.plot(X, Y)
    
    return (j, i)

def PlotDiode(path, draw=False):
    df = pd.read_csv(path)
    VS=df['Vf']
    IS=df['Is']
    ID=df['Id']
    
    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.grid(True, which='both')

    ax1.plot(VS, ID, 'b')

    ax2.plot(VS, IS, 'r--')
    
    ax1.set_xlabel('V')
    ax1.set_xlim(np.min(VS), np.max(VS))
    ax1.set_ylabel('I_D', color='b')

    if(np.abs(np.min(ID))>np.abs(np.max(ID))):
       ax1.set_ylim(1.1*np.min(ID), -0.05*np.min(ID))
    else:
       ax1.set_ylim(-0.05*np.max(ID), 1.1*np.max(ID))
        
    ax2.set_ylabel('Is', color='r')
    
    if(np.abs(np.min(IS))>np.abs(np.max(IS))):
       ax1.set_ylim(1.1*np.min(IS), -0.05*np.min(IS))
    else:
       ax1.set_ylim(-0.05*np.max(IS), 1.1*np.max(IS))
    
    if(draw):
        plt.draw()
        plt.pause(0.001)

    return save_path # type: ignore

def PlotVgs(path, sizex=640, draw=False):

    try: df=pd.read_csv(path, header=[0, 1])
    except: print("Error opening VGS\n")
        
    if df.columns.levels[1][0] != 'None':
        df.columns.levels[1][0] != ''
    
    VG=getpd(df, 'Vg')
    VD=float(df.columns.levels[1][0])
    ID=getpd(df, 'Id')
    
    
    if 'gm' not in df.columns:
        gm=(np.diff(df['Id'].T)/np.diff(df['Vg'].T)).T
        gm=np.append([gm[0]], gm)
    
        header=pd.MultiIndex.from_product([['gm'],
                                    df['Vg'].columns])
    
        df2=pd.DataFrame(data=gm, columns=header)
        df=pd.concat((df, df2), axis=1)
    
        df.to_csv(path, index=False, float_format='%.5E')
    else:
        gm=getpd(df, 'gm')
    
    if 'dgm' not in df.columns:
        dgm=(np.diff(df['gm'].T)/np.diff(df['Vg'].T)).T
        dgm=np.append(dgm, [dgm[-1]])
    
        header=pd.MultiIndex.from_product([['dgm'],
                                    df['Vg'].columns])
    
        df2=pd.DataFrame(data=dgm, columns=header)
        df=pd.concat((df, df2), axis=1)
    
        df.to_csv(path, index=False, float_format='%.5E')
    else:
        dgm=getpd(df, 'dgm')
    
    VGfit=VG[np.argmax(gm)-2:np.argmax(gm)+2]
    IDfit=ID[np.argmax(gm)-2:np.argmax(gm)+2]
    
    m, b= np.polyfit(VGfit, IDfit, 1)
    LIN=-b/m+VD/2
    fitID=m*VG[:np.argmax(gm)]+b
    
    Plot(path, 'Vg', ['Id', 'gm'], sizex=sizex)
    
    for n, V in enumerate(VG):
        if V > LIN:
            break
    
    Vgfit=VG[n-20:n+50]
    Idfit=ID[n-20:n+50]
    
    p0=[1e-6, 0, 1, 1]
    res=least_squares(fun, p0, args=(Idfit, Vgfit, 300), loss='huber')
    
    dgmfit=np.diff(Id(res.x, Vgfit, 300), n=2)/(np.diff(Vgfit)[:-1]**2)
        
    fig1, ax1=plt.subplots()
    fig2, ax2=plt.subplots()
    fig3, ax3=plt.subplots()
    
    ax1.plot(VG, ID)
    ax1.set_ylim(0, ax1.get_ylim()[1])
    ax1.plot(VG, VG*m+b, '--r')
    
    
    ax2.plot(VG, ID)
    ax2.plot(Vg(res.x, Idfit, 300), Idfit, '--r')
    
    ax3.plot(VG, dgm)
    ax3.plot(Vgfit[1:-1], np.diff(Id(res.x, Vgfit, 300), n=2)/(np.diff(Vgfit)[:-1]**2), 'r--')
    
    DGM=Vgfit[np.argmax(dgmfit)]
    
    return [np.around(LIN, 3), DGM]

def PlotSubVt(path):

    try: df=pd.read_csv(path, header=[0, 1])
    except: print("Error opening VGS\n")
    if df.columns.levels[1][0] != 'None':
        df.columns.levels[1][0] != ''
        
    VG=df['Vg'][df.columns.levels[1][0]].to_numpy()
    ID=np.clip(df['Id'][df.columns.levels[1][0]].to_numpy(), 1e-15, 1)

    median=int(len(VG)/2)
    th=5
    
    VGfit=VG[median-th:median+th]    
    IDfit=ID[median-th:median+th]

    p = np.polyfit(VGfit, np.log10(IDfit), 1)

    # IDfit=m*VGfit+b
    
    fig, ax1 = plt.subplots()

    print(np.polyval(p, VGfit))
    
    ax1.plot(VG, ID)
    ax1.plot(VGfit, 10**np.polyval(p, VGfit), '--r')
    
    ax1.grid(True, which='both')
    ax1.axhline(y=0, color='k', linewidth=.5)

    ax1.set_xlabel('$V_{GS}$')
    ax1.set_ylabel('$I_D$', color='b')

    ax1.set_yscale('log')
    
    if not os.path.isdir(path.rsplit('/',1)[0]+'/fig/'):
        os.mkdir(path.rsplit('/',1)[0]+'/fig/')
    save_path=path.rsplit('/',1)[0]+'/fig/'+path.rsplit('/',1)[1].rsplit('.',1)[0]+'.png'
    
    plt.savefig(save_path)    

    return np.around((1/p[0])*1000, 0)

def PlotVp(path):
    try: df=pd.read_csv(path, header=[0, 1])
    except: print("Error opening VGS\n")
        
    if df.columns.levels[1][0] != 'None':
        df.columns.levels[1][0] != ''
    
    VG=getpd(df, 'Vg')
    VS=getpd(df, 'Vs')

    Plot(path, 'Vg', 'Vs', bar='both')
    
    return VG[np.argmin(np.abs(VS))]
    

def Plot2P(path):
    try: df=pd.read_csv(path, header=[0, 1])
    except: print("Error opening CSV\n")

    V=df['Vf'][df.columns.levels[1][0]].to_numpy()
    I=df['If'][df.columns.levels[1][0]].to_numpy()

    m, b = np.polyfit(I, V, 1)

    Plot(path, "Vf", "If")
    
    return m

def PlotSi4P(path,dop,draw=False):
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

def Early():
    VDS=0
    VGS=0
    IDS=0
    EarlyLimitAvg=0

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

def CalcIs(path, T, ptype=False):
    
    df = pd.read_csv(path, header=[0, 1])
    try: VG=[np.around(float(x), 2) for x in df.columns.levels[1][1:]]
    except: VG=[np.around(float(x), 2) for x in df.columns.levels[1][:-1]]
        
    VS=df['Vs']
    ID=df['Id']
    
    if ptype:
        VS=-VS
        ID=-ID
        
    ID=np.sqrt(np.clip(ID, 0, 1))

    slope=[]

    fig, ax=plt.subplots()
    
    for n, key in enumerate(VG):
    
        Y=ID[ID.columns[n]]
        X=VS[ID.columns[n]]
        ax.plot(X, Y, label=key)
        
        y=Y
        y=y[y>np.max(y)/(2+0.3*n)]
        x=X[:len(y)]
        
        ax.plot(x, y, '--')
        m, b= np.polyfit(x, y, 1)
        # ax.plot(VS[:len(x)], np.polyval([m, b], VS[:len(x)]))
        slope+=[m]

    plt.legend(title='$V_{G}$', loc='upper right')
    ax.set_ylabel("$\sqrt{I_D}$  ($\sqrt{A}$)")
    ax.set_xlabel("$V_S$  (V)")
    ax.set_title("$\sqrt{I_D}$ vs $V_S$")

    Is=(np.array(slope)*2*k*T/e)**2
    if not ptype: Is=-Is
    # print(Is)
    
    # print(f"Is={format(np.average(Is), '.2e')}   R2: {np.sum((Is-np.average(Is))**2)}")
    fig.savefig(os.path.splitext(path)[0])
    
    return np.average(Is)

def frange(start, stop, step, eps=1e-5):
    out=np.arange(start, stop+step, step)
    if abs(out[-1]-stop)<eps: return out
    else: return out[:-1]

def ETF(value):
    try: return float(value)
    except:
        pass
    exp=value[len(value)-1]
    try: value=np.around(float(value[:-1]), 1)
    except:
        return "Invalid mantissa"

    match exp:
        case 'P':
            return float(str(value)+'e15')
        case 'T':
            return float(str(value)+'e12')
        case 'G':
            return float(str(value)+'e9')
        case 'M':
            return float(str(value)+'e6')
        case 'k':
            return float(str(value)+'e3')
        
        #0#
        
        case 'm':
            return float(str(value)+'e-3')
        case 'u':
            return float(str(value)+'e-6')
        case 'n':
            return float(str(value)+'e-9')
        case 'p':
            return float(str(value)+'e-12')
        case 'f':
            return float(str(value)+'e-15')
        
    return "Invalid expoent"

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
        
def ScaleTrace(path, scaling, tracelist):
    df=pd.read_csv(path, header=[0, 1])
    out_path="-raw".join(os.path.splitext(path))
    df.to_csv(out_path, index=False, float_format='%.5E')
    for trace in tracelist:
        df[trace]=df[trace]*scaling
    df.to_csv(path, index=False, float_format='%.5E')

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
