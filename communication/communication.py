"""
Communication.py: Provides CommunicationSocket and Poller classes used for communication.

CommunicationSocket is a wrapper around ZMQ's socket that abstracts away direct access to ZMQ for simplicity.
Poller works with CommunicationSockets to avoid the need to busy-wait or poll on Sockets to retrieve messages from them,
enabling asynchronous responses.
"""
import logging
import uuid
import zmq

import utils.misc

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.2'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'

logger = logging.getLogger(__name__)

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

    @property
    def identity(self):
        return self._socket.identity

    @identity.setter
    def identity(self, value):
        self._socket.identity = value

    @property
    def send_timeout(self):
        return self._socket.sndtimeo

    @send_timeout.setter
    def send_timeout(self, value):
        self._socket.sndtimeo = value

    @property
    def receive_timeout(self):
        return self._socket.rcvtimeo

    @receive_timeout.setter
    def receive_timeout(self, value):
        self._socket.rcvtimeo = value

    def router_mandatory(self, value):
        if self.type != CommunicationSocket.SocketType.ROUTER:
            raise self.SocketTypeError('Must be a router to set router_mandatory')
        self._socket.router_mandatory = int(bool(value))

    @property
    def linger(self):
        return self._socket.linger

    @linger.setter
    def linger(self, value):
        self._socket.linger = value

    class SocketType(object):
        """
            Indicates the type of CommunicationSocket this instance is and therefore which messages are associated
            with the send() and receive() functions.
        """
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
        PAIR = zmq.PAIR

    class SocketTypeError(Exception):
        """
        Indicates that the socket is of the wrong type to perform the requested operation.
        """
        pass

    class MessageRoutingError(Exception):
        """
        Indicates that the message could not be routed to the specified destination.
        """
        pass

    class TimeoutError(Exception):
        """
        Indicates that the communication operation requested has timed out.
        """
        pass

    class StateError(Exception):
        """
        Indicates that this communication socket is in the incorrect state to perform the requested operation.

        For example, a REQUEST socket that has sent a message already cannot send a second until it receives a reply.
        Attempting to do so may raise a StateError.
        """
        pass

    def __init__(self, socket_type):
        if not isinstance(socket_type, int):
            msg = 'Socket_type must be an int, not {}'.format(type(socket_type))
            logging.warn(msg)
            raise TypeError(msg)
        self._context = zmq.Context.instance()
        self.type = socket_type
        try:
            self._socket = self._context.socket(socket_type=socket_type)
        except zmq.ZMQError as e:
            msg = "Couldn't construct ZMQ socket. Incorrect socket_type value?: {}".format(socket_type)
            logging.warn("Couldn't construct ZMQ socket. Incorrect socket_type value?: {}".format(socket_type))
            raise ValueError(msg, e)
        self.log = logging.getLogger(__name__)
        self._socket.identity = self.generate_id()
        self.data_wrapper_func = None
        self.data_wrapper_args = None


    # Socket setup functions

    def bind_to(self, address):
        """
        Binds this socket to the given address. Typically used on the server-side, although in practical terms there is
        little difference between `bind_to` and `connect_to`

        Args:
            address (str): the address string to bind to. Format is "protocol://interface:port" e.g. "tcp://*:10000".
                See ZMQ's `bind` function for more details on the format of the address string.
        """
        if not self._socket.closed:
            return self._socket.bind(address)

    def connect_to(self, address):
        """
        Connects to a socket at the given address. Typically used on client-side, although in practical terms there is
        little difference between `connect_to` and `bind_to`.

        Args:
            address: the address string to bind to. Format is "protocol://interface:port" e.g. "tcp://*:10000".
                See ZMQ's `bind` function for more details on the format of the address string.
        """
        if not self._socket.closed:
            return self._socket.connect(address)

    def disconnect_from(self, address):
        """
        Disconnect from a socket at the given address's endpoint.

        Args:
           address: the address string to disconnect from. Format is "protocol://interface:port" e.g. "tcp://*:10000".
               See ZMQ's `bind` function for more details on the format of the address string.
        """
        if not self._socket.closed:
            return self._socket.disconnect(address)

    def close(self, linger=None):
        """
        Closes the socket associated with this CommunicationSocket.

        Warnings: the socket cannot be reopened! This function will effectively kill this CommunicationSocket.
        """
        return self._socket.close(linger=linger)

    def setsockopt(self, sockopt, value=None):
        """
        Wrapper around the ZMQ method `set_sockopt`. Consult ZMQ documentation for sockopt's and values.
        """
        return self._socket.setsockopt(sockopt, value)

    def getsockopt(self, sockopt):
        """
        Wrapper around the ZMQ method `get_sockopt`. Consult ZMQ documentation for sockopt's and values.

        Returns:
            int or string: the socket option retrieved
        """
        return self._socket.getsockopt(sockopt)

    # Raw ZMQ sending/receiving functions

    def _send_raw(self, message):
        return self._socket.send(message)

    def _receive_raw(self):
        return self._socket.recv()

    def _receive_multipart_raw(self):
        assert self.type in {CommunicationSocket.SocketType.ROUTER, CommunicationSocket.SocketType.DEALER}
        if self.type == CommunicationSocket.SocketType.ROUTER:
            logging.debug('Router calling _receive_multipart_raw()')
            # Routers will receive identity information
            data = self._socket.recv_multipart()
            return data
        elif self.type == CommunicationSocket.SocketType.DEALER:
            # Dealers cannot access identity, but need to return empty frame anyways to maintain compatibility
            logging.debug('Dealer calling _receive_multipart_raw(), returning empty frame for compatibility')
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
            msg = 'Called send() but message cannot be None - nothing to send'
            logging.warn(msg)
            raise ValueError(msg)
        if self.type == CommunicationSocket.SocketType.ROUTER:
            msg = 'Router called send(), but must use send_multipart with an identity'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)

        try:
            if self.type == CommunicationSocket.SocketType.DEALER:
                self._socket.send_multipart(msg_parts=['', message])
            else:
                self._send_raw(message)
        except (zmq.ZMQError, zmq.error, zmq.error.Again) as e:
            if isinstance(e, zmq.error.Again) or e.errno == zmq.EAGAIN:
                msg = 'Send() timed out after {} ms'.format(self._socket.sndtimeo)
                logging.warn(msg)
                raise self.TimeoutError(msg)
            elif e.errno == zmq.EFSM:
                msg = 'Cannot send() in current state. Out of lock-step?'.format(self._socket.sndtimeo)
                logging.warn(msg)
                raise self.StateError(msg)
            else:
                raise

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
            msg = 'A non-None Identity is required call send_multipart()'
            logging.warn(msg)
            raise ValueError(msg)
        if not isinstance(message, str):
            msg = 'Send_multipart() message must be a str, not {}'.format(type(message))
            logging.warn(msg)
            raise TypeError(msg)
        if self.type not in {CommunicationSocket.SocketType.ROUTER, CommunicationSocket.SocketType.DEALER}:
            msg = 'Only sockets of type ROUTER/DEALER can call send_multipart()'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)
        msg_parts = [identity, '', message]
        try:
            return self._socket.send_multipart(msg_parts=msg_parts)
        except (zmq.ZMQError, zmq.error, zmq.error.Again) as e:
            if isinstance(e, zmq.error.Again) or e.errno == zmq.EAGAIN:
                msg = 'Send_multipart() timed out after {} ms'.format(self._socket.sndtimeo)
                logging.warn(msg)
                raise self.TimeoutError(msg)
            elif e.errno == zmq.EHOSTUNREACH:
                msg = 'Send_multipart() had no route to given identity ({}). Identity incorrect, or recipient not ' \
                      'connected?'.format(identity)
                logging.warn(msg)
                raise self.MessageRoutingError(msg)

    def receive_multipart(self):
        """
        Receives a multipart message on this socket.
        Returns:
            (identity, data): identity that sent this message, data received in the message
        """
        if self.type not in {CommunicationSocket.SocketType.ROUTER, CommunicationSocket.SocketType.DEALER}:
            msg = 'Only sockets of type ROUTER/DEALER can call receive_multipart()'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)
        try:
            values = self._receive_multipart_raw()
            identity, _, data = values
            return identity, data
        except ValueError:
            return None, None
        except (zmq.ZMQError, zmq.error, zmq.error.Again) as e:
            if isinstance(e, zmq.error.Again) or e.errno == zmq.EAGAIN:
                msg = 'Receive_multipart() timed out after {} ms.'.format(self._socket.rcvtimeo)
                logging.warn(msg)
                raise self.TimeoutError(msg)
            else:
                raise

    def receive(self):
        """
        Receives a message on this socket.
        Returns:
            str: the message's data
        Raises:
            SocketTypeError: if called on a ROUTER socket, which must use `receive_multipart`
        """
        if self.type == CommunicationSocket.SocketType.ROUTER:
            msg = 'Router called receive(), but must use receive_multipart() instead'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)
        if self.type == CommunicationSocket.SocketType.DEALER:
            frames = self._receive_multipart_raw()[2]  # Two empty frames when a dealer receives, but only want 3rd
            return frames
        else:
            try:
                return self._receive_raw()
            except (zmq.ZMQError, zmq.error, zmq.error.Again) as e:
                if isinstance(e, zmq.error.Again) or e.errno == zmq.EAGAIN:
                    msg = 'Receive() timed out after {} ms.'.format(self._socket.rcvtimeo)
                    logging.warn(msg)
                    raise self.TimeoutError(msg)
                elif e.errno == zmq.EFSM:
                    msg = 'Cannot receive() in current state. Out of lock-step?'.format(self._socket.sndtimeo)
                    logging.warn(msg)
                    raise self.StateError(msg)
                else:
                    raise

    def write(self, data):
        """
        Writes to this CommunicationSocket in a file-like manner. Not yet implemented.
        Args:
            data:
        """
        if self.type == CommunicationSocket.SocketType.ROUTER:
            msg = 'ROUTERs may not use write() function as they require an identity'
            logging.error(msg)
            raise CommunicationSocket.SocketTypeError(msg)
        if self.data_wrapper_func:
            if self.data_wrapper_args:
                data = self.data_wrapper_func(data, **self.data_wrapper_args)
            else:
                data = self.data_wrapper_func(data)
        self.send(message=data)

    def flush(self):
        """
        Flushes to this CommunicationSocket in a file-like manner. Not yet implemented.
        """
        pass
        # raise NotImplementedError('Flushing in a file-like manner not yet supported')

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
            msg = 'Only PUBLISHER socket types can publish()'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)
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
            msg = 'Only SUBSCRIBER socket types can subscribe()'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)
        return self._socket.setsockopt(zmq.SUBSCRIBE, topic)

    def listen(self):
        """
        Listens for a published message on this socket, so long as this is a SUBSCRIBER socket.
        Raises:
            SocketTypeError: when this CommunicationSocket is not a SUBSCRIBER.
        """
        if not self.type == self.SocketType.SUBSCRIBER:
            msg = 'Only SUBSCRIBER socket types can listen() for a message'
            logging.warn(msg)
            raise CommunicationSocket.SocketTypeError(msg)
        return self._receive_raw()


