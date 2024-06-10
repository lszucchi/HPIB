import numpy as np
import pandas as pd
from scipy.constants import epsilon_0, e, k
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename

e_0=epsilon_0/100
T=300
e_si=11.9
e_sio2=3.9
ni=1.45e10

def IsPType(CV):
    if np.average(CV['C'].to_numpy()[5:10]) > np.average(CV['C'].to_numpy()[-5:-10]):
        return True
    return False

def GetCac(df):
    if IsPType(df):
        return np.average(df['C'].to_numpy()[5:10])
    return np.average(df['C'].to_numpy()[-5:-10])

def GetCinv(df):
    if not IsPType(df):
        return np.average(df['C'].to_numpy()[5:10])
    return np.average(df['C'].to_numpy()[-5:-10])

def CalcTox(Cac, eox, A):
    if isinstance(Cac, pd.DataFrame):
        Cac=GetCac(Cac)   
    if not isinstance(Cac, float):
        return 'Incalid C_ac'
    
    return e_0*eox*A/Cac

def CalcWf(df, eox, A, tox=None):
    Cac=GetCac(df)
    Cinv=GetCinv(df)

    if tox is None:
        tox=CalcTox(Cac, eox, A)

    return (Cac/Cinv-1)*tox

def ItNad(Nad, Wf):
    return (4*e_0*e_si/(e*Wf**2))*(k*T/e)*np.log(Nad/ni)

def CalcNad(Wf):
    Nad=np.array([1e15])
    for i in range(20):
        Nad=np.concatenate((Nad, [ItNad(Nad[-1], Wf)]))
        if np.abs(Nad[i+1]/Nad[i]-1) < 1e-4:
            break
    print(Nad)
    return Nad[-1]

def CalcCfb(tox, e_ox, A, Nad):
    return (e_0*e_si*A)        /             (tox           +             (e_ox/e_si)            *     (e_0*e_si*(k*T/e)/(e*Nad))**2)

def GetVfb(df, Cfb):
    return df[np.argmin(np.abs(df-Cfb))]

def CalcPsi(Nad):
    return (k*T/e)*np.log(Nad/ni)

def CalcQefq(Cac, VB, Nad, A):
    return (VB-CalcPsi(Nad))*(Cac/(e*A))
    
Tk().withdraw()
filename = askopenfilename()

df=pd.read_csv(filename, header=[0, 1])
