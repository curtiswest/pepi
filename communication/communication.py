"""
Communication.py: Provides CommunicationSocket and Poller classes used for communication.

CommunicationSocket is a wrapper around ZMQ's socket that abstracts away direct access to ZMQ for simplicity.
Poller works with CommunicationSockets to avoid the need to busy-wait or poll on Sockets to retrieve messages from them,
enabling asynchronous responses.
"""
import logging
import uuid
import zmq
import utils

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class CommunicationSocket(object):
    """
    A socket that can be used to communicate with other CommunicationSockets in a variety of patterns.

    CommunicationSocket is a wrapper around ZMQ that (mostly) removes the need to directly access ZMQ to receive and
    send messages.
    """
    @staticmethod
    def generate_id(num_digits=4):
        """
        Generates a num_digits long unique hexadecimal ID, based on a UUID
        """
        return uuid.uuid4().hex[-num_digits:]

    def _get_identity(self):
        return self._socket.identity

    def _set_identity(self, value):
        self._socket.identity = value

    identity = property(_get_identity, _set_identity)

    class SocketType:
        """
            Indicates the type of CommunicationSocket this instance is and therefore which messages are associated
            with the send() and receive() functions.
        """
        def __init__(self):
            pass

        SERVER = zmq.REP
        REPLY = zmq.REP
        CLIENT = zmq.REQ
        REQUEST = zmq.REQ
        PUBLISHER = zmq.PUB
        SUBSCRIBER = zmq.SUB
        ROUTER = zmq.ROUTER
        DEALER = zmq.DEALER
        PUSH = zmq.PUSH
        PULL = zmq.PULL

    # noinspection PyMissingOrEmptyDocstring
    class SocketTypeError(Exception):
        pass

    def __init__(self, socket_type):
        if socket_type not in utils.variables_in_class(CommunicationSocket.SocketType).values():
            raise TypeError('Socket Type must be one of SocketType, not {}'.format(type(socket_type)))
        self._context = zmq.Context.instance()
        self.type = socket_type
        try:
            self._socket = self._context.socket(socket_type=socket_type)
        except zmq.ZMQError:
            raise ValueError("Couldn't construct ZMQ socket. Incorrect socket_type value?")
        self.log = logging.getLogger(__name__)
        self._socket.identity = self.generate_id()

    # Socket setup functions

    def bind_to(self, address):
        """
        Binds this socket to the given address. Typically used on the server-side, although in practical terms there is
        little difference between `bind_to` and `connect_to`

        Args:
            address (str): the address string to bind to. Format is "protocol://interface:port" e.g. "tcp://*:10000".
                See ZMQ's `bind` function for more details on the format of the address string.
        """
        return self._socket.bind(address)

    def connect_to(self, address):
        """
        Connects to a socket at the given address. Typically used on client-side, although in practical terms there is
        little difference between `connect_to` and `bind_to`.

        Args:
            address: the address string to bind to. Format is "protocol://interface:port" e.g. "tcp://*:10000".
                See ZMQ's `bind` function for more details on the format of the address string.
        """
        return self._socket.connect(address)

    def disconnect_from(self, address):
        """
        Disconnect from a socket at the given address's endpoint.

        Args:
           address: the address string to disconnect from. Format is "protocol://interface:port" e.g. "tcp://*:10000".
               See ZMQ's `bind` function for more details on the format of the address string.
        """
        return self._socket.disconnect(address)

    def close(self):
        """
        Closes the socket associated with this CommunicationSocket.

        Warnings: the socket cannot be reopened! This function will effectively kill this CommunicationSocket.
        """
        return self._socket.close()

    def setsockopt(self, sockopt, value=None):
        """
        Wrapper around the ZMQ method `set_sockopt`. Consult ZMQ documentation for sockopt's and values.
        """
        return self._socket.setsockopt(sockopt, value)

    def getsockopt(self, sockopt, value=None):
        """
        Wrapper around the ZMQ method `get_sockopt`. Consult ZMQ documentation for sockopt's and values.

        Returns:
            int or string: the socket option retrieved
        """
        return self._socket.getsockopt(sockopt, value)

    # Raw ZMQ sending/receiving functions

    def _send_raw(self, message):
        return self._socket.send(message)

    def _receive_raw(self):
        return self._socket.recv()

    def _receive_multipart_raw(self):
        assert self.type in {CommunicationSocket.SocketType.ROUTER, CommunicationSocket.SocketType.DEALER}
        if self.type == CommunicationSocket.SocketType.ROUTER:
            # Routers will receive identity information
            data = self._socket.recv_multipart()
            return data
        elif self.type == CommunicationSocket.SocketType.DEALER:
            # Dealers cannot access identity, but need to return empty frame anyways to maintain compatibility
            data = ['']
            data.extend(self._socket.recv_multipart())
            return data

    # Send/receive methods

    def send(self, message):
        """
        Sends a message over this socket.

        Args:
            message: the message to send
        Raises:
            ValueError: when a None message is received
            SocketTypeError: when called on a ROUTER socket. Routers must use `send_multipart` with an `identity`.
        """
        if message is None:
            raise ValueError('Message cannot be None - nothing to send')
        if self.type == CommunicationSocket.SocketType.ROUTER:
            raise CommunicationSocket.SocketTypeError('Routers must use send_multipart with an identity')
        if self.type == CommunicationSocket.SocketType.DEALER:
            # Dealers need to insert empty frame to maintain REQ/REP compatibility
            self._socket.send_multipart(msg_parts=['', message])
        else:
            self._send_raw(message)

    def send_multipart(self, identity, message):
        """
        Sends a multipart message to the given identity.
        Args:
            identity: the identity to send to
            message: the message to send

        Raises:
            ValueError: when `identity` is None or `message` is not of type str.
            SocketTypeError: when called on a non-ROUTER/DEALER socket.
        """
        if identity is None:
            raise ValueError('A non-None Identity is required to send a multipart message')
        if not isinstance(message, str):
            raise ValueError('Message must be a str, not {}'.format(type(message)))
        if self.type not in {CommunicationSocket.SocketType.ROUTER, CommunicationSocket.SocketType.DEALER}:
            raise CommunicationSocket.SocketTypeError('Only sockets of type ROUTER/DEALER can send multipart')
        msg_parts = [identity, '', message]
        return self._socket.send_multipart(msg_parts=msg_parts)

    def receive_multipart(self):
        """
        Receives a multipart message on this socket.
        Returns:
            (identity, data): identity that sent this message, data received in the message
        """
        if self.type not in {CommunicationSocket.SocketType.ROUTER, CommunicationSocket.SocketType.DEALER}:
            raise CommunicationSocket.SocketTypeError('Only sockets of type ROUTER/DEALER can receive multipart '
                                                      'messages')
        identity, _, data = self._receive_multipart_raw()
        return identity, data

    def receive(self):
        """
        Receives a message on this socket.
        Returns:
            str: the message's data
        Raises:
            SocketTypeError: if called on a ROUTER socket, which must use `receive_multipart`
        """
        if self.type == CommunicationSocket.SocketType.ROUTER:
            raise CommunicationSocket.SocketTypeError('ROUTERs must use receive_multipart')
        if self.type == CommunicationSocket.SocketType.DEALER:
            frames = self._receive_multipart_raw()[2]  # Two empty frames when a dealer receives, but only want 3rd
            return frames
        else:
            return self._receive_raw()

    def write(self, data):
        # TODO: implement using protobuf for consistency
        """
        Writes to this CommunicationSocket in a file-like manner. Not yet implemented.
        Args:
            data:
        """
        raise NotImplementedError('Writing in a file-like manner not yet supported')

    def flush(self):
        # TODO: implement
        """
        Flushes to this CommunicationSocket in a file-like manner. Not yet implemented.
        """
        raise NotImplementedError('Flushing in a file-like manner not yet supported')

        # PUB/SUB functions

    def publish(self, message, topic=''):
        """
        Publishes a message through this CommunicationSocket, so long as this is a PUBLISHER socket.
        Args:
            message: the message to publish
            topic: the topic to prefix to the message which subscribers may subscribe to
        Raises:
            SocketTypeError: when this CommunicationSocket is not a PUBLISHER.
        """
        if not self.type == self.SocketType.PUBLISHER:
            raise CommunicationSocket.SocketTypeError('Only PUBLISHER socket types can publish')
        return self._send_raw('{} {}'.format(topic, message))

    def subscribe(self, topic=''):
        """
        Subscribes to a topic this CommunicationSocket, so long as this is a SUBSCRIBER socket.
        Args:
            topic: the topic subscribe to. '' will subscribe to all topics.
        Raises:
            SocketTypeError: when this CommunicationSocket is not a SUBSCRIBER.
        """
        if not self.type == self.SocketType.SUBSCRIBER:
            raise CommunicationSocket.SocketTypeError('Only SUBSCRIBER socket types can subscribe')
        return self._socket.setsockopt(zmq.SUBSCRIBE, topic)

    def listen(self):
        """
        Listens for a published message on this socket, so long as this is a SUBSCRIBER socket.
        Raises:
            SocketTypeError: when this CommunicationSocket is not a SUBSCRIBER.
        """
        if not self.type == self.SocketType.SUBSCRIBER:
            raise CommunicationSocket.SocketTypeError('Only SUBSCRIBER socket types can listen for a message')
        return self._receive_raw()


