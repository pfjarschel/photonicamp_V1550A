# Import stuff
import time
import numpy as np
import matplotlib.pyplot as plt
from arduinodac import ArduinoDAC as DAC
from olp55 import OLP55

# Create objects and open communication
dac1 = DAC()
# dac1.connect_serial("/dev/ttyACM0")
dac1.connect_ethernet("192.168.0.141")
pm = OLP55()
pm.connect("/dev/ttyACM0")

# Apply initial voltage
dac1.apply_voltage(0.0)

# Prepare calibration loop
wait = 0.5  # seconds, mainly for PM response
pm_int_time = 1.0  # seconds
initial_pwr_dbm = 0.0  # dBm
initial_pwr_mw = 10.0**(initial_pwr_dbm/10.0)
v_start = 0.0  # volts
v_stop = 5.0  # volts
v_n = 4096  # 4096 for full DAC resolution
volts = np.linspace(v_start, v_stop, v_n)
pwrs_dbm = np.zeros(v_n)
pwrs_mw = np.zeros(v_n)
atts_db = np.zeros(v_n)
atts_lin = np.zeros(v_n)

# Run calibration routine
for i in range(v_n):
    dac1.apply_voltage(volts[i])
    time.sleep(wait)

    # Average power meter reading
    i_p = 0
    t0 = time.time()
    t1 = time.time()
    pwr_dbm = pm.get_pwr()
    while t1 - t0 < pm_int_time:
        pwr_dbm += pm.get_pwr()
        t1 = time.time()
        i_p += 1
    pwr_dbm = pwr_dbm/i_p

    pwr_mw = 10.0**(pwr_dbm/10.0)
    att_db = initial_pwr_dbm - pwr_dbm
    att_lin = pwr_mw/initial_pwr_mw

    pwrs_dbm[i] = pwr_dbm
    pwrs_mw[i] = pwr_mw
    atts_db[i] = att_db
    atts_lin[i] = att_lin

    print(f"Measured {att_db:.2f} attenuation for {volts[i]:.3f} V.")

# Plot results
fig, [ax1, ax2] = plt.subplots(1, 2)
ax1.plot(volts, atts_db)
ax1.set_xlabel("Voltage (V)")
ax1.set_ylabel("Attenuation (dB)")

ax2.semilogy(volts, atts_lin)
ax2.set_xlabel("Voltage (V)")
ax2.set_ylabel("Attenuation (%)")

fig.tight_layout()

plt.show()

# Save data
with open("VL1550A_calibration_eth_slow.csv", 'w') as file:
    file.write("Voltage (V),Attenuation (dB)\n")
    for i in range(v_n):
        file.write(f"{volts[i]:.3f},{atts_db[i]:.2f}\n")
    
    file.close()