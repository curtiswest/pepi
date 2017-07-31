"""
Pymsg.py: Provides the ProtobufMessageWrapper abstract class to wrap around Google's generated Protobuf messages,
along with concrete implementations for the messages used for the Pepi system.
"""
from abc import ABCMeta, abstractmethod
import google.protobuf.message
import pepimessage_pb2 as ppmsg

__author__ = 'Curtis West'
__copyright__ = 'Copyright 2017, Curtis West'
__version__ = '0.1'
__maintainer__ = 'Curtis West'
__email__ = "curtis@curtiswest.net"
__status__ = 'Development'


class ProtobufMessageWrapper(object):
    """
    An abstract class defining how a Protobuf message should be wrapped as a Python object.
    """
    __metaclass__ = ABCMeta

    # noinspection PyMissingOrEmptyDocstring
    class DecodeError(Exception):
        pass

    # noinspection PyMissingOrEmptyDocstring
    class EncodeError(Exception):
        pass

    # noinspection PyMissingOrEmptyDocstring
    class MessageTypeError(Exception):
        pass

    @abstractmethod
    def __init__(self):
        pass

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
            raise ProtobufMessageWrapper.MessageTypeError('WrapperMessage can only work on WrapperMessage protobufs.'
                                                          'Given a protobuf of type: {}'.format(type(protobuf)))
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
        raise NotImplementedError('A wrap message cannot itself be wrapped')

    def unwrap(self):
        """
        Unwraps this WrapperMessage and returns the ProtobufMessageWrapper subclass that this WrapperMessage contains.
        Returns:
            ProtobufMessageWrapper: the unwrapped message
        """
        # type: () -> ProtobufMessageWrapper
        set_msg = self.pb.WhichOneof('msg')
        if set_msg == 'ident':
            msg = IdentityMessage(self.pb.ident.ip, self.pb.ident.identifier)
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
            pb = self.pb.inproc
            msg = InprocMessage(pb.msg_req, pb.server_id, pb.serial_msg)
        else:
            raise NotImplementedError('The Protobuf that unwrap() is working on contains an unknown field in the Oneof '
                                      'field. Specifically, unwrap() cannot handle the field ({}).'.format(set_msg))
        return msg

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
        def _ingest_message(destination, source, has_nested_types=False, has_dict_type=False):
            protobuf = source.protobuf()
            for descriptor in protobuf.DESCRIPTOR.fields:
                if has_nested_types:
                    try:
                        if protobuf.HasField(descriptor.name):
                            values = getattr(getattr(protobuf, descriptor.name), 'values')
                            field = getattr(getattr(destination, descriptor.name), 'values')
                            field.extend(values)
                    except ValueError:
                        setattr(destination, descriptor.name, getattr(protobuf, descriptor.name))
                elif has_dict_type:
                    try:
                        setattr(destination, descriptor.name, getattr(protobuf, descriptor.name))
                    except AttributeError:
                        # Might be a dictionary type
                        pb_dict = getattr(protobuf, descriptor.name)
                        for key, value in pb_dict.iteritems():
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
        else:
            raise ProtobufMessageWrapper.MessageTypeError('Cannot handle message of type {}'.format(type(message)))
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
        except google.protobuf.message.DecodeError as e:
            raise ProtobufMessageWrapper.DecodeError('Given string cannot be decoded. Error: {}'.format(e.message))
        return cls(pb)


class IdentityMessage(ProtobufMessageWrapper):
    """
    Encapsulates an IdentityMessage .proto message.
    """

    # noinspection PyMissingConstructor
    def __init__(self, ip, identifier):
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
        self.ip = ip
        self.identifier = identifier

    def protobuf(self):
        """
        Generates the actual Protobuf representation of this message.
        Returns:
            ppmsg.IdentityMessage: a protobuf of this message
        """
        pb = ppmsg.IdentityMessage()
        pb.ip = self.ip
        pb.identifier = self.identifier
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
            for key, value in value.iteritems():
                cleaned_dict[key.strip().lower()] = value
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

        if not self.setting and self.payload is not None:
            payload = dict.fromkeys(self.payload, 0)  # If getting, only payload keys are kept, values are ignored
        else:
            payload = self.payload

        for key, value in payload.iteritems():
            pb.payload[key] = value
        return pb


class DataMessage(ProtobufMessageWrapper):
    """
    Encapsulates an DataMessage .proto message.
    """

    # noinspection PyMissingConstructor
    def __init__(self, data_code, data_string='', data_bytes='', info=None):
        """
        Initialises a DataMessage with the given parameters.
        Args:
            data_code (str): the code/ID associated with the message
            data_string (str): a string holding some data
            data_bytes (str or bytearray): a bytes string holding some data
            info (dict): key-value pairs of request or reply info
        """
        if not isinstance(data_code, (str, unicode)):
            raise TypeError('Data_code must be a string. Got instead: {}'.format(type(data_code)))
        if data_code == '':
            raise ValueError('Data_code must be a non-empty string')
        if not isinstance(data_string, (str, unicode)):
            raise TypeError('Data_string must be a string')
        if not isinstance(data_bytes, (str, unicode, bytearray)):
            raise TypeError('Data_bytes must be a string or bytearray')
        self.data_code = str(data_code)
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

        # TODO implement info map
        # for key, value in self.info.iteritems():
        #     pb.info[key] = value
        return pb


class InprocMessage(ProtobufMessageWrapper):
    def __init__(self, msg_req, server_id='', serial_msg=''):
        self.msg_req = msg_req
        self.server_id = server_id
        self.serial_msg = serial_msg

    def protobuf(self):
        pb = ppmsg.InprocMessage()
        pb.msg_req = self.msg_req
        pb.server_id = self.server_id
        pb.serial_msg = self.serial_msg
        return pb


class FileLikeDataWrapper:
    @staticmethod
    def serialize_data(data_code, data_bytes):
        msg = DataMessage(data_code, data_bytes=data_bytes)
        return msg.wrap().serialize()
