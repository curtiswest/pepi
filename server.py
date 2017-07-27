#!/usr/bin/python
import time
import logging
import sys
import signal
import random
import string
from subprocess import check_output
from stoppablethread import StoppableThread
from picamera import PiCamera
from picamera.array import PiRGBArray
import pepi_config
from communication.communication import CommunicationSocket, Poller
from communication.pymsg import *
import communication.pepimessage_pb2 as ppmsg

__author__ = 'Curtis West, Claudio Pizzolato'
__copyright__ = 'Copyright 2017, Curtis West, Claudio Pizzolato'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class StreamingThread(StoppableThread):
    def __init__(self, camera_instance, socket):
        super(StreamingThread, self).__init__()
        self.camera_instance = camera_instance
        self.socket = socket

        self.old_resolution = self.camera_instance.resolution
        self.old_framerate = self.camera_instance.framerate
        self.camera_instance.resolution = pepi_config.RESOLUTION_640
        self.camera_instance.framerate = 24
        self.camera_instance.start_preview()
        self.socket.data_wrapper_class = FileLikeDataWrapper.serialize_data  # TODO: refactor into better design

    def run(self):
        self.camera_instance.start_recording(self.socket, format='h264', quality=20)
        while not self.is_stopped():
            time.sleep(0.1)
        self.camera_instance.stop_recording()
        self.camera_instance.framerate = self.old_framerate
        self.camera_instance.resolution = self.old_resolution


