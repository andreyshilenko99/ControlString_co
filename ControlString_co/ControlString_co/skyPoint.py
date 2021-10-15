#!/usr/bin/env python3
import json
import pickle

from django.apps import apps
import socket
import time


def skypoint():
    port = 12000  # TODO Add port into models
    okos = apps.get_model('geo', 'SkyPoint').objects.all()
    if len(okos) == 0:
        print("Нет скайпоинтов в бд")
    # HOST = oko.ip
    okos_dict = {}
    try:
        for oko in okos:
            okos_dict[oko.name] = [oko.ip]
            print(okos_dict)
            for oko in okos_dict:
                for i in okos_dict[oko]:
                    aeroPoint = apps.get_model('geo', 'AeroPoints')
                    msg = gimmeLoot(i, port)
                    msg = json.loads(msg)
                    print(type(msg))
                    if msg != "NoNewData":
                        point = aeroPoint(drone_id=str(msg[0]), system_name=str(msg[0]),
                                          center_freq=0,
                                          brandwidth=0,
                                          detection_time=str(msg[4]),
                                          comment_string=str('-'),
                                          drone_lat=float(msg[1][0]),
                                          drone_lon=float(msg[1][1]),
                                          azimuth='azimuth 0',
                                          area_sector_start_grad=float(0),
                                          area_sector_end_grad=float(0),
                                          area_radius_m=float(0),
                                          ip=i,
                                          current_time=str(msg[4]), strig_name=oko, height=msg[3])
                        point.save()
    except TypeError:
        # TODO Добавить исключение или логи или сообщение для серва4ка чтоб он
        pass


def gimmeLoot(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    message = 'GimmeLoot'
    addr = (host, port)
    client_socket.sendto(message.encode(), addr)
    try:
        data, server = client_socket.recvfrom(1024)
        print(data)
        msg = 'OK'
        if data:
            client_socket.sendto(msg.encode(), addr)
        else:
            # TODO Write exception
            pass
        return data
    except socket.timeout:
        print('REQUEST TIMED OUT')


def are_you_alive(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    message = 'Alive?'
    addr = (host, port)
    client_socket.connect(("192.168.1.159", port))
    client_socket.send(message.encode())
    try:
        data, server = client_socket.recvfrom(1024)
        if data.decode() == 'Alive_bro':
            print(data.decode())
            pass
    except socket.timeout:
        print('REQUEST TIMED OUT')


def get_old(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.settimeout(1.0)
    message = 'Oldshit'
    addr = (host, port)
    client_socket.sendto(message.encode(), addr)
    value, server = client_socket.recvfrom(1024)
    value = int(value.decode())
    try:
        for i in range(value):
            data, server = client_socket.recvfrom(1024)
            print(i, data)
            msg = 'OK'
            client_socket.sendto(msg.encode(), addr)
    except socket.timeout:
        print('REQUEST TIMED OUT')
