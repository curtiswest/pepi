import imghdr
import sys

import pytest
from PIL import Image

from ..meta_server import ImageUnavailable

if sys.version_info < (3,):
    text_type = (str, unicode)
    binary_type = str
else:
    text_type = str
    binary_type = bytes


# noinspection PyMethodMayBeStatic
class MetaCameraServerContract(object):
    @pytest.fixture(scope="module")
    def server(self):
        raise NotImplementedError('You must override the @pytest.fixture `server`')

    def test_ping(self, server):
        assert server.ping() is True

    def test_identify(self, server):
        identifier = server.identify()
        assert isinstance(identifier, text_type)
        assert len(identifier) > 0

    def test_stream_url(self, server):
        stream_urls = server.stream_urls()
        assert isinstance(stream_urls, list)
        print('text type: {}'.format(text_type))
        for url in stream_urls:
            print(type(url))
        assert all([isinstance(x, text_type) for x in stream_urls])
        assert all([x.startswith('http://') or x.startswith('https://') for x in stream_urls])

    def test_capturing_to_jpgs(self, server):
        import time
        from io import BytesIO
        data_code = 'my_data_code'
        server.start_capture(data_code)
        time.sleep(1)
        jpg_strings = server.retrieve_stills_jpg(data_code)

        assert isinstance(jpg_strings, list)
        assert all([isinstance(image, binary_type) for image in jpg_strings])
        assert all([len(image) > 0 for image in jpg_strings])
        for jpg in jpg_strings:
            image_bytes = BytesIO(jpg)
            assert imghdr.what(image_bytes) == 'jpeg'
            image = Image.open(image_bytes)
            assert image.size > (0, 0)
            assert image.format == 'JPEG'

    def test_image_unavailable(self, server):
        with pytest.raises(ImageUnavailable):
            server.retrieve_stills_jpg('not_a_real_data_code')
        with pytest.raises(ImageUnavailable):
            server.retrieve_stills_png('not_a_real_data_code')

    def test_capturing_to_pngs(self, server):
        import time
        from io import BytesIO
        data_code = 'my_data_code'
        server.start_capture(data_code)
        time.sleep(1)
        png_strings = server.retrieve_stills_png(data_code)

        assert isinstance(png_strings, list)
        assert all([isinstance(image, binary_type) for image in png_strings])
        assert all([len(image) > 0 for image in png_strings])
        for count, png in enumerate(png_strings):
            image_bytes = BytesIO(png)
            assert imghdr.what(image_bytes) == 'png'
            image = Image.open(image_bytes)
            assert image.size > (0, 0)
            assert image.format == 'PNG'
            image.save('test_{}.png'.format(count))

    def test_enumerate_methods(self, server):
        result = server.enumerate_methods()
        assert isinstance(result, dict)
        assert all([isinstance(key, text_type) for key in result])
        assert all([isinstance(value, list) for value in result.values()])
        assert result['ping'] == []
        assert result['identify'] == []
        assert result['stream_urls'] == []
        assert result['shutdown'] == []
        assert 'start_capture' in result
        assert 'retrieve_stills_jpg' in result
        assert 'retrieve_stills_png' in result
        assert 'enumerate_methods' in result
