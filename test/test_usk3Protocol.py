# coding=utf-8
from test.extended_clock import ExtendedClock
from usk3_protocol.usk3_packet import Usk3Packet
from usk3_protocol.usk3_protocol import Usk3Protocol, Usk3ProtocolSharedData
from twisted.test import proto_helpers

__author__ = 'SVS'

from twisted.trial.unittest import TestCase


class FakeTransport(object):
    def __init__(self):
        self.current_data = bytearray()
        self.counter = 0

    def write(self, data):
        self.current_data += data
        self.counter += 1

    def reset(self):
        del(self.current_data[:])


# noinspection PyPep8Naming
class TestUsk3Protocol(TestCase):
    def __init__(self, methodName):
        super(TestUsk3Protocol, self).__init__(methodName)
        self.clock = None
        self.protocol = None
        self.shared_data = Usk3ProtocolSharedData()
        self.test_val = 0

    def setUp(self):
        self.clock = ExtendedClock()
        del self.shared_data.command_queue[:]
        self.protocol = Usk3Protocol(self.shared_data, self.clock)

    def tearDown(self):
        self.protocol.release_resources()

    def test_protocol(self):
        self.test_val = 0

        def callback(response):
            self.test_val += 1

        protocol = self.protocol
        self.assertIsInstance(protocol, Usk3Protocol)
        transport = proto_helpers.StringTransportWithDisconnection()
        transport.protocol = protocol
        transport.write('hello')
        self.assertEquals(transport.value(), 'hello')
        transport.clear()

        protocol.makeConnection(transport)

        self.assertTrue(protocol.connected)
        self.assertEquals(transport.value(), '')
        self.clock.advance(22)
        self.assertTrue(protocol.connected)
        packet = Usk3Packet(1, 0x100)
        packet.callback_func = callback
        protocol.add_command(packet)
        protocol.add_command(packet)
        protocol.add_command(packet)
        self.clock.advance(20)
        self.assertFalse(protocol.connected)
        transport.connected = True
        protocol.makeConnection(transport)
        self.assertTrue(protocol.connected)
        self.clock.advance(10)
        self.assertTrue(protocol.connected)
        self.clock.advance(6)
        self.assertFalse(protocol.connected)
        transport.connected = True
        protocol.makeConnection(transport)
        self.assertTrue(protocol.connected)
        self.assertEquals(len(self.shared_data.command_queue), 0x02)
        self.assertIsInstance(self.shared_data.current_command, Usk3Packet)
        protocol.dataReceived(str(Usk3Packet(0, 0x00)))
        self.assertEquals(len(self.shared_data.command_queue), 0x01)
        self.assertIsInstance(self.shared_data.current_command, Usk3Packet)
        protocol.dataReceived(str(Usk3Packet(0, 0x00)))
        self.assertEquals(len(self.shared_data.command_queue), 0x00)
        self.assertIsInstance(self.shared_data.current_command, Usk3Packet)
        protocol.dataReceived(str(Usk3Packet(0, 0x00)))
        self.assertEquals(None, self.shared_data.current_command)

        self.assertEquals(self.test_val, 0x03)