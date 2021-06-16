"""
Class pyRehaStimNode
Basic serial communications
Based on protocol docs

Oscar Yanez-Suarez, LINI, 2021
oyanez@izt.uam.mx
"""
import sys
import serial

class pyRehaStimNode():
    # Configuration parameters
    SETTINGS = {
                'bytesize': serial.EIGHTBITS,
                'baudrate': 460800,
                'stopbits': serial.STOPBITS_ONE,
                'timeout': 0.1,
                'parity': serial.PARITY_EVEN
               }

    def __init__(self, port_path):
        """
        open and configure port

        * port_path: serial device system path
        """
        self.port_path = port_path
        self.port = serial.Serial(self.port_path)
        self.port.apply_settings(pyRehaStimNode.SETTINGS)
        self.packet_count = 0

    def __del__(self):
        """
        close port
        """
        self.port.close()

    def send_packet(self, packet):
        self.port.write(packet.packet_bytes)

    def receive_packet(self):
        return self.port.readline()
