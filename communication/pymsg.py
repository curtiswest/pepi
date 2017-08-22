"""
Pymsg.py: Provides the ProtobufMessageWrapper abstract class to wrap around Google's generated Protobuf messages,
along with concrete implementations for the messages used for the Pepi system.
"""
import logging
import json

from abc import ABCMeta, abstractmethod
from future.utils import viewitems
import google.protobuf.message

import pepimessage_pb2 as ppmsg

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.2'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'

logger = logging.getLogger(__name__)

class ProtobufMessageWrapper(object):
    """
    An abstract class defining how a Protobuf message should be wrapped as a Python object.
    """
    __metaclass__ = ABCMeta

    class DecodeError(Exception):
        """
        Indicates that the given serial string could not be decoded into its backing Protobuf.
        """
        pass

    class EncodeError(Exception):
        """
        Indicates that the given message cannot be encoded into the backing Protobuf, probably because of a type
        mis-match between the object and the Protobuf message declaration (.proto).
        """
        pass

    class MessageTypeError(Exception):
        """
        Indicates that an operation was being performed on unsupported message type (e.g. trying to unwrap a message
        that has not been implemented in the unwrapping method)
        """
        pass

    @abstractmethod
    def __init__(self):
        pass

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return str(self.protobuf())

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        """
        pass

    def serialize(self):
        # type: () -> str
        """
        Serialises this message's Protobuf for transmission over a wire.
        Returns:
            str: this message serialized
        """
        return self.protobuf().SerializeToString()

    def wrap(self):
        # type: () -> WrapperMessage
        """
        Wraps this protobuf message in a WrapperMessage.
        Returns:
            WrapperMessage: this message wrapped
        """
        # noinspection PyCallByClass
        return WrapperMessage.wrap(self)


class WrapperMessage(ProtobufMessageWrapper):
    """
    Encapsulates an WrapperMessage .proto message.
    """

    # noinspection PyMissingConstructor
    def __init__(self, protobuf):
        """
        Initialises a WrapperMessage from the given WrapperMessage Protobuf.
        Args:
            protobuf: the WrapperMessage protobuf to initialise the class on.
        Throws:
            MessageTypeError: if given a protobuf that is not a WrapperMessage
        """
        if not isinstance(protobuf, ppmsg.WrapperMessage):
            msg = 'WrapperMessage can only work on WrapperMessage protobufs.' \
                  'Given a protobuf of type: {}'.format(type(protobuf))
            logging.warn(msg)
            raise ProtobufMessageWrapper.MessageTypeError(msg)
        super(WrapperMessage, self).__init__()
        self.pb = protobuf

    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        Returns:
            ppmsg.WrapperMessage: a protobuf of this message
        """
        return self.pb

    # noinspection PyMissingOrEmptyDocstring
    def wrap(self):
        msg = 'A wrap message cannot itself be wrapped - tried to call wrap() on one'
        logging.warn(msg)
        raise NotImplementedError(msg)

    def unwrap(self):
        """
        Unwraps this WrapperMessage and returns the ProtobufMessageWrapper subclass that this WrapperMessage contains.
        Returns:
            ProtobufMessageWrapper: the unwrapped message
        """
        # type: () -> ProtobufMessageWrapper
        set_msg = self.pb.WhichOneof('msg')
        if set_msg == 'ident':
            msg = IdentityMessage(self.pb.ident.ip, self.pb.ident.identifier, self.pb.ident.is_stream)
        elif set_msg == 'control':
            pb = self.pb.control
            setting = pb.setting
            payload = dict(pb.payload)
            msg = ControlMessage(setting=setting, payload=payload)
        elif set_msg == 'data':
            pb = self.pb.data
            data_code = pb.data_code
            data_string = pb.data_string
            data_bytes = pb.data_bytes
            msg = DataMessage(data_code=data_code, data_string=data_string, data_bytes=data_bytes)
        elif set_msg == 'inproc':
            msg = InprocMessage.from_protobuf(self.pb.inproc)
            # pb = self.pb.inproc
            # msg = InprocMessage(pb.msg_req, pb.server_id)
        else: # pragma: no cover
            msg = 'The Protobuf that unwrap() is working on contains an unknown field in the Oneof ' \
                  'field. Specifically, unwrap() cannot handle the field ({}).'.format(set_msg)
            logging.warn(msg)
            raise NotImplementedError(msg)
        return msg

    # noinspection PyMethodOverriding
    @classmethod
    def wrap(cls, message):
        # type: (ProtobufMessageWrapper) -> WrapperMessage
        """
        Wraps the given ProtobufMessageWrapper object inside of a WrapperMessage object.
        Currently supports wrapping IdentityMessage, ControlMessage and DataMessage classes.
        Args:
            message: a ProtobufMessageWrapper subclass to wrap
        Returns:
            WrapperMessage: the wrapped message
        Raises:
            MessageTypeError: when given a `message` that cannot be handled or is of the wrong type
        """
        def _ingest_message(destination, source, has_dict_type=False):
            protobuf = source.protobuf()
            for descriptor in protobuf.DESCRIPTOR.fields:
                if has_dict_type:
                    try:
                        setattr(destination, descriptor.name, getattr(protobuf, descriptor.name))
                    except AttributeError:
                        # Might be a dictionary type
                        pb_dict = getattr(protobuf, descriptor.name)
                        for key, value in viewitems(pb_dict):
                            getattr(destination, descriptor.name)[key] = value
                else:
                    setattr(destination, descriptor.name, getattr(protobuf, descriptor.name))

        pb = ppmsg.WrapperMessage()
        if isinstance(message, IdentityMessage):
            _ingest_message(pb.ident, message)
        elif isinstance(message, ControlMessage):
            _ingest_message(pb.control, message, has_dict_type=True)
        elif isinstance(message, DataMessage):
            _ingest_message(pb.data, message)
        elif isinstance(message, InprocMessage):
            _ingest_message(pb.inproc, message)
        else: # pragma: no cover
            raise ProtobufMessageWrapper.MessageTypeError('Cannot handle message of type {}'.format(type(message)))

        logging.debug('wrap() ingested protobuf as: {}'.format(pb))
        return cls(pb)

    @classmethod
    def from_serialized_string(cls, string):
        """
        Initializes a WrapperMessage from a serialized string.
        Args:
            string: the serialized string.

        Returns:
            WrapperMessage: the deserialized object.
        Raises:
            DecodeError: when given a string that cannot be parsed into a Protobuf
        """
        # type: (str) -> WrapperMessage
        pb = ppmsg.WrapperMessage()
        try:
            pb.ParseFromString(string)
        except google.protobuf.message.DecodeError as e: # pragma: no cover
            msg = 'Given string cannot be decoded. Error: {}'.format(e.message)
            logging.warn(msg)
            raise ProtobufMessageWrapper.DecodeError(msg)
        return cls(pb)


