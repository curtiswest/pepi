# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pepimessage.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
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
  serialized_pb=_b('\n\x11pepimessage.proto\"D\n\x0fIdentityMessage\x12\n\n\x02ip\x18\x01 \x01(\t\x12\x12\n\nidentifier\x18\x02 \x01(\t\x12\x11\n\tis_stream\x18\x03 \x01(\x08\"I\n\x0b\x44\x61taMessage\x12\x11\n\tdata_code\x18\x01 \x01(\x05\x12\x13\n\x0b\x64\x61ta_string\x18\x02 \x01(\t\x12\x12\n\ndata_bytes\x18\x03 \x01(\x0c\"\x80\x01\n\x0e\x43ontrolMessage\x12\x0f\n\x07setting\x18\x01 \x01(\x08\x12-\n\x07payload\x18\x02 \x03(\x0b\x32\x1c.ControlMessage.PayloadEntry\x1a.\n\x0cPayloadEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\x02:\x02\x38\x01\"\x9e\x01\n\x0eWrapperMessage\x12!\n\x05ident\x18\x01 \x01(\x0b\x32\x10.IdentityMessageH\x00\x12\x1c\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x0c.DataMessageH\x00\x12\"\n\x07\x63ontrol\x18\x03 \x01(\x0b\x32\x0f.ControlMessageH\x00\x12 \n\x06inproc\x18\x04 \x01(\x0b\x32\x0e.InprocMessageH\x00\x42\x05\n\x03msg\"3\n\rInprocMessage\x12\x0f\n\x07msg_req\x18\x01 \x01(\t\x12\x11\n\tserver_id\x18\x02 \x01(\tb\x06proto3')
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
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='is_stream', full_name='IdentityMessage.is_stream', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
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
  serialized_end=89,
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
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
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
  serialized_start=91,
  serialized_end=164,
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
  serialized_start=249,
  serialized_end=295,
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
  serialized_start=167,
  serialized_end=295,
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
  serialized_start=298,
  serialized_end=456,
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
  serialized_start=458,
  serialized_end=509,
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
DESCRIPTOR.message_types_by_name['IdentityMessage'] = _IDENTITYMESSAGE
DESCRIPTOR.message_types_by_name['DataMessage'] = _DATAMESSAGE
DESCRIPTOR.message_types_by_name['ControlMessage'] = _CONTROLMESSAGE
DESCRIPTOR.message_types_by_name['WrapperMessage'] = _WRAPPERMESSAGE
DESCRIPTOR.message_types_by_name['InprocMessage'] = _INPROCMESSAGE
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

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
