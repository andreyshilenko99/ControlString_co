import socket
import time

from Trace import trace_remote_pb2 as con


def check_state(host):
    # TODO Исключения
    message = con.TraceRemoteMessage()
    message.message_type = 7

    lel = message.SerializeToString()
    print(message)

    port = 10100  # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(bytearray(lel))
    data = s.recv(1024)
    # signal = con.TraceRemoteMessage()
    # print(data)

    # data = signal.ParseFromString(data)
    data = data[9:-8]
    # print(data)
    s.close()
    print(data)
    if data == b'\x00\x10\x00':
        return "all_stop"
    elif data == b'\x01\x10\x00':
        return "scan_on"
    elif data == b'\x00\x10\x01':
        return "jammer_on"


def scan_on_off(host):
    # TODO Исключения
    message = con.TraceRemoteMessage()
    message.message_type = 0
    mes = message.SerializeToString()
    print(message)
    port = 10100  # The same port as used by the server
    _try = 0
    while _try < 3:
        if check_state(host) == "all_stop":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.send(bytearray(mes))
            data = s.recv(1024)
            print(data)
            s.close()
            time.sleep(1)
            if data and check_state(host) == "scan_on":
                return "scan_on"
            elif _try > 3:
                return "error"
            else:
                _try += 1
        else:
            return

    while _try < 3:
        if check_state(host) == "scan_on":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.send(bytearray(mes))
            data = s.recv(1024)
            print(data)
            s.close()
            time.sleep(1)
            if data and check_state(host) == "all_stop":
                return "all_stop"
            elif _try > 3:
                return "error"
            else:
                _try += 1
        else:
            return


def jammer_on_off(host):
    # TODO Исключения
    message = con.TraceRemoteMessage()
    message.message_type = 1
    mes = message.SerializeToString()
    print(message)
    port = 10100  # The same port as used by the server
    while True:
        if check_state(host) == "all_stop":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.send(bytearray(mes))
            data = s.recv(1024)
            print(data)
            s.close()
            if data and check_state(host) == "jammer_on":
                return "jammer_on"
            else:
                return "error"
        elif check_state(host) == "scan_on":
            state = check_state(host)
            while state == "scan_on":
                scan_on_off(host)
                time.sleep(1)
                state = check_state(host)

        elif check_state(host) == "jammer_on":
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((host, port))
            s.send(bytearray(mes))
            data = s.recv(1024)
            print(data)
            s.close()
            if data and check_state(host) == "all_stop":
                return "all_stop"
            else:
                return "error"


# Примеры ответов Trace
# all_stop = b'\x10\x00\x00\x00\x08\x072\x0c\x08\x00\x10\x00\x18\x01"\x04\x08\x00\x10\x00'
# scan_on = b'\x10\x00\x00\x00\x08\x072\x0c\x08\x01\x10\x00\x18\x01"\x04\x08\x00\x10\x00'
# jammer_on = b'\x10\x00\x00\x00\x08\x072\x0c\x08\x00\x10\x01\x18\x01"\x04\x08\x00\x10\x00'

# check_state('192.168.2.241')
