import time
from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)
sock.connect(('192.168.2.101', 1201))
mes = bytearray(b'\xe4\x01\x00\x00\x00\xff\x00\x00\x00')
fh = b'\xe4\x03\x01\x00'
sh = b'\x01\xff\xff'
cnt = 0
sum = 252
slash = "\\"
while True:
    sock.send(mes)
    data_resp = sock.recv(1024)
    print(data_resp)
    time.sleep(1)
    if len(data_resp) < 25:
        sum = data_resp[5]
        msg = (slash + str((hex(cnt)[1::]) + '0') + slash + str(hex(sum)[1::])).encode()
        message = fh + msg + sh
        sock.send(message)
        print(message)
        # cnt += 1
        # sum -= 1
        data = sock.recv(1024)
        print(data)
        time.sleep(1)

# sock = socket(AF_INET, SOCK_STREAM)
# sock.connect(('192.168.2.120', 23))
# msg = b'\xba\xba\xad\xde\x06\x00\x00\x00\x0c\x00\x00\x00\x3e\x00'
# sock.send(msg)
# daa = sock.recv(1024)
# print(daa)