class IdentityMessage(ProtobufMessageWrapper):
    """
    Encapsulates an IdentityMessage .proto message.
    """
    # noinspection PyMissingConstructor
    def __init__(self, ip, identifier, is_stream=False):
        """
        Initialises a IdentityMessage with the given `ip` and `identifier`.
        Args:
            ip (str): the ip for the message
            identifier: the identifier for the message
        """
        if ip is None or ip == '':
            raise ValueError('IP cannot be None nor empty')
        if identifier is None or identifier == '':
            raise ValueError('Identifier cannot be None nor empty')
        super(IdentityMessage, self).__init__()
        self.ip = ip
        self.identifier = identifier
        self.is_stream = bool(is_stream)

    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        Returns:
            ppmsg.IdentityMessage: a protobuf of this message
        """
        pb = ppmsg.IdentityMessage()
        pb.ip = self.ip
        pb.identifier = self.identifier
        pb.is_stream = bool(self.is_stream)
        return pb


class ControlMessage(ProtobufMessageWrapper):
    """
    Encapsulates an ControlMessage .proto message.
    """
    @property
    def payload(self):
        return self._payload

    @payload.setter
    def payload(self, value):
        if value is not None:
            if not isinstance(value, dict):
                raise TypeError('Payload must be a dictionary or None')
            if any(not isinstance(x, (str, unicode)) for x in value.keys()):
                raise TypeError('All payload keys must be Strings')
            if any(not isinstance(x, (int, float)) and x is not None for x in value.values()):
                raise TypeError('All values must be int, floats or None')
            cleaned_dict = dict()
            for key, value_ in viewitems(value):
                cleaned_dict[key.strip().lower()] = value_
            if self._payload:
                self._payload.update(cleaned_dict)
            else:
                self._payload = cleaned_dict
        else:
            self._payload = None

    def __init__(self, setting, payload):
        """
        Initialises a control message with the given command and values list.
        Args:
            setting (bool): whether this is a set (True) or get (False) command
            payload (dict<string, float>): key-value pairs of the values to get or set. If setting, the values for all
                keys are ignored.
        Raises:
            TypeError: when command is not an int, or values are of mixed type
        """
        super(ControlMessage, self).__init__()
        self._payload = None
        self.setting = setting
        self.payload = payload

    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        Returns:
            ppmsg.ControlMessage: a protobuf of this message
        """
        pb = ppmsg.ControlMessage()
        pb.setting = self.setting

        if self.payload is not None:
            for key, value in viewitems(self.payload):
                pb.payload[key] = value if value is not None and self.setting else 0.0
        return pb


