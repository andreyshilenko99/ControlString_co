import os.path
import re
import time
import json
import datetime
import csv
import requests
from itertools import chain

from django.forms import ModelMultipleChoiceField
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.serializers import serialize
from django.views.decorators.csrf import csrf_exempt

from geo.models import Strizh, Point, DroneJournal, StrizhJournal, ApemsConfiguration, \
    SkyPoint, AeroPoints, DroneTrajectoryJournal, Maps, StrigState
from .forms import StrizhForm, StrizhFilterForm, DroneFilterForm, ApemsConfigurationForm, ApemsChangingForm, \
    TableFilterForm, TableOrderForm, SkyPointFilterForm, MapChoosingForm
from .forms import TimePickForm

from ControlString_co.control_trace import scan_on_off, check_state, jammer_on_off
from ControlString_co.shelest_jam import set_gain

DEGREE_SIGN = u"\u2103"
chosen_strizh = 0
logs = ''
logs_list = []
low_t = 10
high_t = 60
low_h = 5
high_h = 85
message_condition = ''
c = {}

with open("config.json", encoding='utf-8-sig') as json_cfg:
    data_conf = json.load(json_cfg)
try:
    auth = (data_conf.get('uniping').get('login'), data_conf.get('uniping').get('password'))
except:
    auth = ('user', '555')


def init_content():
    c = dict(chosen_strizh=[], start_datetime='', end_datetime='')
    return c


def index(request):
    global c
    c['page_picked'] = 'index'
    return render(request, "index.html", context=c)


def return_conditions(url):
    global low_t, high_t, low_h, high_h, c
    global auth
    temperature = ''
    try:
        temp = requests.get(url + 'thermo.cgi?t1', auth=auth, timeout=0.05)
        temp_str = temp.content.decode("utf-8")
        temp_list = re.findall('[0-9]+', temp_str)
        if len(temp_list) > 0:
            temperature = '.'.join(temp_list) + DEGREE_SIGN
    except:
        temperature = 'ошибка uniping'
    try:
        hum = requests.get(url + 'relhum.cgi?h1', auth=auth, timeout=0.05)
        hum_str = hum.content.decode("utf-8")
        hum_list = re.findall('[0-9]+', hum_str)
        if len(hum_list) > 1:
            humidity = hum_list[0] + ' %'
    except:
        humidity = 'ошибка uniping'

    if 'ошибка' not in temperature and 'ошибка' not in humidity:
        temperature_val = re.findall("[-+]?\d*\.\d+|\d+", temperature)[0]
        humidity_val = re.findall("[-+]?\d*\.\d+|\d+", humidity)[0]
        if low_t < float(temperature_val) < high_t and low_h < float(humidity_val) < high_h:
            weather_state = "OK"
        else:
            weather_state = "NOT OK !!!"
    else:
        weather_state = "ошибка uniping"

    return temperature, humidity, weather_state


def get_info_main(ip1, ip2, name):
    try:
        # TODO UNCOMMENT for working check state
        # mode_ips = [check_state(ip1), check_state(ip2)]
        # mode_ips = ['Все остановлено' for _ in range(2)]
        strizh_state = StrigState.objects.all().filter(strig_name=name).order_by('-pk')[0]
        mode_ips = [strizh_state.ip1_state, strizh_state.ip2_state]
        #
    except:
        mode_ips = ['Все остановлено' for _ in range(2)]

    complex_mode = 'Сканирование активно' if all(
        [True if x == 'Сканирование активно' else False for x in mode_ips]) else 'Все остановлено'
    complex_mode = 'Подавление активно' if all(
        [True if x == 'Подавление активно' else False for x in mode_ips]) else complex_mode
    print(complex_mode)

    if 'Подавление активно' in complex_mode:
        # if 'Подавление активно' in mode_ips:
        action_complex = 'включено'
        button_complex = 'red_jammer'
        complex_mode_rus = 'Глушение: '
    elif 'Сканирование активно' in complex_mode:
        # elif 'Сканирование активно' in mode_ips:
        action_complex = 'включено'
        button_complex = 'red_scan'
        complex_mode_rus = 'Сканирование: '
    else:
        action_complex = 'выключено'
        button_complex = 'green'
        complex_mode_rus = 'Сканирование и глушение: '

    action_strizh = complex_mode_rus + name + ' ' + action_complex

    return complex_mode, button_complex, action_strizh


def journal_view(request):
    global c
    x = Point.objects.all().order_by('-current_time')
    order_sign = '' if c.get('order_sign') == '+' else '-'
    table_filter = c.get('table_filter') if c.get('table_filter', '') != '' else 'current_time'
    try:
        y = Point.objects.all().order_by(order_sign + table_filter)
        geom_as_geojson = serialize('geojson', y)
    except AttributeError:
        geom_as_geojson = ''
    return HttpResponse(geom_as_geojson, content_type='geojson')


def collect_logs(log_string):
    global logs, logs_list
    time_obj = datetime.datetime.now().strftime("%Y-%d-%m  %H:%M:%S")
    log_one = time_obj + '   ' + log_string + '\n\t'
    logs_list.append(log_one)
    c['logs_list'] = logs_list
    print(log_one)


def set_correct_temperature(url, strizh_name, temperature_state):
    global c
    while temperature_state != 0:
        temperature_state = check_condition(c['temperature_dict'][strizh_name], low_border=low_t,
                                            high_border=high_t)
        if temperature_state == 1:
            send_line_command(url, 'вентилятор_команда', 1)
            state0 = obtain_state(url, 'вентилятор')
            if state0 != 'вкл':
                collect_logs('АВАРИЯ! отсутствует вентиляция, возможен перегрев оборудования')
        elif temperature_state == -1:
            send_line_command(url, 'обогрев', 1)
        time.sleep(60)


def back2main(request):
    return redirect(request.META['HTTP_REFERER'])


