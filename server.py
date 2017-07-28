#!/usr/bin/python
import time
import logging
import sys
import signal
import uuid
import atexit
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
__version__ = '0.2'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class StreamingThread(StoppableThread):
    def __init__(self, camera_instance, identity_message):
        assert isinstance(identity_message, IdentityMessage)
        super(StreamingThread, self).__init__()
        raise NotImplementedError('StreamingThread needs to be rewritten with it\'s own socket as sockets aren\'t'
                                  'thread-safe')
        self.camera_instance = camera_instance
        self.socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        self.socket.identity = uuid.uuid4().hex[:8]
        self.socket.connect_to('tcp://{}:{}'.format(pepi_config.CLIENT_IP, pepi_config.IDENT_PORT))
        self.socket.send(identity_message.wrap().serialize())

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
    HB_MIN_INTERVAL = 3  # Seconds between heartbeats to client
    HB_MAX_INTERVAL = 15  # Seconds between heartbeats to client
    HB_HEALTH = 3  # Number of heartbeats missed before assumed dead
    HB_BACKOFF_RATE = 1.75

    def exit_handler(self):
        logging.info("Exit Handler: cleaning up..")
        if self.camera is not None:
            logging.info("Exit Handler: closing camera..")
            self.camera.close()
        if self.socket:
            logging.info("Exit Handler: closing socket..")
            self.socket.close()
        if self.is_streaming:
            self.stream_thread.stop()

        logging.info("Exit Handler: complete & exiting")

    # noinspection PyUnusedLocal
    @staticmethod
    def signal_handler(signal_, frame):
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
        with PiRGBArray(self.camera) as raw_capture:
            self.camera.capture(raw_capture, format='bgr', use_video_port=False)
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

    def socket_setup(self):
        if self.socket:
            # Socket exists, need to destroy
            self.poller.unregister(self.socket)
            self.socket.close(linger=0)
            self.socket = None
        self.socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        # self.socket.identity = generate_server_seeded_id()
        self.socket.identity = uuid.uuid4().hex[:8]
        self.socket.linger = 0
        self.socket.receive_timeout = 1000
        self.socket.send_timeout = 1000
        self.socket.connect_to('tcp://{}:{}'.format(pepi_config.CLIENT_IP, pepi_config.IDENT_PORT))
        self.poller.register(self.socket, Poller.PollingType.POLLIN)
        self.socket.send(self.ident_msg_serial)
        self.connected_client_id = None

    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.INFO, format='%(asctime)s %(levelname)-8s: %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p')
        atexit.register(self.exit_handler)

        # Setup Server variables
        self.server_id = self.get_server_id().zfill(16)
        signal.signal(signal.SIGINT, self.signal_handler)
        logging.info('Server ID #{} starting up..'.format(self.server_id))
        self.camera = self.get_camera_singleton()
        self.is_streaming = False
        self.stream_thread = None
        self.connected_client_id = ''
        self.queued_data = dict()

        # Pre-generate our ident_msg for performance
        self.ip = check_output(['hostname', '-I']).rstrip()  # TODO: convert to property
        self.ident_msg = IdentityMessage(self.ip, self.server_id)
        self.ident_msg_serial = self.ident_msg.wrap().serialize()

        # Setup sockets
        self.socket = None
        self.poller = Poller()
        self.socket_setup()

        # Setup heartbeating
        hb_interval = self.HB_MIN_INTERVAL
        heartbeat_at = time.time() + hb_interval
        client_health = self.HB_HEALTH

        # Start running server
        while True:
            # Handle heartbeating
            if time.time() >= heartbeat_at:
                heartbeat_at += hb_interval  # Move next heartbeat time forward
                if client_health <= 0:
                    logging.warn('Disconnected from client {} by heartbeating.'.format(self.connected_client_id))
                    client_health = self.HB_HEALTH
                    hb_interval = hb_interval * self.HB_BACKOFF_RATE
                    logging.info('Backing off on heartbeat interval. Now {}s'.format(hb_interval))
                    hb_interval = hb_interval if hb_interval < self.HB_MAX_INTERVAL else self.HB_MAX_INTERVAL
                    if self.is_streaming:
                        self.stream_thread.stop()
                    self.socket_setup()
                else:
                    if self.connected_client_id:
                        logging.debug('Pinging {}. Liveness: {}'.format(self.connected_client_id, client_health))
                        self.socket.send(ControlMessage(ppmsg.PING, values=[self.server_id]).wrap().serialize())
                    else:
                        logging.debug('No client. Sending out IdentMessage')
                        self.socket.send(self.ident_msg_serial)
                client_health -= 1

            # Poll for messages
            sockets = self.poller.poll(hb_interval)  # Poll for new messages
            if sockets:
                hb_interval = self.HB_MIN_INTERVAL  # Reset any backoff
                heartbeat_at = time.time() + hb_interval  # Move next heartbeat time forward from this message
                client_health = self.HB_HEALTH  # Reset client health, as must be alive to send this message

            for socket in sockets:
                # Handle any received messages
                data = socket.receive()
                wrapped_msg = WrapperMessage.from_serialized_string(data)
                self.message_router(socket=socket, message=wrapped_msg.unwrap())

    def ident_message_handler(self, socket, message):
        logging.debug('Received an IdentityMessage: {}'.format(message))
        if not self.connected_client_id:
            logging.debug('Got client {} for the first time'.format(message.identifier))
            self.connected_client_id = message.identifier
        elif self.connected_client_id != message.identifier:
            logging.debug('Got a new client unexpectedly. Client: {}. Resetting sockets..'.format(message.identifier))
            self.socket_setup()
        else:
            logging.debug('Got ident from same old client {}'.format(message.identifier))

    def control_message_handler(self, socket, message):
        logging.debug('Received a ControlMessage. Command No: {}'.format(message.command))
        if message.command == ppmsg.GET_STILL:
            data_code = utils.generate_id(8)
            control_reply = ControlMessage(ppmsg.GET_STILL, values=[data_code])
            self.socket.send(control_reply.wrap().serialize())
            img = self.get_camera_still()
            self.queued_data[data_code] = utils.encode_image(img)
            logging.debug('Queued data now: {}'.format(self.queued_data.keys()))
        elif message.command == ppmsg.START_STREAM:
            # TODO move streaming to a new socket and thread - sockets aren't threadsafe
            raise NotImplementedError('Streaming not implemented')
            # data_code = 'stream'
            # control_reply = ControlMessage(ppmsg.START_STREAM, values=[data_code])
            # self.socket.send(control_reply.wrap().serialize())
            # self.is_streaming = True
            # self.stream_thread = StreamingThread(self.camera, self.socket, self.ident_msg)
            # self.stream_thread.daemon = True
            # self.stream_thread.start()
        elif message.command == ppmsg.STOP_STREAM:
            self.is_streaming = False
            self.stream_thread.stop()
            logging.debug('Stopping stream due to control message')
        elif message.command == ppmsg.DISCONNECT:
            logging.info('Got disconnected from client. Reconnecting in 5 seconds..')
            time.sleep(5)
            self.socket_setup()
        elif message.command == ppmsg.PING:
            socket.send(ControlMessage(ppmsg.PONG).wrap().serialize())
        elif message.command == ppmsg.PONG:
            pass
        else:
            logging.error('Received unknown control message! Command No: {}'.format(message.command))

    def data_message_handler(self, message):
        logging.info('Got a request for queued data item: {}'.format(message.data_code))

        data = self.queued_data.pop(message.data_code, None)
        if data:
            reply = DataMessage(message.data_code, data_bytes=data)
            self.socket.send(reply.wrap().serialize())
        else:
            logging.warn('Unknown data code ({}) requested!'.format(message.data_code))
            reply = ControlMessage(ppmsg.DATA_UNAVAILABLE, values=[message.data_code])
            self.socket.send(reply.wrap().serialize())
        logging.debug('Remaining queued data items: {}'.format(self.queued_data.keys()))

    def message_router(self, socket, message):
        if isinstance(message, WrapperMessage):
            # Message is passed wrapped, unwrap to handle
            message = message.unwrap()

        # Handle each different type of message
        if isinstance(message, IdentityMessage):
            self.ident_message_handler(socket, message)
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
