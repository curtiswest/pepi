#!/usr/bin/python
import atexit
import logging
import signal
import sys
import threading
import time
import uuid
from subprocess import check_output
from future.utils import viewitems

from picamera import PiCamera
from picamera.array import PiRGBArray

import pepi_config
import utils
from communication.communication import CommunicationSocket, Poller
from communication.pymsg import WrapperMessage, IdentityMessage, ControlMessage, DataMessage, FileLikeDataWrapper
from stoppablethread import StoppableThread
from iptools import IPTools

__author__ = 'Curtis West, Claudio Pizzolato'
__copyright__ = 'Copyright 2017, Curtis West, Claudio Pizzolato'
__version__ = '0.3'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class StreamingThread(StoppableThread):
    def __init__(self, camera_instance):
        super(StreamingThread, self).__init__()

        # Set up socket for communication back to main comms thread
        self.socket = CommunicationSocket(CommunicationSocket.SocketType.PAIR)
        self.socket.connect_to('inproc://stream')
        self.socket.data_wrapper_func = FileLikeDataWrapper.serialize_data
        self.socket.data_wrapper_args = {'data_code': -1}

        # Set up camera
        self.camera_instance = camera_instance
        self.old_resolution = self.camera_instance.resolution
        self.old_framerate = self.camera_instance.framerate
        self.camera_instance.resolution = pepi_config.RESOLUTION_640
        self.camera_instance.framerate = 25

    def run(self):
        # Keep recording until this thread receives a stop event
        self.camera_instance.start_recording(self.socket, format='h264', quality=20)
        while not self.is_stopped():
            time.sleep(0.1)

        # Stop recording and return camera to previous setup and close socket
        self.camera_instance.stop_recording()
        self.camera_instance.framerate = self.old_framerate
        self.camera_instance.resolution = self.old_resolution
        self.socket.close()


