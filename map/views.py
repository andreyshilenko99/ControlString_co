from django.shortcuts import render
from django.http import HttpResponse

import re
import time

import requests
from django.shortcuts import render


def index(request):
    return render(request, "index.html")


#
#
nomer_strizha = 0
start_datetime = "Начало"
end_datetime = "Конец"
logs = ''
logs_list = []


c = dict(nomer_strizha=0, start_datetime=start_datetime, end_datetime=end_datetime)

#
def journal(request):
    global c
    return render(request, "journal.html", context=c)


#
#
def main(request):
    return render(request, "main.html", context=c)


#
def configuration(request):
    return render(request, "configuration.html", context=c)


def butt_skan_all(request):
    global c
    # nomer_strizha = 0
    print('skanirovanie vseh')
    # TODO action 1 button
    return render(request, "main.html", context=c)


def butt_glush_all(request):
    global c
    print('glushenie vseh')
    # TODO action 2 button
    return render(request, "main.html", context=c)


def butt_gps_all(request):
    global c
    print('gps vseh')
    # TODO action 3 button
    return render(request, "main.html", context=c)


def butt_ku_all(request):
    global c
    print(c)
    print('KU vseh #', nomer_strizha)
    # TODO action 4 button
    return render(request, "main.html", context=c)


#
def choose_nomer_strizha(request):
    global nomer_strizha
    global c
    print(c)
    # TODO action 2 button
    if request.method == 'POST':
        nomer = request.POST['nomer_strizha']
        print('send', nomer, '\n')
        nomer_strizha = nomer
        c = {'nomer': nomer_strizha}
        # return render(request,"main.html", context=c)
    return render(request, "main.html", context=c)


# def update_nomer_strizha(request):
#     error = False
#     if 'nomer' in request.GET:
#         nomer = request.GET['nomer']
#         if not nomer:
#             error = True
#         else:
#             return render(request, 'main.html',
#                 {'nomer': nomer})
#
#     return render(request, 'main.html',
#         {'error': error})


def butt_skan(request):
    global c
    if nomer_strizha != 0:
        print('skanirovanie dlya strizha #', nomer_strizha)
        # TODO action 1 button

    return render(request, "main.html", context=c)


#
def butt_glush(request):
    global c
    if nomer_strizha != 0:
        print('glushenie dlya strizha #', nomer_strizha)
        # TODO action 2 button
    return render(request, "main.html", context=c)


def butt_gps(request):
    global c
    if nomer_strizha != 0:
        print('gps dlya strizha #', nomer_strizha)
        # TODO action 3 button
    return render(request, "main.html", context=c)


def butt_ku(request):
    global c
    if nomer_strizha != 0:
        print('KU dlya strizha #', nomer_strizha)
        # TODO action 4 button
    return render(request, "main.html", context=c)


def apply_period(request):
    global c, start_datetime, end_datetime
    # TODO action 2 button
    if request.method == 'POST':
        if request.POST.get('start_datetime'):
            start = request.POST['start_datetime']
            print('got start ', start, '\n')
            start_arr = start.split(' ')
            start_datetime = "-".join(start_arr)
        if request.POST.get('end_datetime'):
            end = request.POST['end_datetime']
            print('got end', end, '\n')
            end_arr = end.split(' ')
            end_datetime = "-".join(end_arr)

        c = {'start_datetime': start_datetime,
             'end_datetime': end_datetime}
        # return render(request, "journal.html", context=c)
    return render(request, "journal.html", context=c)


low_t = 10
high_t = 60
low_h = 5
high_h = 85
url = "http://192.168.2.51/"
auth = ('user', '555')
message_condition = ''


def return_conditions():
    global low_t, high_t, low_h, high_h, humidity, humidity_temp
    global url
    global auth
    weather_state = 'not ok'

    temp = requests.get(url + 'thermo.cgi?t1', auth=auth)
    temp_str = temp.content.decode("utf-8")
    temp_list = re.findall('[0-9]+', temp_str)
    if len(temp_list) > 0:
        temperature = '.'.join(temp_list)
        c['temperature'] = temperature
    print('temperature:', temperature)

    hum = requests.get(url + 'relhum.cgi?h1', auth=auth)
    hum_str = hum.content.decode("utf-8")
    hum_list = re.findall('[0-9]+', hum_str)
    if len(hum_list) > 1:
        humidity = hum_list[0]
        humidity_temp = '.'.join(hum_list[1:])
        c['humidity'] = humidity
        c['humidity_temp'] = humidity_temp
    print('humidity:', humidity, '% humidity_temp:', humidity_temp)
    if temperature and humidity:
        if low_t < float(temperature) < high_t and low_h < float(humidity) < high_h:
            weather_state = "OK"
        else:
            weather_state = "NOT OK !!!"
    else:
        weather_state = "not known, data cannot be obtained"
    c["weather_state"] = weather_state
    return temperature, humidity, humidity_temp, weather_state

