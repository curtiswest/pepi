#!/usr/local/opt/pyenv/shims/python
from __future__ import print_function

"""
New_client.py: Provides the class used to run the client-side software for Pepi. Currently only works in the terminal,
but will probably be refactored into a separate process for implementation of a GUI at a later date.
"""
import datetime
import os
import logging
import logging.config
import subprocess
import sys
import signal
import time
import uuid
import collections

from future.utils import viewitems
from future.builtins import input
import cv2

from communication.communication import CommunicationSocket, Poller
from communication.pymsg import WrapperMessage, IdentityMessage, ControlMessage, DataMessage, InprocMessage

import utils.pepi_config as pc
from utils.stoppablethread import StoppableThread
import utils.utils
from utils.iptools import IPTools

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.3'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class KnownServer:
    """
    A server that the client knows exists through dynamic discovery.
    """
    def __init__(self, ip, socket_id=None, health=0):
        self.ip = ip
        self.socket_id = socket_id
        self.health = health

    def is_complete(self):
        return self.ip and self.socket_id

    def is_alive(self):
        return self.health > 0

    def __key(self):
        return self.ip, self.socket_id

    def __eq__(self, other):
        return any(self.__key()[i] == other.__key()[i] for i in range(0, len(self.__key())))

    def __hash__(self):
        ip, id_ = self.__key()
        return hash((ip, str(id_)))

    def __str__(self):
        return str(self.__key())


class TerminalThread(StoppableThread):
    def __init__(self):
        super(TerminalThread, self).__init__()
        self.comm_inproc = CommunicationSocket(CommunicationSocket.SocketType.PAIR)
        self.comm_inproc.connect_to('inproc://comms')
        signal.signal(signal.SIGINT, self.signal_handler)

    @staticmethod
    def signal_handler(signal_, frame):
        pass

    def run(self):
        while not self.is_stopped():
            inp = input('Command: ').lower()
            if inp.strip() == 'exit':
                print('Exiting..')
                msg = InprocMessage('exit')
                self.comm_inproc.send(msg.wrap().serialize())
                self.stop()
            else:
                msg = InprocMessage(inp.strip())
                self.comm_inproc.send(msg.wrap().serialize())
            time.sleep(0.1)


