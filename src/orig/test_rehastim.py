#!/usr/bin/env python

import pyRehastim
import serial.tools.list_ports

# Escanea los puerto para encontrar el ttyUSB0
for i, p in enumerate(serial.tools.list_ports.comports()):
    if 'ttyUSB' in p[0]:
        puerto_info = p

# Despliega info de conexión
print('-'*20)
print('Puerto de conexión:')
print(puerto_info[0])
print('-'*20)

# Instancia del estimulador
estimulador = pyRehastim.Stimulator(puerto_info[0])

# Enlace y comunicacion con el rehastim
# -- comentar todas las lineas "simulate_rehastim_packet" si se conecta con el estimulador
# -- esas llamadas están ahí para simular las respuestas en un loopback serial
estimulador.simulate_rehastim_packet(pyRehastim.Stimulator.INIT)
# Espera INIT
p_num = estimulador.wait_for_packet(pyRehastim.Stimulator.INIT)
# y manda INITACK
estimulador.send_packet(pyRehastim.Stimulator.INITACK, init_packet_number=p_num)
# Envía GETSTIMULATIONMODE
estimulador.send_packet(pyRehastim.Stimulator.GETSTIMULATIONMODE)
# Y espera el correspondiente *ACK
estimulador.simulate_rehastim_packet(pyRehastim.Stimulator.GETSTIMULATIONMODEACK, result=0, stimulation_mode=0)
estimulador.wait_for_packet(pyRehastim.Stimulator.GETSTIMULATIONMODEACK)
# Envía inicialización
estimulador.send_packet(pyRehastim.Stimulator.INITCHANNELLISTMODE, lff=0, active_channels=0x01, active_lf_channels=0x00, ipi=0, msi=0x0040, channel_execution=1)
# Y espera el correspondiente *ACK
estimulador.simulate_rehastim_packet(pyRehastim.Stimulator.INITCHANNELLISTMODEACK, result=0)
estimulador.wait_for_packet(pyRehastim.Stimulator.INITCHANNELLISTMODEACK)
# Envía configuración de canales (lista de diccionarios, un diccionario por canal)
channels = [{'mode': 0, 'pulse_width': 0x015E, 'current': 5}]
estimulador.send_packet(pyRehastim.Stimulator.STARTCHANNELLISTMODE, channel_config=channels)
# Y espera el correspondiente *ACK
estimulador.simulate_rehastim_packet(pyRehastim.Stimulator.STARTCHANNELLISTMODEACK, result=0)
estimulador.wait_for_packet(pyRehastim.Stimulator.STARTCHANNELLISTMODEACK)
# Lazo para pulso trapezoidal, definido como lista de pares (ancho de pulso, corriente):
trapezoidal = [(0x015E, 5), (0x015E, 6), (0x015E, 7), (0x015E, 8), (0x015E, 9), (0x015E, 10), (0x015E, 10), (0x015E, 10), (0x015E, 9), (0x015E, 8), (0x015E, 7)]
print('----- INICIA PULSO')
for pulse in trapezoidal:
    # Envía SINGLEPULSE
    estimulador.send_packet(pyRehastim.Stimulator.SINGLEPULSE, channel=0x01, pulse_width=pulse[0], current=pulse[1])
    # y espera el correspondiente *ACK
    estimulador.simulate_rehastim_packet(pyRehastim.Stimulator.SINGLEPULSEACK, result=0)
    estimulador.wait_for_packet(pyRehastim.Stimulator.SINGLEPULSEACK)
print('----- TERMINA PULSO')
# Finalmente, mantiene la conexión un poco lanzando algunos watchdogs
for i in range(10):
    estimulador.send_packet(pyRehastim.Stimulator.WATCHDOG)