class Poller(object):
    """
    A wrapper around ZMQ's `Poller` to work with `CommunicationSocket` instead of raw ZMQ sockets. Enables responding
    to messages as they arrive, rather that waiting on polling on a socket's `receive` method.
    """

    # noinspection PyClassHasNoInit,PyMissingOrEmptyDocstring
    class PollingType(object):
        """
        Valid polling types to respond to.
        """
        NONE = 0  # No events
        POLLIN = zmq.POLLIN  # Inbound message events
        POLLOUT = zmq.POLLOUT  # Outbound message events
        POLLINOUT = zmq.POLLIN | zmq.POLLOUT  # Both inbound and outbound message events

    def __init__(self):
        self._poller = zmq.Poller()
        self.registered_sockets = dict()

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
            msg = 'Cannot Poller.register(). takes a CommunicationSocket not {}'.format(type(comm_socket))
            logging.warn(msg)
            raise TypeError(msg)
        try:
            polling_type = int(polling_type)
        except TypeError:
            msg = 'Poller.register() cannot convert polling_type to int, is of type: {}'.format(type(polling_type))
            logging.warn(msg)
            raise TypeError(msg)
        if polling_type not in utils.misc.variables_in_class(Poller.PollingType).values():
            msg = 'Poller.register() was given polling_type ({}), but that is not valid'.format(polling_type)
            logging.warn(msg)
            raise ValueError()
        self.registered_sockets[str(comm_socket._socket)] = comm_socket
        return self._poller.register(comm_socket._socket, polling_type)

    def unregister(self, comm_socket):
        if not isinstance(comm_socket, CommunicationSocket):
            msg = 'Poller.unregister() takes a CommunicationSocket, not {}'.format(type(comm_socket))
            logging.warn(msg)
            raise TypeError(msg)
        return self._poller.unregister(comm_socket._socket)

    def poll(self, timeout_ms=None):
        # type: (int) -> list
        """
        Polls on this Poller for messages, timing out after the given `timeout`
        Args:
            timeout_ms: the timeout to wait for in milliseconds, None to wait infinitely until message received.

        Returns:
            list(CommunicationSocket): empty list if no messages received on the registered sockets in the given
            `timeout`, else a list of CommunicationSockets that received messages.
        Raises:
            TypeError: when timeout_ms is not None and is not convertible to int
        """
        if timeout_ms is not None:
            try:
                timeout_ms = int(timeout_ms)
            except:
                msg = 'Poll() given timeout_ms is not convertible to int.'
                logging.warn(msg)
                raise TypeError(msg)
        poll_dict = dict(self._poller.poll(timeout=timeout_ms))
        return_list = []

        for key in poll_dict.keys():
            return_list.append(self.registered_sockets[str(key)])
        return return_list