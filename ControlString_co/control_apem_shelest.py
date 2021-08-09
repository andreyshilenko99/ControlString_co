import time
from socket import socket, AF_INET, SOCK_STREAM

def apem_set_gain(host, gain, on_off):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, 23))
    global data_resp
    i = 0  # TODO change loop + exception
    set_gain = bytearray(b'\xba\xba\xad\xde\x06\x00\x00\x00\x0c\x00\x00\x00\x00\x00')
    if on_off == 'on':
        set_gain[13] += 1
    else:
        pass
    set_gain[12] = 32 - gain
    sock.send(set_gain)
    data_resp = sock.recv(1024)
    print(data_resp)
    time.sleep(1)
    i += 1
    print(set_gain)