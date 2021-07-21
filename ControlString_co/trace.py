import socket

from django.apps import apps
from google.protobuf import json_format
import datetime
from Trace import found_signal_params_pb2


def trace():
    srizhes = apps.get_model('geo', 'Strizh').objects.all()
    sstrizhes_dict = {}
    for strizh in srizhes:
        sstrizhes_dict[strizh.name] = [strizh.ip1, strizh.ip2]
        for strizh in sstrizhes_dict:
            for i in sstrizhes_dict[strizh]:
                Point = apps.get_model('geo', 'Point')
                port = 10100  # The same port as used by the server
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((i, port))
                data = s.recv(1024)
                s.close()
                signal = found_signal_params_pb2.FoundSignalParams()
                signal.ParseFromString(data[14::])
                signal_dict = json_format.MessageToDict(signal)
                print(signal_dict)
                if signal_dict:
                    point = Point(system_name=str(signal_dict['systemName']), center_freq=signal_dict['centerFrequencyHz'],
                                  brandwidth=signal_dict['bandwidthHz'], detection_time=signal_dict['detectionTime'],
                                  comment_string=signal_dict['commentString'],
                                  lat=float(signal_dict['location']['latitude']),
                                  lon=float(signal_dict['location']['longitude']), azimuth=signal_dict['location']['name'],
                                  area_sector_start_grad=float(signal_dict['location']['areaSectorStartGrad']),
                                  area_sector_end_grad=float(signal_dict['location']['areaSectorEndGrad']),
                                  area_radius_m=float(signal_dict['location']['areaRadiusM']),
                                  ip=i,
                                  current_time=datetime.datetime.now(), strig_name=strizh)
                    point.save()


