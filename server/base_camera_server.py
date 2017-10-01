"""
base_camera_server.py: Holds the Python implementation of a ``CameraServer`` as defined in ``pepi.thrift``.
"""

import logging
import os
import tempfile
from io import BytesIO
import uuid
import collections
from future.utils import viewitems
import atexit
import threading
import time
import typing

from PIL import Image
import numpy as np

from .stream import MJPGStreamer
from .iptools import IPTools
from .pepi_thrift_loader import ImageUnavailable
from .abstract_camera import AbstractCamera


class CameraTimelapser(threading.Thread):
    """
    CameraTimelapser is a utility class designed to call the
    ``low_res_still()`` method on a concrete ``AbstractCamera``
    at a defined rate and save it to a given folder for the
    purposes of timelapsing or streaming from the camera.
    """
    def __init__(self, camera, folder, interval):
        # type: (AbstractCamera, str, typing.Union[float or int]) -> None
        super(CameraTimelapser, self).__init__()
        self.camera = camera
        self.path = folder
        self.interval = interval
        self.daemon = True

        def cleanup(self):
            self.camera = None
        atexit.register(cleanup, self)

    def run(self):
        start = time.time()
        count = 0
        while True:
            if time.time() > (start + self.interval):
                start = time.time()
                image = Image.fromarray(np.array(self.camera.low_res_still(), dtype=np.uint8))
                image.save(self.path + '/{}.jpeg'.format(count))
                count += 1
            else:
                time.sleep(self.interval/2)

