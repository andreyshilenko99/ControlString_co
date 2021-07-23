import os.path
import re
import time
import datetime
import csv
import json

import requests
from django.core.serializers import serialize
from django.forms import ModelMultipleChoiceField
from django.shortcuts import redirect
from django.shortcuts import render

from geo.models import Strizh, Point, DroneJournal, StrizhJournal
from .forms import StrizhForm, StrizhFilterForm, DroneFilterForm

from ControlString_co.control_trace import scan_on_off
from ControlString_co.control_trace import jammer_on_off, scan_on_off

chosen_strizh = 0
start_datetime = "Начало"
end_datetime = "Конец"
logs = ''
logs_list = []
low_t = 10
high_t = 60
low_h = 5
high_h = 85
auth = ('user', '555')
message_condition = ''
c = dict(chosen_strizh=0, start_datetime=start_datetime, end_datetime=end_datetime)


def index(request):
    return render(request, "index.html")


def return_conditions(url):
    global low_t, high_t, low_h, high_h, humidity, c
    global auth
    try:
        temp = requests.get(url + 'thermo.cgi?t1', auth=auth, timeout=0.05)
        temp_str = temp.content.decode("utf-8")
        temp_list = re.findall('[0-9]+', temp_str)
        if len(temp_list) > 0:
            temperature = '.'.join(temp_list)
            c['temperature'] = temperature
        print('temperature:', temperature)
    except:
        temperature = 'ошибка соединения с uniping'
    try:
        hum = requests.get(url + 'relhum.cgi?h1', auth=auth, timeout=0.05)
        hum_str = hum.content.decode("utf-8")
        hum_list = re.findall('[0-9]+', hum_str)
        if len(hum_list) > 1:
            humidity = hum_list[0]
            c['humidity'] = humidity
            # humidity_temp = '.'.join(hum_list[1:])
            # c['humidity_temp'] = humidity_temp
        print('humidity:', humidity)
    except:
        humidity = 'ошибка соединения с uniping'
    c['humidity'] = humidity
    c['temperature'] = temperature

    if 'ошибка' not in temperature and 'error' not in humidity:
        if low_t < float(temperature) < high_t and low_h < float(humidity) < high_h:
            weather_state = "OK"
        else:
            weather_state = "NOT OK !!!"
    else:
        weather_state = "ошибка соединения с uniping"
    c["weather_state"] = weather_state
    return temperature, humidity, weather_state


def reset_filter_strizh(request):
    global c
    c['filtered_strizhes'] = ''

    return render(request, "journal.html", context=c)


def filter_all(request):
    global c
    if not c.get('saved_table'):
        c['saved_table'] = False
    print(c['saved_table'])

    if not c.get('filtered_strizhes'):
        c['filtered_strizhes'] = ''
        strizh_names = ''
    else:
        strizh_names_arr = [st.name for st in c['filtered_strizhes']]
        strizh_names = ';; '.join(strizh_names_arr)

    c['start_datetime'] = start_datetime
    c['end_datetime'] = end_datetime
    strizh_value = StrizhJournal(filtered_strizhes=strizh_names,
                                 start_datetime=c['start_datetime'], end_datetime=c['end_datetime'])
    strizh_value.save()

    if request.method == 'POST':
        form_drone = DroneFilterForm(request.POST)
        form_filter = StrizhFilterForm(request.POST)
        if form_drone.is_valid():
            drone_toshow = form_drone.cleaned_data.get('drone_toshow')
            c['drone_toshow'] = drone_toshow
        if form_filter.is_valid():
            filtered_strizhes = form_filter.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes

    else:
        # all_drones = DroneFilterForm().AllDrones
        all_drones = Point.objects.order_by('-detection_time')

        filter_values = StrizhJournal.objects.all().order_by('-pk')
        time_start = filter_values[0].start_datetime
        time_end = filter_values[0].end_datetime

        now = datetime.datetime.now()
        if time_start != 'Начало':
            ts1 = time_start.split('/')
            ts2 = ts1[-1].split('-')
            ts3 = ts2[-1].split(':')
            time_start_datetime = now.replace(year=int(ts2[0]), month=int(ts1[0]), day=int(ts1[1]), hour=int(ts3[0]),
                                              minute=int(ts3[1]), second=0)
        else:
            time_start_datetime = now.replace(year=1970)

        if time_end != 'Конец':
            ts11 = time_end.split('/')
            ts22 = ts11[-1].split('-')
            ts33 = ts22[-1].split(':')
            time_end_datetime = now.replace(year=int(ts22[0]), month=int(ts11[0]), day=int(ts11[1]), hour=int(ts33[0]),
                                            minute=int(ts33[1]), second=59)
        else:
            time_end_datetime = now

        drones_pk = []
        for drone in all_drones:
            if time_start_datetime < get_datetime_drone(drone.detection_time) < time_end_datetime:
                drones_pk.append(drone.pk)

        drones_filtered_time = Point.objects.order_by('-detection_time').filter(pk__in=drones_pk)
        names_str = filter_values[0].filtered_strizhes

        form_drone = DroneFilterForm()
        if len(names_str) != 0:
            names_arr = names_str.split(';; ')
            form_drone.fields['drone_toshow'] = ModelMultipleChoiceField(
                queryset=drones_filtered_time.filter(strig_name__in=names_arr),
                required=False, to_field_name="pk",
                label="")
        else:
            form_drone.fields['drone_toshow'] = ModelMultipleChoiceField(queryset=drones_filtered_time,
                                                                         required=False, to_field_name="pk",
                                                                         label="")

        form_filter = StrizhFilterForm()
    c['form_drone'] = form_drone
    c['form_filter'] = form_filter

    return render(request, "journal.html", context=c)


