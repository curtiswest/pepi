import unittest
import zmq
from communication.communication import CommunicationSocket, Poller
from utils.utils import in_out
import communication.pymsg

class TestCommunicationLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 49982
        print('Setting test port to: {}'.format(cls.port))

    def test_init_type_checking(self):
        with self.assertRaises(TypeError):
            _ = CommunicationSocket('hello')
        with self.assertRaises(TypeError):
            _ = CommunicationSocket(0.1)
        with self.assertRaises(ValueError):
            _ = CommunicationSocket(123)

        CommunicationSocket(CommunicationSocket.SocketType.SERVER).close()
        CommunicationSocket(CommunicationSocket.SocketType.REPLY).close()
        CommunicationSocket(CommunicationSocket.SocketType.CLIENT).close()
        CommunicationSocket(CommunicationSocket.SocketType.REQUEST).close()
        CommunicationSocket(CommunicationSocket.SocketType.PUBLISHER).close()
        CommunicationSocket(CommunicationSocket.SocketType.SUBSCRIBER).close()
        CommunicationSocket(CommunicationSocket.SocketType.ROUTER).close()
        CommunicationSocket(CommunicationSocket.SocketType.DEALER).close()
        CommunicationSocket(CommunicationSocket.SocketType.PUSH).close()
        CommunicationSocket(CommunicationSocket.SocketType.PULL).close()
        CommunicationSocket(CommunicationSocket.SocketType.PAIR).close()

    def test_connect_disconnect(self):
        socket = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        socket.connect_to('tcp://localhost:{}'.format(self.port))
        socket.disconnect_from('tcp://localhost:{}'.format(self.port))
        socket.close()

        # Socket closed, try to reconnect
        socket.connect_to('tcp://localhost:{}'.format(self.port))
        socket.bind_to('tcp://*:{}'.format(self.port))
        socket.disconnect_from('tcp://localhost:{}'.format(self.port))
        socket.close()

    def test_sockopts(self):
        socket = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)

        # Test Identity
        self.assertEqual(socket.identity, socket.getsockopt(zmq.IDENTITY))
        self.assertEqual(socket.identity, socket._socket.identity)
        socket.identity = 'test_identity'
        self.assertEqual('test_identity', socket.getsockopt(zmq.IDENTITY))
        self.assertEqual('test_identity', socket._socket.identity)

        # Test Send Timeout
        self.assertEqual(socket.send_timeout, socket.getsockopt(zmq.SNDTIMEO))
        self.assertEqual(socket.send_timeout, socket._socket.sndtimeo)
        socket.send_timeout = 1000
        self.assertEqual(1000, socket.getsockopt(zmq.SNDTIMEO))
        self.assertEqual(1000, socket._socket.sndtimeo)

        # Test Recv Timeout
        self.assertEqual(socket.receive_timeout, socket.getsockopt(zmq.RCVTIMEO))
        self.assertEqual(socket.receive_timeout, socket._socket.rcvtimeo)
        socket.receive_timeout = 1000
        self.assertEqual(1000, socket.getsockopt(zmq.RCVTIMEO))
        self.assertEqual(1000, socket._socket.rcvtimeo)

        # Test Router Mandatory
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            socket.router_mandatory(True)
        socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        socket.router_mandatory(True)
        socket.router_mandatory(False)
        socket.router_mandatory(0)
        socket.router_mandatory(1)

        # Test Linger
        self.assertEqual(socket.linger, socket.getsockopt(zmq.LINGER))
        self.assertEqual(socket.linger, socket._socket.linger)
        socket.linger = 1000
        self.assertEqual(1000, socket.getsockopt(zmq.LINGER))
        self.assertEqual(1000, socket._socket.linger)

    def test_send_recv_against_socket_types(self):
        request = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        request.connect_to('tcp://localhost:{}'.format(self.port))

        reply = CommunicationSocket(CommunicationSocket.SocketType.REPLY)
        reply.bind_to('tcp://*:{}'.format(self.port))

        with self.assertRaises(ValueError):
            request.send(None)
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            request.send_multipart('ident', 'test')
        request.send('test')

        with self.assertRaises(CommunicationSocket.SocketTypeError):
            reply.receive_multipart()
        message = reply.receive()
        self.assertEqual('test', message)
        reply.send('reply')
        request.receive()
        reply.close()

        router = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        router.bind_to('tcp://*:{}'.format(self.port))
        request.send('test to router')
        router.router_mandatory(True)
        router.send_timeout = 3000
        router.receive_timeout = 3000

        _, _ = router.receive_multipart()
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            router.send('test')
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            router.receive()
        with self.assertRaises(CommunicationSocket.MessageRoutingError):
            router.send_multipart(identity='invalid_id', message='test')

        router.close()
        request.close()

    def test_timeout(self):
        request = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        request.connect_to('tcp://localhost:{}'.format(self.port))

        reply = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        reply.bind_to('tcp://*:{}'.format(self.port))

        reply.receive_timeout = 1000
        reply.send_timeout = 1000
        request.receive_timeout = 1000
        request.send_timeout = 1000

        with self.assertRaises(CommunicationSocket.TimeoutError):
            reply.receive_multipart()
        # TODO test sending timeout

    def test_lockstep(self):
        request = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        request.connect_to('tcp://localhost:{}'.format(self.port))

        reply = CommunicationSocket(CommunicationSocket.SocketType.REPLY)
        reply.bind_to('tcp://*:{}'.format(self.port))

        with self.assertRaises(CommunicationSocket.StateError):
            reply.send('test')

        with self.assertRaises(CommunicationSocket.StateError):
            request.receive()

    def test_multipart(self):
        router = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        router.bind_to('tcp://*:{}'.format(self.port))

        with self.assertRaises(ValueError):
            router.send_multipart(identity=None, message='message')
        with self.assertRaises(TypeError):
            router.send_multipart(identity='fake_id', message=int(30))

    def test_req_rep(self):
        request = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        request.connect_to('tcp://localhost:{}'.format(self.port))

        reply = CommunicationSocket(CommunicationSocket.SocketType.REPLY)
        reply.bind_to('tcp://*:{}'.format(self.port))

        # Request -> Reply
        msg_in = 'request message'
        request.send(msg_in)
        msg_out = reply.receive()
        self.assertEqual(msg_in, msg_out, 'Message malformed during Request->Reply transport')

        # Reply -> Request
        reply.send(msg_out)
        req_msg = request.receive()
        self.assertEqual(msg_out, req_msg, 'Message malformed during Reply->Request transport')

        request.close()
        reply.close()

    def test_req_router(self):
        request = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        request.connect_to('tcp://localhost:{}'.format(self.port))

        router = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        router.bind_to('tcp://*:{}'.format(self.port))

        # Request -> Router
        msg_in = 'request message'
        request.send(msg_in)
        identity_out, msg_out = router.receive_multipart()
        self.assertIsNotNone(identity_out, 'Identity value is None, unwrapped incorrectly?')
        self.assertEqual(msg_in, msg_out, 'Message malformed during Req->Router transport')

        # Router -> Request
        router.send_multipart(identity_out, msg_out)
        rep_msg = request.receive()
        self.assertEqual(rep_msg, msg_out, 'Message malformed during Router->Req transport')

        request.close()
        router.close()

    def test_dealer_router(self):
        dealer = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        dealer.connect_to('tcp://localhost:{}'.format(self.port))

        router = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        router.bind_to('tcp://*:{}'.format(self.port))
        router.setsockopt(zmq.ROUTER_MANDATORY, True)

        # Dealer -> Router
        msg_in = 'dealers message'
        dealer.send(msg_in)
        identity_out, msg_out = router.receive_multipart()
        self.assertEqual(msg_in, msg_out, 'Message malformed during Dealer->Router transport' + in_out(msg_in, msg_out))

        # Router -> Dealer
        router.send_multipart(identity_out, msg_out)
        dealer_msg = dealer.receive()
        self.assertEqual(dealer_msg, msg_out, 'Message malformed during Router->Dealer transport' +
                         in_out(dealer_msg, msg_out))

        router.close()
        dealer.close()

    def test_pub_sub(self):
        publisher = CommunicationSocket(CommunicationSocket.SocketType.PUBLISHER)
        publisher.bind_to('tcp://*:{}'.format(self.port))

        subscriber = CommunicationSocket(CommunicationSocket.SocketType.SUBSCRIBER)
        subscriber.connect_to('tcp://localhost:{}'.format(self.port))
        subscriber.subscribe('')

        request = CommunicationSocket(CommunicationSocket.SocketType.REQUEST)
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            request.subscribe('')
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            request.publish('message', 'topic')
        with self.assertRaises(CommunicationSocket.SocketTypeError):
            request.listen()

        for i in range(0, 10000):
            publisher.publish(str(i))

        subscriber.listen()

    def test_filelike_adapter(self):
        router = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)
        router.bind_to('tcp://*:{}'.format(self.port))
        dealer = CommunicationSocket(CommunicationSocket.SocketType.DEALER)
        dealer.connect_to('tcp://localhost:{}'.format(self.port))

        dealer.write('data')
        router.receive_multipart()

        dealer.data_wrapper_class = communication.pymsg.FileLikeDataWrapper.serialize_data
        dealer.write('data')
        router.receive_multipart()
        dealer.flush()

        with self.assertRaises(CommunicationSocket.SocketTypeError):
            router.write('data')

##########################
###       POLLER       ###
##########################

    def test_poller(self):
        poller = Poller()
        socket = CommunicationSocket(CommunicationSocket.SocketType.ROUTER)

        with self.assertRaises(TypeError):
            poller.register(int(1), Poller.PollingType.POLLIN)
        with self.assertRaises(TypeError):
                poller.register(socket, None)
        with self.assertRaises(ValueError):
            poller.register(socket, 123912010912)

        poller.register(socket, Poller.PollingType.POLLIN)
        poller.register(socket, Poller.PollingType.POLLOUT)
        poller.register(socket, Poller.PollingType.POLLINOUT)
        poller.poll(10)
        with self.assertRaises(TypeError):
            poller.poll('str')
        with self.assertRaises(TypeError):
            poller.unregister('str')
        poller.unregister(socket)
        poller.register(socket, Poller.PollingType.NONE)
        poller.poll(1)

