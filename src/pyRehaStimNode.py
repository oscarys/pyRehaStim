"""
Class pyRehaStimNode
Basic serial communications
Based on protocol docs

Oscar Yanez-Suarez, LINI, 2021
oyanez@izt.uam.mx
"""
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
    # Protocol constants
    START_BYTE = 0xF0
    STOP_BYTE  = 0x0F
    STUFFING_BYTE = 0x81
    STUFFING_KEY = 0x55
    MAX_PACKET_BYTES = 69

    def __init__(self, port_path):
        """
        port_path: serial device system path
        """
        self.port_path = port_path
        self.port = serial.Serial(self.port_path)
        self.port.apply_settings(pyRehaStimNode.SETTINGS)

    def __del__(self):
        self.port.close()

    def __full_duplex_test__(self):
        while True:
            msg = self.port.readline().decode().strip()
            if msg == 'fdt':
                print('fdt received')
                break
            else:
                self.port.write('fdt'.encode())
