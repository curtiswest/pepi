from abc import ABCMeta, abstractmethod
import threading
import time

from PIL import Image

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '3.0'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'


class AbstractCamera(object):
    """
    AbstractCamera is an abstract base class that defines the interface
    required from an ``Camera``. ``Camera`` objects are used to capture
    imagery a physical camera. The means in which this image is obtained
    does not matter, as long as presented interface is consistent.

    ``Camera`` objects are intended to be used by ``BaseCameraServer``
    subclasses.

    A concrete ``Camera`` should subclass AbstractCamera and *must*
    implement all methods marked with @abstractmethod.
    """
    __metaclass__ = ABCMeta

    SUPPORTS_STREAMING = True

    def __init__(self):
        self._streaming_thread = None

    @abstractmethod
    def still(self):
        # type: () -> [[int], [int], [int]]
        """
        Captures a still from the camera and returns it as 3-dimensional RGB array representing the image.

        :return: [[[R, G, B]] NumPy array of Numpy.uint8 0-255 values.
        """
        pass

    def stream_jpg_to_folder(self, path, max_framerate=1, resolution=(640, 480)):
        # type: (str, int, (int, int)) -> None
        """
        Continuously captures frames to a the given `path` at the given `resolution`,
        up to the `max_framerate` fps.

        Note: this method should come at a lower priority than the `still` method,
        i.e. if a `still()` method call comes in, you should try to service it
        as soon as possible, even if this means compromising the stream.

        The provided implementation here is not optimised to all cameras, so
        overriding this method is suggested if you have a better method to get
        low-res images quickly from the physical camera.

        Alternatively, if you do not wish to stream from this server, set
        ``SUPPORTS_STREAMING`` to False in your class declaration, and then
        override this method to do nothing.

        :param path: path to save the images to
        :param max_framerate: `maximum` framerate to capture the image at
        :param resolution: resolution to save the JPEG images at
        """

        class StreamingThread(threading.Thread):
            """
            Starts a thread that will call the given `capture_method` method
            at least once every 1/`max_framerate` seconds and saves them to
            the given `path_` folder, for another thread to pick up on and use.
            """

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
                """
                Executes the capture within the given `max_framerate`..
                """
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
        If this Camera is currently streaming, stop the stream.

        :return: None
        """
        if self._streaming_thread:
            self._streaming_thread = None
