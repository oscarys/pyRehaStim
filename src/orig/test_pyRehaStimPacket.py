import pyRehaStimPacket as rhp

p = rhp.pyRHInitPacket(0)
print(p.id, p.packet)
print(p.id, p.get_hex_packet())

p1 = rhp.pyRHInitAckPacket(p.id)
print(p1.id, p1.packet)
print(p1.id, p1.get_hex_packet())
