# coding=utf-8
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from .usk3_packet import Usk3Packet
from .usk3_command import ChangeRelayCommand
from .usk3_command import GetCurrentKpuRelayState
from usk3_protocol_factory import Usk3ProtocolFactory

__author__ = 'SVS'


class Usk3TestManager(object):
    def __init__(self, usk3_protocol_factory):
        """

        :type usk3_protocol_factory: Usk3ProtocolFactory
        """
        self.state = 0
        self.usk3_protocol_factory = usk3_protocol_factory
        self.usk3_protocol_factory.set_incoming_packet_listener(self.incoming_packet)
        l = LoopingCall(self.timeout)
        l.start(1., False)

    def incoming_packet(self, packet):
        if isinstance(packet, Usk3Packet):
            print ("packet:", packet.module_number, packet.packet_data)
            self.usk3_protocol_factory.add_command(Usk3Packet(packet.module_number, packet_id=packet.packet_id))

    def timeout(self):
        command = ChangeRelayCommand(0x01)
        command.change_relay(0, self.state)
        command.change_relay(1, self.state)
        command.change_relay(2, self.state)
        command.change_relay(3, self.state)
        self.state ^= 0x01
        self.usk3_protocol_factory.add_command(command.usk3_packet())
        self.usk3_protocol_factory.add_command(GetCurrentKpuRelayState(0x01).usk3_packet())
