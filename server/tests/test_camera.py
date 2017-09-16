import pytest
from PIL import Image
import numpy as np


# noinspection PyMethodMayBeStatic
class AbstractCameraContract(object):
    """
    Tests a Camera object against the defined Camera contract,
    essentially proving that it is compatible with all servers
    that use this defined contract. It uses a PyTest fixture
    which you must override to use.

    :Example:
        class MyCamera(AbstractCamera):
            def init():
                self._camera = MagicalCamera()

            def still():
                return self._camera.capture()

            ...

        class TestMyCamera(AbstractCameraContract):
            @pytest.fixture(scope="module")
            def camera(self):
                return MyCamera()
    """
    @pytest.fixture(scope="module")
    def camera(self):
        raise NotImplementedError('You must override the @pytest.fixture `camera` '
                                  'with a concreteAbstractCamera')

    def test_still(self, camera):
        image = camera.still()
        Image.fromarray(np.array(image, dtype=np.uint8))
        for x in image:
            for y in x:
                assert all([0 <= c <= 255 for c in y])

    def test_low_res_still(self, camera):
        image = camera.low_res_still()
        pil_image = Image.fromarray(np.array(image, dtype=np.uint8))
        assert pil_image.size == (640, 480)
        for x in image:
            for y in x:
                assert all([0 <= c <= 255 for c in y])

    def test_resolutions(self, camera):
        max_resolution = camera.get_max_resolution()
        assert len(max_resolution) == 2
        camera.set_resolution(x=1280, y=720)
        updated_resolution = camera.get_current_resolution()
        assert len(updated_resolution) == 2
        assert camera.get_max_resolution() == max_resolution
        image = Image.fromarray(np.array(camera.still(), dtype=np.uint8))
        assert updated_resolution == list(image.size)