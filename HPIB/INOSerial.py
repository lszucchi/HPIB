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

        def read(self):
            return self.inst.readline().decode()

        def ask(self, msg):
            self.write(msg)
            time.sleep(0.01)
            return self.read()

        def opench(self, i):
            self.write(0)
            if i == 0:
                return 'Closed'
            if i >= 1 and i <=6:
                self.write(i)
                return 'Open INO: ch'+self.inst.readline().decode()
            else:
                raise RuntimeError('Invalid channel')

        def close(self):
            self.write(0)
            self.inst.close()
                


