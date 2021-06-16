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
            print(f'Sending INIT {node.packet_count}')
            node.send_packet(rhpacket.pyRehaStimInitPacket(node.packet_count))
            packet_bytes = node.receive_packet()
            if packet_bytes:
                pid, cmd = rhpacket.pyRehaStimPacket.parse_packet(packet_bytes)
                if cmd == rhpacket.pyRehaStimPacket.INITACK:
                    print(f'INITACK {pid} received')
                    break
    if sys.argv[1] == 'controller':
        while True:
            packet_bytes = node.receive_packet()
            if packet_bytes:
                pid, cmd = rhpacket.pyRehaStimPacket.parse_packet(packet_bytes)
                if cmd == rhpacket.pyRehaStimPacket.INIT:
                    print(f'Sending INITACK {pid}')
                    node.send_packet(rhpacket.pyRehaStimInitAckPacket(pid))
                    break
