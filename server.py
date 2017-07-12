#!/usr/bin/python
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import sys
import signal
import pepi_config
import atexit
import communication as comm
import logging


def generate_random_img():
    z = np.random.random((2592, 1944))  # Test data
    print z.dtype
    return z


class Server:
    run_condition = True
    camera_instance = None
    server_comm = None
    compressed_transfer = True
    compression_level = 90
    server_id = ""

    def exit_handler(self):
        logging.info("Exit Handler: cleaning up..")
        if self.camera_instance is not None:
            logging.info("Exit Handler: closing camera..")
            self.camera_instance.close()
        if self.server_comm is not None:
            logging.info("Exit Handler: closing CommunicationSocket..")
            self.server_comm.close()
        logging.info("Exit Handler: complete & exiting")

    # noinspection PyUnusedLocal
    @staticmethod
    def signal_handler(_signal, _frame):
        logging.info('Received SIGINT, exiting..')
        sys.exit(0)

    @staticmethod
    def get_camera_singleton(resolution=(2592, 1944)):
        camera = PiCamera()
        try:
            camera.resolution = resolution
            camera.start_preview()
            logging.info('Camera warming up..')
            time.sleep(3)
            logging.info('Camera active')
        except:
            raise
        return camera

    def get_camera_still(self):
        start_time = time.time()
        with PiRGBArray(self.camera_instance) as rawCapture:
            self.camera_instance.capture(rawCapture, format='bgr', use_video_port=False)
            logging.info('Capture took: {} sec'.format(time.time() - start_time))
            return rawCapture.array

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

    def __init__(self):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format='%(asctime)s %(levelname)-8s: %(message)s',
                            datefmt='%d/%m/%Y %I:%M:%S %p')
        atexit.register(self.exit_handler)

        # Setup Server variables
        self.server_id = self.get_server_id().zfill(16)
        signal.signal(signal.SIGINT, self.signal_handler)
        logging.info('Server ID #{} starting up..'.format(self.server_id))
        self.camera_instance = self.get_camera_singleton()

        # Setup communication socket
        self.server_comm = comm.CommunicationSocket(comm.CommunicationSocket.SocketTypes.SERVER)
        address = "tcp://*:{}".format(pepi_config.port)
        logging.info('Binding to {}'.format(address))
        self.server_comm.bind_to(address)

        logging.info('Server startup complete')
        # Start listening for connecting clients
        while True:
            # Get the command from a client
            logging.debug('{} is waiting for message..'.format(self.server_id))
            try:
                # msg = self.server_comm.receive_protobuf()
                msg = self.server_comm.receive()
            except comm.CommunicationSocket.MessageTypeError as e:
                logging.error(e.message)
                continue
            logging.debug('{} received message: {}'.format(self.server_id, msg))
            # Process command and reply to client
            self.handle_command(msg[0])

    def handle_command(self, command, values=None):
        logging.info('Got a command: {}'.format(command))
        # Handle different command cases
        if command == comm.ppmsg.GET_STILL:
            image = self.get_camera_still()
            image = comm.CommunicationSocket.encode_image(image, 90)
            self.server_comm.send(comm.ppmsg.GET_STILL, image_data=image, server_id=self.server_id)
        elif command == comm.ppmsg.GET_SERVER_ID:
            self.server_comm.send(command=command, string_values=self.server_id)
            pass
        elif command == comm.ppmsg.SET_SERVER_ID:
            self.server_id = values[0].zfill(16)
            self.server_comm.send(command=command, string_values=self.server_id)
        else:
            # Received a command that the server doesn't know how to handle, reply with error response
            self.server_comm.send(command=comm.ppmsg.COMMAND_FAILURE)

s = Server()