def choose_nomer_strizha(request):
    global c
    strizhes = Strizh.objects.order_by('-lon').all()
    if request.method == 'POST':
        form = StrizhForm(request.POST)
        url_uniping_dict = {}
        temperature_dict = {}
        humidity_dict = {}
        weather_state_dict = {}

        if form.is_valid() and request.POST['chosen_strizh'] \
                and 'choose_all_strizhes' not in request.POST:
            c['chosen_strizh'] = ['None' for _ in range(len(strizhes))]
            # if 'choose_nomer_strizha' in request.POST:
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            if chosen_strizh:
                c['chosen_strizh'][0] = chosen_strizh.name
                # form.fields.get('chosen_strizh').initial = [chosen_strizh.name]
                # form.initial['chosen_strizh'] = chosen_strizh.name
                # c['form'] = form
                form = StrizhForm(request.POST, initial={'chosen_strizh': chosen_strizh.name})
                c['form'] = form

            for strizh in strizhes:
                if c['chosen_strizh'][0] == strizh.name:
                    url_uniping_dict[strizh.name] = 'http://' + strizh.uniping_ip + '/'
                    temperature_dict[strizh.name], humidity_dict[strizh.name], weather_state_dict[strizh.name] = \
                        return_conditions(url_uniping_dict[strizh.name])
                    complex_mode, button_complex, action_strizh = get_info_main(strizh.ip1, strizh.ip2, strizh.name)
                    c["button_complex"] = button_complex
                    c['complex_mode_dict'][strizh.name] = complex_mode
                    c["action_strizh"][strizh.name] = action_strizh
            c['chosen_strizh_json'] = json.dumps(c['chosen_strizh'][0])

        if form.is_valid() and 'choose_all_strizhes' in request.POST:
            c['chosen_strizh'] = [strizh.name for strizh in strizhes]
            c['chosen_strizh_json'] = json.dumps(c['chosen_strizh'])
            # form.fields['chosen_strizh'].initial = None
            # form.initial['chosen_strizh'] = [None]
            # c['form'] = form
            form = StrizhForm()
            c['form'] = form
            for strizh in strizhes:
                url_uniping_dict[strizh.name] = 'http://' + strizh.uniping_ip + '/'
                temperature_dict[strizh.name], humidity_dict[strizh.name], weather_state_dict[strizh.name] = \
                    return_conditions(url_uniping_dict[strizh.name])
                complex_mode, button_complex, action_strizh = get_info_main(strizh.ip1, strizh.ip2, strizh.name)

                c["button_complex"] = button_complex
                c['complex_mode_dict'][strizh.name] = complex_mode
                c["action_strizh"][strizh.name] = action_strizh
        if all([url_uniping_dict, temperature_dict, humidity_dict, weather_state_dict]):
            c['url_uniping_dict'] = url_uniping_dict
            c['temperature_dict'] = temperature_dict
            c['humidity_dict'] = humidity_dict
            c['weather_state_dict'] = weather_state_dict
    return redirect('/main')
    # return render(request, "main.html", context=c)
    # return HttpResponse(c)


def set_strizh(request):
    global c
    strizhes = Strizh.objects.order_by('-lon').all()
    c['set_strizh_apem'] = ['None' for _ in range(len(strizhes))]
    if request.method == 'POST':
        form_strizh = StrizhForm(request.POST)
        if form_strizh.is_valid():
            set_strizh_apem = form_strizh.cleaned_data.get('chosen_strizh')
            c['set_strizh_apem'][0] = set_strizh_apem.name
            form_apem = ApemsConfigurationForm(request.POST)

            form_apem.fields.get('apem_toshow').choices.field.queryset = form_apem.AllApems.filter(
                strizh_name=c['set_strizh_apem'][0])
            c['is_strizh_chosen'] = 'True'
    else:
        form_strizh = StrizhForm()
        form_apem = ApemsConfigurationForm()
    c['form_strizh'] = form_strizh
    c['form_apem'] = form_apem
    return render(request, "configuration.html", context=c)


def render_main_page(request):
    global c

    c['start_datetime'] = ''
    c['end_datetime'] = ''
    c['page_picked'] = 'main'

    with open("config.json", encoding='utf-8-sig') as json_cfg:
        data_conf = json.load(json_cfg)

    c['map_link_default'] = data_conf['map_config']['default_link']

    temperature_dict = {}
    humidity_dict = {}
    weather_state_dict = {}
    url_uniping_dict = {}
    if request.method == 'POST' or not c.get('complex_state_dict'):
        c['complex_state_dict'] = {}
    c['complex_mode_dict'] = {}
    c['action_strizh'] = {}

    map_form = MapChoosingForm(initial={'chosen_map': c.get('chosen_map_link')})
    c['map_form'] = map_form
    if len(map_form.fields['chosen_map'].choices) == 0:
        map_obj = Maps(map_link=c['map_link_default'], map_name='Спутник')
        map_obj.save()

    strizhes = Strizh.objects.order_by('-lon').all()
    for strizh in strizhes:
        url_uniping_dict[strizh.name] = 'http://' + strizh.uniping_ip + '/'

        temperature_dict[strizh.name], humidity_dict[strizh.name], weather_state_dict[strizh.name], = \
            return_conditions(url_uniping_dict[strizh.name])
        c['complex_state_dict'][strizh.name] = get_complex_state(url_uniping_dict[strizh.name])
        c['complex_state_json'] = json.dumps(c['complex_state_dict'])

        complex_mode, button_complex, action_strizh = get_info_main(strizh.ip1, strizh.ip2, strizh.name)

        c["action_strizh"][strizh.name] = action_strizh
        if not c.get('button_complex'):
            c["button_complex"] = button_complex

        c['complex_mode_dict'][strizh.name] = complex_mode
        # c['complex_mode_dict'][strizh.name] = mode_ips[0]
        c['complex_mode_json'] = json.dumps(c['complex_mode_dict'])

    c['temperature_dict'] = temperature_dict
    c['humidity_dict'] = humidity_dict
    c['weather_state_dict'] = weather_state_dict
    c['url_uniping_dict'] = url_uniping_dict
    # c['complex_state_dict'] = complex_state_dict
    # c['complex_state_json'] = json.dumps(complex_state_dict)

    if not c.get('chosen_strizh'):
        # c['chosen_strizh'] = ['None' for _ in range(len(strizhes))]
        c['chosen_strizh'] = [s.name for s in strizhes]
        c['chosen_strizh_json'] = json.dumps(c['chosen_strizh'])
    if request.method == 'POST':
        form = StrizhForm(request.POST)
        if form.is_valid():
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'][0] = chosen_strizh
    else:
        form = StrizhForm()
    c['form'] = form
    all_drones_a = AeroPoints.objects.all().order_by('-current_time')
    all_drones_s = Point.objects.all().order_by('-current_time')
    all_drones_res = all_drones_s.union(all_drones_a)
    all_drones_res = all_drones_res.order_by('-current_time')

    c['all_drones_res'] = all_drones_res
    c['all_strizhes'] = [s.name for s in strizhes]

    return render(request, "main.html", context=c)


