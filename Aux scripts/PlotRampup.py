import sys, os
sys.path.append("../Modules")

from HPIB_plot import*


def getpd(df, trace):
    return df[trace][df[trace].columns[0]].to_numpy()

include=['.csv']
legend=[]


for file in os.listdir():
    if os.path.isfile(file):
        if os.path.splitext(file)[1] in include:
            df=pd.read_csv(file, header=[0, 1])

            plt.plot(getpd(df, 'VG'), getpd(df, 'ID'), label=os.path.splitext(file)[0])
            plt.legend()
            
            

plt.show()
