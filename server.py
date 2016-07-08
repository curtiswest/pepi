import socket
import communication
import numpy as np

camera_id = "001"

def getData():
    z = np.random.random((500, 500))  # Test data
    print z.dtype
    return z


def waitForClient(sock):
    connection, address = sock.accept()
    communication.send_msg(connection, communication.SERVER_READY)
    msg = communication.recv_msg(connection)
    print "received ", msg
    return connection


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", 10000))
server_socket.listen(5)

while(1):

    connection = waitForClient(server_socket)
    #should receive CLIENT_READY
    print 'received ', communication.recv_msg(connection)
    #send camera id
    communication.send_msg(connection, camera_id)
    #should receive CAMERA_ID_ACK
    print 'received ', communication.recv_msg(connection)
    data = getData()
    communication.send_img(connection, data)

server_socket.close()

