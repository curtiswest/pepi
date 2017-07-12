#!/usr/local/opt/pyenv/shims/python
# TCP client example

import datetime
import time
import cv2
import os
from multiprocessing import Process
import pepi_config
import communication as comm


# args is a list of tuple
def run_parallel(func, args):
    processes = []
    for arg in args:
        p = Process(target=func, args=arg)
        p.start()
        processes.append(p)
    for p in processes:
        p.join()


def get_time_stamp():
    timestamp = datetime.datetime.strftime(datetime.datetime.now(), '%Y%m%d%H%M%S')
    return timestamp


def get_ip_list():
    with open("active_cameras.txt", "r") as f:
        active_ip = [l.strip() for l in f]
    return active_ip


def run(ip, port, output_dir):
    c = comm.CommunicationSocket(comm.CommunicationSocket.SocketTypes.CLIENT)
    addr = "tcp://{}:{}".format(ip, port)
    print('Connecting to {}'.format(addr))
    c.connect_to(addr)

    c.send(comm.ppmsg.GET_STILL)
    # c.send(comm.ppmsg.GET_SERVER_ID)
    (cmd, int_list, str_list, img_data_str, server_id) = c.receive()

    if cmd != comm.ppmsg.COMMAND_FAILURE:
        if cmd == comm.ppmsg.GET_STILL:
            img = comm.CommunicationSocket.decode_image(img_data_str)
            filename = output_dir + '/' + server_id
            cv2.imwrite('%s.png' % filename, img)  # Always write to PNG as lossless
        elif cmd == comm.ppmsg.GET_SERVER_ID:
            print('Got server ID: {}'.format(str_list[0]))
        elif cmd == comm.ppmsg.SET_SERVER_ID:
            print('Server ID successfully updated')
        else:
            pass
    else:
        print('Command failure')


def test_run(ip, port):
    print "Opening socket on ip %s port %s" % (ip, port)
    time.sleep(5)
    print "closing socket on ip %s port %s" % (ip, port)


def __init__():
    image_dir = "images/" + get_time_stamp()
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    ips = get_ip_list()
    args = [(ip, pepi_config.port, image_dir) for ip in ips]
    print "Running parallel connections"
    run_parallel(run, args)


__init__()
