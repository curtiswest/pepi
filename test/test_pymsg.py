import unittest
import time
from communication import pymsg
import communication.pepimessage_pb2 as ppmsg
import numpy as np
import utils


class TestPyMsg(unittest.TestCase):
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

    def control_message_test_helper(self, command=None, values=None):
        # Recall that we always get back a list of values for control messages, so need to handle that for empty cases
        is_input_a_none = not isinstance(values, str) and (values is None or values == [] or values[0] is None)
        is_input_empty_string = (values == '')

        control = pymsg.ControlMessage(command, values)
        self.assertIsInstance(control.protobuf(), ppmsg.ControlMessage)
        wrapped_string = control.wrap().serialize()

        wrapped_msg = pymsg.WrapperMessage.from_serialized_string(wrapped_string)
        msg = wrapped_msg.unwrap()

        self.assertEqual(msg.command, command, 'Command malformed')
        if is_input_a_none:
            values = [None]
        if is_input_empty_string:
            values = ['']
        self.assertEqual(msg.values, values, 'Values malformed. \nIn : {} \nOut: {}'.format(values, msg.values))

        msg_string = msg.wrap().serialize()
        self.assertEqual(wrapped_string, msg_string, 'Protobuf serialisations don\'t match')

    def test_control_message(self):
        command_in, value_in = ppmsg.GET_ISO, [1000, 2000, 3000]
        # Below tests should succeed
        self.control_message_test_helper(command=command_in, values=value_in)
        self.control_message_test_helper(command=-100, values=value_in)
        self.control_message_test_helper(command=command_in)
        self.control_message_test_helper(command=command_in, values=[None])
        self.control_message_test_helper(command=command_in, values='')
        self.control_message_test_helper(command=command_in, values=[None, None, None])

        # Below tests should fail assertions to succeed
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command=[command_in, command_in], values=[None, None, None])
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command=[command_in, command_in], values=[None, None, None])
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command=None)
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command='text command')
        with self.assertRaises(TypeError):
            self.control_message_test_helper(values=[10])
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command='text command')
        with self.assertRaises(TypeError):
            # noinspection PyTypeChecker
            self.control_message_test_helper(command=None, values=None)
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command='', values='')
        with self.assertRaises(TypeError):
            self.control_message_test_helper(command='', values=[10, 10.1, 'str'])

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

        self.data_message_test_helper(data_code='id')
        self.data_message_test_helper(data_code='id', data_string='test data string')
        self.data_message_test_helper(data_code='id', data_string='test data string', data_bytes=data_bytes_in)
        self.data_message_test_helper(data_code='id', data_bytes=data_bytes_in)

        with self.assertRaises(ValueError):
            self.data_message_test_helper(data_code='')
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code='id', data_string=None)
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code='id', data_bytes=None)
        with self.assertRaises(ValueError):
            self.data_message_test_helper(data_code='', data_string=[123])
        with self.assertRaises(TypeError):
            self.data_message_test_helper(data_code='id', data_string=['str list', '2'])

    def timer_test_helper(self, runs, message):
        assert isinstance(message, pymsg.ProtobufMessageWrapper)
        start = time.time()
        for _ in range(0, runs):
            wrapped_msg = pymsg.WrapperMessage.wrap(message)
            serial = wrapped_msg.serialize()
            from_serial = pymsg.WrapperMessage.from_serialized_string(serial)
            unwrapped = from_serial.unwrap()
        delta = time.time() - start
        print '{} {} messages took {} sec. Rate: {} sec per msg'.format(runs, type(message), delta, (delta / runs))
        return delta, (delta/runs)


    def test_wrapper_message_timing(self):
        # ident = pymsg.IdentityMessage('10.0.0.5', 'myID')
        # self.timer_test_helper(1000, ident)
        control = pymsg.ControlMessage(ppmsg.GET_ISO, ['str', 'str2'])
        self.timer_test_helper(10000, control)
        # data = pymsg.DataMessage('my data code', 'my data string', 'my data bytes')
        # self.timer_test_helper(1000, data)




