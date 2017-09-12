#!/usr/bin/env python

import os
import time
import glob
import logging
import threading
from io import BytesIO
import atexit

try:  # pragma: no cover
    # noinspection PyCompatibility
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError:  # pragma: no cover
    # Try with Python 2
    # noinspection PyCompatibility
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import socketserver

from PIL import Image

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.1'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """
    A multi-threaded HTTP server, i.e. creates a new thread to respond
    to each connection, so multiple connections can coexist. 
    """
    allow_reuse_address = True
    daemon_threads = True


class MJPGStreamer(object):
    """
    Starts a HTTP stream based on JPEG images obtained from the specified folder.
    """

    def __init__(self, img_path, ip='0.0.0.0', port=6001):
        # type: (str, str, int) -> None
        """
        Initialises this MJPGStreamer against the given `img_path, and ip:port combination, then starts the server
        as a daemon thread.
        Args:
            img_path: the path to obtain JPEG imagery from
            ip: ip to bind the server to
            port: port to bind the server to
        """
        # noinspection PyPep8Naming
        HandlerClass = self.stream_handler_factory(img_path)
        server = ThreadedHTTPServer((ip, port), HandlerClass)
        # self.server = HTTPServer((ip, port), HandlerClass)
        server.daemon_threads = True
        server.timeout = 5

        def handle_request_loop():
            """
            Handles requests on the server forever (used as a threading target).
            :return: None
            """
            while True:
                server.handle_request()

        def cleanup():
            """
            Cleans up the streamer by deleting any reference to its threads so the
            daemon mode will stop them.
            :return:
            """
            self.server_thread = None

        atexit.register(cleanup)
        # self.server_thread = threading.Thread(target=server.serve_forever)
        self.server_thread = threading.Thread(target=handle_request_loop)
        self.server_thread.daemon = True
        self.server_thread.start()
        print('Serving forever')

    @staticmethod
    def newest_file_in_folder(path, delete_old=True):
        # type: (str) -> str
        """
        Generator that yields the second newest file by modified time in the given `path`. The second newest file is
        yielded so that files in the process of being written are not used before they are complete; this is generally
        not an issue that the second newest file faces.

        Args:
            path: path to the folder to check for new files
            delete_old: True to delete all but the second_newest and newest files, False to not delete any
        """
        if not os.path.exists(path):  # pragma: no cover
            try:
                os.makedirs(path)
            except OSError as e:
                logging.warn(e)
        previous = None
        while True:
            file_list = sorted(glob.glob(path + '/*'), key=os.path.getmtime)
            if not file_list or len(file_list) < 2:  # pragma: no cover
                time.sleep(0.1)
                continue

            second_newest = file_list[-2]
            if second_newest == previous:
                time.sleep(0.1)
                continue

            previous = second_newest
            if delete_old:
                older_than_second_newest = file_list[0:-3]
                for old_file in older_than_second_newest:
                    try:
                        os.remove(old_file)
                    except (IOError, OSError):
                        pass

            yield second_newest

    @staticmethod
    def jpeg_image_generator(path, quality=85, resolution=(640, 480)):
        # type: (str, bool, (int, int)) -> bytes
        """
        Generates JPEG bytes from any image file in the given path based on the second newest file modified in the given
         `path`.

        JPEG files (and other image formats) are compressed to a JPEG as they must be modified to be resized.

        Args:
            path: path to the folder to check for new files
            quality: JPEG quality to compress to (0 lowest quality, 100 highest)
            resolution: resolution to yield the JPEGs as
        """
        for file_ in MJPGStreamer.newest_file_in_folder(path):
            try:
                frame = Image.open(file_)
                frame.thumbnail(resolution)
                frame_buffer = BytesIO()
                frame.save(frame_buffer, 'JPEG', quality=quality)
            except Exception as e:
                logging.warn(e)
                continue
            else:
                yield frame_buffer.getvalue()

    def stream_handler_factory(self, img_path):
        # type: (str) -> MJPGStreamHandler
        """
        Create a MJPGStreamHandler with the `img_path` set inside of it.

        This is necessary due to how BaseHTTPServer creates the BaseHTTPRequestHandler.

        Args:
            img_path: the path to give to MJPGStreamHandler
        """

        class MJPGStreamHandler(BaseHTTPRequestHandler, object):
            """
            MJPGStreamHandler handles HTTP requests for the MJPGStream by
            formatting the JPEGs files provided by a MJPGStreamer.jpeg_image_generator
            in the proper format for a HTTP MJPEG stream.
            """
            def __init__(self, *args, **kwargs):
                self.img_path = img_path
                super(MJPGStreamHandler, self).__init__(*args, **kwargs)

            # noinspection PyPep8Naming
            def do_GET(self):
                """
                Responds to a GET request to this handler.
                """
                if self.path.endswith('.mjpg') or self.path.endswith('.mjpeg'):
                    self.send_response(200)
                    self.send_header('Content-type', b'multipart/x-mixed-replace; boundary=frame')
                    self.end_headers()
                    for image in MJPGStreamer.jpeg_image_generator(self.img_path):
                        self.wfile.write(b'--frame')
                        self.send_header('Content-type', 'image/jpeg')
                        self.send_header('Content-length', str(len(image)))
                        self.end_headers()
                        self.wfile.write(image)

        return MJPGStreamHandler
