#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oscar Yáñez Suárez, 2021.06.16

This work is licensed under the Creative Commons Attribution 4.0
International License. To view a copy of this license, visit
http://creativecommons.org/licenses/by/4.0/ or send a letter to
Creative Commons, PO Box 1866, Mountain View, CA 94042, USA.
"""
# System library
import sys

# RehaStim packet/comm libraries
from rsPacket import RSPACKET
from rsComm import RSCOMM

# Check command line args
if len(sys.argv) != 2:
    print(f'{sys.argv[0]} device')
else:
    # Create communication node
    node = RSCOMM(sys.argv[1])
    # Check for Init packet
    while True:
        bytes = node.receive_packet()
        if bytes:
            # Parse packet
            packet = RSPACKET(raw_packet=bytes)
            print('Receiving ' + str(packet))
            if packet._packet_type == 'Init':
                pid = packet._packet_id
                packet = RSPACKET(packet=(pid, 'InitAck', [RSPACKET.VERSION]))
                print('Sending   ' + str(packet))
                node.send_packet(packet)
                break
