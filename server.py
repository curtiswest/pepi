#!/usr/bin/python
import socket
import communication
import time
import numpy as np
from picamera import PiCamera
from picamera.array import PiRGBArray
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


def getCameraStill(resolution=(2592, 1944)):
    startTime = 0
    with PiCamera() as camera:
        try:
            print 'Camera warming up..'
            camera.resolution = resolution
            camera.start_preview()
            time.sleep(3)
            startTime = time.time()
            print 'Camera warmed. Capturing..'
            with PiRGBArray(camera) as rawCapture:
                camera.capture(rawCapture, format='bgr')
                image = rawCapture.array
        finally:
            camera.close()
            print 'Active capture time: ' + str(round((time.time() - startTime), 4)) + 'seconds'
    return image


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
    # noinspection PyBroadException
    try:
        f = open('/proc/cpuinfo', 'r')
        for line in f:
            if line[0:6] == 'Serial':
                serial = line[10:26]
        f.close()
    except:
        serial = 'ERROR00000000000'
    return serial


def __init__():
    camera_id = getServerID().zfill(16)
    signal.signal(signal.SIGINT, signal_handler)
    print 'starting server ', camera_id

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Avoids TCP timeout waiting on crash
    server_socket.bind(("", pepi_config.port))
    server_socket.listen(5)

    while run_condition:
        try:
            connection = waitForClient(server_socket)

            print "sending ", camera_id
            communication.send_msg(connection, camera_id)

            print "received ", communication.recv_msg(connection)

            data = getCameraStill()
            print "sending image data"
            communication.send_img(connection, data, compressed_transfer=True, level=3)

            print "closing connection"
            connection.close()
        except Exception as e:
            if hasattr(e, 'message'):
                print(e.message)
            print "Server failure, resetting connection"
    server_socket.close()


__init__()