def journal(request):
    global c


    c['start_datetime'] = start_datetime
    c['end_datetime'] = end_datetime

    if request.method == 'POST':
        form_drone = DroneFilterForm(request.POST)
        form_filter = StrizhFilterForm(request.POST)
        if form_drone.is_valid():
            drone_toshow = form_drone.cleaned_data.get('drone_toshow')
            c['drone_toshow'] = drone_toshow
        if form_filter.is_valid():
            filtered_strizhes = form_filter.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes
    else:
        form_drone = DroneFilterForm()
        form_filter = StrizhFilterForm()
    c['form_drone'] = form_drone
    c['form_filter'] = form_filter
    return render(request, "journal.html", context=c)


def filter_nomer_strizha(request):
    global c
    if request.method == 'POST':
        form_filter = StrizhFilterForm(request.POST)
        if form_filter.is_valid():
            filtered_strizhes = form_filter.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes

    return render(request, "journal.html", context=c)


def choose_drone_toshow(request):
    global c
    if request.method == 'POST':
        form_drone = DroneFilterForm(request.POST)
        for el_db in DroneJournal.objects.all():
            el_db.delete()
        if form_drone.is_valid():
            drone_toshow = form_drone.cleaned_data.get('drone_toshow')
            c['drone_toshow'] = drone_toshow
            if len(drone_toshow) != 0:
                DP = drone_toshow[0]
                drone_value = DroneJournal(system_name=DP.system_name,
                                           center_freq=DP.center_freq,
                                           brandwidth=DP.brandwidth,
                                           detection_time=DP.detection_time,
                                           comment_string=DP.comment_string,
                                           lat=DP.lat,
                                           lon=DP.lon,
                                           azimuth=DP.azimuth,
                                           area_sector_start_grad=DP.area_sector_start_grad,
                                           area_sector_end_grad=DP.area_sector_end_grad,
                                           area_radius_m=DP.area_radius_m,
                                           ip=DP.ip,
                                           current_time=DP.current_time,
                                           strig_name=DP.strig_name)
                drone_value.save()

    return render(request, "journal.html", context=c)


def get_strizhes():
    geojson_strizhes = serialize('geojson', Strizh.objects.all())
    parsed_json = (json.loads(geojson_strizhes))
    arr_strizh = []
    for i in range(len(parsed_json.get("features"))):
        strizh_name = parsed_json.get("features")[i].get("properties").get("name")
        arr_strizh.append(strizh_name)
    return arr_strizh


def configuration(request):
    return render(request, "configuration.html", context=c)


def butt_skan_all(request):
    global c
    # nomer_strizha = 0
    strizh_names = Strizh.objects.all()
    for strizh in strizh_names:
        # TODO action 1 button
        print('skanirovanie vseh: ', strizh.ip1, strizh.ip2)
        scan_on_off(strizh.ip1)
        scan_on_off(strizh.ip2)

    c["action_strizh"] = "Сканирование всех"
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_glush_all(request):
    global c
    strizh_names = Strizh.objects.all()
    print(strizh_names)
    for strizh in strizh_names:
        print('glushenie vseh: ', strizh.ip1, strizh.ip2)
        # jammer_on_off(strizh.ip)

    # TODO trace pomenyat

    c["action_strizh"] = "Глушение всех"
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def back2main(request):
    return redirect(request.META['HTTP_REFERER'])


