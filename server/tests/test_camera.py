import numpy
import os
import glob
import time
import imghdr

import pytest
from PIL import Image


# noinspection PyMethodMayBeStatic
class MetaCameraContract(object):
    """
    Tests a Camera object against the defined Camera contract,
    essentially proving that it is compatible with all servers
    that use this defined contract. It uses a PyTest fixture
    which you must override to use.

    :Example:

        class MyCamera(MetaCamera):
            def init():
                self._camera = MagicalCamera()

            def still():
                return self._camera.capture()

        class TestMyCamera(MetaCameraContract):
            @pytest.fixture(scope="module")
            def camera(self):
                return MyCamera()
    """
    @pytest.fixture(scope="module")
    def camera(self):
        raise NotImplementedError('You must override the @pytest.fixture `camera` with a MetaCamera')

    def test_still(self, camera):
        image = camera.still()
        assert isinstance(image, numpy.ndarray)
        for x in image:
            for y in x:
                assert all([0 <= c <= 255 for c in y])

    def test_stream_jpg_to_folder(self, camera, tmpdir):
        path = str(tmpdir)
        camera.stream_jpg_to_folder(path)
        time.sleep(3)
        camera.stop_streaming()

        for file_ in glob.glob(path + '/*'):
            name, extension = os.path.splitext(file_)
            assert extension == '.jpg' or extension == '.jpeg'
            assert imghdr.what(file_) == 'jpeg'
            try:
                image = Image.open(file_)
                assert image.format == 'JPEG'
            except IOError as e:
                pytest.fail('Couldn\'t open the image (malformed?) at file {}. Exception : {}'.format(file_, e), True)

    def test_stopping_thread(self, camera):
        camera.stop_streaming()
        time.sleep(0.5)
        camera.stop_streaming()
