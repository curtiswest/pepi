import subprocess
import os
import time
import threading
import picamera
import sys
import atexit

sys.path.append('../')
from utils.stoppablethread import StoppableThread

class RecordingToFileThread(StoppableThread):
    def __init__(self, camera):
        super(RecordingToFileThread, self).__init__()

        # Set up camera
        if isinstance(camera, picamera.PiCamera):
            self.camera = camera
        else:
            self.camera = picamera.PiCamera()
        self.old_resolution = self.camera.resolution
        self.old_framerate = self.camera.framerate
        self.camera.resolution = [640, 480]
        self.camera.framerate = 5

    def run(self):
        # Keep recording until this thread receives a stop event
        record_path = '/tmp/stream'
        if not os.path.exists(record_path):
            os.makedirs(record_path)

        for filename in self.camera.capture_continuous('/tmp/stream/img{timestamp:%Y-%m-%d-%H-%M}-{counter:03d}.jpg', use_video_port=True):
            if self.is_stopped():
                break

        # Stop recording and return camera to previous setup and close socket
        self.camera.framerate = self.old_framerate
        self.camera.resolution = self.old_resolution


class MJPG_Streamer(object):
    def exit_handler(self):
        print('exit handler')
        if self.process:
            self.process.kill()

    def __init__(self):
        self.process = None
        pass

    def start_with_file(self, path_to_file, file_name):
        print('input file path: {}'.format(path_to_file + ' / ' + file_name))
        output_arg = '/usr/local/lib/mjpg-streamer/output_http.so -w ./www'
        input_arg =  '/usr/local/lib/mjpg-streamer/input_file.so -f {} -r -delay 0.09'.format(path_to_file)
        args = ['/usr/local/bin/mjpg_streamer',
                '-o', output_arg,
                '-i', input_arg]
        self.process = subprocess.Popen(args=args)
        atexit.register(self.exit_handler)

    def stop(self):
        self.process.kill()

class StreamLauncher(object):
    def __init__(self, camera=None):
        self.mjpg_streamer = MJPG_Streamer()
        self.record_thread = RecordingToFileThread(camera)
        self.record_thread.daemon = True
        self.camera = self.record_thread.camera

    def start(self):
        self.mjpg_streamer.start_with_file('/tmp/stream', 'raspi_image.jpg')
        self.record_thread.start()

    def stop(self):
        self.mjpg_streamer.stop()
        self.record_thread.stop()

if __name__ == '__main__':
    camera = picamera.PiCamera()
    s = StreamLauncher(camera)
    s.start()
    time.sleep(5)
    while threading.active_count > 0:
        time.sleep(0.1)