#!/usr/bin/python
# TCP client example

import socket
import communication
import datetime
import time
import cv2
import os
from multiprocessing import Process

#args is a list of tuple
def run_parallel(func, args):
  proc = []
  for arg in args:
    p = Process(target=func, args=arg)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()

def get_time_stamp():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')
    return timestamp

def get_ip_list():
    with open("active_cameras.txt", "r") as f:
        active_ip = [l.strip() for l in f]
    return active_ip

def run(ip, port, output_dir):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))    
    #receive SERVER_READY
    msg = communication.recv_msg(client_socket)
    print "received ", msg
    #send CLIENT_READY
    print "sending ", communication.CLIENT_READY
    communication.send_msg(client_socket, communication.CLIENT_READY)
    #communication.send_msg(client_socket, communication.DATA_READY_ACK)
    #receive CAMERA_ID
    camera_id = communication.recv_msg(client_socket)
    camera_id = str(int(camera_id)).zfill(2) #add leading zeros
    print "received ", camera_id
    #send CAMERA_ID_ACK
    print "sending ", communication.CAMERA_ID_ACK
    communication.send_msg(client_socket, communication.CAMERA_ID_ACK)
    fname = output_dir + '/' + str(camera_id)
    img = communication.recv_img(client_socket)
    print "received image data"
    cv2.imwrite("%s.bmp"%fname, img)
    print "closing connection"
    client_socket.close()

def test_run(ip, port):
    print "Opening socket on ip %s port %s"%(ip, port)
    time.sleep(5)
    print "closing socket on ip %s port %s"%(ip, port)

def __init__():
    dir = "images/"+get_time_stamp()
    if not os.path.exists(dir):
        os.makedirs(dir)
    ips = get_ip_list()
    args = [(ip, pepi_config.port, dir) for ip in ips]
    print "Running parallel connections"
    run_parallel(run, args)

__init__()