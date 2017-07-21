import unittest
import zmq
from communication.communication import CommunicationSocket
from random import randint
from utils import in_out


class TestCommunicationLibrary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = randint(5000, 60000)
        cls.port = 30001
        print('Setting test port to: {}'.format(cls.port))

    def test_init(self):
        with self.assertRaises(TypeError):
            socket = CommunicationSocket(1231231)

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
