import socket
import communication
import time
import cv2
import numpy as np
from picamera import PiCamera
import sys
import signal

run_condition = True

def signal_handler(signal, frame):
        print('Exiting...')
        global run_condition
        run_condition = False
        sys.exit(0)

def generateRandomImg():
    z = np.random.random((500, 500))  # Test data
    print z.dtype
    return z

def getCameraStill():
    with PiCamera() as camera:
        camera.resolution= (500,500)
        camera.capture('temp.bmp')
    data = np.asarray(cv2.imread('temp.bmp'), dtype='uint16')
    return data

def getData():
    z = getCameraStill()
    return z


def waitForClient(sock):
    connection, address = sock.accept()
    #send SERVER_READY
    print "sending ", communication.SERVER_READY
    communication.send_msg(connection, communication.SERVER_READY)
    #receive CLIENT_READY
    msg = communication.recv_msg(connection)
    print "received ", msg
    return connection

camera_id = sys.argv[1].zfill(2)
signal.signal(signal.SIGINT, signal_handler)
print 'starting server ', camera_id
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("", 10006))
server_socket.listen(5)

while(run_condition):
    try:
        connection = waitForClient(server_socket)
        #send camera id
        print "sending ", camera_id
        communication.send_msg(connection, camera_id)
        #receive CAMERA_ID_ACK
        print "received ", communication.recv_msg(connection)
        data = getData()
        print "sending image data"
        communication.send_img(connection, data)
        print "closing connection"
        connection.close()
    except:
        print "Server failure, resetting connection"
server_socket.close()

