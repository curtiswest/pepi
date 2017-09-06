import os
from abc import ABCMeta, abstractmethod

import thriftpy
import os
from abc import ABCMeta, abstractmethod

import thriftpy

prefix = os.path.abspath('.')
if not prefix.endswith('pibox') or not prefix.endswith('pepi'):
    while not prefix.endswith('pibox') and not prefix.endswith('pepi'):
        prefix, _ = os.path.split(prefix)

poc_thrift = thriftpy.load('{}/poc.thrift'.format(prefix), module_name='poc_thrift')

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.1'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'

ImageUnavailable = poc_thrift.ImageUnavailable


class DocstringMeta(ABCMeta):
    """
    Metaclass that allows docstring 'inheritance'
    """
    pass
#     # noinspection PyInitNewSignature,PyMethodParameters
#     def __new__(mcls, classname, bases, cls_dict):
#         cls = ABCMeta.__new__(mcls, classname, bases, cls_dict)
#         mro = cls.__mro__[1:]
#         for name, member in viewitems(cls_dict):
#             if not getattr(member, '__doc__'):
#                 for base in mro:
#                     try:
#                         member.__doc__ = getattr(base, name).__doc__
#                         break
#                     except AttributeError:
#                         pass
#         return cls


class MetaImager(object):
    """
    MetaImager is an abstract base class that defines the interface
    required from an Imager. Imagers are used to capture imagery
    from its associated device in a consistent format. This allows
    various concrete implementations of Imager to obtain imagery from
    different sources, such as different USB webcams, DSLRs and embedded
    cameras, etc.

    A Imager subclasses MetaImagingServer *must* implement all methods marked
    with @abstractmethod.
    """
    __metaclass__ = DocstringMeta

    def __init__(self):
        self._streaming_thread = None

    @abstractmethod
    def still(self):
        # type: () -> [[int], [int], [int]]
        """
        Captures a still from the camera and returns it as 3-dimensional RGB array representing the image

        :return: [[[R, G, B]] NumPy array of Numpy.uint8 0-255 values.
        """
        pass

    def stream_jpg_to_folder(self, path, max_framerate=1, resolution=(640, 480)):
        # type: (str, int, (int, int)) -> None
        """
        Continuously captures frames to a the given `path` at the given `resolution`, up to the `max_framerate` fps.

        Note: this method should come at a lower priority than the `still` method, i.e. if a `still()` method call comes
        in, it should be capture immediately rather than for this method even if this means dropping the framerate.

        :param path: path to save the images to
        :param max_framerate: maximum framerate to capture the image at. Note that implementations may have a
                              (significantly) lower framerate
        :param resolution: resolution to save the JPEG images at
        """
        import threading
        import time
        from PIL import Image

        class StreamingThread(threading.Thread):
            def __init__(self, capture_method, path_, max_framerate_=1, resolution_=(640, 480)):
                self.capture_method = capture_method
                self.path = path_
                self.max_framerate = max_framerate_
                self.resolution = resolution_
                self.frame_counter = 0
                super(StreamingThread, self).__init__()
                self.daemon = True
                self.start()

            def run(self):
                last_time = time.time()
                while True:
                    if time.time() > (last_time + (1 / max_framerate)):
                        last_time = time.time()
                        im = Image.fromarray(self.capture_method())
                        im.thumbnail(self.resolution)
                        im.save(self.path + '/{}.jpg'.format(self.frame_counter))
                        self.frame_counter += 1
                    else:
                        time.sleep(1 / self.max_framerate / 4)

        self._streaming_thread = StreamingThread(self.still, path_=path, max_framerate_=max_framerate,
                                                 resolution_=resolution)

    def stop_streaming(self):
        """
        If this Imager is currently streaming, stop the stream.

        :return: None
        """
        if self._streaming_thread:
            self._streaming_thread = None


class MetaImagingServer(object):
    """
    MetaImagingServer is an abstract base class that defines the interface
    required from an ImagingServer. ImagingServers are used in with the
    Apache Thrift protocol to provide RPC mechanisms, allowing remote control
    the server.

    An ImagingServer subclassing MetaImagingServer *must* implement all methods
    marked with @abstractmethod below in a manner that is consistent with their
    documentation and type annotations. Failure to do so will make compatibility
    between different ImagingServers and clients near-impossible or at the very
    least, fragile and unstable.

    An ImagingServer's use-case is to provide a server through which a
    MetaImager may be controlled in a consistent manner. This allows for client's
    to seamlessly connect to many implementations of MetaImagingServer's, each
    possibly using different MetaImager's to obtain imagery.

    A MetaImagingServer is not, however, *required* to use a MetaImager, but is
    a suggestion for maintaining compatibility.

    A MetaImagingServer implementations may use multiple connected cameras, that
    are transparent to the connecting client. In this case, you should return a
    list of encoded images.
    """
    __metaclass__ = DocstringMeta

    def __init__(self, imagers):
        self.imagers = imagers

    @abstractmethod
    def ping(self):
        # type: () -> bool
        """
        Ping the server to check if it is active and responding.

        :return: True (always)
        """
        pass

    @abstractmethod
    def identify(self):
        # type: () -> str
        """
        Get the unique identifier of this server.

        :return: the server's unique identifier string
        """
        pass

    @abstractmethod
    def stream_urls(self):
        # type: () ->  [str]
        """
        Get the a list of URLs where the MJPG image stream of each camera connected to this server may be accessed.

        :return: a list of the stream URLs as a string
        """
        pass

    @abstractmethod
    def shutdown(self):
        # type: () -> None
        """
        Shutdown the server (i.e. power-off). If this does not suit your use-case,
        you may choose to ignore calls to this function (although there will still
        need to be a concrete implementation of it in a concrete ImagingServer).

        :return: None
        """
        pass

    @abstractmethod
    def start_capture(self, data_code):
        # type: (str) -> None
        """
        Immediately starts the process of capturing from this server's Imager(s),
        and stores the captured data under the given unique data_code.

        Note: the received `data_code` may be assumed to be unique. Implementations may choose to implement more
        complex methods of associated `data_codes` with clients, but this is not required.

        :param data_code: the requested data_code to store the capture under
        :return: None
        """
        pass

    @abstractmethod
    def retrieve_still_pngs(self, with_data_code):
        # type: (str) -> [str]
        """
        Retrieves the images stored under `with_data_code`, if they exists, and
        encodes them into a .png str (i.e. bytes).

        :param with_data_code: the data_code from which the image will be retrieved
        :raises: ImageUnavailable: when image requested with an invalid/unknown data_code
        :return: a list of strings with each string containing an encoded as a .png
        """
        pass

    @abstractmethod
    def retrieve_still_jpgs(self, with_data_code):
        # type: (str) -> [str]
        """
        Retrieves the images stored under `with_data_code`, if they exists, and
        encodes them into a .jpg str (i.e. bytes).

        :param with_data_code: the data_code from which the image will be retrieved
        :raises: ImageUnavailable: when image requested with an invalid/unknown data_code
        :return: a list of strings with each string containing an encoded as a .jpg
        """
        pass

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