def butt_scan(request):
    global c
    xx = c
    strizh_names = Strizh.objects.all()

    if c.get("chosen_strizh") != 0:
        print('Сканирование dlya strizha #', c.get('chosen_strizh'))
        for strizh in strizh_names:
            state = c.get("complex_state_dict")[strizh.name]
            bool_val = (state == 'включен' or state == 'выключен вентилятор')
            if strizh.name in c.get("chosen_strizh") and bool_val:
                try:
                    mode_ip1 = scan_on_off(strizh.ip1)
                    # time.sleep(1)
                    mode_ip2 = scan_on_off(strizh.ip2)
                except:
                    # если не включен трэйс
                    mode_ip1 = "all_stop"
                    mode_ip2 = "all_stop"

                if mode_ip1 != mode_ip2:
                    mode_ip2 = scan_on_off(strizh.ip2)
                mode_ips = [mode_ip1, mode_ip2]
                complex_mode = 'Сканирование активно' if all(
                    [True if x == 'scan_on' else False for x in mode_ips]) else 'Все остановлено'
                complex_mode = 'Подавление активно' if all(
                    [True if x == 'jammer_on' else False for x in mode_ips]) else complex_mode
                print('complex_mode: ', complex_mode)
                print('mode_ips: ', mode_ips)
                action_complex = 'включено' if complex_mode == 'Сканирование активно' else 'выключено'
                button_complex = 'red_scan' if complex_mode == 'Сканирование активно' else 'green'
                # mode_ips2 = [check_state(strizh.ip1), check_state(strizh.ip2)]
                c["action_strizh"][strizh.name] = 'Сканирование: ' + strizh.name + ' ' + action_complex
                # ', '.join(str(_) for _ in mode_ips)
                c["button_complex"] = button_complex
                c['complex_mode_dict'][strizh.name] = complex_mode
                c['complex_mode_json'] = json.dumps(c['complex_mode_dict'])

    return redirect('/main')
    # return render(request, "main.html", context=c)


def butt_glush(request):
    global c
    strizh_names = Strizh.objects.all()
    apems = ApemsConfiguration.objects.all()

    if c.get("chosen_strizh") != 0:
        print('glushenie dlya strizha #', c.get('chosen_strizh'))
        for strizh in strizh_names:

            if strizh.name in c.get("chosen_strizh") and c.get("complex_state_dict")[strizh.name] == 'включен':
                # if check_state(strizh.ip1) == 'Сканирование активно':
                #     scan_on_off(strizh.ip1)
                # if check_state(strizh.ip2) == 'Сканирование активно':
                #     scan_on_off(strizh.ip2)
                #
                # if check_state(strizh.ip1) == 'Все остановлено' and check_state(strizh.ip2) == 'Все остановлено':
                #     scan_on_off(strizh.ip1)
                #     scan_on_off(strizh.ip2)
                #     time.sleep(0.5)
                #     scan_on_off(strizh.ip1)
                #     scan_on_off(strizh.ip2)
                #     time.sleep(0.5)
                #     for each_apem in apems.filter(strizh_name=strizh.name):
                #         # TODO test tomorrow and dobavit apem
                #         ip = each_apem.ip_podavitelya
                #         if 'Шелест' in each_apem.type_podavitelya:
                #             set_gain(ip, each_apem.usileniye_db)
                #         elif 'АПЕМ' in apems.filter(strizh_name=strizh.name):
                #             set_gain(ip, each_apem.usileniye_db)
                #         print(ip)

                # mode1 = check_state(strizh.ip1)
                # mode2 = check_state(strizh.ip2)
                # modes = [mode1, mode2]
                # complex_mode = 'Сканирование активно' if all([True if x == 'Сканирование активно' else False for x in mode_ips]) else 'Все остановлено'
                # complex_mode = 'Подавление активно' if all(
                #     [True if x == 'Подавление активно' else False for x in mode_ips]) else complex_mode

                # strizh_state = StrigState.objects.all().filter(strig_name=strizh.name)
                # mode_ips = [strizh_state.ip1_state, strizh_state.ip2_state]

                for i, ip_host in enumerate([strizh.ip1, strizh.ip2]):
                    mode_ = check_state(ip_host)
                    # mode_ = mode_ips[i]

                    if mode_ == 'Сканирование активно':
                        # while check_state(strizh.ip2) != 'Все остановлено':
                        scan_on_off(ip_host)
                mode = check_state(strizh.ip1)
                print(mode)
                if mode != 'Сканирование активно':
                    jammer_on_off(strizh.ip1)
                mode = check_state(strizh.ip1)
                # TODO check with connected apems
                action_complex = 'включено' if mode == 'Подавление активно' else 'выключено'
                button_complex = 'red_jammer' if mode == 'Подавление активно' else 'green'
                # mode_ips2 = [check_state(strizh.ip1), check_state(strizh.ip2)]
                c["action_strizh"][strizh.name] = 'глушение: ' + strizh.name + ' ' + action_complex
                c["button_complex"] = button_complex
                c['complex_mode_dict'][strizh.name] = mode
                c['complex_mode_json'] = json.dumps(c['complex_mode_dict'])
                # jammer_on_off(strizh.ip1, 'on')

    return redirect('/main')
    # return render(request, "main.html", context=c)


def turn_on_bp(request):
    global c, complex_state, logs
    xx = c
    for strizh_name in c.get('chosen_strizh'):
        if strizh_name != 'None':
            url = c['url_uniping_dict'][strizh_name]
            try:
                requests.get(url, auth=auth, timeout=0.2)
            except:
                result_get = 'ошибка uniping'
                collect_logs(strizh_name + ': ' + result_get)
                continue
            temperature_state = check_condition(c['temperature_dict'][strizh_name], low_border=low_t,
                                                high_border=high_t)
            if temperature_state != 0:
                print('температура не в порядке')
                set_correct_temperature(url, strizh_name, temperature_state)
            elif temperature_state == 0:
                # turn everything on
                state0 = obtain_state(url, 'вентилятор')
                if state0 != 'вкл':
                    # pass
                    send_line_command(url, 'вентилятор_команда', 1)
                state1 = obtain_state(url, 'БП ПЭВМ')
                if state1 != 'вкл':
                    # collect_logs('БП ПЭВМ выключен')
                    send_line_command(url, 'БП ПЭВМ', 1)
                state2 = obtain_state(url, 'БП Шелест')
                if state2 != 'вкл':
                    # collect_logs('БП Шелест выключен')
                    send_line_command(url, 'БП Шелест', 1)
                state3 = obtain_state(url, 'БП АПЕМ')
                if state3 != 'вкл':
                    # collect_logs('БП АПЕМ выключен')
                    send_line_command(url, 'БП АПЕМ', 1)
                state4 = obtain_state(url, 'ЭВМ1')
                state5 = obtain_state(url, 'ЭВМ2')
                if state4 != 'вкл':
                    send_impulse(url, 'ЭВМ1', time_pulse=3, action='вкл')
                    state4 = obtain_state(url, 'ЭВМ1')
                    if state4 != 'вкл':
                        send_impulse(url, 'ЭВМ1', time_pulse=3, action='вкл')
                    time.sleep(4)
                if state5 != 'вкл':
                    send_impulse(url, 'ЭВМ2', time_pulse=3, action='вкл')
                time.sleep(1)
                complex_state = get_complex_state(url)
                c['complex_state_dict'][strizh_name] = complex_state
                c['complex_state_json'] = json.dumps(c['complex_state_dict'])
                str_log = strizh_name + ': ' + complex_state
                collect_logs(str_log)
                # render(request, "main.html", context=c)
                # functioning_loop(request)

    return redirect('/main')
    # return render(request, "main.html", context=c)


