import pyvisa as visa

class OLP55():
    rm = None
    dev = None
    addr = ""
    ifaceOK = False
    devOK = False
    idn = ""

    def __init__(self):
        pass

    def __del__(self):
        if self.dev != None:
            self.dev.close()

    def connect(self, addr):
        self.addr = addr
        name = f"ASRL{addr}::INSTR"

        try:
            self.rm = visa.ResourceManager("@py")
            self.ifaceOK = True
        except:
            print("Error opening VISA! Check pyvisa and pyvisa-py packages installation!")

        if self.ifaceOK:
            try:
                self.dev = self.rm.open_resource(name)
                try:
                    self.idn = self.dev.query("*IDN?")
                    if "OLP-55" in self.idn:
                        self.devOK = True 
                except:
                    print("Connection established but not behaving as expected. Is the address correct for OLP-55?")
            except:
                print("Error communicating with device. Is the device connected and the address correct?")

    def get_pwr(self):
        pwr = float(self.dev.query("FETC:POW:INP?"))
        return pwr
