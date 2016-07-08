import numpy
import struct

MSGLEN = 512
CLIENT_READY = "client ready"
SERVER_READY = "server ready"
DATA_RECEIVED = "data received"
DATA_READY = "data ready"
DATA_READY_ACK = "data ready ack"
CAMERA_ID_ACK = "camera id ack"


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
    stringData = frame.flatten().tostring()
    print "sending length ", len(stringData)
    send_msg(sock, stringData)


def recv_img(sock):
    stringData = recv_msg(sock)
    print "receiving length ", len(stringData)
    data = numpy.fromstring(stringData, dtype='float64').reshape((500,500))
    return data
