#!/usr/bin/python
import socket
# import communication
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import sys
import signal
import pepi_config
import atexit
import traceback
import communication_new as comm
import zmq

def generate_random_img():
    z = np.random.random((2592, 1944))  # Test data
    print z.dtype
    return z


class Server:
    run_condition = True
    camera_instance = None
    active_connection = None
    server_comm = comm.CommunicationSocket(zmq.REP)
    compressed_transfer = True
    compression_level = 90
    server_id = ""

    def exit_handler(self):
        print "Exit Handler: cleaning up.."
        if self.camera_instance is not None:
            print "Exit Handler: closing camera.."
            self.camera_instance.close()
        print "Exit Handler: complete & exiting."

    @staticmethod
    def signal_handler(self, signal, frame):
        print('\n Exiting...')
        sys.exit(0)

    @staticmethod
    def get_camera_singleton(resolution=(2592, 1944)):
        camera = PiCamera()
        try:
            camera.resolution = resolution
            camera.start_preview()
            print 'Camera warming up..'
            time.sleep(3)
            print 'Camera active.'
        except:
            raise
        return camera

    def get_camera_still(self):
        start_time = time.time()
        with PiRGBArray(self.camera_instance) as rawCapture:
            self.camera_instance.capture(rawCapture, format='bgr')
            image = rawCapture.array
            print 'Capture took: %.3f sec' % (time.time() - start_time)
            return image

    @staticmethod
    def wait_for_client(sock):
        connection, address = sock.accept()
        print "sending ", communication.SERVER_READY
        communication.send_msg(connection, communication.SERVER_READY)
        msg = communication.recv_msg(connection)
        print "received ", msg
        return connection

    @staticmethod
    def get_server_id():
        # Extract serial from the cpuinfo file as the server ID
        serial = '0000000000000000'
        try:
            f = open('/proc/cpuinfo', 'r')
            for line in f:
                if line[0:6] == 'Serial':
                    serial = line[10:26]
            f.close()
        except:
            serial = 'ERROR00000000000'
        finally:
            return serial

    def __init__(self):
        # Setup communication socket
        addr = "tcp://*:{}".format(pepi_config.port)
        print('Binding to {}'.format(addr))
        self.server_comm.bind_to(addr)

        # Setup Server variables
        self.server_id = self.get_server_id().zfill(16)
        signal.signal(signal.SIGINT, self.signal_handler)
        print 'SERVER START: ', self.server_id
        self.camera_instance = self.get_camera_singleton()
        atexit.register(self.exit_handler)

        # Start listening for connecting clients
        while True:
            # Get the command from a client
            print('Waiting for message..')
            msg = self.server_comm.receive_protobuf()
            print('Got message: {}'.format(msg))

            # Process command and reply to client
            reply = comm.CommunicationSocket.get_new_pepimessage()
            if msg.HasField("command"):
                print('Got a command: {}'.format(msg.command))
                # Handle different command cases
                if msg.command.command == comm.pepimessage_pb2.Command.GET_STILL:
                    image = self.get_camera_still()
                    image = comm.CommunicationSocket.encode_image(image, 90)
                    reply.image.img_data_str = image
                    reply.image.server_id = self.server_id
                    print self.server_comm.send_protobuf(reply)
                else:
                    pass
            else:
                print('ERROR: Server received an image!')


s = Server()
