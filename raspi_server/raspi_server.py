#!/usr/bin/env python

from __future__ import print_function

import logging
import os
import tempfile
from io import BytesIO
import sys
import uuid
import collections
from future.utils import viewitems
import atexit

from PIL import Image
# noinspection PyPep8
sys.path.append('../')
sys.path.append('../../')
from server import MetaCamera, MetaCameraServer, ImageUnavailable, MJPGStreamer, IPTools

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.1'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class RaspPiCameraServer(MetaCameraServer):

    StreamInfo = collections.namedtuple('StreamInfo', 'port, folder, streamer')
    STREAM_PORT = 6001

    def __init__(self, cameras, stream=True):
        # type: ([MetaCamera], bool) -> None
        super(RaspPiCameraServer, self).__init__(cameras=cameras)
        self._stored_captures = dict()
        self.cameras = cameras
        self.streams = dict()

        if stream:
            StreamInfo = collections.namedtuple('StreamInfo', 'port, folder, streamer')
            for count, imager in enumerate(cameras):
                port_ = self.STREAM_PORT + count
                folder_ = tempfile.mkdtemp()
                streamer_ = MJPGStreamer(folder_, port=port_)
                self.streams[imager] = StreamInfo(port=port_, folder=folder_, streamer=streamer_)
                imager.stream_jpg_to_folder(folder_)

        def cleanup():
            logging.info('Cleaning up RaspPiCameraServer')
            self._stored_captures = None
            self.cameras = None
            self.streams = None
            logging.info('Cleanup complete for RaspPiCameraServer')
        atexit.register(cleanup)

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
        logging.info('identify()')
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if line[0:6] == 'Serial':
                        return line[10:26]
                return uuid.uuid4().hex[0:16]
        except IOError:
            return uuid.uuid4().hex[0:16]

    def shutdown(self):  # pragma: no cover
        logging.info('shutdown()')
        logging.info('Got shutdown command')
        os.system('shutdown now')

    def stream_urls(self):
        # type: () -> [str]
        logging.info('stream_urls()')
        out_urls = []
        for imager, stream_info in viewitems(self.streams):
            out_urls.append('http://{}:{}/stream.mjpeg'.format(self._current_ip(), stream_info.port))
        return out_urls

    def start_capture(self, data_code):
        # type: (str) -> None
        """
        Immediately starts the process of capturing from this server's cameras,
        and stores the captured images under the given unique data_code.

        Note: the received `data_code` is assumed to be unique.

        :param data_code: the requested `data_code` to store the capture under
        :return: None
        """
        logging.info('start_capture(data_code: {})'.format(data_code))
        captures = []
        # TODO: parallelize capture from all cameras
        for camera in self.cameras:
            try:
                captures.append(Image.fromarray(camera.still()))
            except (AttributeError, TypeError, ValueError) as e:
                logging.warn('Could not construct image from received RGB array: {}'.format(e))
                continue
        if captures:
            self._stored_captures[data_code] = captures
        logging.info('Stored_captured after start_capture(): {}'.format(self._stored_captures.keys()))

    def _retrieve_and_encode_from_stored_captures(self, data_code, encoding, quality):
        # type: (str, str, int) -> [str]
        try:
            image_list = self._stored_captures.pop(data_code)
        except KeyError:  # pragma: no cover
            raise ImageUnavailable('No images are stored under the data_code "{}"'.format(data_code))
        else:
            out_strings = []
            for image in image_list:
                image_buffer = BytesIO()
                image.save(image_buffer, encoding, quality=quality)
                out_strings.append(image_buffer.getvalue())
            return out_strings

    def retrieve_stills_png(self, with_data_code):
        logging.info('retrieve_stills_png(with_data_code: {})'.format(with_data_code))
        # type: (str) -> [str]
        return self._retrieve_and_encode_from_stored_captures(with_data_code, 'PNG', quality=3)

    def retrieve_stills_jpg(self, with_data_code):
        logging.info('retrieve_stills_jpg(with_data_code: {})'.format(with_data_code))
        # type: (str) -> [str]
        return self._retrieve_and_encode_from_stored_captures(with_data_code, 'JPEG', quality=85)