class CommunicationThread(StoppableThread):
    class DataItem(object):
        """
        Represents a data item stored on a remote server.
        """
        def __init__(self, code, expiry=None, is_stream=False):
            """
            Initialises a data item.
            Args:
                code (int): the data item's data code
                expiry (int): optional, seconds from now until the data item expires
                is_stream (bool): True if this is a streaming data item, False otherwise
            """
            self.code = code
            self.expiry = expiry
            self.is_stream = is_stream
            if expiry:
                self.expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=expiry)
            else:
                self.expiry_time = None

        def update_expiry(self, seconds):
            """
            Updates the expiry to `seconds` from now.
            Args:
                seconds (int): seconds from now to update this data item's expiry to
            """
            self.expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=seconds)

        def is_expired(self):
            """
            Whether this data item is expired.
            Returns:
                bool: True if expired, False if either not expired, or no expiry time set.
            """
            if self.expiry_time:
                return datetime.datetime.now() > self.expiry_time
            else:
                return False

        def seconds_to_expiry(self):
            """
            How many seconds until this data item is expired.
            Returns:
                int: number of seconds until expiry if this data item has an expiry, -1 otherwise
            """
            if self.expiry_time:
                return (self.expiry_time - datetime.datetime.now()).total_seconds()
            else:
                return -1

        def __str__(self):
            if self.is_stream:
                return's_{}'.format(self.code)
            elif self.expiry_time:
                return '"{}" exp\'s in {}s'.format(self.code, round(self.seconds_to_expiry()))
            else:
                return str(self.code)

        def __repr__(self):
            return self.__str__()

        def __hash__(self):
            return hash(self.code)

        def __eq__(self, rhs):
            if isinstance(rhs, self.__class__):
                return rhs.code == self.code
            elif isinstance(rhs, (str, unicode)):
                return rhs == self.code
            else:
                return False

        def __ne__(self, other):
            return not self.__eq__(other)

    HB_INTERVAL = 9  # Seconds between heartbeats to client
    HB_HEALTH = 3  # Number of heartbeats missed before assumed dead

    def __init__(self):
        # Initialise self and data storage
        super(CommunicationThread, self).__init__()
        self.known_servers = dict()
        self.queued_data = collections.defaultdict(list)
        self.image_dir = ''
        self.player = None
        self.streaming_server_id = None

        # Setup client<->server socket
        self.socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.socket.router_mandatory = True
        self.socket.receive_timeout = 1000
        self.socket.send_timeout = 1000

        # Setup inter-thread socket
        self.comm_inproc = CommunicationSocket(CommunicationSocket.SocketType.PAIR)
        self.comm_inproc.receive_timeout = 1000
        self.comm_inproc.send_timeout = 1000

        # Connect to detected servers sockets & setup
        num_servers = 2
        num_found_servers = 0
        subnet = IPTools.get_subnet_from(IPTools.gateway_ip())
        logging.info('Scanning for {} expected servers..'.format(num_servers))
        for ip in IPTools.check_servers(subnet=subnet, port=pc.SOCKET_PORT, timeout=10, expected_servers=num_servers):
            self.socket.connect_to('tcp://{}:{}'.format(ip, pc.SOCKET_PORT))
            num_found_servers += 1
        logging.info('Found {} of {} expected servers'.format(num_found_servers, num_servers))
        self.comm_inproc.bind_to('inproc://comms')

        # Register Sockets with a Poller
        self.poller = Poller()
        self.poller.register(self.socket, Poller.PollingType.POLLIN)
        self.poller.register(self.comm_inproc, Poller.PollingType.POLLIN)

        # Pre-generate our ident_msg for performance
        self.client_id = uuid.uuid4().hex[:8]
        ip = IPTools.current_ip()
        ip = ip[0] if ip else ''
        ident_msg = IdentityMessage(ip, '{}'.format(self.client_id))
        self.ident_msg_serial = ident_msg.wrap().serialize()

        logging.info('Client ID #{} started and waiting..'.format(self.socket.identity))

    @staticmethod
    def get_image_dir():
        now = datetime.datetime.now()
        image_dir = "images/" + datetime.datetime.strftime(now, '%Y%m%d%H%M%S')  # Directory for writing images
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        return image_dir

    def ident_message_handler(self, socket, identity, message):
        logging.debug('Handling ident message')
        # Try to identify by the server's id given in the message. This may occur when we miss all the heartbeats
        # from the client, causing the client to recreate new sockets (with a new identity). The server will keep
        # its identity and data storage, so if we can identify it in our existing known servers, we can still
        # communicate with it just the same by updating the server's socket identity.
        for server_id_, server in viewitems(self.known_servers):
            if message.identifier == server_id_:
                logging.warn('Reconnecting server, but with a new ID. May have missed heartbeats.')
                if self.streaming_server_id == server_id_:
                    logging.warn('Reconnecting server was streaming to us, but now is not. Killing stream')
                    req_msg = ControlMessage(setting=False, payload={'stop_stream': None}).wrap().serialize()
                    self.socket.send_multipart(server.socket_id, req_msg)
                    if self.player:
                        self.player.kill()
                    self.streaming_server_id = None
                break
            elif server.socket_id == identity:
                # Identified by the server's socket ID
                logging.warn('Identified this server by it\'s socket ID, but the stored server_id doesn\'t match.'
                             'Message\'s ID: {} Stored ID: {}'.format(message.identifier, server_id_))
                break
        else:
            # Couldn't identify server, must be an ident from a new/unknown server
            server_id_ = message.identifier
            self.known_servers[server_id_] = KnownServer(ip=message.ip, health=self.HB_HEALTH)

        self.known_servers[server_id_].ip = message.ip
        self.known_servers[server_id_].socket_id = identity
        socket.send_multipart(identity, self.ident_msg_serial)  # Reply with our ident

    def control_message_handler(self, message, server=None, server_id=None):
        assert server is None or isinstance(server, KnownServer)
        logging.debug('Handling control message')

        if not server:
            logging.info('Control message from unknown server. No response..')
        else:
            for key, value in viewitems(message.payload):
                # Step through the payload and work on each value as needed
                logging.debug('Recv ControlMessage: Key: {} | Value: {}'.format(key, value))

                if key == 'ping':
                    # Reply to ping
                    msg = ControlMessage(setting=False, payload={'pong': None}).wrap().serialize()
                    self.socket.send_multipart(server.socket_id, msg)
                elif key == 'pong':
                    pass
                elif key == 'still':
                    if not server_id:
                        logging.error('Got a data code but not sure which server_id it was from.')
                    else:
                        try:
                            expiry = message.payload['expiry']
                        except KeyError:
                            expiry = None

                        logging.info('Got data_code {} from {}'.format(int(value), server_id))
                        self.queued_data[server_id].append(self.DataItem(int(value), expiry=expiry))
                elif key == 'start_stream':
                    logging.info('Got stream data_code {} from {}'.format(int(value), server_id))
                    self.queued_data[server_id].append(self.DataItem(int(value), is_stream=True))
                elif key == 'data_unavailable':
                    try:
                        value = int(value)
                        logging.warn('Data item {} is unavailable.'.format(value))
                        self.queued_data[server_id].remove(int(value))
                    except (ValueError, KeyError):
                        logging.error('Data item not stored or not code isn\'t in a valid format (int)')
                else:
                    print('Server replied: {} = {}'.format(key, value))

    def data_message_handler(self, message, server=None, server_id=None):
        assert server is None or isinstance(server, KnownServer)
        logging.debug('Handling data message')

        if not server or not server_id:
            logging.info('Data message from unknown server/server_id. No response..')
        else:
            if server_id in self.queued_data.keys():
                data_items = self.queued_data[server_id]
                for data_item in data_items:
                    if data_item.code == message.data_code:
                        break
                else:
                    data_item = None

                if data_item:
                    if data_item.is_stream:
                        print('Stream frame data size: {} bytes'.format(len(message.data_bytes)))
                        try:
                            self.player.stdin.write(message.data_bytes)
                        except IOError as e:
                            logging.warn('Couldn\'t write to player: {}'.format(e.message))
                    else:
                        if message.data_bytes:
                            image = utils.decode_image(message.data_bytes)
                            fname = self.image_dir + '/' + server_id + '_' + str(message.data_code)
                            cv2.imwrite('{}.png'.format(fname), image)
                            self.queued_data[server_id].remove(data_item)  # Remove the data from internal data queue
                        else:
                            logging.warn('Cannot yet handle DataMessages with data_string')
                else:
                    logging.error('Unexpected data item received. Data code: {}'.format(message.data_code))

    def inproc_message_handler(self, message):
        assert isinstance(message, InprocMessage), 'Inproc handler get a non-InprocMessage message'
        logging.debug('Handling inproc message')

        parts = message.msg_req.split()
        if parts:
            if 'exit' in parts:
                if self.player:
                    self.player.kill()
                self.socket.close()
                self.stop()

            if 'rescan' in parts:
                try:
                    num_servers = int(parts[parts.index('rescan')+1])
                except (IndexError, ValueError, AttributeError):
                    num_servers = len(self.known_servers.keys()) + 1
                num_found_servers = 0
                subnet = IPTools.get_subnet_from(IPTools.gateway_ip())

                for ip in IPTools.check_servers(subnet=subnet, port=pc.SOCKET_PORT, timeout=10,
                                                expected_servers=num_servers):
                    self.socket.connect_to('tcp://{}:{}'.format(ip, pc.SOCKET_PORT))
                    num_found_servers += 1
                logging.info('Found {} of {} expected servers.'.format(num_found_servers, num_servers))


            # Data Message Parts
            if 'download' in parts:
                self.image_dir = self.get_image_dir()

                dict_copy = self.queued_data
                for server_id, data_items in viewitems(dict_copy):
                    logging.debug('Server id: {}. Data codes: {}'.format(server_id, data_items))
                    server = self.known_servers[server_id]

                    for data_item in data_items:
                        if not data_item.is_expired() and not data_item.is_stream:
                            req_msg = DataMessage(data_item.code).wrap().serialize()
                            self.socket.send_multipart(server.socket_id, req_msg)
                        elif data_item.is_expired():
                            logging.warn('Tried to download data_code {}, but is expired'.format(data_item.code))
                            self.queued_data[server_id].remove(data_item)
                        elif data_item.is_stream:
                            # Can't and shouldn't download a stream data item
                            pass
            elif 'start_stream' in parts:
                if not self.streaming_server_id:
                    # TODO server selection
                    if len(self.known_servers.keys()) > 0:
                        if self.player is None:
                            cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264',
                                       '--network-caching=1000', '-']
                            self.player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)

                        server_id = self.known_servers.keys()[0]
                        server = self.known_servers[server_id]
                        req_msg = ControlMessage(setting=False, payload={'start_stream': None}).wrap().serialize()
                        self.socket.send_multipart(server.socket_id, req_msg)
                        self.streaming_server_id = server_id
                    else:
                        print('Cannot stream - no servers connected.')
                else:
                    print('Server {} is already streaming'.format(self.streaming_server_id))
            elif 'stop_stream' in parts:
                if self.streaming_server_id in self.known_servers:
                    server = self.known_servers[self.streaming_server_id]
                    req_msg = ControlMessage(setting=False, payload={'stop_stream': None}).wrap().serialize()
                    self.socket.send_multipart(server.socket_id, req_msg)
                    try:
                        self.queued_data[self.streaming_server_id].remove(self.DataItem(-1))
                        # TODO fix to work with any streaming data code?
                    except KeyError:
                        logging.warn('Couldn\'t remove streaming data item, wrong streaming_server_id?')

                    self.streaming_server_id = None
                    if self.player:
                        self.player.kill()
                        self.player = None
                else:
                    logging.error('Thought server {} was streaming, but no record of that server being connected now.'
                                  .format(self.streaming_server_id))
                    self.streaming_server_id = None
            elif 'get' in parts and 'set' in parts:
                print('Cannot set and get in the same command')
            elif 'get' in parts:
                get_parts = parts[parts.index('get')+1:]
                req_msg = ControlMessage(setting=False, payload={})

                # Meta message parts
                if 'servers' in get_parts:
                    get_parts.remove('servers')
                    print('Known servers\'s IDs: {}'.format(self.known_servers.keys()))

                if 'data_codes' in get_parts:
                    get_parts.remove('data_codes')
                    print('Queued data: {}'.format(self.queued_data))

                # Control message parts
                for part in get_parts:
                    # For each word after 'get', add it to the payload
                    req_msg.payload[part] = None

                for s in self.known_servers.values():
                    # Send the control message to all complete, alive servers
                    if s.is_complete() and s.is_alive():
                        self.socket.send_multipart(s.socket_id, req_msg.wrap().serialize())
            elif 'set' in parts:
                set_parts = parts[parts.index('set')+1:]
                req_msg = ControlMessage(setting=True, payload={})

                for i in range(0, len(set_parts), 2):
                    # Take each 'pair' (command, value) of elements after 'set'
                    try:
                        command = str(set_parts[i])
                        value = int(set_parts[i+1])
                    except IndexError:
                        # noinspection PyUnboundLocalVariable
                        logging.warn('Command {} was missing a value to set. Ignoring..'.format(command))
                    except ValueError:
                        logging.warn('Expected an integer/string value for command/value, but got {} of type {}'.format(
                            set_parts[i+1], type(set_parts[i+1])))
                    else:
                        req_msg.payload[command] = value
                for s in self.known_servers.values():
                    # Send the control message to all complete, alive servers
                    if s.is_complete() and s.is_alive():
                        self.socket.send_multipart(s.socket_id, req_msg.wrap().serialize())
        else:
            pass  # Empty message

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
            # Unwrap any wrapped messages
            message = message.unwrap()

        if isinstance(message, InprocMessage):
            # Message from the another thread, forward to the handler
            self.inproc_message_handler(message=message)
        elif isinstance(message, IdentityMessage):
            # Identity messages identify the server better than below methods
            self.ident_message_handler(socket=socket, identity=identity, message=message)
        else:
            # Must be a message from a server. Need to determine which server the message is from
            for server_id, server in viewitems(self.known_servers):
                # Try to identify the server by socket ID the message came from
                if server.socket_id == identity:
                    self.known_servers[server_id].health = self.HB_HEALTH  # Reset health of this server
                    break
            else:
                # Couldn't find the server by socket ID.
                logging.warn('Got a ControlMessage or DataMessage from an unknown server with '
                             'identity {}'.format(identity))
                server = None
                server_id = None

            try:
                # Route the message to the correct handler based on message type
                if isinstance(message, ControlMessage):
                    self.control_message_handler(message=message, server=server, server_id=server_id)
                elif isinstance(message, DataMessage):
                    self.data_message_handler(message=message, server=server, server_id=server_id)
                else:
                    raise TypeError('Cannot handle message of type {}'.format(type(message)))
            except CommunicationSocket.TimeoutError:
                logging.warn('Tried to send/receive on socket, but timed out. Continuing..')
            except CommunicationSocket.MessageRoutingError:
                logging.warn('Couldn\'t find route to send message. Possible server disconnection?')

    def purge_server(self, server_id):
        self.known_servers.pop(server_id, None)
        self.queued_data.pop(server_id, None)

    def run(self):
        heartbeat_at = time.time() + self.HB_INTERVAL
        while not self.is_stopped():
            if time.time() >= heartbeat_at:
                heartbeat_at += self.HB_INTERVAL  # Move next heartbeat time forward

                # Check each server for it's health
                dead_server_ids = []
                for server_id, server in viewitems(self.known_servers):
                    if not server.is_alive():
                        dead_server_ids.append(server_id)
                        logging.warn('Server {} is dead'.format(server_id))
                        continue
                    elif server.health < self.HB_HEALTH:
                        # Less than max health, might die soon
                        logging.debug('Need a heartbeat from server at {} soon. Health: {}'.format(server.ip,
                                                                                                   server.health))
                        try:
                            self.socket.send_multipart(server.socket_id,
                                                       ControlMessage(setting=False,
                                                                      payload={'ping': None}).wrap().serialize())
                        except CommunicationSocket.MessageRoutingError:
                            # Couldn't send message to server, so it is already dead
                            dead_server_ids.append(server_id)
                        except CommunicationSocket.TimeoutError as e:
                            logging.warn(e.message)
                    server.health -= 1

                # Remove any dead servers
                for server_id in dead_server_ids:
                    self.purge_server(server_id)

            sockets = self.poller.poll(self.HB_INTERVAL)
            for socket in sockets:
                if socket == self.comm_inproc:
                    identity, data = None, socket.receive()
                else:
                    identity, data = socket.receive_multipart()
                msg = WrapperMessage.from_serialized_string(data).unwrap()
                self.server_message_router(socket, identity, msg)
        else:
            logging.info('Stopping CommunicationThread..')


class ClientBackend(object):
    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%%(levelname)-8s: %(message)s')

        # Setup local environment
        logging.config.fileConfig('setup/logging_config.ini')

        # Spin up threads
        comm_thread = CommunicationThread()
        comm_thread.daemon = True
        comm_thread.start()
        terminal_thread = TerminalThread()
        terminal_thread.daemon = True
        terminal_thread.start()

        # Collect threads when they decide to exit
        terminal_thread.join()
        comm_thread.join()

if __name__ == '__main__':
    c = ClientBackend()