def butt_gps_all(request):
    global c
    print('gps vseh')
    # TODO action 3 button
    c["action_strizh"] = "GPS для всех"
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_ku_all(request):
    global c
    print('KU vseh #')
    # TODO action 4 button
    c["action_strizh"] = "КУ всех"
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def choose_nomer_strizha(request):
    global c

    strizhes = Strizh.objects.order_by('-lon').all()
    if request.method == 'POST':
        form = StrizhForm(request.POST)
        if form.is_valid():
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'] = chosen_strizh

            for strizh in strizhes:
                if c['chosen_strizh'] == strizh:
                    c['url_uniping'] = 'http://' + strizh.uniping_ip + '/'

        nomer = request.POST['chosen_strizh']
        c['chosen_strizh'] = nomer

    if c.get("chosen_strizh"):
        # c["action_strizh"] = "Выбрано: '{}'".format(c.get("chosen_strizh"))
        temperature, humidity, weather_state = return_conditions(c['url_uniping'])
        c['temperature'] = temperature
        c['humidity'] = humidity
        c['weather_state'] = weather_state
    # return redirect(request.META['HTTP_REFERER'])
    # return HttpResponseRedirect('/main')
    return render(request, "main.html", context=c)


def render_main_page(request):
    global c
    complex_state = ''
    if not c.get('chosen_strizh'):
        c['chosen_strizh'] = 0
    if not c.get('url_uniping'):
        c['url_uniping'] = ''

    c['start_datetime'] = start_datetime
    c['end_datetime'] = end_datetime

    temperature, humidity, weather_state = return_conditions(c['url_uniping'])
    c['temperature'] = temperature
    c['humidity'] = humidity
    c['weather_state'] = weather_state

    strizhes = Strizh.objects.order_by('-lon').all()
    if request.method == 'POST':
        form = StrizhForm(request.POST)
        if form.is_valid():
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'] = chosen_strizh


    else:
        form = StrizhForm()
    c['form'] = form
    # filter(id=id)

    # TODO current_time
    drones = Point.objects.order_by('-detection_time').all()

    c['info_drones'] = drones

    return render(request, "main.html", context=c)


