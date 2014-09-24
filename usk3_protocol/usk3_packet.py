# coding=utf-8
__author__ = 'SVS'

from usk_util import crc16_ccitt
from usk3_common import get_bytearray_from_number, get_number_from_bytearray
import uuid, time


class Usk3Packet(object):
    CORRECT_PACKET = 0x00
    INCORRECT_PACKET = 0x1
    INCOMPLETE_PACKET = 0x02
    packet_signature = bytearray.fromhex('e447d67d')

    def __init__(self, module_number=0x00, command=0x00, packet_data=bytearray(), packet_id='', state=CORRECT_PACKET):
        self.packet_data = packet_data
        self.command = command
        self.module_number = module_number
        self.state = state
        self.length = 0x2b + len(packet_data)
        self._callback_func = None
        if len(packet_id) == 0:
            self.packet_id = uuid.uuid4().hex
        else:
            self.packet_id = packet_id
        id_len = len(self.packet_id)
        if id_len > 32:
            self.packet_id = self.packet_id[:32]
        elif id_len < 32:
            delta = 32 - id_len
            self.packet_id += ' ' * delta
        self.sent_time = None

    def set_current_timestamp(self):
        self.sent_time = time.time()

    def passed_time(self):
        if self.sent_time is None:
            return None
        return self.sent_time - time.time()

    @property
    def callback_func(self):
        return self._callback_func

    @callback_func.setter
    def callback_func(self, value):
        self._callback_func = value

    def _from_raw_data(self, raw_data):
        """

        :type raw_data: bytearray
        """
        self.state = Usk3Packet.INCORRECT_PACKET
        if not isinstance(raw_data, bytearray):
            return
        raw_data_len = len(raw_data)
        self.state = Usk3Packet.INCOMPLETE_PACKET
        if raw_data_len < 0x2b:
            # не полный пакет
            return

        if raw_data[:0x04] != Usk3Packet.packet_signature:
            # не совпала сигнатура
            self.state = Usk3Packet.INCORRECT_PACKET
            return

        self.length = get_number_from_bytearray(raw_data[0x04:0x06])
        if raw_data_len < self.length:
            # неполный пакет
            return
        self.packet_id = str(raw_data[0x06:0x26])
        self.module_number = int(raw_data[0x026])
        self.command = get_number_from_bytearray(raw_data[0x27:0x29])

        expected_crc = get_number_from_bytearray(raw_data[self.length - 2:self.length])
        real_crc = crc16_ccitt(str(raw_data[:self.length - 2]))
        if expected_crc == real_crc:
            data_len = self.length - 0x2b
            self.packet_data = raw_data[0x29:(0x29 + data_len)]
            xxx = len(self.packet_data)
            self.state = Usk3Packet.CORRECT_PACKET
        else:
            self.state = Usk3Packet.INCORRECT_PACKET

    @classmethod
    def from_raw_data(cls, raw_data):
        ret_val = cls()
        ret_val._from_raw_data(raw_data)
        return ret_val

    def __str__(self):
        binary_packet = str()
        if self.state == Usk3Packet.CORRECT_PACKET:
            packet = list()
            packet.append(str(Usk3Packet.packet_signature))
            packet.append(str(get_bytearray_from_number(self.length, 0x02)))
            packet_id = bytearray([' ' for x in range(0x20)])
            packet_id_len = len(self.packet_id)
            if packet_id_len > 0x20:
                packet_id_len = 0x20
            packet_id[0:packet_id_len] = self.packet_id[0:packet_id_len]
            packet.append(str(packet_id))
            packet.append(chr(self.module_number))
            packet.append(str(get_bytearray_from_number(self.command, 0x02)))
            packet.append(str(self.packet_data))
            binary_packet = ''.join(packet)
            binary_packet += str(get_bytearray_from_number(crc16_ccitt(binary_packet), 0x02))
        return binary_packet