class Server:
    HB_MIN_INTERVAL = 10  # Seconds between heartbeats to client
    HB_MAX_INTERVAL = 30  # Seconds between heartbeats to client
    HB_HEALTH = 3  # Number of heartbeats missed before assumed dead
    HB_BACKOFF_RATE = 1.75  # How aggressively we back off on heartbeats (i.e. HB_INTERVAL * HB_BACKOFF_RATE)
    DATA_EXPIRY_SECONDS = 60 * 10  # How long a capture data item is guaranteed to be available on this server

    def exit_handler(self):
        logging.info("Exit Handler: cleaning up..")
        if self.is_streaming:
            logging.info("Exit Handler: stopping streaming..")
            self.stream_thread.stop()
            time.sleep(0.5)
        if self.camera is not None:
            logging.info("Exit Handler: closing camera..")
            self.camera.close()
        if self.socket:
            logging.info("Exit Handler: closing socket..")
            self.socket.close()

        logging.info("Exit Handler: complete & exiting")

    # noinspection PyUnusedLocal
    @staticmethod
    def signal_handler(signal_, frame):
        # logging.info('Received SIGINT, exiting..')
        sys.exit('Received SIGINT, exiting..')
        time.sleep(1)

    @staticmethod
    def get_camera_singleton(resolution=pepi_config.RESOLUTION_MAX):
        camera = PiCamera()
        camera.resolution = resolution
        logging.debug('Camera instance fetched..')
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

    def delete_data_item(self, with_data_code, reason=''):
        assert isinstance(with_data_code, int)
        logging.debug('Deleting data code {}. Reason: {}'.format(with_data_code, reason))
        self.queued_data.pop(with_data_code, None)

    def socket_setup(self):
        if self.is_streaming or self.stream_thread:
            # Stop the streaming thread if it exists
            self.stream_thread.stop()
            time.sleep(0.5)
            self.is_streaming = False
            self.stream_thread = None
        if self.socket:
            # Socket exists, need to destroy
            self.poller.unregister(self.socket)
            self.socket.close(linger=0)
            self.socket = None

        self.socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        self.socket.identity = uuid.uuid4().hex[:8]
        logging.debug('Socket identity set to: {}'.format(self.socket.identity))
        self.socket.linger = 0
        self.socket.send_timeout = 2000
        self.socket.receive_timeout = 2000

        if not self.inproc_socket:
            self.inproc_socket = CommunicationSocket(CommunicationSocket.SocketType.PAIR)
            self.inproc_socket.bind_to('inproc://stream')
            self.socket.receive_timeout = 2000

        self.socket.bind_to('tcp://*:{}'.format(pepi_config.SOCKET_PORT))
        self.poller.register(self.socket, Poller.PollingType.POLLIN)
        self.poller.register(self.inproc_socket, Poller.PollingType.POLLIN)
        try:
            self.socket.send(self.ident_msg_serial)
        except CommunicationSocket.TimeoutError:
            pass
        self.connected_client_id = None

    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)-8s: %(message)s',
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
        self.next_data_code = 0
        self.compressed_transfer = True
        self.compression_level = 90

        # Pre-generate our ident_msg for performance
        self.ip = IPTools.current_ip()
        self.ip = self.ip[0] if self.ip else ''
        self.ident_msg = IdentityMessage(self.ip, self.server_id)
        self.ident_msg_serial = self.ident_msg.wrap().serialize()

        # Setup sockets
        self.socket = None
        self.inproc_socket = None
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

                    self.socket_setup()
                else:
                    if self.connected_client_id:
                        logging.debug('Pinging {}. Liveness: {}'.format(self.connected_client_id, client_health))
                        try:
                            self.socket.send(ControlMessage(setting=False, payload={'ping': None}).wrap().serialize())
                        except CommunicationSocket.TimeoutError:
                            pass
                    else:
                        logging.debug('No client. Sending out IdentMessage')
                        try:
                            self.socket.send(self.ident_msg_serial)
                        except CommunicationSocket.TimeoutError:
                            pass
                client_health -= 1

            # Poll for messages
            sockets = self.poller.poll(hb_interval)  # Poll for new messages
            if self.socket in sockets:
                hb_interval = self.HB_MIN_INTERVAL  # Reset any backoff
                heartbeat_at = time.time() + hb_interval  # Move next heartbeat time forward from this message
                client_health = self.HB_HEALTH  # Reset client health, as must be alive to send this message

            for socket in sockets:
                # Handle any received messages
                try:
                    data = socket.receive()
                except CommunicationSocket.TimeoutError as e:
                    logging.warn(e.message)
                else:
                    if socket == self.inproc_socket:
                        logging.debug('Inproc message. Length: {}'.format(len(data)))
                        try:
                            self.socket.send(data)  # Forward through socket
                        except CommunicationSocket.TimeoutError:
                            pass
                    else:
                        wrapped_msg = WrapperMessage.from_serialized_string(data)
                        self.message_router(socket=socket, message=wrapped_msg.unwrap())

    def ident_message_handler(self, message):
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
        setting = message.setting  # Shorthand access to setting
        reply = ControlMessage(setting=True, payload={})  # Reply message that is built upon and sent at end

        if 'still' in message.payload:
            # Get stills first, as time sensitive
            reply.payload['still'] = self.next_data_code
            reply.payload['expiry'] = self.DATA_EXPIRY_SECONDS
            img = self.get_camera_still()
            self.queued_data[self.next_data_code] = utils.encode_image(img, self.compressed_transfer,
                                                                       self.compression_level)

            logging.debug('Queued data now: {}'.format(self.queued_data.keys()))
            data_timer = threading.Timer(self.DATA_EXPIRY_SECONDS, self.delete_data_item, [self.next_data_code])
            data_timer.start()
            self.next_data_code += 1
        for key, value in viewitems(message.payload):
            # Handle remaining payload
            logging.debug('Control Msg Payload: Key: {} | Value: {}'.format(key, value))

            if key == 'still':
                pass  # Already handled above
            elif key == 'ping':
                reply.payload['pong'] = None
            elif key == 'pong':
                pass
            elif key == 'iso':
                if setting:
                    self.camera.iso = value
                reply.payload[key] = self.camera.iso
            elif key == 'shutter_speed':
                if setting:
                    self.camera.shutter_speed = value
                reply.payload[key] = self.camera.shutter_speed
            elif key == 'brightness':
                if setting:
                    self.camera.brightness = value
                reply.payload[key] = self.camera.brightness
            elif key == 'sharpness':
                if setting:
                    self.camera.sharpness = value
                reply.payload[key] = self.camera.sharpness
            elif key == 'start_stream':
                reply.payload[key] = -1
                self.stream_thread = StreamingThread(self.camera)
                self.stream_thread.daemon = True
                self.is_streaming = True
                self.stream_thread.start()
            elif key == 'stop_stream':
                self.stream_thread.stop()
                self.is_streaming = False
                time.sleep(0.5)
                self.stream_thread = None
            elif key == 'awb_red':
                pass
            elif key == 'awb_blue':
                pass
            elif key == 'resolution_x':
                if setting:
                    self.camera.resolution = value, self.camera.resolution[1]
                reply.payload[key] = self.camera.resolution[0]
            elif key == 'resolution_y':
                if setting:
                    self.camera.resolution = self.camera.resolution[0], value
                reply.payload[key] = self.camera.resolution[1]
            elif key == 'compression':
                if bool(value):
                    self.compressed_transfer = True
                    self.compression_level = 90
                else:
                    self.compressed_transfer = False
                    self.compression_level = 3
            elif key == 'disconnect':
                logging.info('Got disconnected from client. Reconnecting in 5 seconds..')
                time.sleep(5)
                self.socket_setup()
            else:
                logging.warn('Unknown key: {}'.format(key))

        if reply.payload:
            try:
                socket.send(reply.wrap().serialize())
            except CommunicationSocket.TimeoutError as e:
                logging.warn(e.message)

    def data_message_handler(self, message):
        logging.info('Got a request for queued data item: {}'.format(message.data_code))

        data = self.queued_data.pop(message.data_code, None)
        if data:
            reply = DataMessage(message.data_code, data_bytes=data)
            try:
                self.socket.send(reply.wrap().serialize())
            except CommunicationSocket.TimeoutError as e:
                logging.warn(e.message)
        else:
            logging.warn('Unknown data code ({}) requested!'.format(message.data_code))
            try:
                code = int(message.data_code)
            except ValueError:
                code = None
            reply = ControlMessage(True, {'data_unavailable': code})
            try:
                self.socket.send(reply.wrap().serialize())
            except CommunicationSocket.TimeoutError as e:
                logging.warn(e.message)
        logging.debug('Remaining queued data items: {}'.format(self.queued_data.keys()))

    def message_router(self, socket, message):
        if isinstance(message, WrapperMessage):
            # Message is passed wrapped, unwrap to handle
            message = message.unwrap()

        # Handle each different type of message
        if isinstance(message, IdentityMessage):
            self.ident_message_handler(message)
        elif isinstance(message, ControlMessage):
            self.control_message_handler(socket, message)
        elif isinstance(message, DataMessage):
            self.data_message_handler(message)
        else:
            raise TypeError('Cannot handle message of type {}'.format(type(message)))


if __name__ == '__main__':
    s = Server()
