#!/usr/bin/env python

from __future__ import print_function

import logging
import os
import tempfile
from io import BytesIO
import sys
import uuid

from PIL import Image
sys.path.append('..')
# noinspection PyPep8
from server import MetaImager, MetaImagingServer, MJPGStreamer, IPTools

logging.basicConfig(level=logging.INFO)

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.0a'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class RaspPiImagingServer(MetaImagingServer):

    STREAM_PORT = 6001

    def __init__(self, imager):
        # type: (MetaImager) -> None
        super(RaspPiImagingServer, self).__init__(imager=imager)
        self._stored_captures = dict()
        self.imager = imager
        self.stream_path = tempfile.mkdtemp()
        self.streamer = MJPGStreamer(self.stream_path, port=self.STREAM_PORT)
        self.imager.stream_jpg_to_folder(self.stream_path)

    @staticmethod
    def _current_ip():
        # type: () -> str
        return IPTools.current_ips()[0]

    def ping(self):
        # type: () -> bool
        logging.info('ping()')
        return True

    def identify(self):
        # type: () -> str
        # Extract serial from the "/proc/cpuinfo" file as the server ID
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        return line[10:26]
                else:
                    return uuid.uuid4().hex[0:16]
        except IOError:
            return uuid.uuid4().hex[0:16]

    def shutdown(self):  # pragma: no cover
        logging.info('Got shutdown command')
        os.system('shutdown now')

    def stream_url(self):
        # type: () -> str
        return 'http://{}:{}/stream.mjpeg'.format(self._current_ip(), self.STREAM_PORT)

    def start_capture(self, data_code):
        image = Image.fromarray(self.imager.still())
        self._stored_captures[data_code] = image

    def _encode_from_stored_capture_(self, data_code, encoding, quality):
        # type: (str, str, int) -> str or None
        image_buffer = BytesIO()
        try:
            image = self._stored_captures.pop(data_code)
        except KeyError:  # pragma: no cover
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
