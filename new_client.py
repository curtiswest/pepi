#!/usr/local/opt/pyenv/shims/python
"""
New_client.py: Provides the class used to run the client-side software for Pepi. Currently only works in the terminal,
but will probably be refactored into a separate process for implementation of a GUI at a later date.
"""
from datetime import datetime
import os
import logging
import logging.config
import uuid
import zmq
from communication.communication import CommunicationSocket, Poller
from communication.pymsg import *
import pepi_config as pc
from utils import tic, toc, toc_seconds

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class NewClient(object):
    """
    NewClient runs the client-side software for talking to Servers.
    """

    class KnownServer:
        """
        A server that the client knows exists through dynamic discovery/
        """
        def __init__(self, ip, server_id, control_socket_id=None, data_socket_id=None):
            self.ip = ip
            self.server_id = server_id
            self.control_socket_id = control_socket_id
            self.data_socket_id = data_socket_id

        def __key(self):
            return self.ip, self.server_id, self.control_socket_id, self.data_socket_id

        def __eq__(self, other):
            print 'Checking equality'
            return any(self.__key()[i] == other.__key()[i] for i in range(0, len(self.__key())))

        def __hash__(self):
            ip, sid, cid, did, = self.__key()
            cid = str(cid)
            did = str(did)
            tup = ip, sid, cid, did,
            return hash(tup)

        def __str__(self):
            return str(self.__key())

    def message_handler(self, socket, identity, message):
        """
        Handles the message on the given socket, and replies to identity if necessary.
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
            # Need to check if this is a known server
            for server in self.known_servers:
                if server.ip == message.ip or server.identifier == message.identifier:
                    # Known server, update
                    server.ip = message.ip
                    server.identifier = message.identifier
                    if socket == self.ident_socket:
                        pass
                    if socket == self.control_socket:
                        server.control_socket_id = identity
                    if socket == self.data_socket:
                        server.data_socket_id = identity
                    break
            else:
                # New server, add to list of known
                new_server = self.KnownServer(message.ip, message.identifier)
                self.known_servers.append(new_server)
            socket.send_multipart(identity, self.ident_msg_serial)
        elif isinstance(message, ControlMessage):
            raise NotImplementedError('Cannot yet handle ControlMessages')
        elif isinstance(message, DataMessage):
            raise NotImplementedError('Cannot yet handle DataMessages')
        else:
            raise TypeError('Cannot handle message of type {}'.format(type(message)))

    def __init__(self):
        self.known_servers = []
        self.ident_socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.control_socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.data_socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.poller = Poller()
        self.image_dir = "images/" + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')  # Directory for writing images
        if not os.path.exists(self.image_dir):
            os.makedirs(self.image_dir)
        logging.config.fileConfig('setup/logging_config.ini')

        # Bind sockets & setup
        self.ident_socket.bind_to('tcp://*:{}'.format(pc.IDENT_PORT))
        self.control_socket.bind_to('tcp://*:{}'.format(pc.CONTROL_PORT))
        self.data_socket.bind_to('tcp://*:{}'.format(pc.DATA_PORT))
        self.ident_socket.setsockopt(zmq.ROUTER_MANDATORY, True)
        self.control_socket.setsockopt(zmq.ROUTER_MANDATORY, True)
        self.data_socket.setsockopt(zmq.ROUTER_MANDATORY, True)

        # Register Sockets with the Poller
        self.poller.register(self.ident_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.control_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.data_socket, Poller.PollingType.POLLIN)

        # Pre-generate our ident_msg for performance
        self.ident_msg = IdentityMessage('10.0.0.5', 'client_{}'.format(uuid.uuid4().hex[:4]))
        self.ident_msg_serial = self.ident_msg.wrapped().serialize()

        # Start polling
        tic()
        messages_handled = 0
        try:
            while True:
                sockets = self.poller.poll()
                messages_handled += len(sockets)

                for socket in sockets:
                    identity, data = socket.receive_multipart()
                    wrapped_msg = WrapperMessage.from_serialized_string(data)
                    self.message_handler(socket=socket, identity=identity, message=wrapped_msg.unwrap())
        except KeyboardInterrupt:
            print 'Messages handled: {}'.format(messages_handled)
            print 'Time taken: {}'.format(toc())
            print 'Messages/sec: {}'.format(messages_handled / toc_seconds())

c = NewClient()
