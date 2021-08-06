import re
import time
import datetime
import json
import requests
from django.core.serializers import serialize

from geo.models import Strizh
from views import collect_logs

lines_map = {'обогрев': 1,
             'вентилятор': 2,
             'БП ПЭВМ': 3,
             'БП Шелест': 5,
             'БП АПЕМ': 7,
             'ЭВМ1': 10,
             'ЭВМ2': 14,
             'РЕЗЕТ': 15,
             }

lines_control_map = {
    'вентилятор': 2,
    'БП ПЭВМ': 4,
    'БП Шелест': 6,
    'БП АПЕМ': 8,
    'ЭВМ1': 9,
    'ЭВМ2': 13,
    'датчик потока': 16,
}


def get_strizhes():
    geojson_strizhes = serialize('geojson', Strizh.objects.all())
    parsed_json = (json.loads(geojson_strizhes))
    arr_strizh = []
    for i in range(len(parsed_json.get("features"))):
        strizh_name = parsed_json.get("features")[i].get("properties").get("name")
        arr_strizh.append(strizh_name)
    return arr_strizh


def obtain_state(url, line_name, to_collect_logs=False):
    global lines_control_map
    result_state = 0
    line = lines_control_map.get(line_name)
    try:
        stroka = requests.get(url + 'io.cgi?io{}'.format(line), auth=auth, timeout=0.05) \
            .content.decode("utf-8")
    except:
        stroka = 'err in connection to uniping'

    stroka_list = re.findall('[0-9]+', stroka)
    if 'ok' in stroka and len(stroka_list) == 3:
        result_state = stroka_list[1]
    state = "вкл" if int(result_state) == 1 else "выкл"
    log_str = 'контроль {} {}ючен'.format(line_name, state)
    if to_collect_logs:
        collect_logs(log_str)
    return state


def get_complex_state(url):
    state0 = obtain_state(url, 'датчик потока')
    state1 = obtain_state(url, 'БП ПЭВМ')
    state2 = obtain_state(url, 'БП Шелест')
    state3 = obtain_state(url, 'БП АПЕМ')
    state4 = obtain_state(url, 'ЭВМ1')
    state5 = obtain_state(url, 'ЭВМ2')
    states = [state0, state1, state2, state3, state4, state5]
    complex_state = 'включен' if all([True if x == 'вкл' else False for x in states]) else 'выключен'
    return complex_state


def get_datetime_drone(time_dron):
    t1 = time_dron.split('-')
    t2 = t1[-1].split(' ')
    t3 = t2[-1].split(':')
    now = datetime.datetime.now()
    return now.replace(year=int(t1[0]), month=int(t1[1]), day=int(t2[0]), hour=int(t3[0]),
                       minute=int(t3[1]), second=int(t3[2]))


def check_condition(value, low_border, high_border, condition="температура"):
    assert low_border < high_border, 'error in defining low or high border'
    try:
        value = float(value)
        if low_border < value < high_border:
            return 0
        elif value > high_border:
            print("{} выше разрешенной ({} > {})".format(condition, value, high_border))
            return 1
        elif value < low_border:
            print("{} ниже разрешенной ({} < {})".format(condition, value, low_border))
            return -1
    except:
        print('value is not ok')
        print('error')


def send_impulse(url, line_name, time_pulse=3, action=''):
    global auth, lines_map
    line = lines_map.get(line_name)
    try:
        result_get = requests.get(url + 'io.cgi?io{}=f,{}'.format(line, time_pulse), auth=auth,
                                  timeout=0.05) \
            .content.decode("utf-8")
    except:
        result_get = 'err in connection to uniping'
    if 'ok' in result_get:
        collect_logs("{} {}ючен".format(line_name, action))
    else:
        print("send_impulse error")
    time.sleep(time_pulse + 1)


def send_line_command(url, line_name, arg):
    # arg = 0 or 1
    global auth, lines_map

    state = "вкл" if arg == 1 else "выкл"
    log_str = '{} {}ючен'.format(line_name, state)
    line = lines_map.get(line_name)
    try:
        result_get = requests.get(url + 'io.cgi?io{}={}'.format(line, arg), auth=auth, timeout=0.05) \
            .content.decode("utf-8")
    except:
        result_get = 'ошибка соединения с uniping'
    if 'ok' in result_get:
        collect_logs("{}".format(log_str))
    else:
        collect_logs("проверьте, выбран ли стриж")