temperature, humidity, humidity_temp, weather_state = return_conditions()

def get_conditions(request):
    # global temperature, humidity, humidity_temp, weather_state
    temperature, humidity, humidity_temp, weather_state = return_conditions()
    c['temperature'] = temperature
    c['humidity'] = humidity
    c['humidity_temp'] = humidity_temp
    c["weather_state"] = weather_state
    return render(request, "main.html", context=c)


def check_condition(value, low_border, high_border, condition="температура"):
    assert low_border < high_border, 'error in defining low or high border'
    try:
        value = float(value)
    except:
        print('value is not ok')
    if low_border < value < high_border:
        return 0
    elif value > high_border:
        print("{} выше разрешенной ({} > {})".format(condition, value, high_border))
        return 1
    elif value < low_border:
        print("{} ниже разрешенной ({} < {})".format(condition, value, low_border))
        return -1



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
    'БП ПЭВМ': 4,
    'БП Шелест': 6,
    'БП АПЕМ': 8,
    'ЭВМ1': 9,
    'ЭВМ2': 13,
    'датчик потока': 16,
}


def collect_logs(log_string):
    global logs, logs_list
    time_obj = time.gmtime()
    y, m, d, h, min, sec, _, _, _ = time_obj

    date_time = "{}.{}.{}   {}:{}:{}  ".format(d, m, y, h + 3, min, sec)
    log_one = date_time + log_string + '\n\t'
    logs += log_one
    logs_list.append(log_one)
    c['logs_list'] = logs_list
    print(log_one)


def send_line_command(line_name, arg):
    # arg = 0 or 1
    global url, auth, lines_map
    state = "вкл" if arg == 1 else "выкл"
    log_str = '{} {}ючен'.format(line_name, state)
    line = lines_map.get(line_name)
    result_get = requests.get(url + 'io.cgi?io{}={}'.format(line, arg), auth=auth) \
        .content.decode("utf-8")
    if 'ok' in result_get:
        collect_logs("{}".format(log_str))
    else:
        collect_logs("send_line_command error")


def send_impulse(line_name, time_pulse=3, action=''):
    global url, auth, lines_map
    line = lines_map.get(line_name)
    result_get = requests.get(url + 'io.cgi?io{}=f,{}'.format(line, time_pulse), auth=auth) \
        .content.decode("utf-8")
    if 'ok' in result_get:
        # print("send_impulse ok {}".format(line_name))
        collect_logs("{} {}ючен".format(line_name, action))
    else:
        print("send_impulse error")
    time.sleep(time_pulse + 1)


# def turn_on_ventilator():
#     print('turning on ventilator')
#     global url, auth
#     temp = requests.get(url + 'io.cgi?io2=1', auth=auth)
#     # temp_str = temp.content.decode("utf-8")
#     # temp_list = re.findall('[0-9]+', temp_str)
#
#
# def turn_on_obogrev():
#     print('turning on obogrev')
#     global url, auth
#     temp = requests.get(url + 'io.cgi?io1=1', auth=auth)
#     # http: // 192.168.2.51/io.cgi?io2 = 0


def do_nothing():
    print('do nothing, all is good')
    #     TODO check ventilator state


def obtain_state(line_name, to_collect_logs=False):
    global lines_control_map
    result_state = 0
    line = lines_control_map.get(line_name)
    stroka = requests.get(url + 'io.cgi?io{}'.format(line), auth=auth) \
        .content.decode("utf-8")
    stroka_list = re.findall('[0-9]+', stroka)
    if 'ok' in stroka and len(stroka_list) == 3:
        result_state = stroka_list[1]
    state = "вкл" if int(result_state) == 1 else "выкл"
    log_str = 'контроль {} {}ючен'.format(line_name, state)
    if to_collect_logs:
        collect_logs(log_str)
    # print(log_str)
    return state


def set_correct_temperature(temperature_state):
    global temperature
    if temperature_state != 0:
        while temperature_state != 0:
            temperature_state = check_condition(temperature, low_border=low_t, high_border=high_t)
            if temperature_state == 1:
                send_line_command('вентилятор', 1)
                state0 = obtain_state('датчик потока')
                if state0 != 'вкл':
                    collect_logs('АВАРИЯ! отсутствует вентиляция, возможен перегрев оборудования')
            elif temperature_state == -1:
                send_line_command('обогрев', 1)
            time.sleep(60)


complex_state = ''


