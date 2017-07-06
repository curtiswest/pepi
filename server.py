#!/usr/bin/python
import socket
import communication
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
import sys
import signal
import pepi_config
import atexit


def generate_random_img():
    z = np.random.random((2592, 1944))  # Test data
    print z.dtype
    return z


class Server:
    run_condition = True
    camera_instance = None
    active_connection = None
    server_socket = None
    compressed_transfer = True
    compression_level = 90
    server_id = ""

    def exit_handler(self):
        print "Exit Handler: cleaning up.."
        if self.camera_instance is not None:
            print "Exit Handler: closing camera.."
            self.camera_instance.close()
        if self.active_connection is not None:
            print "Exit Handler: closing active connection.."
            self.active_connection.close()
        if self.server_socket is not None:
            print "Exit Handler: closing server socket.."
            self.server_socket.close()
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoids TCP timeout waiting on crash
        self.server_socket.bind(("", pepi_config.port))
        self.server_socket.listen(5)

        # Setup Server variables
        self.server_id = self.get_server_id().zfill(16)
        signal.signal(signal.SIGINT, self.signal_handler)
        print 'SERVER START: ', self.server_id
        self.camera_instance = self.get_camera_singleton()
        atexit.register(self.exit_handler)

        # Start listening for connecting clients
        while self.run_condition:
            try:
                self.active_connection = self.wait_for_client(self.server_socket)
                print("Temp Connection: now active")

                print "Sending image from ", self.server_id
                communication.send_msg(self.active_connection, self.server_id)

                print "Received: ", communication.recv_msg(self.active_connection)
                print "Sending image data.."
                communication.send_img(self.active_connection, self.get_camera_still(),
                                       self.compressed_transfer, self.compression_level)
                print "Sent image data."
            except Exception as e:
                if hasattr(e, 'message'):
                    print(e.message)
                print "Server failure, exiting"
                exit() # Will call exit_handler
            finally:
                # Clean up the current temporary connection
                if self.active_connection is not None:
                    self.active_connection.close()
                    print("Temp Connection: now closed")
                    self.active_connection = None


s = Server()
