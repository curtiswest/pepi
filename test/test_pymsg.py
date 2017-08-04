import time
import unittest

import communication.pepimessage_pb2 as ppmsg
import utils
from communication import pymsg


def isclose(a, b, rel_tol=1e-09, abs_tol=0.001):
    return abs(a-b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def timer_test_helper(runs, message):
    assert isinstance(message, pymsg.ProtobufMessageWrapper)
    start = time.time()
    for _ in range(0, runs):
        wrapped_msg = pymsg.WrapperMessage.wrap(message)
        serial = wrapped_msg.serialize()
        from_serial = pymsg.WrapperMessage.from_serialized_string(serial)
        _ = from_serial.unwrap()
    delta = time.time() - start
    print '{} {} messages took {} sec. Rate: {} sec per msg'.format(runs, type(message), delta, (delta / runs))
    return delta, (delta/runs)


class TestPyMsg(unittest.TestCase):
    def inproc_message_helper(self, msg_req='', server_id=''):
        inproc = pymsg.InprocMessage(msg_req=msg_req, server_id=server_id)
        self.assertIsInstance(inproc.protobuf(), ppmsg.InprocMessage)
        wrapped_string = inproc.wrap().serialize()

        wrapped_msg = pymsg.WrapperMessage.from_serialized_string(wrapped_string)
        msg = wrapped_msg.unwrap()
        self.assertEqual(msg.msg_req, msg_req, 'msg_req malformed')
        self.assertEqual(msg.server_id, server_id, 'server_id malformed')

        msg_string = msg.wrap().serialize()
        self.assertEqual(wrapped_string, msg_string, 'Protobuf serialisations don\'t match')

    def test_inproc_message(self):
        self.inproc_message_helper('req', 'sid')
        self.inproc_message_helper('req')
        self.inproc_message_helper()


    def ident_message_helper(self, ip=None, identifier=None):
        ident = pymsg.IdentityMessage(ip, identifier)
        self.assertIsInstance(ident.protobuf(), ppmsg.IdentityMessage)
        wrapped_string = ident.wrap().serialize()

        wrapped_msg = pymsg.WrapperMessage.from_serialized_string(wrapped_string)
        msg = wrapped_msg.unwrap()
        self.assertEqual(msg.ip, ip, 'IP malformed')
        self.assertEqual(msg.identifier, identifier, 'Identifier malformed')

        msg_string = msg.wrap().serialize()
        self.assertEqual(wrapped_string, msg_string, 'Protobuf serialisations don\'t match')

    def test_ident_message(self):
        ip_in, identifier = '192.168.1.1', 'test_server_id'
        self.ident_message_helper(ip=ip_in, identifier=identifier)

        with self.assertRaises(ValueError):
            self.ident_message_helper(ip='', identifier='')
        with self.assertRaises(ValueError):
            self.ident_message_helper(ip=ip_in)
        with self.assertRaises(ValueError):
            self.ident_message_helper(identifier=identifier)
        with self.assertRaises(ValueError):
            self.ident_message_helper()
        with self.assertRaises(TypeError):
            self.ident_message_helper(ip=100, identifier=identifier)
        with self.assertRaises(TypeError):
            self.ident_message_helper(ip=ip_in, identifier=100)

    def control_message_test_helper(self, setting=None, payload=None):
        msg = pymsg.ControlMessage(setting=setting, payload=payload)
        self.assertIsInstance(msg.protobuf(), ppmsg.ControlMessage)
        wrapped_string = msg.wrap().serialize()

        wrapped_msg = pymsg.WrapperMessage.from_serialized_string(wrapped_string)
        unwrap_msg = wrapped_msg.unwrap()
        self.assertEqual(msg.setting, setting, 'Setting bool malformed')

        if not setting:
            expected_payload = dict.fromkeys(payload, 0)  # Values get ignored
        else:
            expected_payload = payload

        for key, value in unwrap_msg.payload.iteritems():
            self.assertTrue(isclose(value, expected_payload[key]),
                            'Payload malformed. \nIn : {} \nOut: {}'.format(expected_payload[key], value))

        msg_string = unwrap_msg.wrap().serialize()
        self.assertEqual(wrapped_string, msg_string, 'Protobuf serialisations don\'t match')

    def test_control_message(self):
        # Below tests should succeed
        self.control_message_test_helper(setting=True, payload={'iso': 1000})
        self.control_message_test_helper(setting=True, payload={'shutter_speed': 1313})
        self.control_message_test_helper(setting=True, payload={'shutter_speed': 1313, 'iso': 1000, 'brightness': 10})
        self.control_message_test_helper(setting=False, payload={'iso': 1000})
        self.control_message_test_helper(setting=True, payload={'iso': 10.1})
        self.control_message_test_helper(setting=True, payload=None)

        # Below test should 'fail'
        with self.assertRaises(TypeError):
            self.control_message_test_helper(setting='string', payload={'iso': 1000})
        with self.assertRaises(TypeError):
            self.control_message_test_helper(setting='string', payload='not a dict')
        with self.assertRaises(TypeError):
            self.control_message_test_helper(setting=True, payload={'iso': 'string'})
        with self.assertRaises(TypeError):
            self.control_message_test_helper(setting=True, payload={10: 1000})

    def data_message_test_helper(self, data_code='', data_bytes='', data_string=''):
        data = pymsg.DataMessage(data_code=data_code, data_bytes=data_bytes, data_string=data_string)
        self.assertIsInstance(data.protobuf(), ppmsg.DataMessage)
        wrapped_string = data.wrap().serialize()

        wrapped_msg = pymsg.WrapperMessage.from_serialized_string(wrapped_string)
        msg = wrapped_msg.unwrap()
        self.assertEqual(msg.data_code, data_code,
                         'Identifier malformed. New ({}) vs Old ({})'.format(msg.data_code, data_code))
        self.assertEqual(msg.data_bytes, data_bytes, 'Data_bytes malformed')
        self.assertEqual(msg.data_string, data_string, 'Data_string malformed')

        msg_string = msg.wrap().serialize()
        self.assertEqual(wrapped_string, msg_string, 'Protobuf serialisations don\'t match')

    def test_data_message(self):
        image = utils.generate_random_img()
        data_bytes_in = utils.encode_image(image)

        self.data_message_test_helper(data_code=0)
        self.data_message_test_helper(data_code=0, data_string='test data string')
        self.data_message_test_helper(data_code=0, data_string='test data string', data_bytes=data_bytes_in)
        self.data_message_test_helper(data_code=0, data_bytes=data_bytes_in)

        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code=None)
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code=10.1)
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code=0, data_string=None)
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code=0, data_bytes=None)
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code=0, data_string=[123])
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code=0, data_string=['str list', '2'])

    def test_wrapping_messages(self):
        with self.assertRaises(pymsg.ProtobufMessageWrapper.MessageTypeError):
            pymsg.WrapperMessage('not a protobuf')

        with self.assertRaises(pymsg.ProtobufMessageWrapper.MessageTypeError):
            pymsg.WrapperMessage.wrap('not a message type')

        control = pymsg.ControlMessage(setting=True, payload={'iso': 1000})
        wrapped = control.wrap()
        self.assertEqual(wrapped.unwrap(), control)

        data = pymsg.DataMessage(1, 'datastring')
        wrapped = data.wrap()
        self.assertEqual(wrapped.unwrap(), data)

        ident = pymsg.IdentityMessage('ip', 'id', True)
        wrapped = ident.wrap()
        self.assertEqual(wrapped.unwrap(), ident)

        inproc = pymsg.InprocMessage('msg_req', '1')
        wrapped = inproc.wrap()
        self.assertEqual(wrapped.unwrap(), inproc)

        with self.assertRaises(pymsg.ProtobufMessageWrapper.DecodeError):
            _ = pymsg.WrapperMessage.from_serialized_string('not a real protubuf string!')

    def test_protobuf_abstract_class(self):
        with self.assertRaises(TypeError):
            abstract = pymsg.ProtobufMessageWrapper()
            abstract.protobuf()

    def test_wrapper_message_timing(self):
        ident = pymsg.IdentityMessage('10.0.0.5', 'myID')
        timer_test_helper(1000, ident)
        control = pymsg.ControlMessage(setting=True, payload={'iso': 1000})
        timer_test_helper(10000, control)
        data = pymsg.DataMessage(1, 'my data string', 'my data bytes')
        timer_test_helper(1000, data)
