import socket
import communication
import time
import cv2
import numpy as np
from picamera import PiCamera
import sys
import signal
import io

run_condition = True

def signal_handler(signal, frame):
        print('Exiting...')
        global run_condition
        run_condition = False
        sys.exit(0)

def generateRandomImg():
    z = np.random.random((2592, 1944))  # Test data
    print z.dtype
    return z

def getCameraStill():
    stream = io.BytesIO()
    with PiCamera() as camera:
        camera.resolution=(2592, 1944)
	camera.start_preview()
	time.sleep(5)
        camera.capture(stream, "bmp")
	camera.stop_preview()
    data = np.fromstring(stream.getvalue(), dtype='uint8')
    image = cv2.imdecode(data, 1)
#    data = np.asarray(cv2.imread('temp.bmp'), dtype='uint16')
    data_to_send = np.asarray(image, dtype='uint16')
    return data_to_send

def getData():
    z = getCameraStill()
    return z


def waitForClient(sock):
    connection, address = sock.accept()
    print "sending ", communication.SERVER_READY
    communication.send_msg(connection, communication.SERVER_READY)
    msg = communication.recv_msg(connection)
    print "received ", msg
    return connection

def __init__():
    with open(sys.argv[1]) as f:
        camera_id = f.readline().zfill(2)
    signal.signal(signal.SIGINT, signal_handler)
    print 'starting server ', camera_id
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", pepi_config.port))
    server_socket.listen(5)

    while(run_condition):
        try:
            connection = waitForClient(server_socket)
            print "sending ", camera_id
            communication.send_msg(connection, camera_id)
            print "received ", communication.recv_msg(connection)
            data = getData()
            print "sending image data"
            communication.send_img(connection, data)
            print "closing connection"
            connection.close()
        except:
            print "Server failure, resetting connection"
    server_socket.close()

__init__()
