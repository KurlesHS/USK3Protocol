# coding=utf-8
from usk3_protocol.usk3_packet import Usk3Packet

__author__ = 'SVS'

from twisted.trial.unittest import TestCase


class TestUsk3Packet(TestCase):
    def test_usk3_packet(self):
        packet = Usk3Packet(0x00, 0x00, bytearray('1234567890'), bytearray('12345'))
        raw_data = str(packet)
        packet2 = Usk3Packet.from_raw_data(bytearray(raw_data))
        self.assertEqual(packet2.state, Usk3Packet.CORRECT_PACKET)
        self.assertEqual(raw_data, str(packet2))