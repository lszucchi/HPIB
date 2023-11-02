import sys
sys.path.append("../Modules")

from HPIB_plot import*

path="C:/Users/Zucchi/Documents/Medidas/TN2/231031/Ex_Ib-231031 121402.csv"
path2="C:/Users/Zucchi/Documents/Medidas/teste/231028/csv/IdxVds-231028 144521.csv"

df=pd.read_csv(path, header=[0, 1])

##df=pd.read_csv(path, header=[0, 1])
##
##df2=(np.diff(df['ID'].T)/np.diff(df['VG'].T)).T
##df2=np.vstack((df2[0], df2))
##
##header=pd.MultiIndex.from_product([['gm'],
##                            df['VG'].columns])

##df3=pd.DataFrame(data=df2, columns=header)
##df4=pd.concat((df, df3), axis=1)
##df4.to_csv('a.csv', index=False)
##
##Plot("a.csv", 'VG', ['ID', 'gm'])
CalcIb(path, False)

##Plot(path, 'VF', ['ID', 'IS'])
plt.show()
