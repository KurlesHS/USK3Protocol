# coding=utf-8

from twisted.internet.protocol import ClientFactory
from twisted.python.log import err

from .usk3_protocol import Usk3Protocol
from .usk3_protocol import Usk3ProtocolSharedData


class Usk3ProtocolFactory(ClientFactory):

    def __init__(self, clock=None, tcp_client=None):

        if clock is None:
            from twisted.internet import reactor
            clock = reactor
        self.clock = clock
        self.shared_data = Usk3ProtocolSharedData()
        self.tcp_client = tcp_client

    def set_incoming_packet_listener(self, listener):
        self.shared_data.incoming_packet_listener = listener

    def start_listen(self):
        if self.tcp_client is not None:
            d = self.tcp_client.connect(self)
            d.addErrback(err)

    def startedConnecting(self, connector):
        print 'Started to connect.'

    def buildProtocol(self, addr):
        print 'Connected.'
        print 'Resetting reconnection delay'
        return Usk3Protocol(self.shared_data, self.clock)

    def clientConnectionLost(self, connector, reason):
        print 'Lost connection.  Reason:', reason

    def clientConnectionFailed(self, connector, reason):
        print 'Connection failed. Reason:', reason
        self.clock.callLater(1., connector.connect)

    def stopFactory(self):
        print 'Stop factory'
        self.clock.callLater(1., self.start_listen)

    def add_command(self, packet):
        self.shared_data.add_command(packet)
