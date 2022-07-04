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

# Threading library
from threading import Timer

# RehaStim packet/comm libraries
from rsPacket import RSPACKET
from rsComm import RSCOMM

class RSCONTROLLER:
    
    WATCHDOG_INTERVAL = 1.2
    
    def __init__(self, device):
        self._pid = 0
        self._device = device
        self._comm_port = RSCOMM(self._device)
        self._state = 'IDLE'
        self._watchdog = Timer(self.WATCHDOG_INTERVAL, self._on_watchdog)
        self._watchdog_on = False
        self._watchdog.start()
    
    def _on_watchdog(self):
        if self._watchdog_on:
            self._pid = (self._pid + 1) % 256
            packet = RSPACKET(packet=(self._pid, 'Watchdog', []))
            print('Sending   ' + str(packet))
        self._watchdog.run()
    
    def start(self):
        # Check for Init packet
        while True:
            rp = self._comm_port.receive_packet()
            # Simulate an INIT packet
            #rp = RSPACKET(packet=(20, 'Init', [RSPACKET.VERSION])).get_packet()
            if rp:
                # Parse packet
                packet = RSPACKET(raw_packet=rp)
                if self._state == 'IDLE':
                    print('Receiving ' + str(packet))
                    if packet._packet_type == 'Init':
                        pid = packet._packet_id
                        packet = RSPACKET(packet=(pid, 'InitAck', [RSPACKET.VERSION]))
                        print('Sending   ' + str(packet))
                        self._comm_port.send_packet(packet)
                        self._pid = (self._pid + 1) % 256
                        self._state = 'ON'
                        self._watchdog_on = True
                elif self._state == 'ON':
                    pass
                
    def stop(self):
        self._watchdog_on = False
        self._watchdog.cancel()
                
        
if __name__ == '__main__':
    # Check command line args
    if len(sys.argv) != 2:
        print(f'{sys.argv[0]} device')
    else:
        try:
            # Create controller
            controller = RSCONTROLLER(sys.argv[1])
            controller.start()
        except KeyboardInterrupt:
            controller.stop()