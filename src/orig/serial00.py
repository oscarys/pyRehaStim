#!/usr/bin/env python

import sys
import serial, serial.tools.list_ports

for i, p in enumerate(serial.tools.list_ports.comports()):
    if 'ttyUSB' in p[0]:
        puerto_info = p

print('-'*20)
print('Puerto de conexión:')
print(puerto_info[0])
print('-'*20)

puerto_settings = {
                   'bytesize': serial.EIGHTBITS,
                   'baudrate': 115200, #460800,
                   'stopbits': serial.STOPBITS_ONE,
                   'timeout': 10,
                   'parity': serial.PARITY_EVEN
                  }

puerto = serial.Serial(puerto_info[0])
puerto.apply_settings(puerto_settings)



while True:
    msg = input('Enviar >> ')
    puerto.write(msg.encode())
    msg = puerto.readline().decode()
    print('Recibido << ' + msg)
    if msg.lower().strip() == 'bye':
        break
puerto.close()
