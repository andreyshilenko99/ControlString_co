#!/usr/bin/env python3
from django.apps import apps
import socket
import time


def skypoint():
    port = 666
    okos = apps.get_model('geo', 'SkyPoint').objects.all()
    # HOST = oko.ip
    okos_dict = {}
    for oko in okos:
        okos_dict[oko.name] = [oko.ip]
        for oko in okos_dict:
            for i in okos_dict[oko]:
                aeroPoint = apps.get_model('geo', 'AeroPoints')
                udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                addr = (i, port)
                conn, addr = udp_socket.recvfrom(1024)
                msg = conn.decode('utf-8')
                print('msg: ', msg)
                print('client addr: ', addr)
                udp_socket.sendto(b'OK', addr)
                udp_socket.close()
                if msg:
                    point = aeroPoint(system_name=str(msg[0]),
                                      center_freq=0,
                                      brandwidth=0,
                                      detection_time=str(msg[4]),
                                      comment_string=str(msg[2][0],msg[2][1]),
                                      lat=float(msg[1][0]),
                                      lon=float(msg[1][1]),
                                      azimuth='-',
                                      area_sector_start_grad=float(0),
                                      area_sector_end_grad=float(0),
                                      area_radius_m=float(0),
                                      ip=i,
                                      current_time=msg[4], strig_name=oko)
                    point.save()
