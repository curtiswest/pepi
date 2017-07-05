import numpy
import struct
import cv2

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


def send_img(sock, frame, compressed_transfer=True, level=90):
    if compressed_transfer:
        # Compress the image using OpenCV JPG
        print 'Image size pre : %10i' % frame.size
        _, image_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, level])
        print 'Image size post: %10i' % image_data.size
    else:
        # Encode to lossless PNG
        _, image_data = cv2.imencode('.png', frame, [cv2.IMWRITE_PNG_COMPRESSION, level])

    # Transform into string for transfer
    img_data_str = image_data.flatten().tostring()
    print 'Sending image of length: ', len(img_data_str)
    send_msg(sock, img_data_str)


def recv_img(sock):
    # Receive image string and decode into an Image
    img_data_str = recv_msg(sock)
    print 'Received image of length: ', len(img_data_str)
    image_data = cv2.imdecode(numpy.fromstring(img_data_str, dtype='uint8'), 1)
    return image_data