class Server:
    HEARTBEAT_INTERVAL = 5  # Seconds between heartbeats to client
    HEARTBEAT_LIVELINESS = 3  # Number of heartbeats missed before assumed dead

    def exit_handler(self):
        logging.info("Exit Handler: cleaning up..")
        if self.camera_instance is not None:
            logging.info("Exit Handler: closing camera..")
            self.camera_instance.close()
        if self.ident_socket is not None:
            logging.info("Exit Handler: closing control_socket..")
            self.ident_socket.close()
        if self.control_socket is not None:
            logging.info("Exit Handler: closing control_socket..")
            self.control_socket.close()
        if self.data_socket is not None:
            logging.info("Exit Handler: closing data_socket..")
            self.data_socket.close()

        logging.info("Exit Handler: complete & exiting")

    # noinspection PyUnusedLocal
    @staticmethod
    def signal_handler(_signal, _frame):
        logging.info('Received SIGINT, exiting..')
        sys.exit(0)

    @staticmethod
    def get_camera_singleton(resolution=pepi_config.RESOLUTION_MAX):
        camera = PiCamera()
        camera.resolution = resolution
        logging.info('Camera warming up..')
        return camera

    def get_camera_still(self):
        start_time = time.time()
        with PiRGBArray(self.camera_instance) as raw_capture:
            self.camera_instance.capture(raw_capture, format='bgr', use_video_port=False)
            logging.info('Capture took: {} sec'.format(time.time() - start_time))
            return raw_capture.array

    @staticmethod
    def get_server_id():
        # Extract serial from the "/proc/cpuinfo" file as the server ID
        try:
            f = open('/proc/cpuinfo', 'r')
        except IOError:
            return 'ERROR00000000000'
        else:
            serial = '0000000000000000'
            for line in f:
                if line[0:6] == 'Serial':
                    serial = line[10:26]
            f.close()
            return serial

    def send_idents(self):
        self.ident_socket.send(self.ident_msg_serial)
        self.control_socket.send(self.ident_msg_serial)
        self.data_socket.send(self.ident_msg_serial)

    def connect_to_client(self):
        def generate_server_seeded_id(self, num_digits=4):
            """
            Generates an ID based of this servers self.server_id, such that the server always receives the same
            ID's in order from the first time the function is called.
            """
            try:
                _ = self.__rand_id_gen__
            except AttributeError:
                self.__rand_id_gen__ = random.Random(hash(self.server_id))  # First run, make own gen
            return ''.join(self.__rand_id_gen__.choice(string.ascii_lowercase) for _ in range(num_digits))

        # Setup message queues
        self.queued_data = dict()

        # Setup ident socket
        self.ident_socket.identity = generate_server_seeded_id(self)
        address = 'tcp://{}:{}'.format(pepi_config.CLIENT_IP, pepi_config.IDENT_PORT)
        logging.info('Ident socket (ID: {}) is connecting to {}'.format(self.ident_socket.identity, address))
        self.ident_socket.connect_to(address)

        # Setup control socket
        self.control_socket.identity = generate_server_seeded_id(self)
        address = "tcp://{}:{}".format(pepi_config.CLIENT_IP, pepi_config.CONTROL_PORT)
        logging.info('Control Socket (ID: {}) is binding to {}'.format(self.control_socket.identity, address))
        self.control_socket.connect_to(address)

        # Setup data socket
        self.data_socket.identity = generate_server_seeded_id(self)
        address = "tcp://{}:{}".format(pepi_config.CLIENT_IP, pepi_config.DATA_PORT)
        logging.info('Data socket (ID: {}) is binding to {}'.format(self.data_socket.identity, address))
        self.data_socket.connect_to(address)

        # Identify ourselves to client
        self.send_idents()

    def disconnect_from_client(self):
        address = 'tcp://{}:{}'.format(pepi_config.CLIENT_IP, pepi_config.IDENT_PORT)
        self.ident_socket.disconnect_from(address)
        self.ident_socket_connected = False

        address = "tcp://{}:{}".format(pepi_config.CLIENT_IP, pepi_config.CONTROL_PORT)
        self.control_socket.disconnect_from(address)
        self.control_socket_connected = False

        address = "tcp://{}:{}".format(pepi_config.CLIENT_IP, pepi_config.DATA_PORT)
        self.data_socket.disconnect_from(address)
        self.data_socket_connected = False

    def create_sockets(self):
        logging.debug('Creating all sockets')
        self.ident_socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        self.control_socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        self.data_socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)

        self.ident_socket_connected = False
        self.control_socket_connected = False
        self.data_socket_connected = False

        # Register Sockets with the Poller
        self.poller = Poller()
        self.poller.register(self.ident_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.control_socket, Poller.PollingType.POLLIN)
        self.poller.register(self.data_socket, Poller.PollingType.POLLIN)

    def recreate_sockets(self):
        logging.debug('Recreating all sockets')
        self.disconnect_from_client()
        self.poller.unregister(self.ident_socket)
        self.poller.unregister(self.control_socket)
        self.poller.unregister(self.data_socket)
        self.ident_socket.close()
        self.control_socket.close()
        self.data_socket.close()

        self.create_sockets()

    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)-8s: %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p')
        # atexit.register(self.exit_handler)

        # Setup Server variables
        self.server_id = self.get_server_id().zfill(16)
        signal.signal(signal.SIGINT, self.signal_handler)
        logging.info('Server ID #{} starting up..'.format(self.server_id))
        self.camera_instance = self.get_camera_singleton()
        self.is_streaming = False

        # Pre-generate our ident_msg for performance
        self.ip = check_output(['hostname', '-I']).rstrip()  # TODO: convert to property
        self.ident_msg = IdentityMessage(self.ip, self.server_id)
        self.ident_msg_serial = self.ident_msg.wrap().serialize()

        # Setup sockets
        self.create_sockets()

        # Connect to clients
        self.connected_client_id = None
        self.heartbeat_successful = True
        self.connect_to_client()
        self.time_at_last_message = time.time()
        self.time_to_heartbeat = time.time() + self.HEARTBEAT_INTERVAL

        while True:
            if time.time() >= self.time_to_heartbeat:
                if time.time() > (self.time_at_last_message + self.HEARTBEAT_INTERVAL * self.HEARTBEAT_LIVELINESS):
                    # Client is dead
                    logging.info('Client heartbeat failure. Reconnecting in 5 seconds..')
                    self.time_at_last_message = time.time()

                    self.recreate_sockets()
                    self.connected_client_id = None
                    self.connect_to_client()
                else:
                    # Need to get a heartbeat
                    logging.info('Need a heartbeat from client')
                    msg = ControlMessage(ppmsg.PING).wrap().serialize()
                    self.control_socket.send(msg)
                    # self.ident_socket.send(self.ident_msg_serial)
                self.time_to_heartbeat = time.time() + self.HEARTBEAT_INTERVAL

            sockets = self.poller.poll(self.HEARTBEAT_INTERVAL)  # Poll for new messages
            for socket in sockets:
                self.time_at_last_message = time.time()
                # Handle any received messages
                data = socket.receive()
                wrapped_msg = WrapperMessage.from_serialized_string(data)
                self.message_router(socket=socket, message=wrapped_msg.unwrap())

    def ident_message_handler(self, socket, message):
            pass

    def control_message_handler(self, socket, message):
        logging.debug('Received a ControlMessage. Command No: {}'.format(message.command))
        if message.command == ppmsg.GET_STILL:
            data_code = utils.generate_id(8)
            control_reply = ControlMessage(ppmsg.GET_STILL, values=[data_code])
            print control_reply
            self.control_socket.send(control_reply.wrap().serialize())
            img = self.get_camera_still()
            self.queued_data[data_code] = utils.encode_image(img)
        elif message.command == ppmsg.START_STREAM:
            data_code = 'stream'
            control_reply = ControlMessage(ppmsg.START_STREAM, values=[data_code])
            self.control_socket.send(control_reply.wrap().serialize())
            self.is_streaming = True
            s = StreamingThread(self.camera_instance, self.data_socket)
            s.daemon = True
            s.start()
        elif message.command == ppmsg.STOP_STREAM:
            self.is_streaming = False
            logging.debug('Stopping stream due to control message')
        elif message.command == ppmsg.DISCONNECT:
            logging.info('Got disconnected from client. Reconnecting in 5 seconds..')
            time.sleep(5)
            self.recreate_sockets()
            self.connected_client_id = None
            self.connect_to_client()
        elif message.command == ppmsg.PING:
            logging.debug('PINGed')
            socket.send(ControlMessage(ppmsg.PONG).wrap().serialize())
        elif message.command == ppmsg.PONG:
            logging.debug('PONGed')
            pass
        else:
            logging.error('Received unknown control message! Command No: {}'.format(message.command))

    def data_message_handler(self, message):
        logging.debug('Received a DataMessage. Data code: {}'.format(message.data_code))
        if message.data_code in self.queued_data:
            print 'Got a request for queued data item: {}'.format(message.data_code)
            reply = DataMessage(message.data_code, data_bytes=self.queued_data[message.data_code])
            del self.queued_data[message.data_code]
            self.data_socket.send(reply.wrap().serialize())
            print 'Remaining queued data items: {}'.format(self.queued_data.keys())
        else:
            print 'Unknown data code requested!'

    def message_router(self, socket, message):
        # Update connection status for each socket based on if they received a message
        if socket == self.ident_socket:
            self.ident_socket_connected = True
        elif socket == self.control_socket:
            self.control_socket_connected = True
        elif socket == self.data_socket:
            self.data_socket_connected = True

        if isinstance(message, WrapperMessage):
            # Message is passed wrapped, unwrap to handle
            message = message.unwrap()

        # Handle each different type of message
        if isinstance(message, IdentityMessage):
            # TODO: move to ident_message_handler
            logging.debug('Received an IdentityMessage: {}'.format(message))
            if not self.connected_client_id:
                logging.debug('Got client {} for the first time'.format(message.identifier))
                self.connected_client_id = message.identifier
            elif self.connected_client_id != message.identifier:
                logging.debug('Got a new client unexpectedly. Client: {}'.format(message.identifier))
                self.recreate_sockets()
                self.connected_client_id = None
                self.connect_to_client()
            else:
                logging.debug('Got ident from same old client {}'.format(message.identifier))
        elif isinstance(message, ControlMessage):
            self.control_message_handler(socket, message)
        elif isinstance(message, DataMessage):
            self.data_message_handler(message)
        else:
            raise TypeError('Cannot handle message of type {}'.format(type(message)))

            # def handle_command(self, identity, command, values=None):
            #     logging.debug('Handling command: {}'.format(command))
            #     # Handle different command cases
            #     ## Camera specific
            #     if command == ppmsg.SET_ISO:
            #         try:
            #             # self.camera_instance.iso = values[0]
            #             self.control_socket.send(command, values[0])
            #             # self.command_socket.send_old(command=command, int_values=self.camera_instance.iso)
            #         except Exception as e:
            #             self.control_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_ISO:
            #     # self.command_socket.send_old(command=command, int_values=self.camera_instance.iso)
            # elif command == ppmsg.SET_SHUTTER_SPEED:
            #     try:
            #         self.camera_instance.shutter_speed = values[0]
            #         self.command_socket.send_old(command=command, int_values=self.camera_instance.shutter_speed)
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_SHUTTER_SPEED:
            #     self.command_socket.send_old(command=command, int_values=self.camera_instance.shutter_speed)
            # elif command == ppmsg.SET_BRIGHTNESS:
            #     try:
            #         self.camera_instance.brightness = values[0]
            #         self.command_socket.send_old(command=command, int_values=self.camera_instance.brightness)
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_BRIGHTNESS:
            #     self.command_socket.send_old(command=command, int_values=self.camera_instance.brightness)
            # elif command == ppmsg.SET_AWB_GAINS:
            #     try:
            #         self.camera_instance.awb_gains = values[0:2]
            #         self.command_socket.send_old(command=command,
            #                                      float_values=[float(val) for val in self.camera_instance.awb_gains])
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            #     pass
            # elif command == ppmsg.GET_AWB_GAINS:
            #     self.command_socket.send_old(command=command, float_values=[float(val)
            #                                  for val in self.camera_instance.awb_gains])
            # elif command == ppmsg.SET_RESOLUTION:
            #     try:
            #         self.camera_instance.resolution = [values[0], values[1]]
            #         self.command_socket.send_old(command=command, int_values=list(self.camera_instance.resolution))
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_RESOLUTION:
            #     self.command_socket.send_old(command=command, int_values=list(self.camera_instance.resolution))
            # elif command == ppmsg.SET_SATURATION:
            #     try:
            #         self.camera_instance.saturation = values[0]
            #         self.command_socket.send_old(command=command, int_values=self.camera_instance.saturation)
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_SATURATION:
            #     self.command_socket.send_old(command=command, int_values=self.camera_instance.saturation)
            # elif command == ppmsg.SET_ZOOM:
            #     try:
            #         self.camera_instance.zoom = values[0:3]
            #         self.command_socket.send_old(command=command, int_values=list(self.camera_instance.zoom))
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_ZOOM:
            #     self.command_socket.send_old(command=command, float_values=self.camera_instance.zoom)
            #     pass
            # elif command == ppmsg.SET_AWB_MODE:
            #     try:
            #         self.camera_instance.awb_mode = values[0]
            #         self.command_socket.send_old(command=command, string_values=self.camera_instance.awb_mode)
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_AWB_MODE:
            #     self.command_socket.send_old(command=command, string_values=self.camera_instance.awb_mode)
            # ## Server specific commands
            # elif command == ppmsg.SET_SERVER_ID:
            #     try:
            #         self.server_id = values[0].zfill(16)
            #         self.command_socket.send_old(command=command, string_values=self.server_id)
            #     except Exception as e:
            #         self.command_socket.raise_remote_exception(e)
            # elif command == ppmsg.GET_SERVER_ID:
            #     self.command_socket.send_old(command=command, string_values=self.server_id)
            # elif command == ppmsg.ENABLE_COMPRESSION:
            #     self.compressed_transfer = True
            #     self.compression_level = 90
            #     self.command_socket.send_old(command=command)
            # elif command == ppmsg.DISABLE_COMPRESSION:
            #     self.compressed_transfer = False
            #     self.compression_level = 3
            #     self.command_socket.send_old(command=command)
            # ## Image capture commands
            # elif command == ppmsg.GET_STILL:
            #     image = self.get_camera_still()
            #     image = utils.encode_image(image, self.compressed_transfer, self.compression_level)
            #     # self.command_socket.send_old(ppmsg.GET_STILL, image_data=image, server_id=self.server_id)
            #     self.control_socket.send(command) # ACK
            #     print('Sending..')
            #     self.control_socket.send_image(identity, image, self.server_id)
            #     print('Sent.')
            # elif command == ppmsg.START_STREAM:
            #     self.command_socket.send_old(ppmsg.START_STREAM)
            #     self.start_image_stream()
            # elif command == ppmsg.STOP_STREAM:
            #     if self.stream_thread is not None:
            #         self.stream_thread.stop()
            #     self.command_socket.send_old(ppmsg.STOP_STREAM)
            # else:
            #     # Received a command that the server doesn't know how to handle, reply with error response
            #     logging.warn('Received an command code ({}) that is unknown how to handle'.format(command))
            #     self.control_socket.send_old(command=ppmsg.COMMAND_FAILURE)

if __name__ == '__main__':
    s = Server()
