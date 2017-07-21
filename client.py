#!/usr/local/opt/pyenv/shims/python
# TCP client example

import datetime
import time
import cv2
import os
from multiprocessing import Process
import pepi_config
import communication as comm
from stoppablethread import StoppableLoopingThread
import numpy as np

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

total_data_len = 0
# player = None
lastest_frame = None

def run(ip, port, stream_port, output_dir):
    c = comm.CommunicationSocket(comm.CommunicationSocket.SocketTypes.CLIENT)
    addr = "tcp://{}:{}".format(ip, port)
    c.connect_to(addr)
    print('Connecting to {}'.format(addr))

    s = comm.CommunicationSocket(comm.CommunicationSocket.SocketTypes.SUBSCRIBER)
    addr = "tcp://{}:{}".format(ip, stream_port)
    s.connect_to(addr)
    s.subscribe() # Subscribe to all messages


    # c.send(comm.ppmsg.SET_RESOLUTION, int_values=pepi_config.RESOLUTION_MAX)
    # c.receive()

    for i in range(0, 1):
        start = time.time()
        #Send Message
        # c.send(comm.ppmsg.GET_STILL)
        c.send_old(comm.ppmsg.START_STREAM)
        # c.send(comm.ppmsg.GET_ZOOM)
        # c.send(comm.ppmsg.SET_ISO, int_values=1000)
        # c.send(comm.ppmsg.GET_SHUTTER_SPEED)
        # c.send(comm.ppmsg.SET_RESOLUTION, string_values='LOL')
        # c.send(comm.ppmsg.SET_SHUTTER_SPEED, int_values=1)

        # Receive message
        (cmd, int_list, flt_list, str_list, img_data_str, server_id) = c.receive_old()

        if cmd != comm.ppmsg.COMMAND_FAILURE:
            if cmd == comm.ppmsg.GET_STILL:
                img = comm.CommunicationSocket.decode_image(img_data_str)
                filename = output_dir + '/' + str(i) + '_' + server_id
                cv2.imwrite('%s.png' % filename, img)  # Always write to PNG as lossless
                new_img = cv2.imread('%s.png' % filename)
                # cv2.imshow('Image Window', new_img)
                # print(type(new_img))
                # cv2.waitKey(0)
            elif cmd == comm.ppmsg.GET_SERVER_ID:
                # print('Got server ID: {}'.format(str_list[0]))
                pass
            elif cmd == comm.ppmsg.SET_SERVER_ID:
                print('Server ID successfully updated')
            elif cmd == comm.ppmsg.START_STREAM:
                print('Stream starting')


                def sub_func(socket):
                    data = socket.listen()
                    global total_data_len
                    total_data_len += len(data)
                    print(len(data))

                    global latest_frame
                    latest_frame = data
                    # img = comm.CommunicationSocket.decode_image(data)
                    # latest_frame = data

                    # global player
                    # player.stdin.write(data)


                start = time.time()

                # Video streaming demo
                # cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
                # cmdline = ['/Applications/VLC.app/Contents/MacOS/VLC', '--demux', 'h264', '-']
                # global player
                # player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)

                sub_thread = StoppableLoopingThread(target=sub_func, args=(s,))
                sub_thread.start()
                print('Subscribing to {}'.format(addr))
                start_time = time.time()
                while time.time() - start_time < 15:
                    print(len(latest_frame))
                    if lastest_frame:
                        img = cv2.imdecode(np.fromstring(data, dtype='uint8'), 1)
                        cv2.imshow('Image Window', img)
                        cv2.waitKey(0)

                        # if not sub_thread.is_stopped():
                        #     sub_thread.stop()
                        #     break
                    time.sleep(0.1)


                sub_thread.join(15)
                delta = time.time() - start
                # player.terminate()

                print('Received {} bytes in {} sec: {}bytes/sec'.format(total_data_len, delta, (total_data_len/delta)))
                c.send_old(comm.ppmsg.STOP_STREAM)
                c.receive_old()
            else:
                print('CMD: {}'.format(cmd))
                print('int: {}'.format(int_list))
                print('flt: {}'.format(flt_list))
                print('str: {}'.format(str_list))
                print('imd: {}'.format(len(img_data_str)))
                print('Got unknown command response')
        else:
            print('Command failure ({})'.format(str_list[0] if str_list else 'no reason given'))
        print 'Took: {} sec'.format(time.time()-start)

def test_run(ip, port):
    print "Opening socket on ip %s port %s" % (ip, port)
    time.sleep(5)
    print "closing socket on ip %s port %s" % (ip, port)



def __init__():

    image_dir = "images/" + get_time_stamp()
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    ips = get_ip_list()
    args = [(ip, pepi_config.PORT, pepi_config.STREAM_PORT, image_dir) for ip in ips]
    print "Running parallel connections"
    run_parallel(run, args)


__init__()
