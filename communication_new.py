import zmq
import msg.pepimessage_pb2 as pepimessage_pb2
import cv2
import numpy as np

class CommunicationSocket:
    _context = zmq.Context()
    socket = None

    def __init__(self, socket_type):
        self.socket = self._context.socket(socket_type=socket_type)

    def bind_to(self, address):
        return self.socket.bind(address)

    def connect_to(self, address):
        return self.socket.connect(address)

    def send(self, message):
        return self.socket.send(message)

    def receive(self):
        return self.socket.recv()

    def send_protobuf(self, protobuf):
        if not isinstance(protobuf, pepimessage_pb2.PepiMessage):
            raise TypeError('CommunicationSocket only supports PepiMessage protobufs, not {}'.format(type(protobuf)))
        return self.send(protobuf.SerializeToString())

    def receive_protobuf(self):
        data = self.receive()
        pb = pepimessage_pb2.PepiMessage()
        pb.ParseFromString(data)
        return pb

    @staticmethod
    def get_new_pepimessage():
        return pepimessage_pb2.PepiMessage()

    @staticmethod
    def encode_image(image, level):
        _, image_data = cv2.imencode('.jpg', image, [cv2.IMWRITE_JPEG_QUALITY, level])
        return image_data.flatten().tostring()

    @staticmethod
    def decode_image(image_data_str):
        return cv2.imdecode(np.fromstring(image_data_str, dtype='uint8'), 1)