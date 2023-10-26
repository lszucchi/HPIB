import serial
import time


class Arduino:

        def __init__(self, addr, baud=9600):
                try:
                        self.inst = serial.Serial(addr, baud)
                        time.sleep(2)
                except:
                        print("Comm Er")
        def write(self, msg):
                self.inst.write(str(msg).encode())

        def opench(self, i):
                self.write(0)
                if i >= 1 and i <=6:
                        self.write(i)
                        print('Open INO: ch' + str(i))
                else:
                        raise RuntimeError('Invalid channel')

        def close(self):
                self.write(0)
                print('Close INO ')
                


