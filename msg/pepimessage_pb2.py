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
  serialized_pb=_b('\n\x11pepimessage.proto\"0\n\x05Image\x12\x14\n\x0cimg_data_str\x18\x01 \x01(\x0c\x12\x11\n\tserver_id\x18\x02 \x01(\t\"\x1b\n\tIntValues\x12\x0e\n\x06values\x18\x01 \x03(\x05\"\x1e\n\x0cStringValues\x12\x0e\n\x06values\x18\x01 \x03(\t\"x\n\x07Request\x12\x19\n\x07\x63ommand\x18\x01 \x01(\x0e\x32\x08.Command\x12 \n\nint_values\x18\x02 \x01(\x0b\x32\n.IntValuesH\x00\x12&\n\rstring_values\x18\x03 \x01(\x0b\x32\r.StringValuesH\x00\x42\x08\n\x06values\"\x8f\x01\n\x05Reply\x12\x19\n\x07\x63ommand\x18\x01 \x01(\x0e\x32\x08.Command\x12 \n\nint_values\x18\x02 \x01(\x0b\x32\n.IntValuesH\x00\x12&\n\rstring_values\x18\x03 \x01(\x0b\x32\r.StringValuesH\x00\x12\x17\n\x05image\x18\x04 \x01(\x0b\x32\x06.ImageH\x00\x42\x08\n\x06values*\xa2\x04\n\x07\x43ommand\x12\x0b\n\x07\x44\x45\x46\x41ULT\x10\x00\x12\x0b\n\x07SET_ISO\x10\x01\x12\x0b\n\x07GET_ISO\x10\x65\x12\x15\n\x11SET_SHUTTER_SPEED\x10\x02\x12\x15\n\x11GET_SHUTTER_SPEED\x10\x66\x12\x12\n\x0eGET_BRIGHTNESS\x10\x03\x12\x12\n\x0eSET_BRIGHTNESS\x10g\x12\x11\n\rSET_AWB_GAINS\x10\x04\x12\x11\n\rGET_AWB_GAINS\x10h\x12\x12\n\x0eSET_RESOLUTION\x10\x05\x12\x12\n\x0eGET_RESOLUTION\x10i\x12\x11\n\rSET_SHARPNESS\x10\x06\x12\x11\n\rGET_SHARPNESS\x10j\x12\x12\n\x0eSET_SATURATION\x10\x07\x12\x12\n\x0eGET_SATURATION\x10k\x12\x0c\n\x08SET_ZOOM\x10\x08\x12\x0c\n\x08GET_ZOOM\x10l\x12\x12\n\rSET_SERVER_ID\x10\xc8\x01\x12\x12\n\rGET_SERVER_ID\x10\xc9\x01\x12\x17\n\x12\x45NABLE_COMPRESSION\x10\xca\x01\x12\x18\n\x13\x44ISABLE_COMPRESSION\x10\xcb\x01\x12\x0e\n\tGET_STILL\x10\xac\x02\x12\x12\n\rSTILL_SUCCESS\x10\xb3\x02\x12\x12\n\rSTILL_FAILURE\x10\xb4\x02\x12\x11\n\x0cSTART_STREAM\x10\x90\x03\x12\x10\n\x0bSTOP_STREAM\x10\x91\x03\x12\x14\n\x0f\x43OMMAND_SUCCESS\x10\xbc\x05\x12\x14\n\x0f\x43OMMAND_FAILURE\x10\xa0\x06\x62\x06proto3')
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
      name='GET_BRIGHTNESS', index=5, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SET_BRIGHTNESS', index=6, number=103,
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
      name='SET_SERVER_ID', index=17, number=200,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_SERVER_ID', index=18, number=201,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ENABLE_COMPRESSION', index=19, number=202,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DISABLE_COMPRESSION', index=20, number=203,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GET_STILL', index=21, number=300,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STILL_SUCCESS', index=22, number=307,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STILL_FAILURE', index=23, number=308,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='START_STREAM', index=24, number=400,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='STOP_STREAM', index=25, number=401,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_SUCCESS', index=26, number=700,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMMAND_FAILURE', index=27, number=800,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=401,
  serialized_end=947,
)
_sym_db.RegisterEnumDescriptor(_COMMAND)

Command = enum_type_wrapper.EnumTypeWrapper(_COMMAND)
DEFAULT = 0
SET_ISO = 1
GET_ISO = 101
SET_SHUTTER_SPEED = 2
GET_SHUTTER_SPEED = 102
GET_BRIGHTNESS = 3
SET_BRIGHTNESS = 103
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
SET_SERVER_ID = 200
GET_SERVER_ID = 201
ENABLE_COMPRESSION = 202
DISABLE_COMPRESSION = 203
GET_STILL = 300
STILL_SUCCESS = 307
STILL_FAILURE = 308
START_STREAM = 400
STOP_STREAM = 401
COMMAND_SUCCESS = 700
COMMAND_FAILURE = 800



