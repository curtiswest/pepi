"""
An implementation of `MetaImager` that generates random images of RGB noise for debugging purposes.
"""
import numpy as np

from server import MetaImager


class DummyImager(MetaImager):
    """
    `DummyImager` is a `MetaImager` that generates random images of RGB noise.
    """
    def __init__(self, resolution=(1920, 1080)):
        super(DummyImager, self).__init__()
        self.resolution = resolution

    @staticmethod
    def _random_image_gen(resolution=(1920, 1080)):
        return (np.random.rand(resolution[1], resolution[0], 3) * 255).astype(np.uint8)

    def still(self):
        """

        :return: Numpy array of [[[R, G, B]]] representing the randomly generated image.
        """
        return self._random_image_gen(resolution=self.resolution)
