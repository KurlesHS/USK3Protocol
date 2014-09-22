# coding=utf-8
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from usk_util import crc16, crc16_ccitt
from usk3_protocol.usk3_protocol import Usk3Protocol
from usk3_protocol.usk3_protocol_factory import Usk3ProtocolFactory
from usk3_protocol.usk3_test_manager import Usk3TestManager


__author__ = 'SVS'

from twisted.python import log
from sys import stdout
import sys
from twisted.internet.endpoints import TCP4ClientEndpoint

x = 0


def callback():
    global x
    x += 1


def callback2():
    global x
    print x


def main():
    f = stdout
    if len(sys.argv) > 1:
        f = file(sys.argv[1], 'w')
    log.startLogging(f)
    client = TCP4ClientEndpoint(reactor, 'localhost', 6666, timeout=Usk3Protocol.WAIT_RESPONSE_TIMEOUT)
    factory = Usk3ProtocolFactory(tcp_client=client)
    Usk3TestManager(factory)
    factory.start_listen()

    print type(reactor)
    #lp = LoopingCall(callback)
    #lp.start(0.001)

    #lp2 = LoopingCall(callback2)
    #lp2.start(1.)
    reactor.run()

if __name__ == '__main__':
    main()