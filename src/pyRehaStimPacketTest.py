import sys

import pyRehaStimNode as rhnode
import pyRehaStimPacket as rhpacket

if len(sys.argv) != 3:
    print(f'{sys.argv[0]} [stimulator|controller] device')
elif not sys.argv[1] in {'stimulator', 'controller'}:
    print(f'{sys.argv[0]} [stimulator|controller] device')
else:
    node = rhnode.pyRehaStimNode(sys.argv[2])
    packet = rhpacket.pyRehaStimInitPacket(node.packet_count)
    if sys.argv[1] == 'stimulator':
        while True:
            node.send_packet(rhpacket.pyRehaStimInitPacket(node.packet_count))
            packet_bytes = node.receive_packet()
            if packet_bytes:
                cmd = rhpacket.pyRehaStimPacket.parse_packet(packet_bytes)
                if cmd == rhpacket.pyRehaStimPacket.INITACK:
                    print('INITACK received')
                    break
    if sys.argv[1] == 'controller':
        while True:
            packet_bytes = node.receive_packet()
            if packet_bytes:
                cmd = rhpacket.pyRehaStimPacket.parse_packet(packet_bytes)
                if cmd == rhpacket.pyRehaStimPacket.INIT:
                    node.send_packet(rhpacket.pyRehaStimInitAckPacket(node.packet_count))
                    print('INITACK sent')
                    break
