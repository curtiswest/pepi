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


def generate_format_string(values_to_pack):
    """
    Generates a format string used for packing strings, ints and long into strings with the `struct` module.

    Args:
        values_to_pack: a list containing ints, long or strings to generate the format string for

    Returns:
        str: the format string
    """
    format_string = '>'
    if not isinstance(values_to_pack, (list,tuple)):
        values_to_pack = [values_to_pack]

    for value in values_to_pack:
        if isinstance(value, str):
            format_string += (str(len(value)) + 's')
        elif isinstance(value, (int,long)):
            format_string += 'L'
        else:
            raise ValueError('Format strings can only be generated for int, long and string types.')
    return format_string

def send_command(sock, command, values=None):
    """
    Sends a command as a binary-packed string over the given socket with the given optional values.

    Args:
        sock (socket): the socket over which the command will be sent
        command (int): a one-dimension list or tuple of int values associated with the command.
        values ([int or long or str]): the values to send along with the `command`. `Values` must be a single-dimension
            list or tuple with each element being one of the following types: int, long, string. Defaults to None.

    Returns:
        None: on success

    Raises:
        ValueError: when at least one of the elements of `values` is not of type int, long, string or when it is
            multi-dimensional (e.g. a list) and therefore cannot be packed.
        SocketError: when an error occurs during transmission over the socket. An unspecified amount of data may have
            been sent over the socket before the error is raised.
    """
    def _check_types_of(_values):
        if not all(isinstance(x, (int, long, str)) for x in _values):
            raise ValueError('{} contains an element that is a not of type int, long, or string '.format(_values) +
                             'or alternatively is a list or tuple. The list of values must take that format.')

    values_to_pack = [command]
    if values is not None:
        if not isinstance(values, (list, tuple)):
            values = [values] # Must be in a list before checking and packing
        _check_types_of(values)
        values_to_pack.extend(values)

    try:
        # The packed data being sent to the send_msg function is a binary-packed string of the format:
        #   fmt_string_len : 4 bytes representing length (z bytes) of the format string to unpack
        #   fmt_string: z bytes containing the format string to unpack the rest of the message
        #   remaining message: remaining bytes up to msg_len, unpacked with the format_string where:
        #       cmd: the first element in the unpacked message i.e. [0]
        #       values: the remaining elements in the unpacked message i.e. [1:]
        fmt_string = generate_format_string(values_to_pack)
        values_to_pack = [fmt_string] + values_to_pack
        values_to_pack = [len(fmt_string)] + values_to_pack
        fmt_string = generate_format_string(values_to_pack)
        packed_data = struct.pack(fmt_string, *values_to_pack)
        send_msg(sock, packed_data)
    except:
        raise

def recv_command(sock, msg_len=None):
    """
    Receives a command and any associated values over the `socket`.

    Args:
        sock: the socket over which the command will be received
        msg_len: the length of the message to receive in bytes. Defaults to None, in which case the function will call
            wait_for_msg on this socket to retrieve a message length (which will make this function block).

    Returns:
        (cmd (int), values ([])): a tuple where the first element is the received command, and the second is
            a list of values (of type int, long, or string) received, if any.

    Raises:
        SocketError: when an error occurs while receiving the packed message
        struct.error: when an error occurs during unpacked the message, presumably because it has been encoding incorrectly
            or corrupted at some stage.
    """
    # If not given a message length, then wait for an incoming message
    if msg_len is None:
        msg_len = wait_for_msg(sock)

    # Now, retrieve remaining message of length msg_len
    packed_msg = recvall(sock, msg_len)
    if packed_msg is None:
        raise SocketError('Reached end of socket ')

    try:
        # Recall that a command message is a binary-packed string of the format:
        #   msg_len : 4 bytes
        #   fmt_string_len : 4 bytes representing length (z bytes) of the format string to unpack
        #   fmt_string: z bytes containing the format string to unpack the rest of the message
        #   remaining message: remaining bytes up to msg_len, unpacked with the format_string where:
        #       cmd: the first element in the unpacked message i.e. [0]
        #       values: the remaining elements in the unpacked message i.e. [1:]
        # As such, it is necessary to step through the received message and pull out each of the above in order.
        fmt_string_len = struct.unpack('>L', packed_msg[0:4])[0]
        packed_msg = packed_msg[4:]  # Move forward
        fmt_string = struct.unpack('>' + str(fmt_string_len) + 's', packed_msg[:fmt_string_len])[0]
        packed_msg = packed_msg[fmt_string_len:]
        unpacked_msg = struct.unpack(fmt_string, packed_msg)
        cmd = unpacked_msg[0]
        values = unpacked_msg[1:]
    except:
        raise
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

    Args:
        sock (socket): the socket to transfer over
        frame (cv2.image): the image to transfer in OpenCV2 image format, i.e. a BGR array
        compressed_transfer (bool): whether to compress during transfer
        level (int):  what level of compression to use, 0-100 (highest) for JPG or 0-9 (smaller file, longer) for PNG

    Returns:
        None: on success
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
    """
    Receives an image over the given socket and decodes it into an OpenCV2 style image (i.e. a BGR array)

    Args:
        sock(socket): the socket over which to receive the image

    Returns:
        [[int, int, int]]: the BGR array holding the OpenCV2 image
    """
    # Receive image string and decode into an Image
    img_data_str = recv_msg(sock)
    print 'Received image of length: ', len(img_data_str)
    image_data = cv2.imdecode(np.fromstring(img_data_str, dtype='uint8'), 1)
    return image_data
