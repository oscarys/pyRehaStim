#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oscar Yáñez Suárez, 2021.06.16

This work is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

# CRC8 library
import crccheck.checksum

# Packet class

class rsPacket:

    # Packet types

    TYPES = {'Init': 0x01, 'InitAck': 0x02, 'Unknown': 0x03, 'Watchdog': 0x04,
             'GetStimulationMode': 0x0A, 'GetStimulationModeAck': 0x0B,
             'InitChannelListMode': 0x1E, 'InitChannelListModeAck': 0x1F,
             'StartChannelListMode': 0x20, 'StartChannelListModeAck': 0x21,
             'StopChannelListMode': 0x22, 'StopChannelListModeAck': 0x23,
             'SinglePulse': 0x24, 'SinglePulseAck': 0x25, 'StimulationError': 0x26}

    # Packet-related constants

    VERSION = 0x01

    INITACK_RESULT_OK = 0x00
    INITACK_RESULT_ERR = -0x05

    START_BYTE = 0xF0
    STOP_BYTE  = 0x0F
    STUFFING_BYTE = 0x81
    STUFFING_KEY = 0x55
    MAX_PACKET_BYTES = 69

    ### Class methods

    # Get packet type from command int
    def packet_type_from_cmd(cmd):
        for type in rsPacket.TYPES:
            if rsPacket.TYPES[type] == cmd:
                return type

    # "byte stuffing", i.e, xoring with STUFFING_KEY
    def stuff_byte(byte):
        return ((byte & ~rsPacket.STUFFING_KEY) | (~byte & rsPacket.STUFFING_KEY))

    # Build packet from byte string
    def parse_packet(packet_id, bytes):
        # Convert byte string to byte sub-lists
        packet_lead = [byte for byte in bytes[0:5]]
        packet_payload = [byte for byte in bytes[5:-1]]
        packet_trail = [bytes[-1]]
        print(packet_lead+packet_payload+packet_trail)
        # Compute stuffed payload checksum and length
        checksum = rsPacket.stuff_byte(crccheck.crc.Crc8.calc(packet_payload))
        datalength = rsPacket.stuff_byte(len(packet_payload))
        # Verify packet integrity
        if packet_lead[0] == rsPacket.START_BYTE and packet_trail[0] == rsPacket.STOP_BYTE:
            if packet_lead[1] == rsPacket.STUFFING_BYTE and packet_lead[3] == rsPacket.STUFFING_BYTE:
                if checksum == packet_lead[2]:
                    if datalength == packet_lead[4]:
                        return rsPacket(packet_payload[0], rsPacket.packet_type_from_cmd(packet_payload[1]), packet_payload[2:])
                    else:
                        raise ValueError('Wrong payload length')
                else:
                    raise ValueError('Wrong payload checksum')
            else:
                raise ValueError('Bad stuffing byte in packet')
        else:
            raise ValueError('Unknown start/stop byte in packet')

    ### Instance methods

    # Packet constructor from stream id, type string and data list
    def __init__(self, packet_id, packet_type, packet_data):
        # Packet identification number in the communication stream
        self.packet_id = packet_id
        # Packet type and command
        self.packet_type = packet_type
        self.packet_command = self.TYPES[packet_type]
        # Packet payload array
        self.__packet_payload = [packet_id, self.packet_command] + packet_data
        # Compute (stuffed) payload checksum
        self.__checksum = rsPacket.stuff_byte(crccheck.crc.Crc8.calc(self.__packet_payload))
        # Compute (stuffed) payload length
        self.__datalength = rsPacket.stuff_byte(len(self.__packet_payload))
        # Build other packet components
        self.__packet_lead = [self.START_BYTE, self.STUFFING_BYTE, self.__checksum, self.STUFFING_BYTE, self.__datalength]
        self.__packet_trail = [self.STOP_BYTE]

    # Packet print as text
    def __str__(self):
        packet_list = self.get_packet_as_list()
        packet_bytes = self.get_packet_as_bytes()
        return f'[{self.packet_id:03d}] {self.packet_type:23s}: {packet_list} \t {packet_bytes}'

    # Build and return packet as a byte list
    def get_packet_as_list(self):
        return self.__packet_lead + self.__packet_payload + self.__packet_trail

    # Build and return packet as a byte string
    def get_packet_as_bytes(self):
        return b''.join([byte.to_bytes(1, 'little') for byte in self.get_packet_as_list()])


# Module testing
if __name__ == '__main__':
    for i, type in enumerate(rsPacket.TYPES):
        packet = rsPacket(i, type, [100 + i, 101 + i])
        print(packet)
        parsed_packet = rsPacket.parse_packet(i, packet.get_packet_as_bytes())
        print(parsed_packet)


#
#     def get_hex_packet(self):
#         """
#         Packet array getter as hex strings
#         """
#         return [hex(byte) for byte in self.__packet_array]
#
# class pyRehaStimInitPacket(pyRehaStimPacket):
#
#     def __init__(self, packet_id):
#         payload = [packet_id, pyRehaStimPacket.INIT, pyRehaStimPacket.VERSION]
#         super().__init__(packet_id, payload)
#
# class pyRehaStimInitAckPacket(pyRehaStimPacket):
#
#     def __init__(self, packet_id):
#         payload = [packet_id, pyRehaStimPacket.INITACK, pyRehaStimPacket.INITACK_RESULT_OK]
#         super().__init__(packet_id, payload)
