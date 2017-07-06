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
    """
    Sends an image (frame) over the given socket, compressed as JPG by default.

    If using specifying non-standard compression parameters, or the use of uncompressed
    transfers, take special note of the compression levels. By default, JPG compression
    at 90 out of 100 is used which is satisfactory for most cases. However, you may
    use any value between 0 and 100 at the detriment of quality or transfer speed.

    Uncompressed images (i.e. compress_transfer=False) use PNG lossless compression. This
    still uses a compression level between 0 and 9, but instead refers to the time taken
    to compress, with 0 being fast compression, larger file and 9 longer time, smaller
    file.

    :param sock: the transfer socket
    :param frame: the image to transfer (OpenCV2 image, i.e. BGR array)
    :param compressed_transfer: whether to compress during transfer
    :param level: what level of compression to use, 0-100 (highest) for JPG or 0-9 (smaller file, longer) for PNG
    """
    image_data = None
    if compressed_transfer:
        # Compress the image using OpenCV JPG
        if 0 <= level <= 100:
            _, image_data = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, level])
        else:
            raise ValueError('JPG compression level must be between 0 and 100')
    else:
        # Encode to lossless PNG
        if 0 <= level <= 9:
            _, image_data = cv2.imencode('.png', frame, [cv2.IMWRITE_PNG_COMPRESSION, level])
        else:
            raise ValueError('PNG compression level must be between 0 and 9')

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
