from usk3_common import get_bytearray_from_number, get_number_from_bytearray
from .usk3_packet import Usk3Packet


class Usk3Command(object):
    def __init__(self, module_number):
        self.module_number = module_number

    def __str__(self):
        return str(self.usk3_packet())

    def usk3_packet(self):
        return Usk3Packet(self.module_number)


class ChangeRelayCommand(Usk3Command):
    def __init__(self, module_number):
        super(ChangeRelayCommand, self).__init__(module_number)
        self.cmdData = bytearray()

    def change_relay(self, relay_number, state):
        self.cmdData += get_bytearray_from_number(state, 0x01)
        self.cmdData += get_bytearray_from_number(relay_number, 0x02)

    def usk3_packet(self):
        return Usk3Packet(self.module_number, 0x0001, self.cmdData)


class GetCurrentKpuRelayState(Usk3Command):
    def __init__(self, module_number):
        super(GetCurrentKpuRelayState, self).__init__(module_number)

    def usk3_packet(self):
        packet = Usk3Packet(self.module_number, 0x0002)
        packet.callback_func = self.response
        return packet

    def response(self, command):
        """

        :type command: Usk3Packet
        """
        if isinstance(command, Usk3Packet):
            if len(command.packet_data) != 4:
                return
            in_states = get_number_from_bytearray(command.packet_data[:2])
            out_states = get_number_from_bytearray(command.packet_data[2:])
            print in_states, out_states


