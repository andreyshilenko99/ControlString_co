import socket
from found_signal_params_pb2 import FoundSignalParams
import json

def trace(host):
    port = 10100  # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    data = s.recv(1024)
    s.close()
    signal = FoundSignalParams()
    signal.ParseFromString(data[14::])
    print(json.dumps(signal))

    # TODO Запись в БД и Создание отдельного приложения


# trace('192.168.2.241')