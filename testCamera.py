import time
import cv2
import numpy as np
from picamera import PiCamera

def getCameraStill():
    with PiCamera() as camera:
        camera.resolution= (500,500)
#        camera.start_preview()
#       time.sleep(2)
        camera.capture('temp.jpg')
    data = np.asarray(cv2.imread('temp.jpg'), dtype='float64')
    return data

data = getCameraStill()
print data.shape