def turn_off_bp(request):
    global c

    for strizh_name in c.get('chosen_strizh'):
        if strizh_name != 'None':
            url = c['url_uniping_dict'][strizh_name]
            try:
                requests.get(url, auth=auth, timeout=0.2)
            except:
                result_get = 'ошибка uniping'
                collect_logs(strizh_name + ': ' + result_get)
                continue

            state4 = obtain_state(url, 'ЭВМ1')
            state5 = obtain_state(url, 'ЭВМ2')
            if state4 != 'выкл':
                send_impulse(url, 'ЭВМ1', time_pulse=3, action='выкл')
            if state5 != 'выкл':
                send_impulse(url, 'ЭВМ2', time_pulse=3, action='выкл')

            time.sleep(5)
            state1 = obtain_state(url, 'БП ПЭВМ')
            if state1 != 'выкл':
                # collect_logs('БП ПЭВМ включен')
                send_line_command(url, 'БП ПЭВМ', 0)
            state2 = obtain_state(url, 'БП Шелест')
            if state2 != 'выкл':
                # collect_logs('БП Шелест включен')
                send_line_command(url, 'БП Шелест', 0)
            state3 = obtain_state(url, 'БП АПЕМ')
            if state3 != 'выкл':
                # collect_logs('БП АПЕМ включен')
                send_line_command(url, 'БП АПЕМ', 0)

            send_line_command(url, 'вентилятор_команда', 0)
            time.sleep(1)
            send_impulse(url, 'РЕЗЕТ', time_pulse=6, action='выкл')

            complex_state = get_complex_state(url)
            c['complex_state_dict'][strizh_name] = complex_state
            c['complex_state_json'] = json.dumps(c['complex_state_dict'])
            c['logs'] = logs
            c['logs_list'] = logs_list
    # functioning_loop(request)
    return redirect('/main')
    # return render(request, "main.html", context=c)


def show_logs(request):
    global logs
    c['logs'] = logs
    c['logs_list'] = logs_list
    return redirect('/main')
    # return render(request, "main.html", context=c)


def get_map_form(request):
    global c
    if request.method == "POST":
        chosen_map_link = request.POST.get('chosen_map')
        c['chosen_map_link'] = chosen_map_link
        c['map_form'] = MapChoosingForm(request.POST, initial={'chosen_map': c.get('chosen_map_link')})
    try:
        return redirect(f"/{c.get('page_picked')}")
    except:
        render(request, "journal.html", context=c)


def choose_drone_toshow(request):
    global c
    if request.method == 'POST':
        c['page_picked'] = 'choose_drone_toshow'
        c['chosen_complex_to_show'] = ''
        detection_id = request.POST.get('detection_id')
        drone_id = request.POST.get('drone_id')
        for el_db in DroneTrajectoryJournal.objects.all():
            el_db.delete()
        for el_db in DroneJournal.objects.all():
            el_db.delete()
        if drone_id:
            AP = AeroPoints.objects.filter(drone_id=drone_id)
            for DP in AP:
                drone_value = DroneTrajectoryJournal(system_name=DP.system_name,
                                                     center_freq=DP.center_freq,
                                                     brandwidth=DP.brandwidth,
                                                     detection_time=DP.detection_time,
                                                     comment_string=DP.comment_string,
                                                     drone_lat=DP.drone_lat,
                                                     drone_lon=DP.drone_lon,
                                                     remote_lat=DP.remote_lat,
                                                     remote_lon=DP.remote_lon,
                                                     azimuth=DP.azimuth,
                                                     area_sector_start_grad=DP.area_sector_start_grad,
                                                     area_sector_end_grad=DP.area_sector_end_grad,
                                                     area_radius_m=DP.area_radius_m,
                                                     ip=DP.ip,
                                                     current_time=DP.current_time,
                                                     height=DP.height,
                                                     strig_name=DP.strig_name)
                drone_value.save()
                c['chosen_complex_to_show'] = DP.strig_name
        elif detection_id:
            DP = Point.objects.filter(pk=detection_id)[0]
            drone_value = DroneJournal(drone_id='0',
                                       system_name=DP.system_name,
                                       center_freq=DP.center_freq,
                                       brandwidth=DP.brandwidth,
                                       detection_time=DP.detection_time,
                                       comment_string=DP.comment_string,
                                       drone_lat=DP.drone_lat,
                                       drone_lon=DP.drone_lon,
                                       remote_lat=0,
                                       remote_lon=0,
                                       azimuth=DP.azimuth,
                                       area_sector_start_grad=DP.area_sector_start_grad,
                                       area_sector_end_grad=DP.area_sector_end_grad,
                                       area_radius_m=DP.area_radius_m,
                                       ip=DP.ip,
                                       current_time=DP.current_time,
                                       height=DP.height,
                                       strig_name=DP.strig_name)
            drone_value.save()
            c['chosen_complex_to_show'] = DP.strig_name
            # return redirect('/journal')

    return render(request, "journal.html", context=c)


def reset_filter_strizh(request):
    global c
    c['filtered_strizhes'] = ''
    return redirect('/filter_all')
    # return render(request, "journal.html", context=c)


def reset_filter_skypoint(request):
    global c
    c['filtered_skypoints'] = ''
    return redirect('/filter_all')
    # return render(request, "journal.html", context=c)


