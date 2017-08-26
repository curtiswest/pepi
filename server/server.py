#!/usr/bin/env python

from __future__ import print_function

import logging
import subprocess
import threading
import os
import tempfile
from io import BytesIO

import numpy as np
from PIL import Image
import thriftpy

poc_thrift = thriftpy.load('../poc.thrift', module_name='poc_thrift')
from thriftpy.rpc import make_server
from meta_server import MetaImager, MetaImagingServer
from picamera import PiCamera
from picamera.array import PiRGBArray

import stream
from iptools import IPTools

logging.basicConfig(level=logging.INFO)

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.0a'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


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
        # type: ((int, int)) -> None
        super(RaspPiCameraModuleV1, self).__init__()
        self.camera = PiCamera()
        self.req_reso = resolution
        self.camera.start_preview()
        self.lock = threading.Lock()
        self.folder_capture_thread = None

    def still(self):
        # type: () -> [[(int, int, int)]]
        """
        Captures a still with the cameras current setup.
        """
        with self.lock:
            # Lock is necessary on the camera because this method can be called from different threads with
            # reference to this Imager, but the camera is not thread-safe.
            with PiRGBArray(self.camera) as raw_capture:
                # Save the settings of the camera
                old_resolution = self.camera.resolution
                self.camera.resolution = self.req_reso
                self.camera.capture(raw_capture, format='rgb', use_video_port=False)

                # Restore old camera settings
                self.camera.resolution = old_resolution
                return raw_capture.array[0:self.req_reso[0]][0:self.req_reso[1]]  # Crop to size as can camera rounds up

    def capture_to_folder(self, fpath, framerate=5, resolution=(640, 480)):
        # type: (str, int, (int,int)) -> None
        """
        Starts a continuous capture of .jpgs to the given `path` at the given `framerate`. For example, this may be used
        in an MJPEG streaming scenario, where new .jpgs are streamed out over the web.
        Args:
            fpath: path to store the images in. Note that write permissions will be needed
            framerate: framerate (fps) to capture at. Recommended range of 1-15fps.
            resolution: the resolution to capture at. Recommended below 720p.
        """

        # noinspection PyShadowingNames
        class CaptureThread(threading.Thread):
            def __init__(self, camera, fpath, framerate, resolution):
                super(CaptureThread, self).__init__()
                self.camera = camera
                self.camera.framerate = framerate
                self.camera.resolution = resolution
                self.out_path = fpath
                self.daemon = True
                self._stopevent = threading.Event()
                if not os.path.exists(fpath):
                    os.makedirs(fpath)

            def run(self):
                for _ in self.camera.capture_continuous(
                                self.out_path + '/img{timestamp:%Y-%m-%d-%H-%M}-{counter:03d}.jpg',
                        use_video_port=True):
                    if self._stopevent.isSet():
                        break

            def stop(self, timeout=None):
                self._stopevent.set()
                threading.Thread.join(self, timeout)
                import shutil
                shutil.rmtree(self.out_path)  # Clean up captures

        self.folder_capture_thread = CaptureThread(camera=self.camera, fpath=fpath, framerate=framerate,
                                                   resolution=resolution)
        self.folder_capture_thread.start()

    def stop_capture_to_folder(self):
        """
        Stops the camera from capturing to the folder, if it was set up in the first place.
        """
        if self.folder_capture_thread:
            self.folder_capture_thread.stop()


class RaspPiImagingServer(MetaImagingServer):
    def __init__(self, imager):
        # type: (RaspPiCameraModuleV1) -> None
        super(RaspPiImagingServer, self).__init__(imager=imager)
        self._stored_captures = dict()
        self.imager = imager
        self.stream_path = tempfile.mkdtemp()
        self.streamer = stream.StreamerThread(self.stream_path)
        self.streamer.start()
        self.imager.capture_to_folder(self.stream_path)

    @staticmethod
    def _current_ip():
        # type: () -> str
        return IPTools.current_ip()[0]

    def ping(self):
        # type: () -> bool
        logging.info('ping()')
        return True

    def identify(self):
        # type: () -> str
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
        # type: () -> str
        return 'http://{}:{}/stream.mjpeg'.format(self._current_ip(), 6001)  # TODO convert to getting real port

    def start_capture(self, data_code):
        image = Image.fromarray(self.imager.still())
        self._stored_captures[data_code] = image

    def _encode_from_stored_capture_(self, data_code, encoding, quality):
        # type: (str, str, int) -> Optional[str]
        image_buffer = BytesIO()
        try:
            image = self._stored_captures.pop(data_code)
        except KeyError:
            return None
        else:
            image.save(image_buffer, encoding, quality=quality)
            return image_buffer.getvalue()

    def retrieve_still_png(self, with_data_code):
        # type: (str) -> str
        return self._encode_from_stored_capture_(with_data_code, 'PNG', quality=3)

    def retrieve_still_jpg(self, with_data_code):
        # type: (str) -> str
        return self._encode_from_stored_capture_(with_data_code, 'JPEG', quality=85)


if __name__ == '__main__':
    handler = RaspPiImagingServer(imager=RaspPiCameraModuleV1())
    server = make_server(poc_thrift.ImagingServer, handler, '0.0.0.0', 6000)
    print('Starting RaspPiImagingServer')
    server.serve()
