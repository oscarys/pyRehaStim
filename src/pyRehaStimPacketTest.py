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
        node.send_packet(packet)
    else:
        while True:
            packet_bytes = node.receive_packet()
            if packet_bytes:
                print(packet_bytes)
                rhpacket.pyRehaStimPacket.parse_packet(packet_bytes)