def butt_skan(request):
    global c
    strizh_names = Strizh.objects.all()

    if c.get("chosen_strizh") != 0:

        c["action_strizh"] = "Сканирование: {}".format(c.get('chosen_strizh'))

        for strizh in strizh_names:
            if strizh.name == c.get("chosen_strizh"):
                scan_on_off(strizh.ip1)
                scan_on_off(strizh.ip2)
                print('skanirovanie dlya strizha #', strizh.name)

    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_glush(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('glushenie dlya strizha #', c.get('chosen_strizh'))
        # TODO action 2 button
    c["action_strizh"] = "Глушение: {}".format(c.get('chosen_strizh'))
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_gps(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('gps dlya strizha #', c.get('chosen_strizh'))
        # TODO action 3 button
    c["action_strizh"] = "GPS: {}".format(c.get('chosen_strizh'))
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_ku(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('KU dlya strizha #', c.get('chosen_strizh'))
        # TODO action 4 button
    c["action_strizh"] = "КУ: {}".format(c.get('chosen_strizh'))
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def apply_period(request):
    global c, start_datetime, end_datetime, reset_time
    c['saved_table'] = False
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
    c['filtered_strizhes'] = ''
    c['start_datetime'] = 'Начало'
    c['saved_table'] = False

    if request.method == 'POST':
        form_filter = StrizhFilterForm(request.POST)
        form_drone = DroneFilterForm(request.POST)

        for strizh in StrizhJournal.objects.all():
            strizh.delete()
    else:
        form_filter = StrizhFilterForm()
        form_drone = DroneFilterForm()
    c['form_filter'] = form_filter
    c['form_drone'] = form_drone

    c['end_datetime'] = 'Конец'
    return render(request, "journal.html", context=c)


def get_datetime_drone(time_dron):
    t1 = time_dron.split('-')
    t2 = t1[-1].split(' ')
    t3 = t2[-1].split(':')
    now = datetime.datetime.now()
    return now.replace(year=int(t1[0]), month=int(t1[1]), day=int(t2[0]), hour=int(t3[0]),
                       minute=int(t3[1]), second=int(t3[2]))


def export_csv(request):
    global c
    c['saved_table'] = False
    time_start = c['start_datetime']
    time_end = c['end_datetime']
    strizhes = c['filtered_strizhes']

    now = datetime.datetime.now()
    ts1 = time_start.split('/')
    ts2 = ts1[-1].split('-')
    ts3 = ts2[-1].split(':')
    time_start_datetime = now.replace(year=int(ts2[0]), month=int(ts1[0]), day=int(ts1[1]), hour=int(ts3[0]),
                                      minute=int(ts3[1]), second=0)

    ts11 = time_end.split('/')
    ts22 = ts11[-1].split('-')
    ts33 = ts22[-1].split(':')
    time_end_datetime = now.replace(year=int(ts22[0]), month=int(ts11[0]), day=int(ts11[1]), hour=int(ts33[0]),
                                    minute=int(ts33[1]), second=59)
    print(time_end_datetime > time_start_datetime)

    strizhes_ip = []
    for strizh in strizhes:
        for ip in [strizh.ip1, strizh.ip2]:
            strizhes_ip.append(ip)

    drones_filtered_strizh = Point.objects.order_by('-detection_time').filter(ip__in=strizhes_ip)
    d = datetime.datetime.now()
    csv_name = "log_{}_{}_{}_{}_{}_{}.csv".format(d.hour, d.minute, d.second, d.day, d.month, d.year)
    print(csv_name)
    with open(os.path.join('saved_logs_csv', csv_name), 'w+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        first_row = 'Имя дрона', 'Несущая частота', 'Пропускная способность', 'Время обнаружения', \
                    'Комментарии', 'Широта', 'Долгота', 'Азимут', 'Внутренний радиус сектора', 'Внешний радиус сектора', \
                    'Радиус сектора (м)', 'IP-адрес стрижа'
        writer.writerow(first_row)

        for dr in drones_filtered_strizh:
            writer = csv.writer(f)

            if time_start_datetime < get_datetime_drone(dr.detection_time) < time_end_datetime:
                row = dr.system_name, dr.center_freq, dr.brandwidth, dr.detection_time, \
                      dr.comment_string, dr.lat, dr.lon, dr.azimuth, \
                      dr.area_sector_start_grad, dr.area_sector_end_grad, dr.area_radius_m, dr.ip

                writer.writerow(row)

    return render(request, "journal.html", context=c)


def get_conditions(request):
    temperature, humidity, weather_state = return_conditions(c['url_uniping'])
    c['temperature'] = temperature
    c['humidity'] = humidity
    c["weather_state"] = weather_state
    return render(request, "main.html", context=c)


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
    global auth, lines_map, c

    state = "вкл" if arg == 1 else "выкл"
    log_str = '{} {}ючен'.format(line_name, state)
    line = lines_map.get(line_name)
    try:
        result_get = requests.get(c['url_uniping'] + 'io.cgi?io{}={}'.format(line, arg), auth=auth, timeout=0.05) \
            .content.decode("utf-8")
    except:
        result_get = 'ошибка соединения с uniping'
    if 'ok' in result_get:
        collect_logs("{}".format(log_str))
    else:
        collect_logs("проверьте, выбран ли стриж")


def send_impulse(line_name, time_pulse=3, action=''):
    global auth, lines_map, c
    line = lines_map.get(line_name)
    try:
        result_get = requests.get(c['url_uniping'] + 'io.cgi?io{}=f,{}'.format(line, time_pulse), auth=auth,
                                  timeout=0.05) \
            .content.decode("utf-8")
    except:
        result_get = 'err in connection to uniping'
    if 'ok' in result_get:
        collect_logs("{} {}ючен".format(line_name, action))
    else:
        print("send_impulse error")
    time.sleep(time_pulse + 1)


def obtain_state(line_name, to_collect_logs=False):
    global lines_control_map, c
    result_state = 0
    line = lines_control_map.get(line_name)
    try:
        stroka = requests.get(c['url_uniping'] + 'io.cgi?io{}'.format(line), auth=auth, timeout=0.05) \
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


def check_states_on():
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
            state44 = obtain_state('ЭВМ1')
            if state44 != 'вкл':
                send_impulse('ЭВМ1', time_pulse=3, action='вкл')
            time.sleep(4)
        if state5 != 'вкл':
            send_impulse('ЭВМ2', time_pulse=3, action='вкл')
        complex_state = 'вкл'
        c['complex_state'] = complex_state
        c['logs'] = logs
        c['logs_list'] = logs_list
        render(request, "main.html", context=c)
        # functioning_loop(request)
    return render(request, "main.html", context=c)


def turn_off_bp(request):
    global complex_state

    state4 = obtain_state('ЭВМ1')
    state5 = obtain_state('ЭВМ2')
    if state4 != 'выкл':
        send_impulse('ЭВМ1', time_pulse=3, action='выкл')
    if state5 != 'выкл':
        send_impulse('ЭВМ2', time_pulse=3, action='выкл')

    time.sleep(5)

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

    send_line_command('вентилятор', 0)
    time.sleep(1)
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
