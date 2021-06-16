# pyRehaStim
Native Python implementation of the ScienceMode2 protocol for the RehaStim2 Stimulation Device

### Raspberry Pi 4
Out-of-the-box serial port (miniuart) is enabled and present at pins 8 (TXD, GPIO.14) and 10 (RXD, GPIO.15) in the RPi 4 IO header. However, this UART does not support parity checking, which is part of ScienceMode2 protocol. Therefore, a DT overlay has to be enabled by editing /boot/config.txt and adding:

dtoverlay=miniuart-bt