def filter_all(request):
    global c
    xx = c
    # TODO maybe delete this condition and value
    if not c.get('saved_table'):
        c['saved_table'] = False
    if not c.get('filtered_strizhes'):
        c['filtered_strizhes'] = ''
        strizh_names = ''
    else:
        strizh_names_arr = [st.name for st in c['filtered_strizhes']]
        strizh_names = ';; '.join(strizh_names_arr)
    if not c.get('filtered_skypoints'):
        c['filtered_skypoints'] = ''
        skypoints_names = ''
    else:
        skypoints_names_arr = [st.name for st in c['filtered_skypoints']]
        skypoints_names = ';; '.join(skypoints_names_arr)

    c['start_datetime'] = c.get('start_datetime') if c.get('start_datetime') else ''
    c['end_datetime'] = c.get('end_datetime') if c.get('end_datetime') else ''
    xx = c
    strizh_value = StrizhJournal(filtered_strizhes=strizh_names, filtered_skypoints=skypoints_names,
                                 start_datetime=c['start_datetime'], end_datetime=c['end_datetime'])
    strizh_value.save()
    order_sign = '' if c.get('order_sign') == '+' else '-'
    table_filter = c.get('table_filter') if c.get('table_filter', '') != '' else 'current_time'
    if request.method == '':
        form_filter = StrizhFilterForm(request.POST)
        form_filter_skypoint = SkyPointFilterForm(request.POST)
        if form_filter.is_valid():
            filtered_strizhes = form_filter.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes
        if form_filter_skypoint.is_valid():
            filtered_skypoints = form_filter_skypoint.cleaned_data.get('filtered_skypoints')
            c['filtered_skypoints'] = filtered_skypoints
    else:
        form_filter = StrizhFilterForm()
        form_filter_skypoint = SkyPointFilterForm()
        strizh_drones = Point.objects.order_by(order_sign + table_filter)
        aero_points = AeroPoints.objects.order_by(order_sign + table_filter)
        filter_values = StrizhJournal.objects.all().order_by('-pk')
        time_start = filter_values[0].start_datetime
        time_end = filter_values[0].end_datetime
        now = datetime.datetime.now()
        if time_start != '':
            dateYMDHM = time_start.split('T')
            YMD_arr = dateYMDHM[0].split('-')
            HM_arr = dateYMDHM[1].split(':')
            time_start_datetime = now.replace(year=int(YMD_arr[0]), month=int(YMD_arr[1]), day=int(YMD_arr[2]),
                                              hour=int(HM_arr[0]), minute=int(HM_arr[1]), second=0)
        else:
            time_start_datetime = now.replace(year=1970)
        if time_end != '':
            dateYMDHM = time_end.split('T')
            YMD_arr = dateYMDHM[0].split('-')
            HM_arr = dateYMDHM[1].split(':')
            time_end_datetime = now.replace(year=int(YMD_arr[0]), month=int(YMD_arr[1]), day=int(YMD_arr[2]),
                                            hour=int(HM_arr[0]), minute=int(HM_arr[1]), second=59)
        else:
            time_end_datetime = now
        drones_pk = []
        all_complexes = set()
        for drone in strizh_drones:
            all_complexes.add(drone.strig_name)
            if time_start_datetime <= get_datetime_drone(drone.current_time) <= time_end_datetime:
                drones_pk.append(drone.pk)
        drones_pk_aero = []

        all_complexes_aero = set()
        for drone_aero in aero_points:
            all_complexes_aero.add(drone_aero.strig_name)
            if time_start_datetime <= get_datetime_drone(drone_aero.current_time) <= time_end_datetime:
                drones_pk_aero.append(drone_aero.pk)
        names_str = filter_values[0].filtered_strizhes
        names_sky = filter_values[0].filtered_skypoints

        names_arr = names_str.split(';; ')
        names_arr_sky = names_sky.split(';; ')
        if len(names_str) == 0 and len(names_sky) == 0:
            names_arr = list(all_complexes)
            names_arr_sky = list(all_complexes_aero)
        all_drones_s = strizh_drones.filter(strig_name__in=names_arr, pk__in=drones_pk)
        all_drones_a = aero_points.filter(strig_name__in=names_arr_sky, pk__in=drones_pk_aero)
        if len(all_drones_s) != 0 and len(all_drones_a) != 0:
            all_drones_res = all_drones_s.union(all_drones_a, all=True)
        else:
            if len(all_drones_s) == 0:
                all_drones_res = all_drones_a
            if len(all_drones_a) == 0:
                all_drones_res = all_drones_s
        all_drones_res = all_drones_res.order_by(order_sign + table_filter)
        c['all_drones_res'] = all_drones_res
    c['form_filter'] = form_filter
    c['form_filter_skypoint'] = form_filter_skypoint
    return redirect('/journal')
    # return render(request, "journal.html", context=c)


def journal(request):
    global c
    try:
        c
    except NameError:
        c = init_content()
    c['start_datetime'] = c.get('start_datetime', '')
    c['end_datetime'] = c.get('end_datetime', '')
    xx = c
    c['page_picked'] = 'journal'

    with open("config.json", encoding='utf-8-sig') as json_cfg:
        data_conf = json.load(json_cfg)
    c['map_link_default'] = data_conf['map_config']['default_link']

    for el_db in DroneTrajectoryJournal.objects.all():
        el_db.delete()
    for el_db in DroneJournal.objects.all():
        el_db.delete()

    if request.method == 'POST':

        form_filter = StrizhFilterForm(request.POST)
        form_filter_skypoint = SkyPointFilterForm(request.POST)
        form_filter_table = TableFilterForm(request.POST)
        form_order_table = TableOrderForm(request.POST)
        c['order_sign'] = '-'
        c['table_filter'] = 'current_time'
        all_drones_a = AeroPoints.objects.all().order_by(c['order_sign'] + c['table_filter'])
        all_drones_s = Point.objects.all().order_by(c['order_sign'] + c['table_filter'])
        all_drones_res = all_drones_s.union(all_drones_a)
        c['all_drones_res'] = all_drones_res
    else:
        if not c.get('form_time_pick'):
            c['form_time_pick'] = TimePickForm()
        # form_time_pick = TimePickForm()
        # form_time_pick = TimePickForm(initial={'datetime': c.get('start_datetime'),
        #                                        'end_datetime': c.get('end_datetime') })

        form_filter = StrizhFilterForm()
        map_form = MapChoosingForm(initial={'chosen_map': c.get('chosen_map_link')})
        c['map_form'] = map_form
        if len(map_form.fields['chosen_map'].choices) == 0:
            map_obj = Maps(map_link=c['map_link_default'], map_name='Спутник')
            map_obj.save()
        form_filter_skypoint = SkyPointFilterForm()
        form_filter_table = c.get('form_filter_table', TableFilterForm())
        form_order_table = c.get('form_order_table', TableOrderForm())
        # form_order_table = TableOrderForm()

        order_sign = '' if c.get('order_sign') == '+' else '-'
        table_filter = c.get('table_filter') if c.get('table_filter', '') != '' else 'current_time'
        bool_expr = bool(c.get('start_datetime') != '') or bool(c.get('end_datetime') != '')
        if c.get('all_drones_res') is None:
            if bool_expr or len(c) <= 6:
                # не записан в словарь, но есть фильтр времени след-но выводим все
                all_drones_a = AeroPoints.objects.all().order_by(order_sign + table_filter)
                all_drones_s = Point.objects.all().order_by(order_sign + table_filter)
                all_drones_res = all_drones_s.union(all_drones_a)
                all_drones_res = all_drones_res.order_by(order_sign + table_filter)
                c['all_drones_res'] = all_drones_res
        else:
            # есть в словаре
            all_drones_res = c.get('all_drones_res')
    # c['form_time_pick'] = form_time_pick
    c['form_filter'] = form_filter

    c['form_filter_skypoint'] = form_filter_skypoint
    c['form_filter_table'] = form_filter_table
    c['form_order_table'] = form_order_table
    return render(request, "journal.html", context=c)


