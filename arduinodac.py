import time
import serial
import requests
import numpy as np

MAX_VOLTAGE = 5.0

class ArduinoDAC():
    # Definitions
    serial_addr = ""
    baud = 9600
    ip_addr = ""
    ip_port = 80
    serialOK = False
    ethOK = False
    timeout = 1.0
    volt = 0.0
    uint_val = 0

    def __init__(self):
        # No initialization at this time
        pass

    def __del__(self):
        try:
            self.ser.close()
        except:
            pass
        print("Serial communication ended.")

    # Connect via serial (USB)
    def connect_serial(self, addr, baud=9600, timeout=1.0):
        try:
            self.ser = serial.Serial(addr, baud, timeout=timeout)
            self.addr = addr
            self.baud = baud
            self.timeout = timeout

            time.sleep(2.0)  # Needed for initialziation time        
            print("Serial communication established!")
            self.serialOK = True
        except Exception as e:
            print("Error opening serial communication! Check if the device is connected, and is not being used.")
            self.serialOK = False

    # Connect via ethernet
    def connect_ethernet(self, ip, port=80):
        self.ip_addr = ip
        self.ip_port = port
        response = requests.post(f"http://{ip}:{port:.0f}", "test")
        if response.status_code == 200 and response.text == "test":
            print("Ethernet connection OK!")
            self.ethOK = True
        else:
            print("Error connecting via ethernet. Check the connections and the ip address/port.")
            self.ethOK = False

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
        # Check if value is within range
        if val > 4095:
            val = 4095
        if val < 0:
            val = 0

        self.uint_val = val
        self.volt = self.uint162volt(val)

        # Try sending data through ethernet first, if not available, use serial
        if self.ethOK:
            try:
                response = requests.post(f"http://{self.ip_addr}:{self.ip_port:.0f}", f"set {self.uint_val:.0f}")
            except:
                print("Communication via ethernet failed! Check cables!")
        elif self.serialOK:
            # Format data and send
            data = np.ushort(val).tobytes()
            try:
                self.ser.write(data)
            except:
                print("Communication viaserial failed! Check cables!")
        else:
            print("No communication method available. Try connect_ethernet or connect_serial")

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