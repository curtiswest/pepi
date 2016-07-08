#!/usr/bin/python
# TCP client example

import socket
import communication
import datetime
import matplotlib.pyplot as plt

def getTimeStamp():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')
    return timestamp

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("localhost", 10000))
#receive SERVER_READY
msg = communication.recv_msg(client_socket)
print "received ", msg
communication.send_msg(client_socket, communication.CLIENT_READY)

communication.send_msg(client_socket, communication.DATA_READY_ACK)
camera_id = communication.recv_msg(client_socket)
communication.send_msg(client_socket, communication.CAMERA_ID_ACK)
fname = getTimeStamp() + "-" + camera_id
img = communication.recv_img(client_socket)
plt.imshow(img)
plt.show()
client_socket.close()
