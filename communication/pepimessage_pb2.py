# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pepimessage.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pepimessage.proto',
  package='',
  syntax='proto3',
  serialized_pb=_b('\n\x11pepimessage.proto\"\x1b\n\tIntValues\x12\x0e\n\x06values\x18\x01 \x03(\x05\"\x1d\n\x0b\x46loatValues\x12\x0e\n\x06values\x18\x01 \x03(\x02\"\x1e\n\x0cStringValues\x12\x0e\n\x06values\x18\x01 \x03(\t\"1\n\x0fIdentityMessage\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x12\n\nidentifier\x18\x04 \x01(\t\"I\n\x0b\x44\x61taMessage\x12\x11\n\tdata_code\x18\x01 \x01(\t\x12\x13\n\x0b\x64\x61ta_string\x18\x02 \x01(\t\x12\x12\n\ndata_bytes\x18\x03 \x01(\x0c\"\x80\x01\n\x0e\x43ontrolMessage\x12\x0f\n\x07setting\x18\x01 \x01(\x08\x12-\n\x07payload\x18\x02 \x03(\x0b\x32\x1c.ControlMessage.PayloadEntry\x1a.\n\x0cPayloadEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02:\x02\x38\x01\"\x9e\x01\n\x0eWrapperMessage\x12!\n\x05ident\x18\x01 \x01(\x0b\x32\x10.IdentityMessageH\x00\x12\x1c\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x0c.DataMessageH\x00\x12\"\n\x07\x63ontrol\x18\x03 \x01(\x0b\x32\x0f.ControlMessageH\x00\x12 \n\x06inproc\x18\x04 \x01(\x0b\x32\x0e.InprocMessageH\x00\x42\x05\n\x03msg\"G\n\rInprocMessage\x12\x0f\n\x07msg_req\x18\x01 \x01(\t\x12\x11\n\tserver_id\x18\x02 \x01(\t\x12\x12\n\nserial_msg\x18\x03 \x01(\t*\xf0\x04\n\x07\x43ommand\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\x0b\n\x07SET_ISO\x10\x01\x12\x0b\n\x07GET_ISO\x10\x65\x12\x15\n\x11SET_SHUTTER_SPEED\x10\x02\x12\x15\n\x11GET_SHUTTER_SPEED\x10\x66\x12\x12\n\x0eSET_BRIGHTNESS\x10\x03\x12\x12\n\x0eGET_BRIGHTNESS\x10g\x12\x11\n\rSET_AWB_GAINS\x10\x04\x12\x11\n\rGET_AWB_GAINS\x10h\x12\x12\n\x0eSET_RESOLUTION\x10\x05\x12\x12\n\x0eGET_RESOLUTION\x10i\x12\x11\n\rSET_SHARPNESS\x10\x06\x12\x11\n\rGET_SHARPNESS\x10j\x12\x12\n\x0eSET_SATURATION\x10\x07\x12\x12\n\x0eGET_SATURATION\x10k\x12\x0c\n\x08SET_ZOOM\x10\x08\x12\x0c\n\x08GET_ZOOM\x10l\x12\x10\n\x0cSET_AWB_MODE\x10\t\x12\x10\n\x0cGET_AWB_MODE\x10m\x12\x12\n\rSET_SERVER_ID\x10\xc8\x01\x12\x12\n\rGET_SERVER_ID\x10\xc9\x01\x12\x17\n\x12\x45NABLE_COMPRESSION\x10\xca\x01\x12\x18\n\x13\x44ISABLE_COMPRESSION\x10\xcb\x01\x12\x12\n\rIDENTIFY_SELF\x10\xcc\x01\x12\x0f\n\nDISCONNECT\x10\xcd\x01\x12\t\n\x04PING\x10\xce\x01\x12\t\n\x04PONG\x10\xcf\x01\x12\x0e\n\tGET_STILL\x10\xac\x02\x12\x11\n\x0cSTART_STREAM\x10\x90\x03\x12\x10\n\x0bSTOP_STREAM\x10\x91\x03\x12\x14\n\x0f\x43OMMAND_SUCCESS\x10\xbc\x05\x12\x14\n\x0f\x43OMMAND_FAILURE\x10\xa0\x06\x12\x15\n\x10\x44\x41TA_UNAVAILABLE\x10\xa1\x06\x62\x06proto3')
)

