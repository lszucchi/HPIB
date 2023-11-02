import os, time


for folder in os.listdir():
    if os.path.isdir(folder+'/csv/fig'):
        for fig in os.listdir(folder+'/csv/fig'):
            os.rename(folder+'/csv/fig/'+fig, folder+'/'+fig)
    if os.path.isdir(folder+'/csv'):
        for csv in os.listdir(folder+'/csv'):
            os.rename(folder+'/csv/'+csv, folder+'/'+csv)

time.sleep(5)

for folder in os.listdir():
        if os.path.isdir(folder+'/csv'):
            os.rmdir(folder+'/csv')
        if os.path.isdir(folder+'/fig'):
            os.rmdir(folder+'/fig')
