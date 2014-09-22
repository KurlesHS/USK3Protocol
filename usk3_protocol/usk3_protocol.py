# coding=utf-8

from twisted.internet.task import LoopingCall
from twisted.internet.protocol import Protocol, connectionDone
from .usk3_packet import Usk3Packet


class Usk3ProtocolSharedData(object):
    def __init__(self):
        self.command_queue = list()
        self.commands_in_process = dict()
        self.protocol = None
        self.incoming_packet_listener = None

    def add_command(self, packet):
        if not isinstance(packet, Usk3Packet):
            return
        protocol = self.protocol
        if isinstance(protocol, Usk3Protocol):
            protocol.add_command(packet)
        else:
            self.command_queue.append(packet)

    def inform_about_incoming_packet(self, packet):
        if self.incoming_packet_listener:
            self.incoming_packet_listener(packet)


class Usk3Protocol(Protocol):
    WAIT_RESPONSE_TIMEOUT = 30

    def __init__(self, usk3_protocol_shared_data, clock=None):
        """

        :type usk3_protocol_shared_data: Usk3ProtocolSharedData
        """
        if clock is None:
            from twisted.internet import reactor

            clock = reactor
        self.shared_command_data = usk3_protocol_shared_data
        self.shared_command_data.protocol = self
        self.clock = clock
        self._lc = LoopingCall(self.check_commands_ttl)
        self._lc.clock = clock
        self.received_buffer = bytearray()
        self._callback_func = None

    def _stop_timer(self):
        if self._lc.running:
            self._lc.stop()

    def _start_timer(self):
        self._stop_timer()
        self._lc.start(5., False)

    def release_resources(self):
        self._stop_timer()

    def dataReceived(self, data):
        self.received_buffer += bytearray(data)
        self.parse_received_data()

    def parse_received_data(self):
        if len(self.received_buffer) == 0:
            return
        packet = Usk3Packet.from_raw_data(self.received_buffer)
        if packet.state == Usk3Packet.INCOMPLETE_PACKET:
            self._start_timer()
        elif packet.state == Usk3Packet.INCORRECT_PACKET:
            #self.transport.loseConnection()
            del self.received_buffer[:]
        elif packet.state == Usk3Packet.CORRECT_PACKET:
            del self.received_buffer[:packet.length]
            if packet.command == 0:
                packet_id = packet.packet_id
                if packet_id in self.shared_command_data.commands_in_process:
                    command = self.shared_command_data.commands_in_process[packet_id]
                    if isinstance(command, Usk3Packet):
                        if command.callback_func is not None:
                            command.callback_func(command)
                    del self.shared_command_data.commands_in_process[packet_id]
            else:
                self.shared_command_data.inform_about_incoming_packet(packet)
            self.parse_received_data()

    def connectionLost(self, reason=connectionDone):
        self._stop_timer()
        self.shared_command_data.protocol = None
        self.connected = False

    def connectionMade(self):
        self._start_timer()
        self._check_commands()

    def _check_commands(self):
        if self.connected:
            for command in self.shared_command_data.command_queue:
                if isinstance(command, Usk3Packet):
                    self.transport.write(str(command))
                    if command.callback_func is not None:
                        command.set_current_timestamp()
                        self.shared_command_data.commands_in_process[command.packet_id] = command
            del self.shared_command_data.command_queue[:]

    def check_commands_ttl(self):
        commands_to_delete = list()
        for command_id, command in self.shared_command_data.commands_in_process.iteritems():
            if isinstance(command, Usk3Packet):
                if command.passed_time() >= Usk3Protocol.WAIT_RESPONSE_TIMEOUT:
                    commands_to_delete.append(command_id)
        for command_id in commands_to_delete:
            try:
                del self.shared_command_data.commands_in_process[command_id]
            except KeyError:
                pass

    def add_command(self, command):
        self.shared_command_data.command_queue.append(command)
        self._check_commands()