_IMAGE = _descriptor.Descriptor(
  name='Image',
  full_name='Image',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='img_data_str', full_name='Image.img_data_str', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='server_id', full_name='Image.server_id', index=1,
      number=2, type=9, cpp_type=9, label=1,
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
  serialized_start=21,
  serialized_end=69,
)


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
  serialized_start=71,
  serialized_end=98,
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
  serialized_start=100,
  serialized_end=130,
)


_REQUEST = _descriptor.Descriptor(
  name='Request',
  full_name='Request',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='command', full_name='Request.command', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='int_values', full_name='Request.int_values', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='string_values', full_name='Request.string_values', index=2,
      number=3, type=11, cpp_type=10, label=1,
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
      name='values', full_name='Request.values',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=132,
  serialized_end=252,
)


_REPLY = _descriptor.Descriptor(
  name='Reply',
  full_name='Reply',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='command', full_name='Reply.command', index=0,
      number=1, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='int_values', full_name='Reply.int_values', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='string_values', full_name='Reply.string_values', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='image', full_name='Reply.image', index=3,
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
      name='values', full_name='Reply.values',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=255,
  serialized_end=398,
)

_REQUEST.fields_by_name['command'].enum_type = _COMMAND
_REQUEST.fields_by_name['int_values'].message_type = _INTVALUES
_REQUEST.fields_by_name['string_values'].message_type = _STRINGVALUES
_REQUEST.oneofs_by_name['values'].fields.append(
  _REQUEST.fields_by_name['int_values'])
_REQUEST.fields_by_name['int_values'].containing_oneof = _REQUEST.oneofs_by_name['values']
_REQUEST.oneofs_by_name['values'].fields.append(
  _REQUEST.fields_by_name['string_values'])
_REQUEST.fields_by_name['string_values'].containing_oneof = _REQUEST.oneofs_by_name['values']
_REPLY.fields_by_name['command'].enum_type = _COMMAND
_REPLY.fields_by_name['int_values'].message_type = _INTVALUES
_REPLY.fields_by_name['string_values'].message_type = _STRINGVALUES
_REPLY.fields_by_name['image'].message_type = _IMAGE
_REPLY.oneofs_by_name['values'].fields.append(
  _REPLY.fields_by_name['int_values'])
_REPLY.fields_by_name['int_values'].containing_oneof = _REPLY.oneofs_by_name['values']
_REPLY.oneofs_by_name['values'].fields.append(
  _REPLY.fields_by_name['string_values'])
_REPLY.fields_by_name['string_values'].containing_oneof = _REPLY.oneofs_by_name['values']
_REPLY.oneofs_by_name['values'].fields.append(
  _REPLY.fields_by_name['image'])
_REPLY.fields_by_name['image'].containing_oneof = _REPLY.oneofs_by_name['values']
DESCRIPTOR.message_types_by_name['Image'] = _IMAGE
DESCRIPTOR.message_types_by_name['IntValues'] = _INTVALUES
DESCRIPTOR.message_types_by_name['StringValues'] = _STRINGVALUES
DESCRIPTOR.message_types_by_name['Request'] = _REQUEST
DESCRIPTOR.message_types_by_name['Reply'] = _REPLY
DESCRIPTOR.enum_types_by_name['Command'] = _COMMAND
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

Image = _reflection.GeneratedProtocolMessageType('Image', (_message.Message,), dict(
  DESCRIPTOR = _IMAGE,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:Image)
  ))
_sym_db.RegisterMessage(Image)

IntValues = _reflection.GeneratedProtocolMessageType('IntValues', (_message.Message,), dict(
  DESCRIPTOR = _INTVALUES,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:IntValues)
  ))
_sym_db.RegisterMessage(IntValues)

StringValues = _reflection.GeneratedProtocolMessageType('StringValues', (_message.Message,), dict(
  DESCRIPTOR = _STRINGVALUES,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:StringValues)
  ))
_sym_db.RegisterMessage(StringValues)

Request = _reflection.GeneratedProtocolMessageType('Request', (_message.Message,), dict(
  DESCRIPTOR = _REQUEST,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:Request)
  ))
_sym_db.RegisterMessage(Request)

Reply = _reflection.GeneratedProtocolMessageType('Reply', (_message.Message,), dict(
  DESCRIPTOR = _REPLY,
  __module__ = 'pepimessage_pb2'
  # @@protoc_insertion_point(class_scope:Reply)
  ))
_sym_db.RegisterMessage(Reply)


# @@protoc_insertion_point(module_scope)