def apply_filter_table(request):
    if request.method == 'POST':
        table_filter = request.POST.get('field', c.get('table_filter'))
        order_sign = '' if (c.get('order_sign') == '+' or c.get('order_sign') == '') else '-'
        all_drones_res = c.get('all_drones_res')
        all_drones_res = all_drones_res.order_by(order_sign + table_filter)
        c['all_drones_res'] = all_drones_res
        c['table_filter'] = table_filter
        form_filter_table = TableFilterForm(request.POST, initial={'field': table_filter})
    else:
        form_filter_table = TableFilterForm()
        form_order_table = TableOrderForm()
    c['form_filter_table'] = form_filter_table
    # c['form_order_table'] = form_order_table
    return redirect('/journal')
    # return render(request, "journal.html", context=c)


def apply_order_table(request):
    if request.method == 'POST':
        table_filter = 'current_time' if not c.get('table_filter') else c.get('table_filter')
        order_sign = request.POST.get('order_sign', c.get('order_sign'))
        order_sign2 = '' if order_sign == '+' else '-'
        all_drones_res = c.get('all_drones_res')
        all_drones_res = all_drones_res.order_by(order_sign2 + table_filter)

        # c['form_drone_alldrones'] = form_drone_alldrones
        c['all_drones_res'] = all_drones_res
        c['order_sign'] = order_sign
        c['table_filter'] = table_filter
        form_order_table = TableOrderForm(request.POST, initial={'order_sign': order_sign})
    else:
        form_order_table = TableOrderForm()
    c['form_order_table'] = form_order_table
    return redirect('/journal')
    # return render(request, "journal.html", context=c)


def filter_nomer_strizha(request):
    global c
    if request.method == 'POST':
        form_filter = StrizhFilterForm(request.POST)
        if form_filter.is_valid():
            filtered_strizhes = form_filter.cleaned_data.get('filtered_strizhes')
            c['filtered_strizhes'] = filtered_strizhes
    return redirect('/filter_all')
    # return render(request, "journal.html", context=c)


def filter_nomer_skypoint(request):
    global c
    if request.method == 'POST':
        form_filter_skypoint = SkyPointFilterForm(request.POST)
        if form_filter_skypoint.is_valid():
            filtered_skypoints = form_filter_skypoint.cleaned_data.get('filtered_skypoints')
            c['filtered_skypoints'] = filtered_skypoints
    return redirect('/filter_all')
    # return render(request, "journal.html", context=c)


def apply_period(request):
    global c, reset_time
    c['saved_table'] = False
    if request.method == 'POST':
        start = ''
        end = ''
        if request.POST.get('datetime_start'):
            start = request.POST['datetime_start']
            print('got start ', start, '\n')
            start_arr = start.split(' ')
            start_datetime = "-".join(start_arr)
            form_time_pick = TimePickForm(request.POST, initial={'datetime_start': start})
            c['form_time_pick'] = form_time_pick
            c['start_datetime'] = start_datetime
        if request.POST.get('datetime_end'):
            end = request.POST['datetime_end']
            print('got end', end, '\n')
            end_arr = end.split(' ')
            end_datetime = "-".join(end_arr)
            form_time_pick = TimePickForm(request.POST, initial={'datetime_end': end})
            c['form_time_pick'] = form_time_pick
            c['end_datetime'] = end_datetime
        if start and end:
            form_time_pick = TimePickForm(request.POST, initial={'datetime_start': start, 'datetime_end': end})
            c['form_time_pick'] = form_time_pick
    return redirect('/filter_all')
    # return render(request, "journal.html", context=c)


def reset_filter(request):
    global c
    c['filtered_strizhes'] = ''
    c['filtered_skypoints'] = ''
    c['saved_table'] = False
    c['table_filter'] = 'current_time'
    c['order_sign'] = '-'
    c['start_datetime'] = ''
    c['end_datetime'] = ''
    xx = c
    del c['all_drones_res']
    form_time_pick = TimePickForm()
    form_filter = StrizhFilterForm()
    form_filter_skypoint = SkyPointFilterForm()
    # form_drone = DroneFilterForm()
    form_filter_table = TableFilterForm()
    form_order_table = TableOrderForm()
    if request.method == 'POST':

        # form_filter_table = TableFilterForm(request.POST)
        # form_drone_alldrones = Point.objects.all().order_by('-current_time')
        all_drones_a = AeroPoints.objects.all().order_by('-current_time')
        all_drones_s = Point.objects.all().order_by('-current_time')
        all_drones_res = all_drones_s.union(all_drones_a)
        all_drones_res = all_drones_res.order_by('-current_time')

        c['all_drones_res'] = all_drones_res

        for el in StrizhJournal.objects.all():
            el.delete()
        for el in DroneTrajectoryJournal.objects.all():
            el.delete()
        for el in DroneJournal.objects.all():
            el.delete()

    c['form_time_pick'] = form_time_pick
    c['form_filter'] = form_filter
    c['form_filter_skypoint'] = form_filter_skypoint
    c['form_filter_table'] = form_filter_table
    c['form_order_table'] = form_order_table

    return redirect('/journal')
    # return render(request, "journal.html", context=c)


