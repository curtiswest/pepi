import pytest

from server import MJPGStreamer


def _random_image_gen(resolution=(704, 528)):
    import numpy as np
    return (np.random.rand(resolution[1], resolution[0], 3) * 255).astype(np.uint8)


def test_newest_file_in_folder_generator(tmpdir):
    second_newest = str(tmpdir) + '/0.txt'
    newest = str(tmpdir) + '/1.txt'
    open(second_newest, 'a').close()
    open(newest, 'a').close()

    for count, file_ in enumerate(MJPGStreamer.newest_file_in_folder(str(tmpdir)), start=2):
        assert file_ == second_newest
        second_newest = newest
        newest = str(tmpdir) + '/{}.txt'.format(count)
        open(newest, 'a').close()

        if count >= 10:
            break


def test_jpeg_generator(tmpdir):
    from io import BytesIO

    from PIL import Image

    Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/0.jpg')
    Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/1.jpg')

    for count, jpg in enumerate(MJPGStreamer.jpeg_image_generator(str(tmpdir), resolution=(640, 480)), start=2):
        im = BytesIO(jpg)
        im = Image.open(im)
        assert im.format == 'JPEG'
        assert im.size == (640, 480)
        Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/{}.jpg'.format(count))

        if count >= 10:
            break


def test_response(tmpdir):
    import requests
    from contextlib import closing
    from PIL import Image

    _ = MJPGStreamer(str(tmpdir), port=6002, ip='127.0.0.1')
    Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/0.jpg')
    Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/1.jpg')
    Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/3.jpg')
    Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/4.jpg')

    url = 'http://127.0.0.1:{}/stream.mjpg'.format(6002)

    with closing(requests.get(url, stream=True)) as r:
        assert r.status_code == 200
        if r.encoding is None:
            r.encoding = 'utf-8'
        for count, line in enumerate(r.iter_lines(), start=5):
            if line.startswith(b'\xff\xd8\xff\xe0'):
                Image.fromarray(_random_image_gen()).save(str(tmpdir) + '/{}.jpg'.format(count))
                if count > 10:
                    break
                else:
                    continue
        else:
            pytest.fail('Never got a valid JPG magic number', pytrace=True)
