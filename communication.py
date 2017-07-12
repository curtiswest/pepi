import zmq
import cv2
import msg.pepimessage_pb2 as ppmsg
import numpy as np
import google.protobuf


class CommunicationSocket:
    _context = zmq.Context()
    _socket = None
    _type = None

    class SocketTypes:
        """
            Indicates the type of CommunicationSocket this instance is and therefore which messages are associated
            with the send() and receive() functions.
        """
        SERVER = zmq.REP
        CLIENT = zmq.REQ

    class MessageTypeError(Exception):
        pass

    class ServerTypeError(Exception):
        pass

    def __init__(self, socket_type):
        self._type = socket_type
        self._socket = self._context.socket(socket_type=socket_type)

    def bind_to(self, address):
        """
        Binds this socket to the given address. Typically used on the server-side, although in practical terms there is
        little difference between bind_to() and connect_to()

        Args:
            address (str): the address string to bind to. Format is "protocol://interface:port" e.g. "tcp://*:10000".
                See ZMQ's bind() function for more details on the format of the address string.
        """
        return self._socket.bind(address)

    def connect_to(self, address):
        """
        Connects to a socket at the given address. Typically used on client-side, although in practical terms there is
        little difference between connect_to() and bind_to().

        Args:
            address: the address string to bind to. Format is "protocol://interface:port" e.g. "tcp://*:10000".
                See ZMQ's bind(addr) function for more details on the format of the address string.
        """
        return self._socket.connect(address)

    def _send_raw(self, message):
        return self._socket.send(message)

    def _receive_raw(self):
        return self._socket.recv()

    def send(self, command, int_values=None, string_values=None, image_data=None, server_id=None):
        # type: (str, list[int], list[str], str, str) -> object
        """
        Sends the given command and values on the wire that this socket is connected to.

        Note: only zero or one of int_values, string_values and image_data can be specified, as the underlying
        implementation only supports sending one of these over the wire. If image_data is specified, server_id must
        also be specified or a TypeError will be raised.

        Args:
            command (int): a command as given in pepimessage_pb2, e.g. pepimessage_pb2.GET_SERVER_ID
            int_values ([int]): a list of integer values associated with the command, if needed
            string_values ([str]): a list of string values associated with the command, if needed
            image_data (str): a image data string, if needed
            server_id (str): the ID of the server sending the image data, if needed

        Raises:
            ValueError: when command is None, or when a server_id or image_data is specified with the other
            counterpart set to None.
            ServerTypeError: when a Client-type socket attempts to send a message or value that only a Server-type
            socket is capable of.
            MessageTypeError: when attempting to send more than 1 of the following: int_values, string_values or
            image_data.

        """

        def wrap_to_list(values):
            return values if isinstance(values, list) else [values]

        # Check given appropriate parameters
        if bool(int_values) + bool(string_values) + bool(image_data) > 1:
            raise self.MessageTypeError('Given {} of 3 value parameters, but can only handle <=1 per call'.format(
                bool(int_values) + bool(string_values) + bool(image_data)))
        if command is None:
            raise ValueError('Command cannot be None')

        # Generate and load the message depending on what type of socket this is
        if self._type == self.SocketTypes.SERVER:
            msg = ppmsg.Reply()
            # Servers may send image data, so need to load in here
            if image_data is not None or server_id is not None:
                if bool(image_data) ^ bool(server_id):
                    # One is set but not the other which is invalid
                    raise ValueError('Server_id and image_data must be sent together as per the message protocol.'
                                     'One of these two was not provided in this function call.')
                msg.image.img_data_str = image_data
                msg.image.server_id = server_id
        elif self._type == self.SocketTypes.CLIENT:
            msg = ppmsg.Request()
            if image_data is not None or server_id is not None:
                raise self.ServerTypeError('Attempting to send image data from a client-type server')
        else:
            msg = None

        msg.command = command
        if int_values is not None:
            msg.int_values.values.extend(wrap_to_list(int_values))
        elif string_values is not None:
            msg.string_values.values.extend(wrap_to_list(string_values))

        # Send the reply
        try:
            return self._send_raw(msg.SerializeToString())
        except:
            raise

    def close(self):
        self._socket.close()
        self._context.term()

    def receive(self):
        # type: () -> (int, list[int], list[str], str, str)
        """
        Receives a command message over the wire and returns the values extracted from it.
        Returns:
            message (int, [int], [str], str, str): a tuple containing any values received from in the
            message in the form of (command, int_values, str_values, img_data_str, server_id). Note that the same
            restrictions as sending a message still apply and so several of these values may be None or empty lists.

        """

        def unwrap_to_list(item):
            if isinstance(item, google.protobuf.internal.containers.RepeatedScalarFieldContainer):
                if len(item) > 0:
                    conv_type = int if isinstance(item[0], int) else str
                    return [conv_type(i) for i in item]
                else:
                    return None
            elif isinstance(item, list):
                return item
            else:
                return [item]

        data = self._receive_raw()
        try:
            if self._type == self.SocketTypes.SERVER:
                # Reconstruct a request message
                pb = ppmsg.Request()
                pb.ParseFromString(data)
                return pb.command, pb.int_values, pb.string_values
            elif self._type == self.SocketTypes.CLIENT:
                pb = ppmsg.Reply()
                pb.ParseFromString(data)

                int_out = unwrap_to_list(pb.int_values.values)
                str_out = unwrap_to_list(pb.string_values.values)
                img_data_str_out = pb.image.img_data_str
                server_id_out = pb.image.server_id
                return pb.command, int_out, str_out, img_data_str_out, server_id_out
        except:
            raise

    @staticmethod
    def encode_image(image, compressed=True, level=90):
        if compressed:
            _, image_data = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, level])
        else:
            _, image_data = cv2.imencode('.png', image, [cv2.IMWRITE_PNG_COMPRESSION, level])
        return image_data.flatten().tostring()

    @staticmethod
    def decode_image(image_data_str):
        return cv2.imdecode(np.fromstring(image_data_str, dtype='uint8'), 1)
