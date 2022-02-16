import time
import serial
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

# Read response
reply = ser.readlines(10240)
for i in range(len(reply)):
    print(reply[i])