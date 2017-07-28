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
import sys
import signal
import time
import uuid
import collections
import cv2
from communication.communication import CommunicationSocket, Poller
from communication.pymsg import *
import pepi_config as pc
from stoppablethread import StoppableThread

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.2'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class KnownServer:
    """
    A server that the client knows exists through dynamic discovery.
    """
    # def __init__(self, ip, ident_socket_id=None, control_socket_id=None, data_socket_id=None):
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
        ip, id_, = self.__key()
        tup = ip, str(id_)
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
    def signal_handler(signal_, frame):
        pass

    def run(self):
        while not self.is_stopped():
            inp = raw_input('Command: ')
            if inp.strip() == 'exit':
                print 'Exiting..'
                msg = InprocMessage('exit')
                self.comm_inproc.send(msg.wrap().serialize())
                self.stop()
            else:
                msg = InprocMessage(inp.strip())
                self.comm_inproc.send(msg.wrap().serialize())


class CommunicationThread(StoppableThread):
    HB_INTERVAL = 10  # Seconds between heartbeats to client
    HB_HEALTH = 3  # Number of heartbeats missed before assumed dead

    def __init__(self):
        # Initialise self and data storage
        super(CommunicationThread, self).__init__()
        self.known_servers = dict()
        self.queued_data = collections.defaultdict(list)
        self.image_dir = ''
        self.player = None

        # Setup client<->server socket
        self.socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        self.socket.router_mandatory = True
        self.socket.receive_timeout = 1000
        self.socket.send_timeout = 1000

        # Setup inter-thread socket
        self.comm_inproc = CommunicationSocket(CommunicationSocket.SocketType.PAIR)
        self.comm_inproc.receive_timeout = 1000
        self.comm_inproc.send_timeout = 1000

        # Bind sockets & setup
        self.socket.bind_to('tcp://*:{}'.format(pc.IDENT_PORT))
        self.comm_inproc.bind_to('inproc://comms')

        # Register Sockets with a Poller
        self.poller = Poller()
        self.poller.register(self.socket, Poller.PollingType.POLLIN)
        self.poller.register(self.comm_inproc, Poller.PollingType.POLLIN)

        # Pre-generate our ident_msg for performance
        self.client_id = uuid.uuid4().hex[:8]
        ident_msg = IdentityMessage('10.0.0.5', '{}'.format(self.client_id))  # TODO convert getting IP to method
        self.ident_msg_serial = ident_msg.wrap().serialize()

        logging.info('Client ID #{} starting up..'.format(self.socket.identity))

    @staticmethod
    def get_image_dir():
        image_dir = "images/" + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')  # Directory for writing images
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        return image_dir

    def ident_message_handler(self, socket, identity, message, server=None, server_id=None):
        assert server is None or isinstance(server, KnownServer)
        logging.debug('Handling ident message')
        if not server:
            # Try to identify by the server's id given in the message. This may occur when we miss all the heartbeats
            # from the client, causing the client to recreate new sockets (with a new identity). The server will keep
            # its identity and data storage, so if we can identify it in our existing known servers, we can still
            # communicate with it just the same by updating the server's socket identity.
            for server_id_, server in self.known_servers.iteritems():
                if message.identifier == server_id_:
                    server = self.known_servers[server_id_]
                    logging.warn('Reconnecting server, but with a new ID. May have missed heartbeats.')
                    break
            else:
                # Must be an ident from a new/unknown server
                server = KnownServer(message.ip, health=self.HB_HEALTH)

        server.ip = message.ip
        server.socket_id = identity
        self.known_servers[message.identifier] = server  # Store into dict
        socket.send_multipart(identity, self.ident_msg_serial)  # Reply with our ident

    def control_message_handler(self, socket, identity, message, server=None, server_id=None):
        assert server is None or isinstance(server, KnownServer)
        logging.debug('Handling control message')

        if not server:
            logging.info('Control message from unknown server. No response..')
        else:
            if message.command == ppmsg.PING:
                 socket.send_multipart(identity, ControlMessage(ppmsg.PONG).wrap().serialize())
            elif message.command == ppmsg.PONG:
                pass
            elif message.command == ppmsg.GET_STILL or message.command == ppmsg.START_STREAM:
                if not server_id:
                    pass # TODO handle this case
                else:
                    self.queued_data[server_id].append(message.values[0])
            elif message.command == ppmsg.DATA_UNAVAILABLE:
                data_code = message.values[0]
                logging.warn('Requested data item {} is unavailable.'.format(data_code))
                self.queued_data[server_id].remove(data_code)

    def data_message_handler(self, socket, identity, message, server=None, server_id=None):
        assert server is None or isinstance(server, KnownServer)
        logging.debug('Handling data message')
        if not server:
            logging.info('Data message from unknown server. No response..')
        else:
            if message.data_bytes:
                for server_id, data_codes in self.queued_data.iteritems():
                    if message.data_code in data_codes:
                        if message.data_code == 'stream':
                            # raise NotImplementedError('Cannot stream yet')
                            # print len(message.data_bytes)
                            # global player
                            self.player.stdin.write(message.data_bytes)
                            # self.frames += 1
                            break
                        else:
                            # Save the image under the server_id / data code
                            image = utils.decode_image(message.data_bytes)
                            fname = self.image_dir + '/' + server_id + '_' + message.data_code
                            cv2.imwrite('{}.png'.format(fname), image)
                            # Remove the data from the internal data queue
                            data_codes.remove(message.data_code)
                            self.queued_data[server_id] = data_codes
                            break
                else:
                    logging.error('Data from unknown data source/server!')
            if message.data_string:
                raise NotImplementedError('Cannot yet handle DataMessages with data_string')

    def inproc_message_handler(self, socket, identity, message):
        assert isinstance(message, InprocMessage), 'Inproc handler get a non-InprocMessage message'
        logging.debug('Handling inproc message')

        if message.msg_req == 'list servers':
            print 'Known servers\'s IDs: {}'.format(self.known_servers.keys())
        elif message.msg_req == 'capture':
            req_msg = ControlMessage(ppmsg.GET_STILL).wrap().serialize()
            for s in self.known_servers.values():
                if s.is_complete():
                    self.socket.send_multipart(s.socket_id, req_msg)
            print 'Capture messages sent'
        elif message.msg_req == 'list data':
            print 'Queued data: {}'.format(self.queued_data)
        elif message.msg_req == 'download':
            self.image_dir = self.get_image_dir()
            for server_id, data_codes in self.queued_data.iteritems():
                print('Server id: {}. Data codes: {}'.format(server_id, data_codes))
                server = self.known_servers[server_id]
                if isinstance(data_codes, list):
                    pass
                else:
                    data_codes = [data_codes]
                data_codes = list(data_codes)  # TODO fix wrapping

                for data_code in data_codes:
                    req_msg = DataMessage(data_code).wrap().serialize()
                    self.socket.send_multipart(server.socket_id, req_msg)
            print 'Download request messages sent'
        elif message.msg_req.startswith('start stream'):
            # TODO: implement server selection
            cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
            self.player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
            # self.start_time = time.time()
            # self.frames = 0
            req_msg = ControlMessage(ppmsg.START_STREAM).wrap().serialize()
            test_server = self.known_servers.values()[0]
            self.socket.send_multipart(test_server.socket_id, req_msg)
        elif message.msg_req == 'stop stream':
            self.player.terminate()
            # delta = time.time() - self.start_time
            req_msg = ControlMessage(ppmsg.STOP_STREAM).wrap().serialize()
            test_server = self.known_servers.values()[0]
            self.socket.send_multipart(test_server.socket_id, req_msg)
            # logging.info('Got {} frames in {}s. Frame rate: {} fps'.format(self.frames, delta, (self.frames / delta)))
        elif message.msg_req == 'exit':
            self.socket.close()
            self.stop()
        elif not message.msg_req:
            # Empty message
            pass
        else:
            logging.warn('Unknown command! Given command: {}'.format(message.msg_req))

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

        if isinstance(message, InprocMessage):
            self.inproc_message_handler(socket, identity, message)
        else:
            identified_server = None
            server_id = None
            for server_id, server in self.known_servers.iteritems():
                if server.socket_id == identity:
                    server.health = self.HB_HEALTH
                    identified_server = server
                    break

            if isinstance(message, IdentityMessage):
                self.ident_message_handler(socket, identity, message, identified_server, server_id)
            elif identified_server is not None:
                try:
                    if isinstance(message, ControlMessage):
                        self.control_message_handler(socket, identity, message, identified_server, server_id)
                    elif isinstance(message, DataMessage):
                        self.data_message_handler(socket, identity, message, identified_server, server_id)
                    else:
                        raise TypeError('Cannot handle message of type {}'.format(type(message)))
                except CommunicationSocket.TimeoutError:
                    logging.warn('Tried to send/receive on socket, but timed out. Continuing..')
                except CommunicationSocket.MessageRoutingError:
                    logging.warn('Couldn\'t find route to send message. Possible server disconnection?')
                    # TODO handle disconnection
            else:
                logging.warn('Got a ControlMessage or DataMessage from an unknown server with '
                             'identity {}'.format(identity))

    def delete_server(self, server_id):
        self.known_servers.pop(server_id, None)
        self.queued_data.pop(server_id, None)

    def run(self):
        heartbeat_at = time.time() + self.HB_INTERVAL
        while not self.is_stopped():
            if time.time() >= heartbeat_at:
                heartbeat_at += self.HB_INTERVAL  # Move next heartbeat time forward

                # Check each server for it's health
                dead_server_ids = []
                for server_id, server in self.known_servers.iteritems():
                    if not server.is_alive():
                        dead_server_ids.append(server_id)
                        logging.warn('Server {} is dead'.format(server_id))
                        continue
                    elif server.health == self.HB_HEALTH:
                        # Max health, must have received messages from that server so don't need to heartbeat
                        pass
                    else:
                        # Less than max health, might die soon
                        logging.debug('Need a heartbeat from server at {} soon. Health: {}'.format(server.ip,
                                                                                                   server.health))
                        try:
                            self.socket.send_multipart(server.socket_id, ControlMessage(ppmsg.PING).wrap().serialize())
                        except CommunicationSocket.MessageRoutingError:
                            # Couldn't send message to server, so it is already dead
                            dead_server_ids.append(server_id)
                        except CommunicationSocket.TimeoutError as e:
                            logging.warn(e.message)
                    server.health -= 1

                # Remove any dead servers
                for server_id in dead_server_ids:
                    self.delete_server(server_id)

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
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%%(levelname)-8s: %(message)s')

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
