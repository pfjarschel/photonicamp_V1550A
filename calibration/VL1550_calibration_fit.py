import numpy as np
from scipy.optimize import least_squares
from scipy.signal import savgol_filter
import matplotlib.pyplot as plt

data_file = "VL1550A_calibration_eth_slow.csv"

data = np.loadtxt(data_file, delimiter=",", skiprows=1)
volts = data[:, 0]
atts = data[:, 1]

attsf = savgol_filter(atts, 351, 3)

def fit_func(p, vals):
    result = p[0] + p[1]*vals**(p[2])
    return result

def err_func(p, x, y):
    err = y - fit_func(p, x)
    return err

p0 = [0.0, 1.0, 1.0]
p1 = least_squares(err_func, p0, args=(volts, attsf)).x

print(p1)

plt.plot(volts, atts)
plt.plot(volts, attsf)
plt.plot(volts, fit_func(p1, volts), 'k--')
plt.show()

# Save smoothed data
with open("VL1550A_calibration.csv", 'w') as file:
    file.write("Voltage (V),Attenuation (dB)\n")
    for i in range(len(volts)):
        file.write(f"{volts[i]:.3f},{attsf[i]:.3f}\n")
    
    file.close()