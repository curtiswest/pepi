import pytest
from PIL import Image
import numpy as np
from io import BytesIO

from ..abstract_camera import RGBImage

class TestRGBImage(object):
    @pytest.fixture()
    def image(self):
        return (np.random.rand(720, 600, 3) * 255).astype(np.uint8)

    def test_python_objects(self, image):
        rgb_image = RGBImage(array=image)
        rgb_image.array = image
        with pytest.raises(ValueError):
            rgb_image.array = [10, 20, 30]
        out_array = rgb_image.array
        assert isinstance(out_array, np.ndarray)
        out_list = rgb_image.list
        assert isinstance(out_list, list)

    def test_low_res_resize(self, image):
        rgb_image = RGBImage(array=image)
        low_res = rgb_image.low_res
        assert isinstance(low_res, np.ndarray)
        pil_image = Image.fromarray(low_res)
        assert pil_image.size == (640, 480)

    def test_image_from_file(self, image):
        pil_image = Image.fromarray(image)
        buf = BytesIO()
        pil_image.save(buf, format='PNG')
        buf.seek(0)
        rgb_image = RGBImage.fromfile(buf)
        assert (rgb_image.array==image).all()

    def test_image_from_string(self, image):
        pil_image = Image.fromarray(image)
        buf = BytesIO()
        pil_image.save(buf, format='PNG')
        buf_str = buf.getvalue()
        rgb_image = RGBImage.fromstring(buf_str)
        assert (rgb_image.array==image).all()