import sys

import pyRehaStimNode as rhnode
import pyRehaStimPacket as rhpacket

if len(sys.argv) != 3:
    print(f'{sys.argv[0]} [send|receive] device')
elif not sys.argv[1] in {'send', 'receive'}:
    print(f'{sys.argv[0]} [send|receive] device')
else:
    node = rhnode.pyRehaStimNode(sys.argv[2])
    packet = rhpacket.pyRehaStimInitPacket(node.packet_count)
    if sys.argv[1] == 'send':
        node.send(packet.packet)
    else:
        while True:
            msg = node.receive()
            if msg:
                print(msg)
                rhpacket.pyRehaStimPacket.parse_packet(msg)
