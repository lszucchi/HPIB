import os
include=['.csv', '.png']

prefix=input()

for file in os.listdir():
    if os.path.isfile(file):
        if os.path.splitext(file)[1] in include:
            os.rename(file, prefix+file)
