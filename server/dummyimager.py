import numpy as np

from server import MetaImager


class DummyImager(MetaImager):
    def __init__(self):
        super(DummyImager, self).__init__()
        pass

    @staticmethod
    def _random_image_gen(resolution=(1920, 1080)):
        return (np.random.rand(resolution[1], resolution[0], 3) * 255).astype(np.uint8)

    def still(self):
        return self._random_image_gen()

