#!/usr/bin/env python3

import socket

HOST = '192.168.1.23'  # Standard loopback interface address (localhost)
PORT = 666        # Port to listen on (non-privileged ports are > 1023)

while True:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print('listening')
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = conn.recv(1024)
                dec = data.decode('utf-8')
                print(dec)
                if not data:
                    break
                conn.sendall(data)