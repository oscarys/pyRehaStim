"""
Class pyRehaStimPacket
Protocol packets
Based on protocol docs

Oscar Yanez-Suarez, LINI, 2021
oyanez@izt.uam.mx
"""
import crccheck.checksum

class pyRehaStimPacket:
    # Packet types
    INIT = 0x01
    VERSION = 0x01
    INITACK = 0x02
    INITACK_RESULT_OK = 0x00
    INITACK_RESULT_ERR = -0x05
    UNKNOWN = 0x03
    WATCHDOG = 0x04
    GETSTIMULATIONMODE = 0x0A
    GETSTIMULATIONMODEACK = 0x0B
    INITCHANNELLISTMODE = 0x1E
    INITCHANNELLISTMODEACK = 0x1F
    STARTCHANNELLISTMODE = 0x20
    STARTCHANNELLISTMODEACK = 0x21
    STOPCHANNELLISTMODE = 0x22
    STOPCHANNELLISTMODEACK = 0x23
    SINGLEPULSE = 0x24
    SINGLEPULSEACK = 0x25
    STIMULATIONERROR = 0x26

    # Packet-related constants
    START_BYTE = 0xF0
    STOP_BYTE  = 0x0F
    STUFFING_BYTE = 0x81
    STUFFING_KEY = 0x55
    MAX_PACKET_BYTES = 69

    def parse_packet(packet):
        lead = packet[0:5]
        payload = packet[5:-1]
        trail = packet[-1]
        print(payload[1])

    def stuff_byte(self, byte):
        """
        Bitwise XORing byte with the stuffing key
        """
        return ((byte & ~self.STUFFING_KEY) | (~byte & self.STUFFING_KEY))

    def __init__(self, packet_id, packet_payload):
        # Packet identification number in the communication stream
        self.id = packet_id
        # Packet payload array
        self.__payload = packet_payload
        # Compute (stuffed) payload checksum
        self.__checksum = self.stuff_byte(crccheck.crc.Crc8.calc(self.__payload))
        # Compute (stuffed) payload length
        self.__datalength = self.stuff_byte(len(self.__payload))
        # Build packet
        # Packet lead and trail
        lead = [pyRehaStimPacket.START_BYTE, pyRehaStimPacket.STUFFING_BYTE, self.__checksum, pyRehaStimPacket.STUFFING_BYTE, self.__datalength]
        trail = [pyRehaStimPacket.STOP_BYTE]
        self.__packet_array = lead + self.__payload + trail
        # Convert packet array to bytes
        self.packet = b''.join([byte.to_bytes(1, 'little') for byte in self.__packet_array])

    def get_hex_packet(self):
        """
        Packet array getter as hex strings
        """
        return [hex(byte) for byte in self.__packet_array]

class pyRehaStimInitPacket(pyRehaStimPacket):

    def __init__(self, packet_id):
        payload = [packet_id, pyRehaStimPacket.INIT, pyRehaStimPacket.VERSION]
        super().__init__(packet_id, payload)

class pyRehaStimInitAckPacket(pyRehaStimPacket):

    def __init__(self, packet_id):
        payload = [packet_id, pyRehaStimPacket.INITACK, pyRehaStimPacket.INITACK_RESULT_OK]
        super().__init__(packet_id, payload)
