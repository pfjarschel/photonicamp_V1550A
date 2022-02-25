import time
import serial
import requests
import numpy as np

# Definitions
MAX_VOLTAGE = 5.0


# Function to convert volts to uint16 (12 bit)
def volt2uint16(volt):
    val = int(np.round(4095.0*volt/MAX_VOLTAGE))

    if val > 4095:
        val = 4095
    if val < 0:
        val = 0

    return val

##########
# Serial #
##########
# Initialize
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
time.sleep(1.8)  # Needed for initialziation time
print("Serial communication initialized!")

# Set voltage
volt = 1.89

# Format data and send
data = np.ushort(volt2uint16(volt)).tobytes()
print(data)
ser.write(data)

############
# Ethernet #
############
# Set ip and test connection
ip = "192.168.0.141"
ok = requests.post(f"http://{ip}:80", "test").text == "test"


# Set voltage
volt = 1.89

# Send request
if ok:
    requests.post(f"http://{ip}:80", f"set {volt2uint16(volt)}")