_COMMAND = _descriptor.EnumDescriptor(
  name='Command',
  full_name='Command',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DEFAULT', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_ISO', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_ISO', index=2, number=101,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_SHUTTER_SPEED', index=3, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_SHUTTER_SPEED', index=4, number=102,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_BRIGHTNESS', index=5, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_BRIGHTNESS', index=6, number=103,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_AWB_GAINS', index=7, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_AWB_GAINS', index=8, number=104,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_RESOLUTION', index=9, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_RESOLUTION', index=10, number=105,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_SHARPNESS', index=11, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_SHARPNESS', index=12, number=106,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_SATURATION', index=13, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_SATURATION', index=14, number=107,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_ZOOM', index=15, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_ZOOM', index=16, number=108,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_AWB_MODE', index=17, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_AWB_MODE', index=18, number=109,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_SERVER_ID', index=19, number=200,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_SERVER_ID', index=20, number=201,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENABLE_COMPRESSION', index=21, number=202,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DISABLE_COMPRESSION', index=22, number=203,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IDENTIFY_SELF', index=23, number=204,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DISCONNECT', index=24, number=205,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PING', index=25, number=206,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PONG', index=26, number=207,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_STILL', index=27, number=300,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='START_STREAM', index=28, number=400,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STOP_STREAM', index=29, number=401,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_SUCCESS', index=30, number=700,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_FAILURE', index=31, number=800,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DATA_UNAVAILABLE', index=32, number=801,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=605,
  serialized_end=1229,
)
_sym_db.RegisterEnumDescriptor(_COMMAND)

Command = enum_type_wrapper.EnumTypeWrapper(_COMMAND)
DEFAULT = 0
SET_ISO = 1
GET_ISO = 101
SET_SHUTTER_SPEED = 2
GET_SHUTTER_SPEED = 102
SET_BRIGHTNESS = 3
GET_BRIGHTNESS = 103
SET_AWB_GAINS = 4
GET_AWB_GAINS = 104
SET_RESOLUTION = 5
GET_RESOLUTION = 105
SET_SHARPNESS = 6
GET_SHARPNESS = 106
SET_SATURATION = 7
GET_SATURATION = 107
SET_ZOOM = 8
GET_ZOOM = 108
SET_AWB_MODE = 9
GET_AWB_MODE = 109
SET_SERVER_ID = 200
GET_SERVER_ID = 201
ENABLE_COMPRESSION = 202
DISABLE_COMPRESSION = 203
IDENTIFY_SELF = 204
DISCONNECT = 205
PING = 206
PONG = 207
GET_STILL = 300
START_STREAM = 400
STOP_STREAM = 401
COMMAND_SUCCESS = 700
COMMAND_FAILURE = 800
DATA_UNAVAILABLE = 801



_INTVALUES = _descriptor.Descriptor(
  name='IntValues',
  full_name='IntValues',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='IntValues.values', index=0,
      number=1, type=5, cpp_type=1, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=21,
  serialized_end=48,
)


_FLOATVALUES = _descriptor.Descriptor(
  name='FloatValues',
  full_name='FloatValues',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='FloatValues.values', index=0,
      number=1, type=2, cpp_type=6, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=50,
  serialized_end=79,
)


_STRINGVALUES = _descriptor.Descriptor(
  name='StringValues',
  full_name='StringValues',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='values', full_name='StringValues.values', index=0,
      number=1, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=81,
  serialized_end=111,
)


_IDENTITYMESSAGE = _descriptor.Descriptor(
  name='IdentityMessage',
  full_name='IdentityMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ip', full_name='IdentityMessage.ip', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='identifier', full_name='IdentityMessage.identifier', index=1,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=113,
  serialized_end=162,
)


_DATAMESSAGE = _descriptor.Descriptor(
  name='DataMessage',
  full_name='DataMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='data_code', full_name='DataMessage.data_code', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_string', full_name='DataMessage.data_string', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data_bytes', full_name='DataMessage.data_bytes', index=2,
      number=3, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=164,
  serialized_end=237,
)


_CONTROLMESSAGE_PAYLOADENTRY = _descriptor.Descriptor(
  name='PayloadEntry',
  full_name='ControlMessage.PayloadEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='ControlMessage.PayloadEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='value', full_name='ControlMessage.PayloadEntry.value', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=_descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001')),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=322,
  serialized_end=368,
)

_CONTROLMESSAGE = _descriptor.Descriptor(
  name='ControlMessage',
  full_name='ControlMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='setting', full_name='ControlMessage.setting', index=0,
      number=1, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='payload', full_name='ControlMessage.payload', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[_CONTROLMESSAGE_PAYLOADENTRY, ],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=240,
  serialized_end=368,
)


_WRAPPERMESSAGE = _descriptor.Descriptor(
  name='WrapperMessage',
  full_name='WrapperMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='ident', full_name='WrapperMessage.ident', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='data', full_name='WrapperMessage.data', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='control', full_name='WrapperMessage.control', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='inproc', full_name='WrapperMessage.inproc', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='msg', full_name='WrapperMessage.msg',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=371,
  serialized_end=529,
)


_INPROCMESSAGE = _descriptor.Descriptor(
  name='InprocMessage',
  full_name='InprocMessage',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='msg_req', full_name='InprocMessage.msg_req', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='server_id', full_name='InprocMessage.server_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='serial_msg', full_name='InprocMessage.serial_msg', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=531,
  serialized_end=602,
)

