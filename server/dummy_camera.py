"""
dummy_camera.py: A concrete `AbstractCamera` that generates random images of RGB noise for debugging purposes.
"""

import numpy as np

from server import AbstractCamera

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '3.1'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'

class DummyCamera(AbstractCamera):
    """
    `DummyCamera` is a concrete `AbstractCamera` that generates random images of RGB noise.
    """

    MAX_RESOLUTION = [1920, 1080]

    @property
    def resolution(self):
        return self._resolution

    @resolution.setter
    def resolution(self, value):
        self._resolution = value if value < self.MAX_RESOLUTION else self.MAX_RESOLUTION

    def __init__(self, resolution=MAX_RESOLUTION):
        print('Constructing DummyImager')
        super(DummyCamera, self).__init__()
        self.resolution = list(resolution)

    @staticmethod
    def _random_image_gen(resolution):
        return (np.random.rand(resolution[1], resolution[0], 3) * 255).astype(np.uint8).tolist()

    def still(self):
        # type: () -> [[int], [int], [int]]
        """
        Captures a still from the camera and returns it as 3-dimensional RGB array representing the image.

        :return: multidimensional list of row, column, RGB values between 0-255.
        """
        return self._random_image_gen(resolution=self.resolution)

    def low_res_still(self):
        # type: () -> [[int], [int], [int]]
        """
        Captures a low resolution still from the camera and returns it as 3-dimensional RGB array
        representing the image.

        :return: multidimensional list of row, column, RGB values between 0-255.
        """
        return self._random_image_gen(resolution=(640, 480))

    def get_max_resolution(self):
        # type: () -> [int, int]
        """
        Gets the maximum resolution supported by this camera.

        :return: a list of length 2 representing the resolution i.e. (x, y)
        """
        return self.MAX_RESOLUTION

    def get_current_resolution(self):
        # type: () -> [int, int]
        """
        Gets the current resolution of this camera.

        :return: a list of length 2 representing the resolution i.e. (x, y)
        """
        return self.resolution

    def set_resolution(self, x, y):
        # type: (int, int) -> None
        """
        If supported, sets the resolution of the camera.

        :param x: the x component of the desired resolution
        :param y: the x component of the desired resolution
        """
        self.resolution = [x, y]