class Poller(object):
    """
    A wrapper around ZMQ's `Poller` to work with `CommunicationSocket` instead of raw ZMQ sockets. Enables responding
    to messages as they arrive, rather that waiting on polling on a socket's `receive` method.
    """

    # noinspection PyClassHasNoInit,PyMissingOrEmptyDocstring
    class PollingType:
        POLLIN = zmq.POLLIN
        POLLOUT = zmq.POLLOUT

    def __init__(self):
        self._poller = zmq.Poller()
        self.registered_sockets = dict()
        self.printed = False

    # noinspection PyProtectedMember
    def register(self, comm_socket, polling_type):
        """
        Registers the given `comm_socket` to with this poller for the given polling_types.
        Args:
            comm_socket: a CommunicationSocket to register
            polling_type: a PollingType that designates what events the Poller should respond to

        Raises:
            TypeError: when `comm_socket` is not a CommunicationSocket
        """
        # type: (CommunicationSocket, int) -> bool
        if not isinstance(comm_socket, CommunicationSocket):
            raise TypeError('Comm_socket must be a CommunicationSocket, not {}'.format(type(comm_socket)))
        if polling_type not in utils.variables_in_class(Poller.PollingType).values():
            raise AssertionError('BINGO: {}'.format(utils.variables_in_class(Poller.PollingType)))
        # if not polling_type in {Poller.PollingType.POLLIN}
        self.registered_sockets[str(comm_socket._socket)] = comm_socket
        return self._poller.register(comm_socket._socket, polling_type)

    def poll(self, timeout_ms=None):
        # type: (int) -> list
        """
        Polls on this Poller for messages, timing out after the given `timeout`
        Args:
            timeout_ms: the timeout to wait for in milliseconds, None to wait infinitely until message received.

        Returns:
            list(CommunicationSocket): empty list if no messages received on the registered sockets in the given
            `timeout`, else a list of CommunicationSockets that received messages.
        """
        if timeout_ms is not None and (not isinstance(timeout_ms, int) or timeout_ms < 0):
            raise TypeError('Timeout_ms must be a >=0 int, not {} of type {}'.format(timeout_ms, type(timeout_ms)))
        poll_dict = dict(self._poller.poll(timeout=timeout_ms))
        return_list = []

        for key in poll_dict:
            if str(key) in self.registered_sockets:
                return_list.append(self.registered_sockets[str(key)])
        return return_list
