#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oscar Yáñez Suárez, 2021.06.16

This work is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
# System library (for testing purposes only)
import sys

# Serial communications library
import serial

# RehaStim packet library
import rsPacket as rsp

# Serial packet transceiver class

class rsComm():

    # Serial configuration parameters

    SETTINGS = {
                'bytesize': serial.EIGHTBITS,
                'baudrate': 460800,
                'stopbits': serial.STOPBITS_ONE,
                'timeout': 0.1,
                'parity': serial.PARITY_EVEN
               }

    # Packet related constants
    START_BYTE = rsp.rsPacket.START_BYTE.to_bytes(1, 'little')
    STOP_BYTE = rsp.rsPacket.STOP_BYTE.to_bytes(1, 'little')

    ### Instance methods

    # Constructor from device path
    def __init__(self, port_path):
        # Save device path
        self.port_path = port_path
        # Create serial port
        self.port = serial.Serial(self.port_path)
        # Configure serial port
        self.port.apply_settings(rsComm.SETTINGS)
        # Initialize packet count
        self.packet_count = 0

    # Destructor, closes port
    def __del__(self):
        # Close port
        self.port.close()

    # Send packet
    def send_packet(self, packet):
        # Write byte string
        self.port.write(packet.get_packet_as_bytes())
        # Update packet count
        self.packet_count = (self.packet_count + 1) % 256

    # Receive packet as byte string
    def receive_packet(self):
        # Read port stream
        packet = self.port.read()
        # If it is a start byte, collect packet
        if packet == self.START_BYTE:
            # Collect header bytes
            for i in range(4):
                packet += self.port.read()
            # Collect data bytes
            datalength = rsp.rsPacket.stuff_byte(packet[-1])
            for i in range(datalength):
                packet += self.port.read()
            # Collect stop byte
            packet += self.port.read()
            # Return packet as byte string
            return packet
        else:
            # Return empty string to avoid hanging
            return b''

# Module testing
if __name__ == '__main__':
    # Check command line args
    if len(sys.argv) != 3:
        print(f'{sys.argv[0]} [sender|receiver] device')
    elif not sys.argv[1] in {'sender', 'receiver'}:
        print(f'{sys.argv[0]} [sender|receiver] device')
    else:
        # Create communication node
        node = rsComm(sys.argv[2])
        if sys.argv[1] == 'sender':
            # Send one packet of each, with arbitrary payload data
            for type in rsp.rsPacket.TYPES:
                # Define id from current packet count
                id = node.packet_count + 1
                packet = rsp.rsPacket(id, type, [0x80, 0x40, 0x20, 0x10])
                print('Sending ' + str(packet))
                node.send_packet(packet)
        if sys.argv[1] == 'receiver':
            # Read and parse packets until last type is sent
            last_type = list(rsp.rsPacket.TYPES)[-1]
            type = ''
            while type != last_type:
                # Read packet as byte string
                bytes = node.receive_packet()
                if bytes:
                    # Parse packet
                    packet = rsp.rsPacket.parse_packet(0, bytes)
                    print('Receiving ' + str(packet))
                    type = packet.packet_type
