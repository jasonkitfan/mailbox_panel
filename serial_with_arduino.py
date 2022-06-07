"""
# pip install pyserial
"""

import serial
import time

sdata = serial.Serial("/dev/ttyUSB0", 9600, timeout=1.0)
time.sleep(2)

sdata.reset_input_buffer()
print("Arduino Connected")

try:
    while True:
        time.sleep(0.01)
        if sdata.in_waiting > 0:
            mydata = sdata.readline().decode("utf-8").rstrip()
            print(mydata)
except KeyboardInterrupt:
    print("Serial Closed")
    sdata.close()

