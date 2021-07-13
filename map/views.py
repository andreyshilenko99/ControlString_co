import re
import time

import requests
from django.core.serializers import serialize
from django.shortcuts import redirect
from django.shortcuts import render

from geo.models import Strizh, Point
# from .models import MyModel, MyStrizh
# from .forms import MyModelForm
from .forms import StrizhForm, StrizhFilterForm

chosen_strizh = 0
start_datetime = "Начало"
end_datetime = "Конец"
logs = ''
logs_list = []
low_t = 10
high_t = 60
low_h = 5
high_h = 85
url = "http://192.168.2.51/"
auth = ('user', '555')
message_condition = ''


def index(request):
    return render(request, "index.html")


def return_conditions():
    global low_t, high_t, low_h, high_h, humidity
    global url
    global auth
    weather_state = 'not ok'

    try:
        temp = requests.get(url + 'thermo.cgi?t1', auth=auth, timeout=0.001)
        temp_str = temp.content.decode("utf-8")
        temp_list = re.findall('[0-9]+', temp_str)
        if len(temp_list) > 0:
            temperature = '.'.join(temp_list)
            c['temperature'] = temperature
        print('temperature:', temperature)
    except:
        temperature = 'error in connection to uniping'
    try:
        hum = requests.get(url + 'relhum.cgi?h1', auth=auth, timeout=0.001)
        hum_str = hum.content.decode("utf-8")
        hum_list = re.findall('[0-9]+', hum_str)
        if len(hum_list) > 1:
            humidity = hum_list[0]
            c['humidity'] = humidity
            # humidity_temp = '.'.join(hum_list[1:])
            # c['humidity_temp'] = humidity_temp
        print('humidity:', humidity)
    except:
        humidity = 'error in connection to uniping'
    c['humidity'] = humidity
    c['temperature'] = temperature

    if 'error' not in temperature and 'error' not in humidity:
        if low_t < float(temperature) < high_t and low_h < float(humidity) < high_h:
            weather_state = "OK"
        else:
            weather_state = "NOT OK !!!"
    else:
        weather_state = "error in connection to uniping"
    c["weather_state"] = weather_state
    return temperature, humidity, weather_state


c = dict(chosen_strizh=0, start_datetime=start_datetime, end_datetime=end_datetime, available_strizhes=[])


def journal(request):

    # temperature, humidity, weather_state = return_conditions()
    #
    # c = dict(nomer_strizha=0, start_datetime=start_datetime, end_datetime=end_datetime,
    #          available_strizhes=get_strizhes(), temperature=temperature,
    #          humidity=humidity, weather_state=weather_state)

    global c
    c['filtered_strizhes'] = 0
    c['start_datetime'] = start_datetime
    c['end_datetime'] = end_datetime
    c['available_strizhes'] = get_strizhes()

    temperature, humidity, weather_state = return_conditions()
    c['temperature'] = temperature
    c['humidity'] = humidity
    c['weather_state'] = weather_state

    if request.method == 'POST':
        form = StrizhFilterForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            filtered_strizhes = form.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes
    else:
        form_filter = StrizhFilterForm()
    c['form_filter'] = form_filter
    return render(request, "journal.html", context=c)


def filter_nomer_strizha(request):
    global c
    temperature, humidity, weather_state = return_conditions()
    c['temperature'] = temperature
    c['humidity'] = humidity
    c['weather_state'] = weather_state
    if request.method == 'POST':
        form_filter = StrizhFilterForm(request.POST)
        if form_filter.is_valid():
            print(form_filter.cleaned_data)
            filtered_strizhes = form_filter.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes
        # nomer = request.POST['filtered_strizhes']
        nomer = filtered_strizhes
        print('got', nomer, '\n')
        c = {'filtered_strizhes': nomer}
        # return render(request,"main.html", context=c)
    # if c.get("filtered_strizhes"):
    #     c["filtered_strizhes"] = "{}".format(c.get("filtered_strizhes"))
    xx = c
    print(len(c['filtered_strizhes']))
    return render(request, "journal.html", context=c)



