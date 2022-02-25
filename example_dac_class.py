# Import stuff
import time
from arduinodac import ArduinoDAC as DAC

# Create object and open communication
dac1 = DAC()

# Connect via ethernet or USB
dac1.connect_ethernet("192.168.0.141")
dac1.connect_serial("/dev/ttyACM0")

# Apply initial voltage
dac1.apply_voltage(0)

# Wait a little
time.sleep(1)

# Apply ramp voltage
v = 0.0
v_start = v
v_stop = 5.0
v_step = 0.1
wait = 0.000
step = False;
while True:
   dac1.apply_voltage(v)
   v += v_step
   if v > v_stop:
       v = v_start
    
   # dac1.apply_voltage(step*v_stop)
   # step = not step

   time.sleep(wait)
