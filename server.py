import socket
import communication
import time
import cv2
import numpy as np
from picamera import PiCamera
import sys
import signal
import io
import pepi_config

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
    camera = PiCamera()
    try:
        camera.resolution = (2592, 1944)
        camera.start_preview()
        time.sleep(5)
        camera.capture(stream, "bmp")
        camera.stop_preview()
        data = np.fromstring(stream.getvalue(), dtype='uint8')
        image = cv2.imdecode(data, 1)
        #    data = np.asarray(cv2.imread('temp.bmp'), dtype='uint16')
        data_to_send = np.asarray(image, dtype='uint16')
    finally:
        camera.close()
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


def getServerID():
    # Extract serial from the cpuinfo file as the server ID
    serial = '0000000000000000'
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6]=='Serial':
                serial = line[10:26]
        f.close()
    except:
        serial='ERROR00000000000'
    return serial


def __init__():
    camera_id = getServerID().zfill(16)
    print "GOT CAMERA ID: " + camera_id
    signal.signal(signal.SIGINT, signal_handler)
    print 'starting server ', camera_id
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("", pepi_config.port))
    server_socket.listen(5)

    while run_condition:
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
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            print "Server failure, resetting connection"
    server_socket.close()


__init__()