def get_strizhes():
    geojson_strizhes = serialize('geojson', Strizh.objects.all())
    parsed_json = (json.loads(geojson_strizhes))
    arr_strizh = []
    for i in range(len(parsed_json.get("features"))):
        strizh_name = parsed_json.get("features")[i].get("properties").get("name")
        arr_strizh.append(strizh_name)
    return arr_strizh


# def main(request):
#     temperature, humidity, weather_state = return_conditions()
#
#     c = dict(chosen_strizh=0, start_datetime=start_datetime, end_datetime=end_datetime,
#              available_strizhes=get_strizhes(), temperature=temperature,
#              humidity=humidity, weather_state=weather_state)
#
#     if request.method == 'POST':
#         form = StrizhForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return
#         else:
#             error = "форма неверная"
#     form = StrizhForm()
#     if c.get('form'):
#         c['form'] = form
#     else:
#         c['form'] = ''
#     return render(request, "main.html", context=c)


def configuration(request):
    return render(request, "configuration.html", context=c)


def butt_skan_all(request):
    global c
    # nomer_strizha = 0
    print('skanirovanie vseh')
    # TODO action 1 button
    # return render(request, "journal.html", context=c)
    c["action_strizh"] = "Сканирование всех"
    return redirect(request.META['HTTP_REFERER'])


def butt_glush_all(request):
    global c
    print('glushenie vseh')
    # TODO action 2 button
    c["action_strizh"] = "Глушение всех"
    return redirect(request.META['HTTP_REFERER'])


def back2main(request):
    return redirect(request.META['HTTP_REFERER'])


def butt_gps_all(request):
    global c
    print('gps vseh')
    # TODO action 3 button
    c["action_strizh"] = "GPS для всех"
    return redirect(request.META['HTTP_REFERER'])


def butt_ku_all(request):
    global c
    print(c)
    print('KU vseh #')
    # TODO action 4 button
    c["action_strizh"] = "КУ всех"
    return redirect(request.META['HTTP_REFERER'])


import json


def choose_nomer_strizha(request):
    global c
    # geojson_strizhes = serialize('geojson', Strizh.objects.all())
    # parsed_json = (json.loads(geojson_strizhes))
    # arr_strizh = []
    # for i in range(len(parsed_json.get("features"))):
    #     strizh_name = parsed_json.get("features")[i].get("properties").get("name")
    #     arr_strizh.append(strizh_name)
    # c["available_strizhes"] = arr_strizh
    # print(c["available_strizhes"])

    temperature, humidity, weather_state = return_conditions()
    c['temperature'] = temperature
    c['humidity'] = humidity
    c['weather_state'] = weather_state

    if request.method == 'POST':
        form = StrizhForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'] = chosen_strizh

        nomer = request.POST['chosen_strizh']
        print('send', nomer, '\n')
        c = {'chosen_strizh': nomer}
        # return render(request,"main.html", context=c)
    if c.get("chosen_strizh"):
        c["action_strizh"] = "Выбрано: '{}'".format(c.get("chosen_strizh"))
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)
    # return HttpResponseRedirect('/main')

actual_strizhes = {}

def render_main_page(request):
    global c, actual_strizhes
    c['chosen_strizh'] = 0
    c['start_datetime'] = start_datetime
    c['end_datetime'] = end_datetime
    c['available_strizhes'] = get_strizhes()

    temperature, humidity, weather_state = return_conditions()
    c['temperature'] = temperature
    c['humidity'] = humidity
    c['weather_state'] = weather_state

    if request.method == 'POST':
        form = StrizhForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'] = chosen_strizh
    else:
        form = StrizhForm()
    c['form'] = form
    # filter(id=id)
    strizhes = Strizh.objects.order_by('-lon').all()
    drones = Point.objects.order_by('-lon').all()

    c['actual_strizhes'] = strizhes
    c['drone_lat'] = drones[0].lat
    c['drone_lon'] = drones[0].lon
    c['drone_name'] = drones[0].system_name
    return render(request, "main.html", context=c)


