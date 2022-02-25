# Wrapper class to control Thorlabs V1550A via Arduino + DAC

from arduinodac import ArduinoDAC
import os
import numpy as np


class V1550A():
    
    def __init__(self, use_cal_file=True): 
        self.usbaddr = ""
        self.ipaddr = ""
        self.ipport = 80

        self.dac = ArduinoDAC()
        
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.calfile_path = f"{self.file_path}/calibration/VL1550A_calibration.csv"
        self.cal_x = []
        self.cal_y = []
        self.calOK = False
        if os.path.isfile(self.calfile_path):
            data = np.loadtxt(self.calfile_path, delimiter=",", skiprows=1)
            self.cal_x = data[:, 0]
            self.cal_y = data[:, 1]
            self.calOK = True
        self.use_cal_file = use_cal_file
    
    def __del__(self):
        pass

    def connect_ethernet(self, ip, port=80):
        self.ipaddr = ip
        self.ipport = port
        self.dac.connect_ethernet(ip, port)
        if self.dac.ethOK:
            print("Thorlabs V1550A ethernet communications ready")

    def connect_usb(self, addr):
        self.usbaddr = addr
        self.dac.connect_serial(addr)
        if self.dac.serialOK:
            print("Thorlabs V1550A serial communications ready")
    
    def approximate_voltage(self, att):
        vs = np.linspace(0.0, 5.0, 4096)
        all_atts = -7.30786E-03*vs**6 + 7.58028E-02*vs**5 - 2.31257E-01*vs**4 + 4.22539E-01*vs**3 - 3.14100E-01*vs**2 + 8.67714E-02*vs - 5.58401E-03
        idx = np.abs(att - all_atts).argmin()
        return vs[idx]

    def approximate_attenuation(self, v):
        att = -7.30786E-03*v**6 + 7.58028E-02*v**5 - 2.31257E-01*v**4 + 4.22539E-01*v**3 - 3.14100E-01*v**2 + 8.67714E-02*v - 5.58401E-03
        return att
    
    def calibrated_voltage(self, att):
        idx = np.abs(att - self.cal_y).argmin()
        return self.cal_x[idx]

    def calibrated_attenuation(self, v):
        idx = np.abs(v - self.cal_x).argmin()
        return self.cal_y[idx]
    
    def set_voltage(self, volts):
        self.dac.apply_voltage(volts)
        
    def set_attenuation(self, att):
        volt = 0
        if self.calOK and self.use_cal_file:
            volt = self.calibrated_voltage(att)
        else:
            volt = self.approximate_voltage(att)
            
        self.dac.apply_voltage(volt)

    def set_use_cal_file(self, use):
        self.use_cal_file = use