class DataMessage(ProtobufMessageWrapper):
    """
    Encapsulates an DataMessage .proto message.
    """
    # def __eq__(self, other):
    #     return self.data_code == other.data_code and self.data_string == other.data_string and\
    #            self.data_bytes == other.data_bytes
    #
    # def __ne__(self, other):
    #     return not self.__eq__(other)

    # noinspection PyMissingConstructor
    def __init__(self, data_code, data_string='', data_bytes='', info=None):
        """
        Initialises a DataMessage with the given parameters.
        Args:
            data_code (int): the code/ID associated with the message
            data_string (str): a string holding some data
            data_bytes (str or bytearray): a bytes string holding some data
            info (dict): key-value pairs of request or reply info
        """
        if not isinstance(data_code, int):
            raise TypeError('Data_code must be an int. Got instead: {}'.format(type(data_code)))
        if data_code == '':
            raise ValueError('Data_code must be a non-empty string')
        if not isinstance(data_string, (str, unicode)):
            raise TypeError('Data_string must be a string')
        if not isinstance(data_bytes, (str, unicode, bytearray)):
            raise TypeError('Data_bytes must be a string or bytearray')
        super(DataMessage, self).__init__()
        self.data_code = data_code
        self.data_string = str(data_string)
        self.data_bytes = str(data_bytes)
        self.info = info

    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        Returns:
            ppmsg.DataMessage: a protobuf of this message
        """
        pb = ppmsg.DataMessage()
        pb.data_code = self.data_code
        pb.data_string = self.data_string
        pb.data_bytes = self.data_bytes
        if self.info:
            logging.error('Info map is not yet implemented and will not be in the generated protobuf!')

        # TODO implement info map
        # for key, value in self.info.iteritems():
        #     pb.info[key] = value
        return pb


class InprocMessage(ProtobufMessageWrapper):
    """
    A message between two thread (in-process message).
    """
    def __init__(self, msg_req, server_id='', list_of_dicts=None):
        """
        Initialises a InprocMessage with the given parameters.
        Args:
            msg_req (str): the request associated with the message
            server_id (str): the server requesting the message (an ID)
        """
        super(InprocMessage, self).__init__()
        self.msg_req = '' if msg_req is None else msg_req
        self.server_id = '' if server_id is None else server_id
        self.list_of_dicts = list_of_dicts if list_of_dicts else []

    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        Returns:
            ppmsg.DataMessage: a protobuf of this message
        """
        pb = ppmsg.InprocMessage()
        pb.msg_req = self.msg_req
        pb.server_id = self.server_id
        pb.json_payload = json.dumps(self.list_of_dicts)
        return pb

    @classmethod
    def from_protobuf(cls, protobuf):
        assert isinstance(protobuf, ppmsg.InprocMessage), "Must be a InprocMessage input"
        msg_req = protobuf.msg_req
        server_id = protobuf.server_id
        try:
            list_of_dicts = json.loads(protobuf.json_payload)
        except ValueError:
            logging.warn('JSON payload could not be decoded from string: {}'.format(protobuf.json_payload))
            list_of_dicts = None
        return cls(msg_req=msg_req, server_id=server_id, list_of_dicts=list_of_dicts)


class FileLikeDataWrapper(object):
    """
    Connects a method expecting a file-like object (write, flush, etc) to this PyMsg class by passing the file's data
    into a wrapped and serialized DataMessage.
    """
    def __init__(self):
        super(FileLikeDataWrapper, self).__init__()
        pass

    @staticmethod
    def serialize_data(data, **kwargs):
        """
        Serialized the given data into a DataMessage. Expects a 'data_code' key in the kwargs to generate the
        DataMessage.
        Args:
            data: the data to wrap
            **kwargs: key-value pair arguments to be passed by the file injection point

        Returns:

        """
        if 'data_code' in kwargs:
            return DataMessage(kwargs['data_code'], data_bytes=data).wrap().serialize()
        else:
            print('Required data_code argument for wrapper class not given') # pragma: no cover