_CONTROLMESSAGE_PAYLOADENTRY.containing_type = _CONTROLMESSAGE
_CONTROLMESSAGE.fields_by_name['payload'].message_type = _CONTROLMESSAGE_PAYLOADENTRY
_WRAPPERMESSAGE.fields_by_name['ident'].message_type = _IDENTITYMESSAGE
_WRAPPERMESSAGE.fields_by_name['data'].message_type = _DATAMESSAGE
_WRAPPERMESSAGE.fields_by_name['control'].message_type = _CONTROLMESSAGE
_WRAPPERMESSAGE.fields_by_name['inproc'].message_type = _INPROCMESSAGE
_WRAPPERMESSAGE.oneofs_by_name['msg'].fields.append(
  _WRAPPERMESSAGE.fields_by_name['ident'])
_WRAPPERMESSAGE.fields_by_name['ident'].containing_oneof = _WRAPPERMESSAGE.oneofs_by_name['msg']
_WRAPPERMESSAGE.oneofs_by_name['msg'].fields.append(
  _WRAPPERMESSAGE.fields_by_name['data'])
_WRAPPERMESSAGE.fields_by_name['data'].containing_oneof = _WRAPPERMESSAGE.oneofs_by_name['msg']
_WRAPPERMESSAGE.oneofs_by_name['msg'].fields.append(
  _WRAPPERMESSAGE.fields_by_name['control'])
_WRAPPERMESSAGE.fields_by_name['control'].containing_oneof = _WRAPPERMESSAGE.oneofs_by_name['msg']
_WRAPPERMESSAGE.oneofs_by_name['msg'].fields.append(
  _WRAPPERMESSAGE.fields_by_name['inproc'])
_WRAPPERMESSAGE.fields_by_name['inproc'].containing_oneof = _WRAPPERMESSAGE.oneofs_by_name['msg']
DESCRIPTOR.message_types_by_name['IntValues'] = _INTVALUES
DESCRIPTOR.message_types_by_name['FloatValues'] = _FLOATVALUES
DESCRIPTOR.message_types_by_name['StringValues'] = _STRINGVALUES
DESCRIPTOR.message_types_by_name['IdentityMessage'] = _IDENTITYMESSAGE
DESCRIPTOR.message_types_by_name['DataMessage'] = _DATAMESSAGE
DESCRIPTOR.message_types_by_name['ControlMessage'] = _CONTROLMESSAGE
DESCRIPTOR.message_types_by_name['WrapperMessage'] = _WRAPPERMESSAGE
DESCRIPTOR.message_types_by_name['InprocMessage'] = _INPROCMESSAGE
DESCRIPTOR.enum_types_by_name['Command'] = _COMMAND
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IntValues = _reflection.GeneratedProtocolMessageType('IntValues', (_message.Message,), dict(
  DESCRIPTOR = _INTVALUES,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:IntValues)
  ))
_sym_db.RegisterMessage(IntValues)

FloatValues = _reflection.GeneratedProtocolMessageType('FloatValues', (_message.Message,), dict(
  DESCRIPTOR = _FLOATVALUES,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:FloatValues)
  ))
_sym_db.RegisterMessage(FloatValues)

StringValues = _reflection.GeneratedProtocolMessageType('StringValues', (_message.Message,), dict(
  DESCRIPTOR = _STRINGVALUES,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:StringValues)
  ))
_sym_db.RegisterMessage(StringValues)

IdentityMessage = _reflection.GeneratedProtocolMessageType('IdentityMessage', (_message.Message,), dict(
  DESCRIPTOR = _IDENTITYMESSAGE,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:IdentityMessage)
  ))
_sym_db.RegisterMessage(IdentityMessage)

DataMessage = _reflection.GeneratedProtocolMessageType('DataMessage', (_message.Message,), dict(
  DESCRIPTOR = _DATAMESSAGE,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:DataMessage)
  ))
_sym_db.RegisterMessage(DataMessage)

ControlMessage = _reflection.GeneratedProtocolMessageType('ControlMessage', (_message.Message,), dict(

  PayloadEntry = _reflection.GeneratedProtocolMessageType('PayloadEntry', (_message.Message,), dict(
    DESCRIPTOR = _CONTROLMESSAGE_PAYLOADENTRY,
    __module__ = 'pepimessage_pb2'
    # @@protoc_insertion_point(class_scope:ControlMessage.PayloadEntry)
    ))
  ,
  DESCRIPTOR = _CONTROLMESSAGE,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:ControlMessage)
  ))
_sym_db.RegisterMessage(ControlMessage)
_sym_db.RegisterMessage(ControlMessage.PayloadEntry)

WrapperMessage = _reflection.GeneratedProtocolMessageType('WrapperMessage', (_message.Message,), dict(
  DESCRIPTOR = _WRAPPERMESSAGE,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:WrapperMessage)
  ))
_sym_db.RegisterMessage(WrapperMessage)

InprocMessage = _reflection.GeneratedProtocolMessageType('InprocMessage', (_message.Message,), dict(
  DESCRIPTOR = _INPROCMESSAGE,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:InprocMessage)
  ))
_sym_db.RegisterMessage(InprocMessage)


_CONTROLMESSAGE_PAYLOADENTRY.has_options = True
_CONTROLMESSAGE_PAYLOADENTRY._options = _descriptor._ParseOptions(descriptor_pb2.MessageOptions(), _b('8\001'))
# @@protoc_insertion_point(module_scope)
