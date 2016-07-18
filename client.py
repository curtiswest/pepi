#!/usr/bin/python
# TCP client example

import socket
import communication
import datetime
import cv2

def getTimeStamp():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')
    return timestamp

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 10006))

#receive SERVER_READY
msg = communication.recv_msg(client_socket)
print "received ", msg
#send CLIENT_READY
print "sending ", communication.CLIENT_READY
communication.send_msg(client_socket, communication.CLIENT_READY)
#communication.send_msg(client_socket, communication.DATA_READY_ACK)
#receive CAMERA_ID
camera_id = communication.recv_msg(client_socket)
print "received ", camera_id
#send CAMERA_ID_ACK
print "sending ", communication.CAMERA_ID_ACK
communication.send_msg(client_socket, communication.CAMERA_ID_ACK)
fname = getTimeStamp() + "-" + camera_id
img = communication.recv_img(client_socket)
print "received image data"
cv2.imwrite("%s.bmp"%fname, img)
print "closing connection"
client_socket.close()
