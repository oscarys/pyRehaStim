import serial
import crccheck.checksum

class Stimulator():
    """
    Clase para comunicación con el estimulador
    """
    # parámetros de configuración
    SETTINGS = {
                'bytesize': serial.EIGHTBITS,
                'baudrate': 460800,
                'stopbits': serial.STOPBITS_ONE,
                'timeout': 0.1,
                'parity': serial.PARITY_EVEN
               }
    # constantes del protocolo
    START_BYTE = 0xF0
    STOP_BYTE  = 0x0F
    STUFFING_BYTE = 0x81
    STUFFING_KEY = 0x55
    MAX_PACKET_BYTES = 69
    # comandos
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



    def __init__(self, port_path):
        """
        Constuctor qur recibe el path para el puerto, lo configura y lo abre
        """
        self.port_path = port_path
        self.port = serial.Serial(self.port_path)
        self.port.apply_settings(Stimulator.SETTINGS)
        self.packet_count = 0
        self.rehastim_packet_count = 0

    def __del__(self):
        """
        Destructor que se asegura de cerrar el puerto
        """
        self.port.close()

    def stuff_byte(self, byte):
        """
        Rutina para procesar un byte con XOR con Stimulator.STUFFING_KEY
        """
        return ((byte & ~Stimulator.STUFFING_KEY) | (~byte & Stimulator.STUFFING_KEY))

    def wait_for_packet(self, command):
        """
        Rutina que espera por un paquete "legal" de datos
        """
        received = False
        while not received:
            # Comienza el paquete con el byte de inicio
            packet = [Stimulator.START_BYTE]
            # Espera hasta encontrar un byte de inicio en el puerto
            while (byte := int.from_bytes(self.port.read(1), byteorder='little')) != Stimulator.START_BYTE:
                print(byte)
                pass
            # Almacena bytes hasta encontrar el byte de paro o exceder el límite
            while (byte := int.from_bytes(self.port.read(1), byteorder='little')) != Stimulator.STOP_BYTE and len(packet) < Stimulator.MAX_PACKET_BYTES:
                packet.append(byte)
            # Agrega el byte de paro para completar el paquete
            packet.append(Stimulator.STOP_BYTE)
            # Si se excede el tamaño lanza una excepción
            if len(packet) >= Stimulator.MAX_PACKET_BYTES:
                raise Exception('Packet error')
            # Si está bien lo imprime (sin checar CRC aún)
            else:
                #print('Packet {}'.format(['{:02X}'.format(byte) for byte in packet]))
                if packet[6] == command:
                    received = True
        if command == Stimulator.INIT:
            print('receive INIT #{}'.format(packet[5]))
            return packet[5]
        elif command == Stimulator.UNKNOWN:
            pass
        elif command == Stimulator.GETSTIMULATIONMODEACK:
            print('receive GETSTIMULATIONMODEACK #{}'.format(packet[5]))
            print(f'   result: {packet[7]} stimulation mode: {packet[8]}')
        elif command == Stimulator.INITCHANNELLISTMODEACK:
            print('receive INITCHANNELLISTMODEACK #{}'.format(packet[5]))
            print(f'   result: {packet[7]}')
        elif command == Stimulator.STARTCHANNELLISTMODEACK:
            print('receive STARTCHANNELLISTMODEACK #{}'.format(packet[5]))
            print(f'   result: {packet[7]}')
        elif command == Stimulator.STOPCHANNELLISTMODEACK:
            pass
        elif command == Stimulator.SINGLEPULSEACK:
            print('receive SINGLEPULSEACK #{}'.format(packet[5]))
            print(f'   result: {packet[7]}')
        elif command == Stimulator.STIMULATIONERROR:
            pass

    def send_packet(self, command, **kwargs):
        """
        Rutina que manda un paquete, convirtiéndolo de una lista de hex
        a una de bytes y transmitiendo al puerto
        """
        # Asume que no hay payload
        packet_payload = []
        # Comandos implementados
        if command == Stimulator.INITACK:
            print('send INITACK #{}'.format(self.packet_count))
            packet_payload = [kwargs['init_packet_number'], command, Stimulator.INITACK_RESULT_OK]
        elif command == Stimulator.WATCHDOG:
            print('send WATCHDOG #{}'.format(self.packet_count))
            packet_payload = [self.packet_count, command]
        elif command == Stimulator.GETSTIMULATIONMODE:
            print('send GETSTIMULATIONMODE #{}'.format(self.packet_count))
            packet_payload = [self.packet_count, command]
        elif command == Stimulator.INITCHANNELLISTMODE:
            print('send INITCHANNELLISTMODE #{}'.format(self.packet_count))
            params = [kwargs['lff'], kwargs['active_channels'], kwargs['active_lf_channels'], kwargs['ipi']]
            params = params + [(kwargs['msi'] & 0xFF00)>>8, (kwargs['msi'] & 0x00FF), kwargs['channel_execution']]
            packet_payload = [self.packet_count, command] + params
        elif command == Stimulator.STARTCHANNELLISTMODE:
            print('send STARTCHANNELLISTMODE #{}'.format(self.packet_count))
            params = []
            for channel in kwargs['channel_config']:
                params = params + [channel['mode'], (channel['pulse_width'] & 0xFF00)>>8, channel['pulse_width'] & 0x00FF, channel['current']]
            packet_payload = [self.packet_count, command] + params
        elif command == Stimulator.STOPCHANNELLISTMODE:
            packet_payload = [self.packet_count, command]
        elif command == Stimulator.SINGLEPULSE:
            print('send SINGLEPULSE #{}'.format(self.packet_count))
            params = [kwargs['channel'], (kwargs['pulse_width'] & 0xFF00)>>8, kwargs['pulse_width'] & 0x00FF, kwargs['current']]
            packet_payload = [self.packet_count, command] + params
        # Si el comando está implementado, tiene payload
        if len(packet_payload):
            # Calcula checksum del payload
            checksum = crccheck.crc.Crc8.calc(packet_payload)
            checksum = self.stuff_byte(checksum)
            # Calcula datalength con XOR 0x55
            datalength = self.stuff_byte(len(packet_payload))
            # Preámbulo del paquete
            packet = [Stimulator.START_BYTE, Stimulator.STUFFING_BYTE, checksum, Stimulator.STUFFING_BYTE, datalength]
            # Payload y final del paquete
            packet = packet + packet_payload + [Stimulator.STOP_BYTE]
            # Incrementa el contador de paquetes enviados
            self.packet_count = (self.packet_count + 1)%256
            # transmite los bytes uno a uno
            for byte in packet:
                self.port.write(byte.to_bytes(1, 'little'))
        # Comando no implementado
        else:
            print('N/A')
        return self.packet_count

    def simulate_rehastim_packet(self, command, **kwargs):
        """
        Rutina que simula el envío de un paquete por el rehastim (adaptacion de send_packet)
        """
        # Asume que no hay payload
        packet_payload = []
        # Comandos implementados
        if command == Stimulator.INIT:
            print('(rehastim send INIT)')
            packet_payload = [self.rehastim_packet_count, command, Stimulator.VERSION]
        elif command == Stimulator.UNKNOWN:
            pass
        elif command == Stimulator.GETSTIMULATIONMODEACK:
            print('(rehastim send GETSTIMULATIONMODEACK)')
            packet_payload = [self.rehastim_packet_count, command, kwargs['result'], kwargs['stimulation_mode']]
        elif command == Stimulator.INITCHANNELLISTMODEACK:
            print('(rehastim send INITCHANNELLISTMODEACK)')
            packet_payload = [self.rehastim_packet_count, command, kwargs['result']]
        elif command == Stimulator.STARTCHANNELLISTMODEACK:
            print('(rehastim send STARTCHANNELLISTMODEACK)')
            packet_payload = [self.rehastim_packet_count, command, kwargs['result']]
        elif command == Stimulator.STOPCHANNELLISTMODEACK:
            pass
        elif command == Stimulator.SINGLEPULSEACK:
            print('(rehastim send SINGLEPULSEACK)')
            packet_payload = [self.rehastim_packet_count, command, kwargs['result']]
        elif command == Stimulator.STIMULATIONERROR:
            pass
        # Si el comando está implementado, tiene payload
        if len(packet_payload):
            # Calcula checksum del payload
            checksum = crccheck.crc.Crc8.calc(packet_payload)
            checksum = self.stuff_byte(checksum)
            # Calcula datalength con XOR 0x55
            datalength = self.stuff_byte(len(packet_payload))
            # Preámbulo del paquete
            packet = [Stimulator.START_BYTE, Stimulator.STUFFING_BYTE, checksum, Stimulator.STUFFING_BYTE, datalength]
            # Payload y final del paquete
            packet = packet + packet_payload + [Stimulator.STOP_BYTE]
            # Incrementa el contador de paquetes enviados
            self.rehastim_packet_count = (self.rehastim_packet_count + 1)%256
            # transmite los bytes uno a uno
            for byte in packet:
                self.port.write(byte.to_bytes(1, 'little'))
        # Comando no implementado
        else:
            print('N/A')
        return 0
