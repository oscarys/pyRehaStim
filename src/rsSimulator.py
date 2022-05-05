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
# Time control library
import time

# RehaStim packet/comm libraries
import rsPacket as rsp
import rsComm as rsc

# Simulator parameters
INIT_REPETITION_TIME = 500
WATCHDOG_TIMEOUT = 1200

# Check command line args
if len(sys.argv) != 2:
    print(f'{sys.argv[0]} device')
else:
    # Create communication node
    node = rsc.rsComm(sys.argv[1])
    # Ping controller
    while True:
        # Send Init packet
        id = node.packet_count + 1
        packet = rsp.rsPacket(id, 'Init', [rsp.rsPacket.VERSION])
        print('Sending   ' + str(packet))
        node.send_packet(packet)
        # Check for InitAck packet
        bytes = node.receive_packet()
        if bytes:
            # Parse packet
            packet = rsp.rsPacket.parse_packet(0, bytes)
            print('Receiving ' + str(packet))
            if packet.packet_type == 'InitAck':
                break
        time.sleep(INIT_REPETITION_TIME/1000)
