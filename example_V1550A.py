from thorlabsV1550a import V1550A


# Tipically COMX in Windows, /dev/ttyACMX for Linux, where X must be replaced by a number. No idea for MAC.
attenuator = V1550A("COM8")

# Set desired attenuation. If calibration file is present (calibration/VL1550A_calibration.csv), it will be used to find the closest value. If not, a hard-coded rough fitting will be used.
attenuator.set_attenuation(10.0)