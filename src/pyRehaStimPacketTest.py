import sys

import pyRehaStimNode
import pyRehaStimPacket

if len(sys.argv) != 3:
    print(f'{sys.argv[0]} [send|receive] device')
elif not sys.argv[1] in {'send', 'receive'}:
    print(f'{sys.argv[0]} [send|receive] device')
else:
    node = pyRehaStimNode(sys.argv[1])
    packet = pyRehaStimInitPacket(node.packet_count)
    if sys.argv[1] == 'send':
        node.send(packet.packet)
    else:
        pyRehaStimPacket.parse_packet(node.receive())
