import numpy as np
import struct
import cv2
import socket
import binascii

MSGLEN = 512
CLIENT_READY = "client ready"
SERVER_READY = "server ready"
DATA_RECEIVED = "data received"
DATA_READY = "data ready"
DATA_READY_ACK = "data ready ack"
CAMERA_ID_ACK = "camera id ack"
IMG_SIZE_ACK = "image size ack"

class SocketError(Exception):
    pass

def wait_for_msg(sock):
    """
    Waits for a message on the socket indicated by the presence of at least 4 bytes on available on the socket. Those
    four bytes are decoded into the

    Caution: this is a blocking function which will wait only return on socket disconnect or when 4 bytes are received.

    Args:
        sock: the socket on which to wait for a message

    Returns:
        the length of the message incoming message in bytes
    Raises:
        SocketError: when connection is lost/closed on the socket while waiting for a message
    """
    try:
        raw_msg_len = recvall(sock, 4)  # Get first 4 bytes (length of remaining message)
        msg_len = struct.unpack('>L', raw_msg_len)[0]  # Unpack to get real message length
        return msg_len
    except:
        raise


def send_command(sock, command, values=None):
    """
    Sends a command as a binary-packed string over the given socket with the given optional values.

    Args:
        sock (socket): the socket over which the command will be sent
        command (int): a one-dimension list or tuple of int values associated with the command.
        values ([int]): the values to send with the `command`. `Values` must be a single-dimension list or tuple
            with each element of type int. Defaults to None.

    Returns:
        None: on success
    Raises:
        ValueError: when at least one of the elements of `values` is not an `int` (including when a multi-dimensional
            `values` are passed).
        socket.error: when an error occurs during transmission over the socket. An unspecified amount of data may have
            been sent over the socket before the error is raised.
    """
    fmt_string = '>L' + 'L'*len(values)  # Command, and the actual values tuples
    values_to_pack = [command]
    values_to_pack.extend(values)
    for value in values_to_pack:
        # Ensure values_to_pack only contains ints before packing
        if not isinstance(value, (int, long)):
            raise ValueError('A provided value ({} from {}) is not convertible to an int.'.format(value, values))
    packed_data = struct.pack(fmt_string, *values_to_pack)
    try:
        send_msg(sock, packed_data)
    except:
        raise

def recv_command(sock, msg_len=None):
    if msg_len is None:
        msg_len = wait_for_msg(sock)

    # Now, retrieve the message's command and values tuple
    packed_msg = recvall(sock, msg_len)
    if packed_msg is None:
        raise SocketError('Reached end of socket ')
    unpacked_msg = struct.unpack('>'+'L'*(msg_len/4), packed_msg)
    cmd = unpacked_msg[0]
    values = unpacked_msg[1:]
    return (cmd, values)


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    msg = struct.pack('>L', len(msg)) + msg
    try:
        sock.sendall(msg)
    except:
        raise SocketError('Error when sending message (b"{}")'.format(binascii.hexlify(msg)))

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        raise SocketError('Socket error occurred when receiving message')
    msglen = struct.unpack('>L', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        try:
            packet = sock.recv(n - len(data))
            if not packet:
                raise SocketError('Socket error occurred using recvall to receive message of length {} bytes.'.format(n))
            data += packet
        except socket.error:
            raise SocketError('Socket error occurred using recvall to receive message of length {} bytes.'.format(n))
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
    image_data = cv2.imdecode(np.fromstring(img_data_str, dtype='uint8'), 1)
    return image_data
