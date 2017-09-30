"""
raspi_camera.py: Provide a PEPI-compatible Camera backed by a connected Raspberry Pi Camera Module.
"""

import threading
import time
import atexit
import logging

from picamera import *
from picamera.array import PiRGBArray

from server import AbstractCamera

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '3.1'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'

class RaspPiCamera(AbstractCamera):
    """
    RaspPiCamera is a concrete ``AbstractCamera`` that uses the Raspberry Pi Camera Module
    v1/v2 to obtain imagery. It is capable of taking pictures in various
    resolutions, but defaults to the maximum resolution of 2592x1944.
    It essentially serves as a convenient wrapper around PiCamera, but
    in the PEPI format.
    """

    SUPPORTS_STREAMING = True
    MAX_RESOLUTION = (2592, 1944)

    def __init__(self, resolution=MAX_RESOLUTION):
        # type: ((int, int)) -> None
        super(RaspPiCamera, self).__init__()
        self.camera = PiCamera()
        self.req_resolution = resolution
        self.camera.resolution = self.req_resolution
        self.camera.start_preview()
        self.camera.framerate = 30
        self.lock = threading.RLock()

        # noinspection PyShadowingNames
        def cleanup(self):
            """
            Cleans up the camera by closing the connection to the camera.
            :param self: a RaspPiCamera object
            :return: None
            """
            logging.info('Closing camera from RaspPiCamera..')
            self.camera.close()
            logging.info('Camera closed')

        atexit.register(cleanup, self)

    def still(self):
        # type: () -> [[(int, int, int)]]
        """
        Captures a still from PiCamera with its current setup.
        """
        with self.lock:
            # Lock is necessary on the camera because this method can be called from different threads with
            # reference to this Imager, but the camera is not thread-safe.
            with PiRGBArray(self.camera) as stream:
                start = time.time()
                self.camera.capture(stream, format='rgb', use_video_port=False)
                logging.debug('Full-res capture took: {}'.format(time.time() - start))
                return stream.array
                # return stream.array.tolist() # TODO: change to tolist()?

    def low_res_still(self):
        # type: () -> [[(int, int, int)]]
        """
        Captures a 640x480 still from PiCamera natively.
        """
        with self.lock:
            old_resolution = self.camera.resolution
            self.camera.resolution = (640, 480)
            with PiRGBArray(self.camera) as stream:
                start = time.time()
                self.camera.capture(stream, format='rgb', use_video_port=True)
                logging.debug('Low-res capture took : {}'.format(time.time() - start))
                self.camera.resolution = old_resolution
                return stream.array
                # return stream.array.tolist() # TODO: change to tolist()?

    def get_current_resolution(self):
        # type: () -> (int, int)
        """
        Gets the resolution of this PiCamera
        """
        return self.camera.resolution

    def get_max_resolution(self):
        # type: () -> (int, int)
        """
        Gets the maximum supported resolution of this PiCamera
        """
        return self.MAX_RESOLUTION

    def set_resolution(self, x, y):
        # type: (int, int) -> None
        """
        Sets the resolution of this camera for all future captures from it,
        if the provided resolution is valid.

        :param x: the x-dimension of the desired resolution
        :param y: the y-dimension of the desired resolution
        """
        with self.lock:
            self.camera.resolution = [x, y]