def export_csv(request):
    global c
    c['saved_table'] = False

    drones_filtered_strizh = c.get('all_drones_res')
    d = datetime.datetime.now()
    csv_name = "log_{}_{}_{}_{}_{}_{}.csv".format(d.hour, d.minute, d.second, d.day, d.month, d.year)
    print(csv_name)
    with open(os.path.join('saved_logs_csv', csv_name), 'w+', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        first_row = 'Имя дрона', 'Имя комплекса', 'ID дрона', 'Несущая частота (ГГц)', 'Полоса пропускания (МГц)', \
                    'Время обнаружения', 'Комментарии', 'Координаты дрона', 'Азимут', \
                    'Внутренний радиус сектора (м.)', 'Внешний радиус сектора (м.)', 'Радиус сектора (м)', \
                    'IP-адрес стрижа', 'Высота (м.)'
        writer.writerow(first_row)
        # TODO write frequencies correctly (MGhz..)
        for dr in drones_filtered_strizh:
            writer = csv.writer(f)
            azimuth = int(re.findall('[0-9]+', dr.azimuth)[0])
            row = dr.system_name, dr.strig_name, dr.drone_id, round(dr.center_freq / 1e9, 3), round(dr.brandwidth / 1e6,
                                                                                                    0), \
                  dr.current_time, dr.comment_string, (dr.drone_lat, dr.drone_lon), azimuth, \
                  dr.area_sector_start_grad, dr.area_sector_end_grad, dr.area_radius_m, dr.ip, dr.height

            writer.writerow(row)
    return redirect('/journal')
    # return render(request, "journal.html", context=c)


lines_map = {'обогрев': 1,
             'вентилятор_команда': 2,
             'БП ПЭВМ': 3,
             'БП Шелест': 5,
             'БП АПЕМ': 7,
             'ЭВМ1': 10,
             'ЭВМ2': 14,
             'РЕЗЕТ': 15,
             }

lines_control_map = {
    'вентилятор_команда': 2,
    'БП ПЭВМ': 4,
    'БП Шелест': 6,
    'БП АПЕМ': 8,
    'ЭВМ1': 9,
    'ЭВМ2': 13,
    'вентилятор': 16,
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
    states_map = {0: 'вентилятор', 1: "БП ПЭВМ",
                  2: 'БП Шелест', 3: "БП АПЕМ",
                  4: 'ЭВМ2', 5: "ЭВМ2"}
    states = [obtain_state(url, val) for key, val in states_map.items()]

    states_off = [i for i, e in enumerate(states) if e == 'выкл']
    if len(states_off) == 0:
        complex_state = 'включен'
    elif len(states_off) == 6:
        complex_state = 'выключен'
    else:
        complex_state = 'выключен '
        for i, stat in enumerate(states_off):
            if i == 0:
                complex_state += states_map[stat]
            else:
                complex_state += f", {states_map[stat]}"
    # complex_state = 'включен' if all([True if x == 'вкл' else False for x in states1]) else 'выключен вентилятор'
    # complex_state = 'включен' if all([True if x == 'вкл' else False for x in states2]) else 'выключен'
    print(complex_state)
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
        value = re.findall(r"[-+]?\d*\.\d+|\d+", value)[0]
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
        result_get = 'ошибка uniping'
    if 'ok' in result_get:
        collect_logs("{}".format(log_str))
    else:
        collect_logs("проверьте, выбран ли стриж")


def choose_apem_toshow(request):
    global c
    if request.method == 'POST':
        c['initial'] = 'False'
        form_apem = ApemsConfigurationForm(request.POST)
        c['delete_button'] = 'True'
        if form_apem.is_valid():
            apem_change_form = ApemsChangingForm(request.POST)
            if apem_change_form.is_valid():
                if 'delete_apem' in request.POST:
                    c['initial'] = 'True'
                    if c.get('apem_toshow'):
                        c['apem_action_message'] = '{} был удален'.format(c.get('apem_toshow')[0])
                        print(c.get('apem_toshow'))
                        ApemsConfiguration.objects.get(id=c['apem_toshow'][0].pk).delete()

                elif 'set_apem' in request.POST:
                    AP = apem_change_form.cleaned_data
                    ApemsNew = ApemsConfiguration(strizh_name=AP.get('strizh_name'),
                                                  freq_podavitelya=AP.get('freq_podavitelya'),
                                                  deg_podavitelya=AP.get('deg_podavitelya'),
                                                  type_podavitelya=AP.get('type_podavitelya'),
                                                  ip_podavitelya=AP.get('ip_podavitelya'),
                                                  canal_podavitelya=AP.get('canal_podavitelya'),
                                                  usileniye_db=AP.get('usileniye_db'))

                    apem_change_form.fields['strizh_name'].initial = AP.get('strizh_name')
                    apem_change_form.fields['freq_podavitelya'].initial = AP.get('freq_podavitelya')
                    apem_change_form.fields['deg_podavitelya'].initial = AP.get('deg_podavitelya')
                    apem_change_form.fields['type_podavitelya'].initial = AP.get('type_podavitelya')
                    apem_change_form.fields['ip_podavitelya'].initial = AP.get('ip_podavitelya')
                    apem_change_form.fields['canal_podavitelya'].initial = AP.get('canal_podavitelya')
                    apem_change_form.fields['usileniye_db'].initial = AP.get('usileniye_db')
                    if c.get('apem_toshow'):
                        c['apem_action_message'] = '{} был отредактирован'.format(c.get('apem_toshow')[0])
                        try:
                            ApemsConfiguration.objects.get(id=c['apem_toshow'][0].pk).delete()
                            c['apem_toshow'] = [ApemsNew]
                        except:
                            print(c['apem_toshow'][0])
                        ApemsNew.save()
                    else:
                        c['apem_action_message'] = '{} был создан'.format(ApemsNew)
                        ApemsNew.save()
            else:
                apem_toshow = form_apem.cleaned_data.get('apem_toshow')
                c['apem_toshow'] = apem_toshow
                apem_change_form = ApemsChangingForm()
                AP = ApemsConfiguration.objects.get(id=c['apem_toshow'][0].pk)
                c['apem_action_message'] = 'Редактирование {}'.format(AP)
                apem_change_form.fields['strizh_name'].initial = AP.strizh_name
                apem_change_form.fields['freq_podavitelya'].initial = AP.freq_podavitelya
                apem_change_form.fields['deg_podavitelya'].initial = AP.deg_podavitelya
                apem_change_form.fields['type_podavitelya'].initial = AP.type_podavitelya
                apem_change_form.fields['ip_podavitelya'].initial = AP.ip_podavitelya
                apem_change_form.fields['canal_podavitelya'].initial = AP.canal_podavitelya
                apem_change_form.fields['usileniye_db'].initial = AP.usileniye_db

    else:
        form_apem = ApemsConfigurationForm()
        apem_change_form = ApemsChangingForm()

    if c.get('set_strizh_apem'):
        form_apem.fields.get('apem_toshow').choices.field.queryset = form_apem.AllApems.filter(
            strizh_name=c['set_strizh_apem'][0])

    c['form_apem'] = form_apem
    c['apem_change_form'] = apem_change_form

    return render(request, "configuration.html", context=c)


def set_apem(request):
    global c
    if request.method == 'POST':
        c['initial'] = 'True'
        c['delete_button'] = 'True'
        # form_apem = ApemsConfigurationForm()
        # if form_apem.is_valid():
        apem_change_form = ApemsChangingForm(request.POST)
        if apem_change_form.is_valid():
            AP = apem_change_form.cleaned_data
            ApemsNew = ApemsConfiguration(strizh_name=AP.get('strizh_name'),
                                          freq_podavitelya=AP.get('freq_podavitelya'),
                                          deg_podavitelya=AP.get('deg_podavitelya'),
                                          type_podavitelya=AP.get('type_podavitelya'),
                                          ip_podavitelya=AP.get('ip_podavitelya'),
                                          canal_podavitelya=AP.get('canal_podavitelya'),
                                          usileniye_db=AP.get('usileniye_db'))

            apem_change_form.fields['strizh_name'].initial = AP.get('strizh_name')
            apem_change_form.fields['freq_podavitelya'].initial = AP.get('freq_podavitelya')
            apem_change_form.fields['deg_podavitelya'].initial = AP.get('deg_podavitelya')
            apem_change_form.fields['type_podavitelya'].initial = AP.get('type_podavitelya')
            apem_change_form.fields['ip_podavitelya'].initial = AP.get('ip_podavitelya')
            apem_change_form.fields['canal_podavitelya'].initial = AP.get('canal_podavitelya')
            apem_change_form.fields['usileniye_db'].initial = AP.get('usileniye_db')

            if c.get('apem_toshow'):
                xx = c['apem_toshow']
                c['apem_action_message'] = '{} был отредактирован'.format(c.get('apem_toshow')[0])
                try:
                    ApemsConfiguration.objects.get(id=c['apem_toshow'][0].pk).delete()
                    c['apem_toshow'] = [ApemsNew]
                except:
                    print(c['apem_toshow'][0])
                ApemsNew.save()
            else:
                c['apem_action_message'] = '{} был создан'.format(ApemsNew)
                # c['apem_toshow'] = [ApemsNew]
                ApemsNew.save()
    else:
        form_apem = ApemsConfigurationForm()
        apem_change_form = ApemsChangingForm()
    if c.get('set_strizh_apem'):
        form_apem.fields.get('apem_toshow').choices.field.queryset = form_apem.AllApems.filter(
            strizh_name=c['set_strizh_apem'][0])
    c['form_apem'] = form_apem
    c['apem_change_form'] = apem_change_form

    return render(request, "configuration.html", context=c)


def delete_apem(request):
    global c
    if request.method == 'POST':
        c['initial'] = 'True'
        form_apem = ApemsConfigurationForm(request.POST)

        if form_apem.is_valid():
            apem_change_form = ApemsChangingForm(request.POST)
            xx = c
            if c.get('apem_toshow'):
                c['apem_action_message'] = '{} был удален'.format(c.get('apem_toshow')[0])
                print(c.get('apem_toshow'))
                ApemsConfiguration.objects.get(id=c['apem_toshow'][0].pk).delete()

                # ApemsNew.save()

    else:
        form_apem = ApemsConfigurationForm()
        apem_change_form = ApemsChangingForm()
    if c.get('set_strizh_apem'):
        form_apem.fields.get('apem_toshow').choices.field.queryset = form_apem.AllApems.filter(
            strizh_name=c['set_strizh_apem'][0])
    # c['form_apem'] = form_apem
    # c['apem_change_form'] = apem_change_form

    return render(request, "configuration.html", context=c)


def new_apem(request):
    global c
    if request.method == 'POST':
        c['initial'] = 'False'
        c['delete_button'] = 'False'
        form_apem = ApemsConfigurationForm(request.POST)

        if form_apem.is_valid():
            # apem_change_form = ApemsChangingForm()
            c['apem_action_message'] = 'Создание нового блока'
            c['apem_toshow'] = ''
            # form_apem = ApemsConfigurationForm()
        if 'set_apem' in request.POST:
            apem_change_form = ApemsChangingForm(request.POST)
            if apem_change_form.is_valid():
                AP = apem_change_form.cleaned_data
                ApemsNew = ApemsConfiguration(strizh_name=c.get('set_strizh_apem')[0],
                                              freq_podavitelya=AP.get('freq_podavitelya'),
                                              deg_podavitelya=AP.get('deg_podavitelya'),
                                              type_podavitelya=AP.get('type_podavitelya'),
                                              ip_podavitelya=AP.get('ip_podavitelya'),
                                              canal_podavitelya=AP.get('canal_podavitelya'),
                                              usileniye_db=AP.get('usileniye_db'))
                c['apem_action_message'] = '{} был создан'.format(ApemsNew)
                # c['apem_toshow'] = [ApemsNew]
                ApemsNew.save()
        elif 'new_apem' in request.POST:
            apem_change_form = ApemsChangingForm()
            apem_change_form.fields.get('strizh_name').initial = c['set_strizh_apem'][0]
        else:
            form_apem = ApemsConfigurationForm()
            apem_change_form = ApemsChangingForm()

    if c.get('set_strizh_apem'):
        form_apem.fields.get('apem_toshow').choices.field.queryset = form_apem.AllApems.filter(
            strizh_name=c['set_strizh_apem'][0])
    c['form_apem'] = form_apem
    c['apem_change_form'] = apem_change_form

    return render(request, "configuration.html", context=c)


def configuration(request):
    global c
    Strizhes = Strizh.objects.all()
    c['set_strizh_apem'] = ['None' for _ in range(len(Strizhes))]
    c['page_picked'] = 'configuration'

    if request.method == 'POST':
        form_apem = ApemsConfigurationForm(request.POST)
        # for el_db in DroneJournal.objects.all():
        #     el_db.delete()
        if form_apem.is_valid():
            apem_toshow = form_apem.cleaned_data.get('apem_toshow')
            c['apem_toshow'] = apem_toshow
            c['delete_button'] = 'True'
        c['initial'] = 'True'
    else:
        c['is_strizh_chosen'] = 'False'
        c['initial'] = 'True'
        form_apem = ApemsConfigurationForm()
        form_strizh = StrizhForm()

    if c.get('set_strizh_apem'):
        form_apem.fields.get('apem_toshow').choices.field.queryset = form_apem.AllApems.filter(
            strizh_name=c['set_strizh_apem'][0])

    # c['form_apem'] = form_apem
    c['form_strizh'] = form_strizh

    # apems = ApemsConfiguration.objects.filter(strizh_name=c['set_strizh_apem'][0]).order_by('-freq_podavitelya')
    #
    # c['apems'] = apems

    return render(request, "configuration.html", context=c)


def track_page(request):
    global c

    return render(request, "track_page.html", context=c)

# def check_states_on():
#     temperature_state = check_condition(c['temperature'], low_border=low_t, high_border=high_t)
#     if temperature_state != 0:
#         collect_logs('температура не в порядке')
#         set_correct_temperature(temperature_state)
#
#     state0 = obtain_state('датчик потока', to_collect_logs=True)
#     if state0 != 'вкл':
#         collect_logs('АВАРИЯ! отсутствует вентиляция, возможен перегрев оборудования')
#         # send_line_command('датчик потока', arg=1)
#
#     state1 = obtain_state('БП ПЭВМ', to_collect_logs=True)
#     if state1 != 'вкл':
#         collect_logs('АВАРИЯ! БП ПЭВМ выключен')
#     state2 = obtain_state('БП Шелест', to_collect_logs=True)
#     if state2 != 'вкл':
#         collect_logs('АВАРИЯ! БП Шелест выключен')
#     state3 = obtain_state('БП АПЕМ', to_collect_logs=True)
#     if state3 != 'вкл':
#         collect_logs('АВАРИЯ! БП АПЕМ выключен')
#     state4 = obtain_state('ЭВМ1', to_collect_logs=True)
#     if state4 != 'вкл':
#         collect_logs('АВАРИЯ! ЭВМ1 выключен')
#         send_impulse('ЭВМ1', time_pulse=3, action='вкл')
#     state5 = obtain_state('ЭВМ2', to_collect_logs=True)
#     if state5 != 'вкл':
#         collect_logs('АВАРИЯ! ЭВМ2 выключен')
#         send_impulse('ЭВМ2', time_pulse=3, action='вкл')
#
#     states_names = [state1, state2, state3, state4, state5]
#     states = [True if st == 'вкл' else False for st in states_names]
#     if all(states):
#         return True
