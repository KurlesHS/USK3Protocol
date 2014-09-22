# coding=utf-8
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from .usk3_packet import Usk3Packet
from usk3_protocol_factory import Usk3ProtocolFactory

__author__ = 'SVS'


class Usk3TestManager(object):
    def __init__(self, usk3_protocol_factory):
        """

        :type usk3_protocol_factory: Usk3ProtocolFactory
        """
        self.count = 0
        self.usk3_protocol_factory = usk3_protocol_factory
        self.usk3_protocol_factory.set_incoming_packet_listener(self.incoming_packet)

    def incoming_packet(self, packet):
        if isinstance(packet, Usk3Packet):
            print ("packet:", packet.module_number, packet.packet_data)
            self.usk3_protocol_factory.add_command(Usk3Packet(packet.module_number, packet_id=packet.packet_id))