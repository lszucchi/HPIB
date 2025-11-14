import serial
import time

class serial_sm:

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
            if i == 0:
                return 'Closed'
            if i >= 1 and i <=6:
                self.write(i)
                for j in range(10):
                    try:
                        return f'Open INO: ch {i}'
                    except:
                        time.sleep(1)
                raise RuntimeError('Comm error')
            else:
                raise RuntimeError('Invalid channel')

        def close(self):
            self.write(0)
            self.inst.close()
                


