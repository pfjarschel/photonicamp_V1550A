# Wrapper class to control Thorlabs V1550A via Arduino + DAC

from arduinodac import ArduinoDAC
import os
import numpy as np


class V1550A():
    
    def __init__(self, addr, use_cal_file=True):
        self.file_path = os.path.dirname(os.path.realpath(__file__))
        self.calfile_path = f"{self.file_path}/calibration/VL1550A_calibration_smooth.csv"
        
        self.addr = addr
        self.dac = ArduinoDAC(addr)
        self.dac.set_reply(False)
        
        self.cal_x = []
        self.cal_y = []
        self.calOK = False
        if os.path.isfile(self.calfile_path):
            data = np.loadtxt(self.calfile_path, delimiter=",", skiprows=1)
            self.cal_x = data[:, 0]
            self.cal_y = data[:, 1]
            self.calOK = True
        self.use_cal_file = use_cal_file
        
        print("Thorlabs V1550A ready")
    
    def __del__(self):
        pass
    
    def approximate_voltage(self, att):
        volt = ((att + 0.166331)/0.063457)**(1/3.718712)
        return volt

    def approximate_attenuation(self, v):
        att = 0.063457*(v**3.718712) - 0.166331
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