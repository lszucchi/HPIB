import sys
sys.path.append("../Modules")

from HPIB_plot import*


def getpd(df, trace):
    return df[trace][df[trace].columns[0]].to_numpy()

path="C:/Users/Zucchi-Note/Dropbox/Cryochip/Medidas/TN2/231026/IdxVgs-231026 200848.csv"
path2="C:/Users/Zucchi/Documents/Medidas/teste/231028/csv/IdxVds-231028 144521.csv"

df=pd.read_csv(path, header=[0, 1])

VG=getpd(df, 'VG')
ID=getpd(df, 'ID')

if 'gm' not in df.columns:
    gm=(np.diff(getpd(df,'ID').T)/np.diff(getpd(df,'VG').T)).T
    gm=np.append([gm[0]], gm)
    gm=[format(x, '.6e') for x in gm]

    header=pd.MultiIndex.from_product([['gm'],
                                df['VG'].columns])

    df2=pd.DataFrame(data=gm, columns=header)
    df=pd.concat((df, df2), axis=1)

    df.to_csv(path, index=False, float_format='%.6e')
else:
    gm=getpd(df, 'gm')

if 'dgm' not in df.columns:
    dgm=(np.diff(getpd(df,'gm').T)/np.diff(getpd(df,'VG').T)).T
    dgm=np.append(dgm, [dgm[-1]])
    dgm=[format(x, '.6e') for x in dgm]

    header=pd.MultiIndex.from_product([['dgm'],
                                df['VG'].columns])

    df2=pd.DataFrame(data=dgm, columns=header)
    df=pd.concat((df, df2), axis=1)

    df.to_csv(path, index=False, float_format='%.6e')
else:
    dgm=getpd(df, 'dgm')

df.to_csv(path, index=False, float_format='%+.6e')
VGfit=VG[np.argmax(gm)-2:np.argmax(gm)+3]
IDfit=ID[np.argmax(gm)-2:np.argmax(gm)+3]

m, b= np.polyfit(VGfit, IDfit, 1)
Vth=-b/m
fitID=m*VG[:np.argmax(gm)]+b

Plot(path, 'VG', ['ID', 'gm']) 

plt.show()
