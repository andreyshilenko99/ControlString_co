from socket import socket, AF_INET, SOCK_STREAM


def apem_set_gain(host, gain, on_off):
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect((host, 23))
    global data_resp
    i = 0  # TODO change loop + exception + check answer
    set_gain = bytearray(b'\xba\xba\xad\xde\x06\x00\x00\x00\x0c\x00\x00\x00\x00\x00')
    if on_off == 'on':
        set_gain[13] += 1
    else:
        pass
    set_gain[12] = 32 - gain
    sock.send(set_gain)
    data_resp = sock.recv(1024)
    print(data_resp)
    if data_resp[15] == set_gain[12] and set_gain[12] == data_resp[12]:
        return "Kaif"
    else:
        return  False


apem_set_gain('192.168.2.120', 2, 'off')

lol = b'\xba\xba\xad\xde\x10\x00\x00\x00\x07\x00\x00\x00\x01\x00\x00\x0c\x00\x00\x1c\x00\x00\x00\x00\x01'
loll = b'\xba\xba\xad\xde\x10\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00 \x00\x00\x1c\x00\x02\x00\x00\x01'
off = b'\xba\xba\xad\xde\x10\x00\x00\x00\x07\x00\x00\x00\x01\x00\x00\x1e\x00\x00\x1b\x00\x02\x00\x00\x01'
on = b'\xba\xba\xad\xde\x10\x00\x00\x00\x07\x00\x00\x00\x00\x00\x00\x1e\x00\x00\x1b\x00\x00\x00\x00\x00'