import socket

from Trace import trace_remote_pb2 as con


def lol(host):
    message = con.TraceRemoteMessage()
    message.message_type = 0

    lel = message.SerializeToString()
    print(message)

    port = 10100  # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(bytearray(lel))
    s.close()
    print('dwk')