# noinspection PyMethodMayBeStatic
class BaseCameraServer(object):
    """
    BaseCameraServer is the minimal Python implementation of a CameraServer
    as defined in ``pepi.thrift``. CameraServers are used in with the
    Apache Thrift protocol to provide RPC mechanisms, allowing control
    of this server over RPC, if it is launched with Thrift.

    A CameraServer subclassing BaseCameraServer may override any of these
    methods to better reflect their use. However, care must be taken to
    ensure that the side effects of the subclass's methods do not affect
    other methods. For example, if you were to change the capture method
    to store images in a list for whatever reason, you would need to change
    the image retrieval methods.

    A CameraServer's use-case is to provide a server that controls a
    number of cameras to be controlled in a consistent manner. This allows
    for a client to seamlessly control all implementations of CameraServer's,
    over Thrift without needing to concern themselves with what cameras are
    attached, the procedure call names, etc.

    This BaseCameraServer implementation supports multiple connected cameras,
    that are transparent to the connecting client. When retrieving images, a
    list of encoded images are returned. The order of this list remains
    consistent across procedure calls.
    """

    StreamInfo = collections.namedtuple('StreamInfo', 'port, folder, streamer')
    STREAM_PORT = 6001

    def __init__(self, cameras, stream=True):
        # type: ([AbstractCamera], bool) -> None
        """
        Initialises the BaseCameraServer.

        :param cameras: a list of AbstractCamera objects
        :param stream: True to start streams for all cameras, False to not.
        """
        # self.cameras = CameraManager(cameras)
        self.cameras = cameras
        self._stored_captures = dict()
        self.streams = dict()
        self.identifier = str(uuid.uuid4().hex)

        if stream:
            StreamInfo = collections.namedtuple('StreamInfo', 'port, folder, streamer, capturer')
            for count, camera in enumerate(cameras):
                port_ = self.STREAM_PORT + count
                folder_ = tempfile.mkdtemp()
                streamer_ = MJPGStreamer(folder_, port=port_)
                capturer = CameraTimelapser(camera=camera, folder=folder_, interval=0.5)
                capturer.start()
                self.streams[camera] = StreamInfo(port=port_, folder=folder_, streamer=streamer_, capturer=capturer)

        def cleanup():
            """
            Cleans up after this server by destroying connected cameras
            and their streams, and erasing the stored images.
            """
            logging.info('Cleaning up RaspPiCameraServer')
            self._stored_captures = None
            self.cameras = None
            self.streams = None
            logging.info('Cleanup complete for RaspPiCameraServer')
        atexit.register(cleanup)

    def ping(self):
        # type: () -> bool
        """
        Ping the server to check if it is active and responding.

        :return: True (always)
        """
        logging.info('ping()')
        return True

    def identify(self):
        # type: () -> str
        """
        Get the unique identifier of this server.

        :return: the server's unique identifier string
        """
        logging.info('identify()')
        return self.identifier

    @staticmethod
    def _current_ip():
        # type: () -> str
        return IPTools.current_ips()[0]

    def stream_urls(self):
        # type: () ->  [str]
        """
        Get the a list of URLs where the MJPG image stream of each camera
        connected to this server may be accessed.

        The order of the returned images is consistent, e.g. Camera #1, #2
        .., #x returned in that order.

        :return: a list of the stream URLs as a string
        """
        logging.info('stream_urls()')
        out_urls = []
        for _, stream_info in viewitems(self.streams):
            out_urls.append('http://{}:{}/stream.mjpeg'.format(self._current_ip(), stream_info.port))
        return out_urls

    def shutdown(self):
        # type: () -> None
        """
        Shutdown the server (i.e. power-off).

        Subclasses may choose to
        ignore calls to this function, in which case they should override
        this function to do nothing.

        :return: None
        """
        logging.info('shutdown()')
        os.system('shutdown now')

    def start_capture(self, data_code):
        # type: (str) -> None
        """
        Immediately starts the process of capturing from this server's Camera(s),
        and stores the captured data under the given unique data_code.

        Note: the received `data_code` is assumed to be unique. Subclasses may
        choose to implement better isolation methods, but this is not
        guaranteed nor required.

        :param data_code: the requested data_code to store the capture under
        :return: None
        """
        logging.info('start_capture(data_code: {})'.format(data_code))
        captures = []
        # TODO: parallelize capture from all cameras
        for camera in self.cameras:
            try:
                captures.append(Image.fromarray(np.array(camera.still(), dtype=np.uint8)))
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
        except KeyError:
            raise ImageUnavailable('No images are stored under the data_code "{}"'.format(data_code))
        else:
            out_strings = []
            for image in image_list:
                image_buffer = BytesIO()
                image.save(image_buffer, encoding, quality=quality)
                out_strings.append(image_buffer.getvalue())
            return out_strings

    def retrieve_stills_png(self, with_data_code):
        # type: (str) -> [str]
        """
        Retrieves the images stored under `with_data_code`, if they exist, and
        encodes them into a .png str (i.e. bytes).

        The order of the returned images is consistent, e.g. Camera #1, #2
        .., #x returned in that order.

        :param with_data_code: the data_code from which the image will be retrieved
        :raises: ImageUnavailable: when image requested with an invalid/unknown data_code
        :return: a list of strings with each string containing an encoded as a .png
        """
        logging.info('retrieve_stills_png(with_data_code: {})'.format(with_data_code))
        return self._retrieve_and_encode_from_stored_captures(with_data_code, 'PNG', quality=3)

    def retrieve_stills_jpg(self, with_data_code):
        # type: (str) -> [str]
        """
        Retrieves the images stored under `with_data_code`, if they exist, and
        encodes them into a .jpg str (i.e. bytes).

        The order of the returned images is consistent, e.g. Camera #1, #2
        .., #x returned in that order.

        :param with_data_code: the data_code from which the image will be retrieved
        :raises: ImageUnavailable: when image requested with an invalid/unknown data_code
        :return: a list of strings with each string containing an encoded as a .jpg
        """
        logging.info('retrieve_stills_jpg(with_data_code: {})'.format(with_data_code))
        return self._retrieve_and_encode_from_stored_captures(with_data_code, 'JPEG', quality=85)

    def enumerate_methods(self):
        # type: () -> [(str, str)]
        """
        Retrieves a map of the methods available on this server. This is useful
        for clients to verify the methods it can expect to be able to call
        if being called remotely.

        :return: dict of <method_name: [arguments]>
        """
        import inspect
        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        output_dict = dict()
        for _tuple in methods:
            name, pointer = _tuple
            args = inspect.getargspec(pointer).args
            try:
                args.remove('self')
            except ValueError:  # pragma: no cover
                pass
            output_dict[name] = args

        return output_dict
