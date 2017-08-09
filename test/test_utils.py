import unittest
import numpy as np
import time

from utils import misc, iptools, stoppablethread
import communication.pepimessage_pb2

class UtilsPy(unittest.TestCase):
    def test_wrap_to_list(self):
        lst = [10, 20, 30]
        self.assertEqual(misc.wrap_to_list(lst), lst)

        not_lst = 10
        self.assertEqual(misc.wrap_to_list(not_lst), [10])

        tup = (10, 20, 30)
        self.assertEqual(misc.wrap_to_list(tup), [10, 20, 30])

    def test_iterify(self):
        # Strings should come out as a string
        string = 'hello'
        self.assertEqual(misc.iterify(string), ['hello'])

        # Single element list should come out as a single element list
        string_lst = ['hello']
        self.assertEqual(misc.iterify(string_lst), string_lst)

        # Lists of strings should come out as a list of strings
        string_lst = ['first', 'second', 'third']
        self.assertEqual(misc.iterify(string_lst), string_lst)

    def test_generate_random_img(self):
        img = misc.generate_random_img()
        for x in img:
            for y in x:
                for color in y:
                    self.assertTrue(0 <= color <= 255)

    def test_generate_id(self):
        id = misc.generate_id(4)
        self.assertEqual(len(id), 4)

        id = misc.generate_id(6)
        self.assertEqual(len(id), 6)

        id = misc.generate_id(20)
        self.assertEqual(len(id), 20)

    def test_in_out(self):
        in_out_str = misc.in_out('input', 'output')
        self.assertEqual(in_out_str, '\nIn : input \nOut: output')

    def test_variables_in_class(self):
        vars = misc.variables_in_class(str)
        self.assertIsNotNone(vars)

    def test_encode_decode_image(self):
        img = misc.generate_random_img()
        encoded = misc.encode_image(img, True, 90)
        decoded = misc.decode_image(encoded)

        encoded = misc.encode_image(img, False, 3)
        decoded = misc.decode_image(encoded)

class StoppableThreadPy(unittest.TestCase):
    def test_stoppable_thread(self):
        def func_to_run(stopped, *args):
            self.assertFalse(stopped())
            while not stopped():
                pass
            self.assertTrue(True)

        thread = stoppablethread.StoppableThread(target=func_to_run,args=())
        thread.daemon = True
        thread.start()
        time.sleep(1)
        thread.stop()
        thread.join(5)
        self.assertFalse(thread.isAlive())

    def test_stoppable_looping_thread(self):
        def func_to_run(*args):
            self.assertEqual(args[0] + 1, 1)
            pass

        thread = stoppablethread.StoppableLoopingThread(target=func_to_run, args=[0])
        thread.daemon = True
        thread.start()
        time.sleep(1)
        thread.stop()
        thread.join(5)
        self.assertFalse(thread.isAlive())
