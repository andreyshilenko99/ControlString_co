import time
from socket import socket, AF_INET, SOCK_STREAM


def set_gain(host, gain):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, 1201))
    global data_resp
    i = 0  # TODO change loop
    set_gain = bytearray(b'\xe4\x44\x01\x00\x00\xbb\x0f\xf1\xff')
    set_gain[6] = gain
    set_gain[7] = 256 - gain
    while i < 3:
        sock.send(set_gain)
        data_resp = sock.recv(1024)
        print(data_resp)
        set_gain[4] += 1
        set_gain[5] -= 1
        time.sleep(1)
        i += 1
    if get_gain(host) == gain:
        return True
    else:
        return False  # TODO exception


def get_gain(host):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, 1201))
    global data_resp
    i = 0  # TODO change loop
    get_gain = bytearray(b'\xe4\x45\x01\x00\x00\xba\x00\x00\x00')
    while i < 3:
        sock.send(get_gain)
        data_resp = sock.recv(1024)
        print(data_resp)
        get_gain[4] += 1
        get_gain[5] -= 1
        time.sleep(1)
        i += 1
    return data_resp[7]



def get_state(host):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, 1201))
    stat = bytearray(b'\xe4\x01\x00\x00\x01\xfe\x00\x00')
    sock.send(stat)
    i = 0  # TODO change loop
    ll = b'\xe4\x01\x04\x00\x00\xfb\x01\x10:\x805\xff'
    lol = b'\xe4\x01\x04\x00\x00\xfb\x01\x10:\x805\xff'
    while i < 3:
        stat[4] += 1
        stat[5] -= 1
        i += 1
        data_resp = sock.recv(1024)
        print(data_resp)


def jammer_on_off(host, value):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((str(host), 1201))
    kk = b'\xe4\x03\x01\x00\x00\xfc\x05\xfb\xff\xe4\x03\x01\x00\x00\xfc\x01\xff\xff'
    ll = b'\xe4\x03\x01\x00\x00\xfc\x05\xfb\xff\xe4\x03\x01\x00\x00\xfc\x01\xff\xff'
    jam_on = bytearray(b'\xe4\x03\x01\x00\x00\xfc\x02\xfe\xff')
    jam_off = bytearray(b'\xe4\x03\x01\x00\x00\xfc\x00\x00\x00')
    global data_resp
    i = 0  # TODO change loop
    while i < 3:
        if value == 'on':
            sock.send(jam_on)
        elif value == 'off':
            sock.send(jam_off)
        else:
            return False  # TODO exception
        data_resp = sock.recv(1024)
        print(data_resp)
        jam_on[4] += 1
        jam_on[5] -= 1
        jam_off[4] += 1
        jam_off[5] -= 1
        time.sleep(1)
        i += 1
    return 0

if __name__ == "__main__":
    jammer_on_off('192.168.2.102','off')
    get_state('192.168.2.102')
    b'\xe4\x03\x01\x00\x00\xfc\x05\xfb\xff\xe4\x03\x01\x00\x00\xfc\x01\xff\xff'
    b'\xe4\x03\x01\x00\x00\xfc\x05\xfb\xff\xe4\x03\x01\x00\x00\xfc\x01\xff\xff'
    b'\xe4\x01\x04\x00\x01\xfa\x01R?\x80\xee\xfe'
    