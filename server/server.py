#!/usr/bin/env python

from __future__ import print_function

import logging
logging.basicConfig(level=logging.DEBUG)
import subprocess
import threading

from io import BytesIO
import numpy as np
import time
from PIL import Image

import thriftpy
poc_thrift = thriftpy.load('../poc.thrift', module_name='poc_thrift')
from thriftpy.rpc import make_server
from meta_server import MetaImager, MetaImagingServer
from picamera import PiCamera
from picamera.array import PiRGBArray

class DummyImager(MetaImager):
    def __init__(self):
        super(DummyImager, self).__init__()
        pass

    @staticmethod
    def _random_image_gen(resolution=(1920, 1080)):
        return (np.random.rand(resolution[1], resolution[0], 3) * 255).astype(np.uint8)

    def still(self):
        return self._random_image_gen()

class RaspPiCameraModuleV1(MetaImager):
    """
    RaspPiCameraModule is an imager that uses the Raspberry Pi Camera Module v1 to obtain imagery. It is capable of
    taking pictures in various resolutions, but defaults to the maximum resolution of 2592x1944.
    """

    RESOLUTION_MAX = (2592, 1944)

    def __init__(self, resolution=RESOLUTION_MAX):
        # type: (int, int) -> None
        super(RaspPiCameraModuleV1, self).__init__()
        self.camera = PiCamera()
        self.requested_resolution = resolution
        self.camera.resolution = resolution
        self.camera.start_preview()
        self.lock = threading.Lock()

    def still(self):
        # type: () -> [[(int, int, int)]]
        with self.lock:
            # Lock is neccessary on the camera because this method can be called from different threads with
            # reference to this Imager, but the camera is not thread-safe.
            with PiRGBArray(self.camera) as raw_capture:
                # Save the settings of the camera
                old_resolution = self.camera.resolution
                self.camera.resolution = self.requested_resolution
                self.camera.capture(raw_capture, format='rgb', use_video_port=False)

                # Restore old camera settings
                self.camera.resolution = old_resolution
                return raw_capture.array[0:self.requested_resolution[0]][0:self.requested_resolution[1]] # Crop to size


class RaspPiImagingServer(MetaImagingServer):
    def __init__(self, imager):
        super(RaspPiImagingServer, self).__init__(imager=imager)
        self._stored_captures = dict()
        self.imager = imager
        self._ping_count = 0

    def ping(self):
        logging.info('ping()')
        return True

    def identify(self):
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

    def shutdown(self):
        logging.info('Got shutdown command')
        subprocess.call(['sudo shutdown now'])

    def stream_url(self):
        return 'http://www.google.com.au/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'

    def start_capture(self, data_code):
        im = Image.fromarray(self.imager.still())
        im.load()
        self._stored_captures[data_code] = im

    def _encode_from_stored_capture_(self, data_code, encoding, quality):
        image_buffer = BytesIO()
        try:
            image = self._stored_captures.pop(data_code)
        except KeyError:
            return None
        else:
            image.save(image_buffer, encoding, quality=quality)
            return image_buffer.getvalue()

    def retrieve_still_png(self, with_data_code):
        return self._encode_from_stored_capture_(with_data_code, 'PNG', quality=3)

    def retrieve_still_jpg(self, with_data_code):
        return self._encode_from_stored_capture_(with_data_code, 'JPEG', quality=85)


if __name__ == '__main__':
    handler = RaspPiImagingServer(imager=RaspPiCameraModuleV1())
    server = make_server(poc_thrift.ImagingServer, handler, '0.0.0.0', 6000)
    print('Starting RaspPiImagingServer')
    server.serve()
