from thorlabsV1550a import V1550A
import pylef  # taking advantage os recent work with this
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt
import time
import pickle

# Create objects
attenuator = V1550A("/dev/ttyACM0")
scope = pylef.scope.TektronixTBS1062()

# Scope scale functions
def dc_scale(att):
    return 0.9997 - 0.122*att + 0.0047*(att**2) - 5e-5*(att**3)

def ac_scale(att):
    return 0.00183 + 0.00394*att - 0.000476*(att**2) + 1.8778e-5*(att**3) - 2.405e-7*(att**4)

def ac_pos(att):
    return 88.19 + 5.414*att - 4.507*att**2 + 0.5828*att**3 - 0.03331*att**4 + 8.98e-4*att**5 - 9.291e-6*att**6

# Prepare sweep
n_sweep = 25
atts = np.linspace(0.0, 24.0, n_sweep)
time_scale = 10*scope.horizontal_scale()
max_ffts = np.zeros(n_sweep)
max_rins = np.zeros(n_sweep)
all_data = []

# Sweep
for i in range(n_sweep):
    # Set attenuation
    attenuator.set_attenuation(atts[i])
    time.sleep(1.0)

    # Get DC level
    scope.ch1.set_dc()
    scope.ch1.set_scale(dc_scale(atts[i]))
    scope.ch1.set_position(0.0)
    scope.instr.write("ACQ:STOPA SEQ")
    scope.start_acquisition()
    time.sleep(2*time_scale)
    # scope.ch1.set_smart_scale()
    dc_level = scope.ch1.read_channel()[1].mean()

    # Get noise data
    scope.ch1.set_ac()
    scope.ch1.set_scale(ac_scale(atts[i]))
    scope.ch1.set_position(0.0)
    scope.instr.write("ACQ:STOPA SEQ")
    scope.start_acquisition()
    time.sleep(2*time_scale)
    # scope.ch1.set_smart_scale()
    data = np.array(scope.ch1.read_channel())
    all_data.append(data)

    # Take FFT
    n = len(data[0])
    time_step = (data[0][-1] - data[0][0])/n
    norm = 4*time_step
    data_fft = norm*np.abs(fft(data[1]/dc_level)[:n//2])

    # # The block below is useful to see the data
    # data_fft_db = 10.0*np.log10(data_fft)
    # data_fft_freq = fftfreq(n, time_step)[:n//2]

    # plt.plot(data[0], data[1])
    # plt.figure()
    # plt.semilogx(data_fft_freq, data_fft_db)
    # plt.figure()
    # plt.semilogx(data_fft_freq, data_fft)
    # plt.show()

    # Take max value from FFT and divide by DC level (relative intensity noise, but not really the usual RIN)
    max_ffts[i] = 10.0*np.log10(data_fft.max())
    max_rins[i] = max_ffts[i]/dc_level

    print(f"For {atts[i]:.0f} dB attenuation, relative noise is {max_rins[i]:.2f} dB")


plt.plot(atts, max_rins, "o--")
plt.xlabel("Attenuation (dB)")
plt.ylabel("Relative noise (dB)")
plt.suptitle("USB powered attenuator optical noise (Low frequency)")
plt.show()

with open("opt_noise_dc_usb.pkl", 'wb') as file:
    pickle.dump(all_data, file)
    file.close()