# class CreateMyModelView(CreateView):
#
#     # model = Strizh
#     model = MyStrizh
#     form_class = StrizhForm
#     template_name = 'main.html'
#     success_url = 'main.html'
#     context_object_name = 'strizh_model'
#     print(form_class)
#     temperature, humidity, humidity_temp, weather_state = return_conditions()
#
#     c = dict(nomer_strizha=0, start_datetime=start_datetime, end_datetime=end_datetime,
#              available_strizhes=get_strizhes(), temperature=temperature,
#              humidity=humidity, humidity_temp=humidity_temp, weather_state=weather_state)


def butt_skan(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('skanirovanie dlya strizha #', c.get('chosen_strizh'))
        # TODO action 1 button
    c["action_strizh"] = "Сканирование для стрижа №{}".format(c.get('chosen_strizh'))
    return redirect(request.META['HTTP_REFERER'])


def butt_glush(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('glushenie dlya strizha #', c.get('chosen_strizh'))
        # TODO action 2 button
    c["action_strizh"] = "Глушение для стрижа №{}".format(c.get('chosen_strizh'))
    return redirect(request.META['HTTP_REFERER'])


def butt_gps(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('gps dlya strizha #', c.get('chosen_strizh'))
        # TODO action 3 button
    c["action_strizh"] = "GPS для стрижа №{}".format(c.get('chosen_strizh'))
    return redirect(request.META['HTTP_REFERER'])


def butt_ku(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('KU dlya strizha #', c.get('chosen_strizh'))
        # TODO action 4 button
    c["action_strizh"] = "КУ для стрижа №{}".format(c.get('chosen_strizh'))
    return redirect(request.META['HTTP_REFERER'])


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

        c['start_datetime'] = start_datetime
        c['end_datetime'] = end_datetime
        # return render(request, "journal.html", context=c)
    return render(request, "journal.html", context=c)

def reset_filter(request):
    global c
    c['filtered_strizhes'] = 0
    c['start_datetime'] = 0
    c['end_datetime'] = 0
    return render(request, "journal.html", context=c)


def get_conditions(request):
    # global temperature, humidity, humidity_temp, weather_state
    temperature, humidity, weather_state = return_conditions()
    c['temperature'] = temperature
    c['humidity'] = humidity
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
    try:
        result_get = requests.get(url + 'io.cgi?io{}={}'.format(line, arg), auth=auth, timeout=0.001) \
            .content.decode("utf-8")
    except:
        result_get = 'err in connection to uniping'
    if 'ok' in result_get:
        collect_logs("{}".format(log_str))
    else:
        collect_logs("send_line_command error")


def send_impulse(line_name, time_pulse=3, action=''):
    global url, auth, lines_map
    line = lines_map.get(line_name)
    try:
        result_get = requests.get(url + 'io.cgi?io{}=f,{}'.format(line, time_pulse), auth=auth, timeout=0.001) \
            .content.decode("utf-8")
    except:
        result_get = 'err in connection to uniping'
    if 'ok' in result_get:
        # print("send_impulse ok {}".format(line_name))
        collect_logs("{} {}ючен".format(line_name, action))
    else:
        print("send_impulse error")
    time.sleep(time_pulse + 1)


def obtain_state(line_name, to_collect_logs=False):
    global lines_control_map
    result_state = 0
    line = lines_control_map.get(line_name)
    try:
        stroka = requests.get(url + 'io.cgi?io{}'.format(line), auth=auth, timeout=0.001) \
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
    # print(log_str)
    return state


def set_correct_temperature(temperature_state):
    global temperature
    if temperature_state != 0:
        while temperature_state != 0:
            temperature_state = check_condition(c['temperature'], low_border=low_t, high_border=high_t)
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
    temperature_state = check_condition(c['temperature'], low_border=low_t, high_border=high_t)
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
    temperature_state = check_condition(c['temperature'], low_border=low_t, high_border=high_t)
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
