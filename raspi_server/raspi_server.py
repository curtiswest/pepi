#!/usr/bin/env python

from __future__ import print_function

import logging
import os
import sys
import tempfile
from io import BytesIO

import thriftpy
from PIL import Image

poc_thrift = thriftpy.load('poc.thrift', module_name='poc_thrift')
from thriftpy.rpc import make_server

sys.path.append('..')
from server import MetaImager, MetaImagingServer, StreamerThread, IPTools
from raspi_imager import RPiCameraImager

logging.basicConfig(level=logging.INFO)

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.0a'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class RaspPiImagingServer(MetaImagingServer):
    def __init__(self, imager):
        # type: (MetaImager) -> None
        super(RaspPiImagingServer, self).__init__(imager=imager)
        self._stored_captures = dict()
        self.imager = imager
        self.stream_path = tempfile.mkdtemp()
        self.streamer = StreamerThread(self.stream_path)
        self.streamer.start()
        # if isinstance(imager, RPiCameraImager):
        #     self.imager.capture_to_folder(self.stream_path)

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
        os.system('shutdown now')

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
    handler = RaspPiImagingServer(imager=RPiCameraImager())
    server = make_server(poc_thrift.ImagingServer, handler, '0.0.0.0', 6000)
    print('Starting RaspPiImagingServer')
    server.serve()