def check_states_on():
    # global complex_state
    # if complex_state == 'вкл':
    temperature_state = check_condition(temperature, low_border=low_t, high_border=high_t)
    if temperature_state != 0:
        collect_logs('температура не в порядке')
        set_correct_temperature(temperature_state)

    state0 = obtain_state('датчик потока', to_collect_logs=True)
    if state0 != 'вкл':
        collect_logs('АВАРИЯ! отсутствует вентиляция, возможен перегрев оборудования')
        # send_line_command('датчик потока', arg=1)

    state1 = obtain_state('БП ПЭВМ', to_collect_logs=True)
    if state1 != 'вкл':
        collect_logs('АВАРИЯ! БП ПЭВМ выключен')
    state2 = obtain_state('БП Шелест', to_collect_logs=True)
    if state2 != 'вкл':
        collect_logs('АВАРИЯ! БП Шелест выключен')
    state3 = obtain_state('БП АПЕМ', to_collect_logs=True)
    if state3 != 'вкл':
        collect_logs('АВАРИЯ! БП АПЕМ выключен')
    state4 = obtain_state('ЭВМ1', to_collect_logs=True)
    if state4 != 'вкл':
        collect_logs('АВАРИЯ! ЭВМ1 выключен')
        send_impulse('ЭВМ1', time_pulse=3, action='вкл')
    state5 = obtain_state('ЭВМ2', to_collect_logs=True)
    if state5 != 'вкл':
        collect_logs('АВАРИЯ! ЭВМ2 выключен')
        send_impulse('ЭВМ2', time_pulse=3, action='вкл')

    states_names = [state1, state2, state3, state4, state5]
    states = [True if st == 'вкл' else False for st in states_names]
    if all(states):
        return True


def turn_on_bp(request):
    global comlex_state, logs
    temperature_state = check_condition(temperature, low_border=low_t, high_border=high_t)
    if temperature_state != 0:
        print('температура не в порядке')
        set_correct_temperature(temperature_state)
    elif temperature_state == 0:
        # turn everything on
        send_line_command('вентилятор', 1)

        state1 = obtain_state('БП ПЭВМ')
        if state1 != 'вкл':
            # collect_logs('БП ПЭВМ выключен')
            send_line_command('БП ПЭВМ', 1)

        state2 = obtain_state('БП Шелест')
        if state2 != 'вкл':
            # collect_logs('БП Шелест выключен')
            send_line_command('БП Шелест', 1)

        state3 = obtain_state('БП АПЕМ')
        if state3 != 'вкл':
            # collect_logs('БП АПЕМ выключен')
            send_line_command('БП АПЕМ', 1)

        state4 = obtain_state('ЭВМ1')
        state5 = obtain_state('ЭВМ2')
        if state4 != 'вкл':
            send_impulse('ЭВМ1', time_pulse=3, action='вкл')
        if state5 != 'вкл':
            send_impulse('ЭВМ2', time_pulse=3, action='вкл')
        complex_state = 'вкл'
        c['complex_state'] = complex_state
        c['logs'] = logs
        c['logs_list'] = logs_list
        render(request, "main.html", context=c)
        functioning_loop(request)
    return render(request, "main.html", context=c)


def turn_off_bp(request):
    global complex_state
    state1 = obtain_state('БП ПЭВМ')
    if state1 != 'выкл':
        # collect_logs('БП ПЭВМ включен')
        send_line_command('БП ПЭВМ', 0)
    state2 = obtain_state('БП Шелест')
    if state2 != 'выкл':
        # collect_logs('БП Шелест включен')
        send_line_command('БП Шелест', 0)
    state3 = obtain_state('БП АПЕМ')
    if state3 != 'выкл':
        # collect_logs('БП АПЕМ включен')
        send_line_command('БП АПЕМ', 0)

    state4 = obtain_state('ЭВМ1')
    state5 = obtain_state('ЭВМ2')
    if state4 != 'выкл':
        send_impulse('ЭВМ1', time_pulse=3, action='выкл')
    if state5 != 'выкл':
        send_impulse('ЭВМ2', time_pulse=3, action='выкл')

    send_line_command('вентилятор', 0)
    send_impulse('РЕЗЕТ', time_pulse=6, action='выкл')

    complex_state = 'выкл'
    c['complex_state'] = complex_state
    c['logs'] = logs
    c['logs_list'] = logs_list
    render(request, "main.html", context=c)
    functioning_loop(request)

    return render(request, "main.html", context=c)


def show_logs(request):
    global logs
    c['logs'] = logs
    c['logs_list'] = logs_list
    return render(request, "main.html", context=c)


def functioning_loop(request):
    global c
    print('loop')
    is_on = True
    if c['complex_state'] == 'вкл':
        while is_on:
            is_on = check_states_on()
            render(request, "main.html", context=c)
            time.sleep(10)
    elif c['complex_state'] == 'выкл':
        print('всё выключено')
        # while True:
        #     # check_states_off()
        #     break
