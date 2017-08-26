#!/usr/bin/env python

from flask import Flask, Response, redirect
import os
import glob
from PIL import Image
import logging
from io import BytesIO
import threading
import time

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '2.0a'
__maintainer__ = 'Curtis West'
__email__ = 'curtis@curtiswest.net'
__status__ = 'Development'

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)


def stream_from_folder(path, stream_resolution=(640, 480)):
    if not os.path.exists(path):
        os.makedirs(path)
    if path[-1:] != '/':
        path = path + '/'

    last = None
    while True:
        file_list = sorted(glob.glob(path + '/*.jpg'), key=os.path.getctime)
        if not file_list:
            continue
        elif len(file_list) < 2:
            continue

        second_newest = file_list[-2]
        if second_newest == last:
            continue
        try:
            frame = Image.open(second_newest)
            last = second_newest
            frame.thumbnail(stream_resolution)
            frame_buffer = BytesIO()
            frame.save(frame_buffer, 'JPEG', quality=85)
            os.remove(second_newest)
        except IOError as e:
            time.sleep(0.1)
            # Not a JPG, or file deleted under our feet
            logging.warn(e)
            continue
        except Exception as e:
            print(e)
            continue

        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame_buffer.getvalue() + b'\r\n')


# TODO this is really hacky, fix it to not use globals
stream_path = '/tmp/stream'


@app.route('/')
def index():
    return redirect('/stream.mjpeg')


@app.route('/stream.mjpeg')
def stream():
    return Response(stream_from_folder(stream_path), mimetype='multipart/x-mixed-replace; boundary=frame')


class StreamerThread(threading.Thread):
    def __init__(self, path):
        super(StreamerThread, self).__init__()
        self.path = path
        self.daemon = True

    def run(self):
        global stream_path
        stream_path = self.path
        app.run(host='0.0.0.0', debug=False, port=6001)
