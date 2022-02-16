import numpy as np
from scipy.optimize import least_squares
import matplotlib.pyplot as plt

data_file = "VL1550A_calibration.csv"

data = np.loadtxt(data_file, delimiter=",", skiprows=1)
volts = data[:, 0]
atts = data[:, 1]

def fit_func(p, vals):
    result = p[0] + p[1]*vals**(p[2])
    return result

def err_func(p, x, y):
    err = y - fit_func(p, x)
    return err

p0 = [0.0, 1.0, 1.0]
p1 = least_squares(err_func, p0, args=(volts, atts)).x

print(p1)

plt.plot(volts, atts)
plt.plot(volts, fit_func(p1, volts), 'k--')
plt.show()
