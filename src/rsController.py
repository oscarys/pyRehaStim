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
import rsPacket as rsp
import rsComm as rsc

# Check command line args
if len(sys.argv) != 2:
    print(f'{sys.argv[0]} device')
else:
    # Create communication node
    node = rsc.rsComm(sys.argv[1])
    # Check for Init packet
    while True:
        bytes = node.receive_packet()
        if bytes:
            # Parse packet
            packet = rsp.rsPacket.parse_packet(0, bytes)
            print('Receiving ' + str(packet))
            if packet.packet_type == 'Init':
                id = packet.packet_id
                packet = rsp.rsPacket(id, 'InitAck', [rsp.rsPacket.VERSION])
                print('Sending   ' + str(packet))
                node.send_packet(packet)
                break
