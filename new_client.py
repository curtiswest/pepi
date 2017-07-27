#!/usr/local/opt/pyenv/shims/python
"""
New_client.py: Provides the class used to run the client-side software for Pepi. Currently only works in the terminal,
but will probably be refactored into a separate process for implementation of a GUI at a later date.
"""
from datetime import datetime
import os
import subprocess
import logging
import logging.config
import signal
import time
import uuid
import zmq
import cv2
from communication.communication import CommunicationSocket, Poller
from communication.pymsg import *
import pepi_config as pc
from stoppablethread import StoppableThread
from utils import tic, toc, toc_seconds

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class KnownServer:
    """
    A server that the client knows exists through dynamic discovery.
    """
    def __init__(self, ip, ident_socket_id=None, control_socket_id=None, data_socket_id=None):
        self.ip = ip
        self.ident_socket_id = ident_socket_id
        self.control_socket_id = control_socket_id
        self.data_socket_id = data_socket_id

    def is_complete(self):
        return self.ip and self.ident_socket_id and self.control_socket_id and self.data_socket_id

    def __key(self):
        return self.ip, self.ident_socket_id, self.control_socket_id, self.data_socket_id

    def __eq__(self, other):
        return any(self.__key()[i] == other.__key()[i] for i in range(0, len(self.__key())))

    def __hash__(self):
        ip, iid, cid, did, = self.__key()
        iid = str(iid)
        cid = str(cid)
        did = str(did)
        tup = ip, iid, cid, did
        return hash(tup)

    def __str__(self):
        return str(self.__key())


class TerminalThread(StoppableThread):
    def __init__(self):
        super(TerminalThread, self).__init__()
        self.comm_inproc = CommunicationSocket(CommunicationSocket.SocketType.PAIR)
        self.comm_inproc.connect_to('inproc://comms')
        signal.signal(signal.SIGINT, self.signal_handler)

    @staticmethod
    def signal_handler(frame, signal):
        pass

    def run(self):
        while not self.is_stopped():
            try:
                inp = raw_input('Command: ')
            finally:
                if inp.strip() == 'exit':
                    print 'Exiting..'
                    msg = InprocMessage('exit')
                    self.comm_inproc.send(msg.wrap().serialize())
                    time.sleep(1)
                    self.stop()
                else:
                    msg = InprocMessage(inp.strip())
                    self.comm_inproc.send(msg.wrap().serialize())

