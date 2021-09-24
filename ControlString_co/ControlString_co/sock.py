#!/usr/bin/env python3

import socket
import time

HOST = '192.168.1.23'  # Standard loopback interface address (localhost)
PORT = 666        # Port to listen on (non-privileged ports are > 1023)
#
# while True:
#     with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
#         s.bind((HOST, PORT))
#         s.listen()
#         print('listening')
#         conn, addr = s.accept()
#         with conn:
#             print('Connected by', addr)
#             while True:
#                 data = conn.recv(1024)
#                 dec = data.decode('utf-8')
#                 print(dec)
#                 if not data:
#                     break
#                 conn.sendall(data)

# socket - функция создания сокета
# первый параметр socket_family может быть AF_INET или AF_UNIX
# второй параметр socket_type может быть SOCK_STREAM(для TCP) или SOCK_DGRAM(для UDP)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# bind - связывает адрес и порт с сокетом
addr = (HOST, PORT)
udp_socket.bind(addr)

# Бесконечный цикл работы программы
while True:

    print('wait data...')
    # recvfrom - получает UDP сообщения
    conn, addr = udp_socket.recvfrom(1024)
    msg = conn.decode('utf-8')
    print('msg: ', msg)
    print('client addr: ', addr)
    udp_socket.sendto(b'OK', addr)
    # sendto - передача сообщения UDP

# udp_socket.close()