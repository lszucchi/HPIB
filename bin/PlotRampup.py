import sys, os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
sys.path.append("./modules")

from HPIB_plot import *

def moving_average(x, n=3):
    return np.convolve(x, np.ones(n), 'valid') / n

def getpd(df, trace):
    return df[trace][df[trace].columns[0]].to_numpy()

root = tk.Tk()
root.withdraw()

path = filedialog.askdirectory()

avg=8

include=['.csv']
legend=[]

tox=4.2e-7
eps0=8.854e-14
eps=3.9

COX=eps*eps0/tox

W=3e-4
L=240e-7

VD=25e-3

VG=None
ID=None

f1, ax1 = plt.subplots(figsize=(11, 9.6))
f2, ax2 = plt.subplots(figsize=(11, 9.6))
f3, ax3 = plt.subplots(figsize=(11, 9.6))

with open(f'{path}/Rampup.csv', 'w') as myfile:
                myfile.write("Temp, Vth, SS, Ion, Ioff, gm, Mob\n")

for file in os.listdir(path):
    if os.path.isfile(f'{path}\\{file}'):
        if os.path.splitext(f'{path}\\{file}')[1] in include:
            try:
                df=pd.read_csv(f'{path}\\{file}', header=[0, 1])
                VG=np.abs(getpd(df, 'Vg'))
                ID=np.abs(getpd(df, 'Id'))
            except: continue

            gm=np.diff(ID)/np.diff(VG)

            gm=moving_average(gm, avg)
            
            Vfit=VG[np.argmax(gm)-5:np.argmax(gm)+5]
            Ifit=ID[np.argmax(gm)-5:np.argmax(gm)+5]
            
            m, b = np.polyfit(Vfit, Ifit, 1)
            Vt=-b/m
            
            ax1.plot(VG, ID*1e6, label=f"{os.path.splitext(file)[0]} - Vt={format(Vt, '.3f')}")

            mi=np.max(gm)*L/(W*VD*COX)
            
            
            ax2.plot(VG[int(np.ceil(avg/2)):-int(np.floor(avg/2))], gm*1e6, '.', label=f"{os.path.splitext(file)[0]} - max $g_m$={format(np.max(gm), '.2e')} S @ {VG[np.argmax(gm)+1]} V")

            ion=0
            j=0

            for idx, val in enumerate(ID):
                if val >= 3e-10:
                    j=idx
                    break

            for idx, val in enumerate(VG):
                if val >= Vt:
                    ion=ID[idx]
                    break
                    
            Vfit=VG[j:j+4]
            Ifit=ID[j:j+4]

            m, b = np.polyfit(np.log10(Ifit), Vfit, 1)

            ax3.plot(VG, ID, label=f"{os.path.splitext(file)[0]} - SS={format(m*1e3, '.2f')} mV/dec")
            ax3.plot(Vfit, Ifit, '.')
            with open(f'{path}/Rampup.csv', 'a') as myfile:
                myfile.write(f"{os.path.splitext(file)[0]}, {format(Vt, '.3f')} V, {format(m*1e3, '.2f')} mV/dec,{format(ion, '.2e')} A, {format(ID[0], '.2e')} A, {format(np.max(gm), '.2e')} S, {format(mi, '.2f')} cm2.v-1.s-1\n")
            print(f"{os.path.splitext(file)[0]}, {format(Vt, '.3f')} V, {format(mi, '.2f')} cm2.v-1.s-1, {format(m*1e3, '.2f')} mV/dec, {format(ID[0], '.2e')} A")

prefix='TN3 - L=240 nm W=3 $\mu$m'
##prefix=input()

ax1.set_title(prefix+" - $I_D$ x $V_{GS}$ - Temperature - $V_{DS}$=25 mV")
# f1.legend(title="Temperature", loc='upper left', bbox_to_anchor=(0.13, 0.88))
ax1.grid(True)

ax1.set_ylabel("$I_D$ ($\mu A$)")
ax1.set_xlabel("$V_G$ (V)")

ax1.set_xlim((0, 1.5))
            
ax2.set_title(prefix+" - $g_m$ x $V_{GS}$ - Temperature - $V_{DS}$=25 mV")
# f2.legend(title="Temperature", loc='upper left', bbox_to_anchor=(0.13, 0.88))
ax2.grid(True)

ax2.set_ylabel("$g_m$ ($\mu S$)")
ax2.set_xlabel("$V_G$ (V)")

ax2.set_xlim((0, 1.5))

ax2.text(0.3, 101, "8-point rolling average")

ax3.set_title(prefix+" - $I_D$ (log) x $V_{GS}$ - Temperature - $V_{DS}$=25 mV")            
# f3.legend(title= "Temperature", loc='lower right', bbox_to_anchor=(0.8, 0.3))
ax3.grid(True)

ax3.set_ylabel("$I_D$ (A)")
ax3.set_xlabel("$V_G$ (V)") 

ax3.set_ylim((1e-13, np.max(ID)*3))            
ax3.set_yscale('log')
ax3.set_xlim((0, 1.5))

            
f1.savefig(f"{path}\\IdxVgs (T).png")

f2.savefig(f"{path}\\gmxVgs (T).png")

f3.savefig(f"{path}\\IdxVgs log (T).png")

plt.show()