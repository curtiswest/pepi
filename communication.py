import numpy
import struct

MSGLEN = 512
CLIENT_READY = "client ready"
SERVER_READY = "server ready"
DATA_RECEIVED = "data received"
DATA_READY = "data ready"
DATA_READY_ACK = "data ready ack"
CAMERA_ID_ACK = "camera id ack"
IMG_SIZE_ACK = "image size ack"


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def send_img(sock, frame):
    img_size_str = numpy.asarray(frame.shape, dtype="uint16").tostring()
    print "sending img_size_str", frame.shape
    send_msg(sock, img_size_str)
    #wait for data size ack
    msg = recv_msg(sock)
    print "rceived ", msg
    img_data_str = frame.flatten().tostring()
    print "sending length ", len(img_data_str)
    send_msg(sock, img_data_str)


def recv_img(sock):
    img_size_str = recv_msg(sock)
    print "received img_size_str"
    img_size = tuple(numpy.fromstring(img_size_str, dtype='uint16'))
    print "image size ", img_size
    print "sending ", IMG_SIZE_ACK
    send_msg(sock, IMG_SIZE_ACK)
    img_data_str = recv_msg(sock)
    print "received img_data_str"
    img_data = numpy.fromstring(img_data_str, dtype='uint16').reshape(img_size)
    return img_data
