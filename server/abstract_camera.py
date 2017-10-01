"""
abstract_camera.py: Holds the Python definition of a ``Camera`` as defined in ``pepi.thrift``.
"""

from abc import ABCMeta, abstractmethod
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '3.1'
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

    def low_res_still(self):
        # type: () -> [[int], [int], [int]]
        """
        Captures a still from the camera and returns it as 3-dimensional RGB array representing the image.

        :return: [[[R, G, B]] NumPy array of Numpy.uint8 0-255 values.
        """
        return RGBImage(self.still()).low_res

    @abstractmethod
    def get_max_resolution(self):
        # type: () -> [int, int]
        """
        Gets the maximum resolution supported by this camera.

        :return: a list of length 2 representing the resolution i.e. (x, y)
        """
        pass

    @abstractmethod
    def get_current_resolution(self):
        # type: () -> [int, int]
        """
        Gets the current resolution of this camera.

        :return: a list of length 2 representing the resolution i.e. (x, y)
        """
        pass

    @abstractmethod
    def set_resolution(self, x, y):
        # type: (int, int) -> None
        """
        If supported, sets the resolution of the camera.

        :param x: the x component of the desired resolution
        :param y: the x component of the desired resolution
        """
        pass

class RGBImage(object):
    """
    A utility object to convert images of different formats to RGB arrays
    """

    @property
    def array(self):
        """
        The array RGB array that represents this RGBImage
        :return:
        """
        return np.array(self._array)

    @array.setter
    def array(self, value):
        value = np.array(value)
        try:
            Image.fromarray(value)
        except (TypeError, ValueError, IOError) as e:
            raise ValueError('Array does not form a valid image: {}'.format(e.message))
        else:
            self._array = value

    def __init__(self, array):
        """
        Initialises a RGBImage with the given array.

        :raises: ValueError: when the array is malformed for an image
        :param array: an RGB array
        """
        self.array = np.array(array)

    @property
    def list(self):
        # type: () -> [[[int, int, int]]]
        """
        RGBImage as a native Python list.

        :return: Returns this RGB as a native Python list.
        """
        return list(self.array)

    @property
    def low_res(self):
        # type: () -> np.ndarray
        """
        Returns this RGB image as a numpy array.

        :return: this RGB image as a numpy array
        """
        return np.array(ImageOps.fit(Image.fromarray(self.array), size=(640,480)))

    @classmethod
    def fromstring(cls, string):
        image_buffer = BytesIO()
        image_buffer.write(string)
        image_buffer.seek(0)
        return cls(array=np.array(Image.open(image_buffer)))

    @classmethod
    def frombytes(cls, mode, size, bytes_):
        # type: (str, (int, int), (str or bytes)) -> RGBImage
        """
        Construct a RGBImage from the pixel data in a buffer.

        :param mode: the image mode, see https://pillow.readthedocs.io/en/3.1.x/handbook/concepts.html#concept-modes
        :param size: the image size
        :param bytes_: a byte buffer containing raw data for the given mode
        :raises: ValueError: when the bytes are malformed or not an image
        :return: RGBImage
        """
        return cls(array=np.array(Image.frombytes(mode, size, bytes_)))

    @classmethod
    def fromfile(cls, file):
        # type: (BytesIO or str) -> RGBImage
        """
        Construct a RGB image from the given file

        :param file: a filename (str) or file object.
        :raises: ValueError: when the file object is malformed or not an image
        :return: RGBImage
        """
        return cls(array=np.array(Image.open(file)))