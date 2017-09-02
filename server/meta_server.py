from abc import ABCMeta, abstractmethod

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.0a'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


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
    __metaclass__ = ABCMeta

    def __init__(self):
        self._streaming_thread = None

    @abstractmethod
    def still(self):
        # type: () -> [[int], [int], [int]]
        """
        Uncompressed still returning a RGB array representing the image
        :return: [[R], [G], [B]] array of 0-255 values representing RGB
        """
        pass

    def stream_jpg_to_folder(self, path, max_framerate=1, resolution=(640, 480)):
        # type: (str, int) -> None
        """
        Continuously captures frames to a the given `path` at the given `resolution`, up to the `max_framerate` fps.
        This method should come at a lower priority than the `still` method, i.e. if a `still()` method call comes in,
        it should be capture immediately rather than for this method even if this means dropping the framerate.
        Args:
            path: path to save the images to
            max_framerate: maximum framerate, note that implementations may have a (significantly) lower framerate
            resolution: resolution to save the JPEG images as
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
    """
    __metaclass__ = ABCMeta

    def __init__(self, imager):
        self.imager = imager

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
    def stream_url(self):
        # type: () ->  str
        """
        Get the URL where the direct MJPG image stream of this server may be accessed.
        :return: the stream URL as a string
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
        Immediately starts the process of capturing from this server's Imager,
        and stores the captured data under the given unique data_code.

        Note: the data_code should always be unique. You may choose to implement
        more complex methods such each connecting client having their own
        data_code namespace, but this is not strictly required.

        :param data_code: the requested data_code to store the capture under
        :return: None
        """
        pass

    @abstractmethod
    def retrieve_still_png(self, with_data_code):
        # type: (str) -> str
        """
        Retrieves the image stored under `with_data_code`, if it exists, and
        encodes it into a .png str (i.e. bytes).

        :param with_data_code: the data_code from which the image will be retrieved
        :return: a string with the image encoded as a .png
        """
        pass

    @abstractmethod
    def retrieve_still_jpg(self, with_data_code):
        # type: (str) -> str
        """
        Retrieves the image stored under `with_data_code`, if it exists, and
        encodes it into a .jpg str (i.e. bytes).

        :param with_data_code: the data_code from which the image will be retrieved
        :return: a string with the image encoded as a .jpg
        """
        pass

    def enumerate_methods(self):
        # type: () -> [(str, str)]
        """
        Retrieves a map of the methods available on this server. This is useful
        for clients to verify the methods it can expect to be able to call
        if being called remotely.

        :return: dict of <method_name, [arguments]>
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
