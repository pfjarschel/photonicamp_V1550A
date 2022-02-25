from thorlabsV1550a import V1550A

attenuator = V1550A()

# Serial example
# Tipically COMX in Windows, /dev/ttyACMX or /dev/ttyUSBX for Linux, where X must be replaced by a number. No idea for MAC.
addr = "/dev/ttyUSB0"
# attenuator.connect_usb(addr)

# Ethernet example
# If DHCP is not available, fixed IP will be 192.168.0.141.
# May not be accessible without changing the PC ethernet adapter IP settings to the same subnet.
attenuator.connect_ethernet("192.168.0.141")

# Set desired attenuation. If calibration file is present (calibration/VL1550A_calibration.csv), it will be used to find the closest value. If not, a hard-coded rough fitting will be used.
attenuator.set_attenuation(0)
