#!/usr/bin/python
import time
import numpy as np
import logging
import sys
import signal
import atexit
from picamera import PiCamera
from picamera.array import PiRGBArray
import pepi_config
from communication.communication import CommunicationSocket
from communication.pymsg import *

__author__ = 'Curtis West, Claudio Pizzolato'
__copyright__ = 'Copyright 2017, Curtis West, Claudio Pizzolato'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class Server:
    run_condition = True
    camera_instance = None
    stream_thread = None
    compressed_transfer = True
    compression_level = 90
    server_id = ""

    ident_socket = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
    control_socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
    data_socket = CommunicationSocket(CommunicationSocket.SocketType.DEALER)

    def exit_handler(self):
        logging.info("Exit Handler: cleaning up..")
        if self.camera_instance is not None:
            logging.info("Exit Handler: closing camera..")
            self.camera_instance.close()
        if self.stream_thread is not None:
            logging.info("Exit Handler: stopping StreamThread..")
            self.stream_thread.stop()
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
        try:
            camera.resolution = resolution
            logging.info('Camera warming up..')
            time.sleep(3)
            logging.info('Camera active')
        except:
            raise
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

    # def start_image_stream(self):
    #     def capture_loop(stopped_func):
    #         logging.debug('Spinning up thread at T:{}'.format(time.time()))
    #
    #         for _ in self.camera_instance.capture_continuous(self.stream_comm, format='jpeg'):
    #             if stopped_func():
    #                 break
    #             time.sleep(0.1)
    #         # self.camera_instance.start_recording(self.stream_comm, format='h264')
    #         # while not stopped_func():
    #         #     time.sleep(0.1)
    #         # logging.debug('Stopped func result: {}'.format(stopped_func()))
    #         # self.camera_instance.stop_recording()
    #         self.camera_instance.framerate = self.old_framerate
    #         self.camera_instance.resolution = self.old_resolution
    #         logging.debug('Breaking out of thread at T:{}'.format(time.time()))
    #
    #     # Save old camera settings to restore later
    #     self.old_resolution = self.camera_instance.resolution
    #     self.old_framerate = self.camera_instance.framerate
    #     self.camera_instance.resolution = pepi_config.RESOLUTION_720
    #     self.camera_instance.framerate = 5
    #
    #     # Start a thread to send stream over network
    #     self.stream_thread = StoppableThread(capture_loop)
    #     logging.debug('Self.stream_thread set: {}'.format(self.stream_thread))
    #     self.stream_thread.start()

    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)-8s: %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p')
        atexit.register(self.exit_handler)

        # Setup Server variables
        self.server_id = self.get_server_id().zfill(16)
        signal.signal(signal.SIGINT, self.signal_handler)
        logging.info('Server ID #{} starting up..'.format(self.server_id))
        # self.camera_instance = self.get_camera_singleton()

        # Setup ident socket
        address = 'tcp://{}:{}'.format(pepi_config.CLIENT_IP, pepi_config.IDENT_PORT)
        logging.info('Ident socket is connecting to {}'.format(address))
        self.ident_socket.connect_to(address)

        # Setup control socket
        address = "tcp://{}:{}".format(pepi_config.CLIENT_IP, pepi_config.CONTROL_PORT)
        logging.info('Control Socket is binding to {}'.format(address))
        self.control_socket.connect_to(address)

        # Setup data socket
        address = "tcp://{}:{}".format(pepi_config.CLIENT_IP, pepi_config.DATA_PORT)
        logging.info('Data socket is binding to {}'.format(address))
        self.data_socket.connect_to(address)

        # Print ID's
        print '\n=== SOCKET IDS ==='
        print self.ident_socket.identity
        print self.control_socket.identity
        print self.data_socket.identity
        print '\n'

        ident_msg = IdentityMessage('10.0.0.4', self.server_id)

        while True:
            # Identify self to Client
            self.ident_socket.send(ident_msg.wrapped().serialize())
            self.control_socket.send(ident_msg.wrapped().serialize())
            self.data_socket.send(ident_msg.wrapped().serialize())
            # Receive ident acknowledgements
            _ = WrapperMessage.from_serialized_string(self.ident_socket.receive())
            _ = WrapperMessage.from_serialized_string(self.control_socket.receive())
            _ = WrapperMessage.from_serialized_string(self.data_socket.receive())

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


s = Server()
