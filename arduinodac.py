import time
import serial
import numpy as np

MAX_VOLTAGE = 5.0

class ArduinoDAC():
    # Definitions
    addr = ""
    baud = 9600
    timeout = 1.0
    volt = 0.0
    uint_val = 0
    reply = True

    def __init__(self, addr, baud=9600, timeout=1.0):
        self.ser = serial.Serial(addr, baud, timeout=timeout)
        self.addr = addr
        self.baud = baud
        self.timeout = timeout

        time.sleep(2.0)  # Needed for initialziation time

        self.set_reply(self.reply)
        
        print("Serial communication established!")

    def __del__(self):
        try:
            self.ser.close()
        except:
            pass
        print("Serial communication ended.")

    # Function to convert volts to uint16 (12 bit)
    def volt2uint16(self, volt):
        val = int(np.round(4095.0*volt/MAX_VOLTAGE))

        if val > 4095:
            val = 4095
        if val < 0:
            val = 0

        return val

    # Function to convert uint16 (12 bit) to voltage
    def uint162volt(self, val):
        if val > 4095:
            val = 4095
        if val < 0:
            val = 0
        
        volt = float(val)*MAX_VOLTAGE/4095.0

        return volt

    # Apply uint value to dac
    def apply_uint_val(self, val):
        if val > 4095:
            val = 4095
        if val < 0:
            val = 0

        self.uint_val = val
        self.volt = self.uint162volt(val)

        # Format data and send
        data = np.ushort(val).tobytes()
        self.ser.write(data)

        # Read response
        if self.reply:
            resp = self.ser.readlines(10240)
            for i in range(len(resp)):
                print(resp[i].decode('UTF-8').replace("\r\n", ""))

    # Apply voltage (converts to uint value first)
    def apply_voltage(self, volt):
        if volt > MAX_VOLTAGE:
            volt = MAX_VOLTAGE
        if volt < 0:
            volt = 0

        self.volt = volt
        uint_val = self.volt2uint16(volt)
        self.uint_val = uint_val

        self.apply_uint_val(uint_val)

    # Enable or suppress replies from arduino
    # Suppress for faster operation
    def set_reply(self, reply=True):
        if reply:
            self.ser.write(b'ry')
            self.reply = True
        else:
            self.ser.write(b'rn')
            self.reply = False

        resp = self.ser.readlines(10240)
        for i in range(len(resp)):
            print(resp[i].decode('UTF-8').replace("\r\n", ""))