class CommunicationThread(StoppableThread):
    def __init__(self):
        super(CommunicationThread, self).__init__()
        self.known_servers = {}
        self.ident_socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.control_socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.data_socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.comm_inproc = CommunicationSocket(CommunicationSocket.SocketType.PAIR)

        # Bind sockets & setup
        self.ident_socket.bind_to('tcp://*:{}'.format(pc.IDENT_PORT))
        self.control_socket.bind_to('tcp://*:{}'.format(pc.CONTROL_PORT))
        self.data_socket.bind_to('tcp://*:{}'.format(pc.DATA_PORT))
        self.comm_inproc.bind_to('inproc://comms')
        self.ident_socket.setsockopt(zmq.ROUTER_MANDATORY, True)
        self.control_socket.setsockopt(zmq.ROUTER_MANDATORY, True)
        self.data_socket.setsockopt(zmq.ROUTER_MANDATORY, True)

        # Register Sockets with a Poller
        self.poller = Poller()
        self.poller.register(self.ident_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.control_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.data_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.comm_inproc, Poller.PollingType.POLLIN)

        # Setup storage
        self.queued_data = []
        self.heartbeat_successful = False

        # Pre-generate our ident_msg for performance
        ident_msg = IdentityMessage('10.0.0.5', '{}'.format(uuid.uuid4().hex[:8]))
        self.ident_msg_serial = ident_msg.wrap().serialize()

    def get_image_dir(self):
        image_dir = "images/" + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')  # Directory for writing images
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        return image_dir

    def disconnect_notifier(self):
        for server in self.known_servers.values():
            msg = ControlMessage(ppmsg.DISCONNECT)
            if server.control_socket_id:
                self.control_socket.send_multipart(server.control_socket_id, msg.wrap().serialize())
            else:
                logging.error('Could not disconnect from server because control socket not connected!')
        time.sleep(3)

    def ident_message_handler(self, socket, identity, message):
        logging.debug('Handling ident message')
        # Need to check if this is a known server
        try:
            # Try updating server
            server = self.known_servers[message.identifier]
        except KeyError:
            # Else, work with a new server
            server = KnownServer(message.ip)
        server.ip = message.ip
        if socket == self.ident_socket:
            server.ident_socket_id = identity
        elif socket == self.control_socket:
            server.control_socket_id = identity
        elif socket == self.data_socket:
            server.data_socket_id = identity
        self.known_servers[message.identifier] = server
        # Acknowledge ident message with our ident
        socket.send_multipart(identity, self.ident_msg_serial)

    def control_message_handler(self, socket, identity, message):
        logging.debug('Handling control message')
        if message.command == ppmsg.PING:
            socket.send_multipart(identity, ControlMessage(ppmsg.PONG).wrap().serialize())
        elif message.command == ppmsg.GET_STILL:
            for id in self.known_servers.keys():
                if self.known_servers[id].control_socket_id == identity:
                    self.queued_data.append((id, message.values[0]))
                    break
            else:
                logging.error('Control message from unknown server!')
        elif message.command == ppmsg.START_STREAM:
            for id in self.known_servers.keys():
                if self.known_servers[id].control_socket_id == identity:
                    self.queued_data.append((id, message.values[0]))
                    break
            else:
                logging.error('Stream message from unknown server!')
        pass

    def data_message_handler(self, socket, identity, message):
        logging.debug('Handling data message')
        if message.data_bytes:
            bytes_transferred = 0
            for (server_id, data_code) in self.queued_data:
                if data_code == message.data_code:
                    bytes_transferred += len(message.data_bytes)
                    if data_code == 'stream':
                        global player
                        player.stdin.write(message.data_bytes)
                        self.frames += 1
                        break
                    else:
                        # Save the image under the server_id / data code
                        image = utils.decode_image(message.data_bytes)
                        fname = self.image_dir + '/' + server_id + '_' + data_code
                        cv2.imwrite('{}.png'.format(fname), image)
                        # Remove the data from the internal data queue
                        self.queued_data.remove((server_id, data_code))
                        break
            else:
                print 'Data from unknown data source/server!'
        if message.data_string:
            raise NotImplementedError('Cannot yet handle DataMessages with data_string')

    def inproc_message_handler(self, socket, identity, message):
        assert isinstance(message, InprocMessage), 'Inproc handler get a non-InprocMessage message'
        logging.debug('Handling inproc message')

        if message.msg_req == 'list servers':
            print 'Known servers\'s IDs: ' + str(self.known_servers.keys())
        elif message.msg_req == 'capture':
            req_msg = ControlMessage(ppmsg.GET_STILL).wrap().serialize()
            for s in self.known_servers.values():
                if s.is_complete():
                    self.control_socket.send_multipart(s.control_socket_id, req_msg)
            print 'Captured'
        elif message.msg_req == 'download':
            self.image_dir = self.get_image_dir()
            for (server_id, data_code) in self.queued_data:
                # Send off requests for the data to associated servers
                server = self.known_servers[server_id]
                req_msg = DataMessage(data_code).wrap().serialize()
                self.data_socket.send_multipart(server.data_socket_id, req_msg)
            print 'Downloaded.'
        elif message.msg_req.startswith('start stream'):
            #TODO: implement server selection
            cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
            self.player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)

            self.start_time = time.time()
            self.frames = 0
            req_msg = ControlMessage(ppmsg.START_STREAM).wrap().serialize()
            test_server = self.known_servers.values()[0]
            self.control_socket.send_multipart(test_server.control_socket_id, req_msg)
        elif message.msg_req == 'stop stream':
            self.player.terminate()
            delta = time.time() - self.start_time
            req_msg = ControlMessage(ppmsg.STOP_STREAM).wrap().serialize()
            test_server = self.known_servers.values()[0]
            self.control_socket.send_multipart(test_server.control_socket_id, req_msg)
            logging.info('Got {} frames in {}s. Frame rate: {} fps'.format(self.frames, delta, (self.frames / delta)))
        elif message.msg_req == 'disconnect':
            req_msg = ControlMessage(ppmsg.DISCONNECT).wrap().serialize()
            for server in self.known_servers.values():
                self.control_socket.send_multipart(server.control_socket_id, req_msg)
        elif message.msg_req == 'exit':
            # Send disconnects out
            req_msg = ControlMessage(ppmsg.DISCONNECT).wrap().serialize()
            for server in self.known_servers.values():
                self.control_socket.send_multipart(server.control_socket_id, req_msg)
            time.sleep(1)
            self.ident_socket.close()
            self.control_socket.close()
            self.data_socket.close()
            self.stop()
        elif not message.msg_req:
            # Empty message
            pass
        else:
            logging.error('Unknown command! Given command: {}'.format(message.msg_req))

    def server_message_router(self, socket, identity, message):
        """
        Routes the message received on the given socket to the appropriate handler for processing.
        Args:
            socket (CommunicationSocket): the CommunicationSocket the `message` was received on
            identity: the identity that `socket` can send a message to if it needs to reply
            message (ProtobufMessageWrapper): the received message to handle
        Raises:
            TypeError: when given a message of a type that cannot be handled
        """
        if isinstance(message, WrapperMessage):
            message = message.unwrap()

        if isinstance(message, IdentityMessage):
            self.ident_message_handler(socket, identity, message)
        elif isinstance(message, ControlMessage):
            self.control_message_handler(socket, identity, message)
        elif isinstance(message, DataMessage):
            self.data_message_handler(socket, identity, message)
        elif isinstance(message, InprocMessage):
            self.inproc_message_handler(socket, identity, message)
        else:
            raise TypeError('Cannot handle message of type {}'.format(type(message)))

    def run(self):
        # Start polling
        bytes_transferred = 0
        time_taken = 0
        self.frames = 0

        while not self.is_stopped():
            sockets = self.poller.poll(100)
            for socket in sockets:
                tic()

                try:
                    identity, data = socket.receive_multipart()
                except CommunicationSocket.SocketTypeError:
                    identity, data = None, socket.receive()
                finally:
                    msg = WrapperMessage.from_serialized_string(data).unwrap()
                    self.server_message_router(socket, identity, msg)
                    time_taken += toc_seconds()
                    bytes_transferred += len(data)
        else:
            logging.info('Stopping CommunincationThread..')
            # self.disconnect_notifier()

class ClientBackend(object):
    def __init__(self):
        # Setup local environment
        logging.config.fileConfig('setup/logging_config.ini')

        # Spin up threads
        comm_thread = CommunicationThread()
        comm_thread.daemon = True
        comm_thread.start()
        terminal_thread = TerminalThread()
        terminal_thread.daemon = True
        terminal_thread.start()

        # Collect threads when they decjde to exit
        while not comm_thread.is_stopped() and not terminal_thread.is_stopped():
            pass
        terminal_thread.join()
        comm_thread.join()

if __name__ == '__main__':
    c = ClientBackend()