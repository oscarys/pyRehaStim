#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oscar Yáñez Suárez, 2022.07.01

This work is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""

# CRC8 library
import crccheck.checksum

# Packet class

class RSPACKET:

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
    def cmd_to_type(cmd):
        for type in RSPACKET.TYPES:
            if RSPACKET.TYPES[type] == cmd:
                return type

    # "byte stuffing", i.e, xoring with STUFFING_KEY
    def stuff_byte(byte):
        return ((byte & ~RSPACKET.STUFFING_KEY) | (~byte & RSPACKET.STUFFING_KEY))

    ### Instance methods

    # Packet constructor from stream id, type string and data list
    def __init__(self, *, packet=None, raw_packet=None):
        # Build packet from bytearray
        if raw_packet != None and packet == None:
            # Convert byte string to byte sub-lists
            packet_lead = [byte for byte in raw_packet[0:5]]
            packet_payload = [byte for byte in raw_packet[5:-1]]
            packet_trail = [raw_packet[-1]]
            # Compute stuffed payload checksum and length
            checksum = RSPACKET.stuff_byte(crccheck.crc.Crc8.calc(packet_payload))
            datalength = RSPACKET.stuff_byte(len(packet_payload))
            # Verify packet integrity
            if packet_lead[0] == RSPACKET.START_BYTE and packet_trail[0] == RSPACKET.STOP_BYTE:
                if packet_lead[1] == RSPACKET.STUFFING_BYTE and packet_lead[3] == RSPACKET.STUFFING_BYTE:
                    if checksum == packet_lead[2]:
                        if datalength == packet_lead[4]:
                            # Build packet object
                            # Packet identification number in the communication stream
                            self._packet_id = packet_payload[0]
                            # Packet type and command
                            self._packet_type = RSPACKET.cmd_to_type(packet_payload[1])
                            self._packet_command = packet_payload[1]
                            # Packet payload array
                            self._packet_payload = [self._packet_id, self._packet_command] + packet_payload[2:]
                            #return rsPacket(packet=(packet_payload[0], rsPacket.packet_type_from_cmd(packet_payload[1]), packet_payload[2:]))
                        else:
                            raise ValueError('Wrong payload length')
                    else:
                        raise ValueError('Wrong payload checksum')
                else:
                    raise ValueError('Bad stuffing byte in packet')
            else:
                raise ValueError('Unknown start/stop byte in packet')
        # Build packet from packet info
        elif raw_packet == None and packet != None:
            p_id, p_type, p_data = packet
            # Packet identification number in the communication stream
            self._packet_id = p_id
            # Packet type and command
            self._packet_type = p_type
            self._packet_command = RSPACKET.TYPES[self._packet_type]
            # Packet payload array
            self._packet_payload = [self._packet_id, self._packet_command] + p_data
        # Signal error in the call
        else:
            raise ValueError('Either packet info or raw bytes must be provided, but not both')
        # Compute (stuffed) payload checksum
        self._checksum = RSPACKET.stuff_byte(crccheck.crc.Crc8.calc(self._packet_payload))
        # Compute (stuffed) payload length
        self._datalength = RSPACKET.stuff_byte(len(self._packet_payload))
        # Build packet as a list
        self._packet = [self.START_BYTE, self.STUFFING_BYTE, self._checksum, self.STUFFING_BYTE, self._datalength]
        self._packet = self._packet + self._packet_payload + [self.STOP_BYTE]
        # Build packet as a bytearray
        self._raw_packet = b''.join([byte.to_bytes(1, 'little') for byte in self._packet])


    # Packet print as text
    def __str__(self):
        packet_dec = self.get_packet_as_dec()
        packet_hex = self.get_packet_as_hex()
        return f'[{self._packet_id:03d}] {self._packet_type:23s}: {packet_dec} \t {packet_hex}'

    # Encode packet as a decimal string
    def get_packet_as_dec(self):
        return '|'.join([f'{b:03d}' for b in self._packet])
    
    # Encode packet as a hex string
    def get_packet_as_hex(self):
        return '|'.join(['{:>02s}'.format(hex(b)[2:]) for b in self._packet]).upper()

    # Build and return packet as a byte string
    def get_packet(self):
        return self._raw_packet


# Module testing
if __name__ == '__main__':
    for i, type in enumerate(RSPACKET.TYPES):
        # Create each packet with arbitrary payload data
        p = RSPACKET(packet=(i, type, [100 + i, 101 + i]))
        print(f'Encode: {p}')
        # Re-parse packet and display for comparison
        pp = RSPACKET(raw_packet=p.get_packet())
        print(f'Decode: {pp}')
        print('-'*50)
