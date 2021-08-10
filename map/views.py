import os.path
import re
import time
import json
import datetime
import csv

import requests
from django.forms import ModelMultipleChoiceField
from django.shortcuts import redirect
from django.shortcuts import render
from django.core.serializers import serialize

from geo.models import Strizh, Point, DroneJournal, StrizhJournal, ApemsConfiguration
from .forms import StrizhForm, StrizhFilterForm, DroneFilterForm, ApemsConfigurationForm, ApemsChangingForm

from ControlString_co.control_trace import scan_on_off, check_state
from ControlString_co.shelest_jam import jammer_on_off


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
c = dict(chosen_strizh=[], start_datetime=start_datetime, end_datetime=end_datetime)


def index(request):
    return render(request, "index.html")


def return_conditions(url):
    global low_t, high_t, low_h, high_h, humidity, c
    global auth
    temperature = ''
    try:
        temp = requests.get(url + 'thermo.cgi?t1', auth=auth, timeout=0.05)
        temp_str = temp.content.decode("utf-8")
        temp_list = re.findall('[0-9]+', temp_str)
        if len(temp_list) > 0:
            temperature = '.'.join(temp_list)
    except:
        temperature = 'ошибка соединения с uniping'
    try:
        hum = requests.get(url + 'relhum.cgi?h1', auth=auth, timeout=0.05)
        hum_str = hum.content.decode("utf-8")
        hum_list = re.findall('[0-9]+', hum_str)
        if len(hum_list) > 1:
            humidity = hum_list[0]
    except:
        humidity = 'ошибка соединения с uniping'

    if 'ошибка' not in temperature and 'ошибка' not in humidity:
        if low_t < float(temperature) < high_t and low_h < float(humidity) < high_h:
            weather_state = "OK"
        else:
            weather_state = "NOT OK !!!"
    else:
        weather_state = "ошибка соединения с uniping"

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
                    xxx = c
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


def back2main(request):
    return redirect(request.META['HTTP_REFERER'])


def choose_nomer_strizha(request):
    global c

    strizhes = Strizh.objects.order_by('-lon').all()
    c['chosen_strizh'] = ['None' for _ in range(len(strizhes))]
    temperature_dict = {}
    humidity_dict = {}
    weather_state_dict = {}
    if request.method == 'POST':
        c['action_strizh'] = ''
        form = StrizhForm(request.POST)
        if form.is_valid():
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'][0] = chosen_strizh.name
            for strizh in strizhes:
                if c['chosen_strizh'][0] == strizh.name:
                    c['url_uniping_dict'][strizh.name] = 'http://' + strizh.uniping_ip + '/'
                    temperature_dict[strizh.name], humidity_dict[strizh.name], weather_state_dict[strizh.name] = \
                        return_conditions(c['url_uniping_dict'][strizh.name])
            c['temperature_dict'] = temperature_dict
            c['humidity_dict'] = humidity_dict
            c['weather_state_dict'] = weather_state_dict

        # nomer = request.POST['chosen_strizh']
        # c['chosen_strizh'] = nomer
        xx = c

    return render(request, "main.html", context=c)


def choose_all_strizhes(request):
    global c

    strizhes = Strizh.objects.order_by('-lon').all()
    if request.method == 'POST':
        c['action_strizh'] = ''
        c['chosen_strizh'] = [strizh.name for strizh in strizhes]

        temperature_dict = {}
        humidity_dict = {}
        weather_state_dict = {}
        url_uniping_dict = {}
        for strizh in strizhes:
            url_uniping_dict[strizh.name] = 'http://' + strizh.uniping_ip + '/'
            temperature_dict[strizh.name], humidity_dict[strizh.name], weather_state_dict[strizh.name] = \
                return_conditions(url_uniping_dict[strizh.name])
        c['temperature_dict'] = temperature_dict
        c['humidity_dict'] = humidity_dict
        c['weather_state_dict'] = weather_state_dict
        c['url_uniping_dict'] = url_uniping_dict

        # nomer = request.POST['chosen_strizh']
        # c['chosen_strizh'] = nomer

    # if c.get("chosen_strizh"):
    #     # c["action_strizh"] = "Выбрано: '{}'".format(c.get("chosen_strizh"))
    #     temperature, humidity, weather_state = return_conditions(c['url_uniping'])
    #     c['temperature'] = temperature
    #     c['humidity'] = humidity
    #     c['weather_state'] = weather_state

    return render(request, "main.html", context=c)


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
    complex_state = ''

    c['start_datetime'] = start_datetime
    c['end_datetime'] = end_datetime

    temperature_dict = {}
    humidity_dict = {}
    weather_state_dict = {}
    url_uniping_dict = {}
    complex_state_dict = {}

    strizhes = Strizh.objects.order_by('-lon').all()
    for strizh in strizhes:
        url_uniping_dict[strizh.name] = 'http://' + strizh.uniping_ip + '/'

        temperature_dict[strizh.name], humidity_dict[strizh.name], weather_state_dict[strizh.name], = \
            return_conditions(url_uniping_dict[strizh.name])

        complex_state_dict[strizh.name] = get_complex_state(url_uniping_dict[strizh.name])
    c['temperature_dict'] = temperature_dict
    xx = c
    c['humidity_dict'] = humidity_dict
    c['weather_state_dict'] = weather_state_dict
    c['url_uniping_dict'] = url_uniping_dict
    c['complex_state_dict'] = complex_state_dict

    if not c.get('chosen_strizh'):
        # c['chosen_strizh'] = ['None' for _ in range(len(strizhes))]
        c['chosen_strizh'] = [_.name for _ in strizhes]
    if request.method == 'POST':
        form = StrizhForm(request.POST)
        if form.is_valid():
            chosen_strizh = form.cleaned_data.get('chosen_strizh')
            c['chosen_strizh'][0] = chosen_strizh
    else:
        form = StrizhForm()
    c['form'] = form
    # TODO current_time
    drones = Point.objects.order_by('-detection_time').all()
    c['info_drones'] = drones
    c['all_strizhes'] = [_.name for _ in strizhes]

    return render(request, "main.html", context=c)


def butt_skan(request):
    global c
    strizh_names = Strizh.objects.all()
    c["action_strizh"] = "Сканирование: "
    if c.get("chosen_strizh") != 0:
        print('Сканирование dlya strizha #', c.get('chosen_strizh'))
        for strizh in strizh_names:
            if strizh.name in c.get("chosen_strizh") and c.get("complex_state_dict")[strizh.name] == 'включен':
                # print(strizh.ip1)
                c["action_strizh"] = c["action_strizh"] + strizh.name + ' '
                scan_on_off(strizh.ip1)
                scan_on_off(strizh.ip2)

    return render(request, "main.html", context=c)


def butt_glush(request):
    global c
    strizh_names = Strizh.objects.all()
    apems = ApemsConfiguration.objects.all()
    c["action_strizh"] = "Глушение: "
    if c.get("chosen_strizh") != 0:
        print('glushenie dlya strizha #', c.get('chosen_strizh'))
        for strizh in strizh_names:

            if strizh.name in c.get("chosen_strizh") and c.get("complex_state_dict")[strizh.name] == 'включен':
                # print(strizh.ip1)
                c["action_strizh"] = c["action_strizh"] + strizh.name + ' '
                if check_state(strizh.ip1) == 'scan_on':
                    scan_on_off(strizh.ip1)
                if check_state(strizh.ip2) == 'scan_on':
                    scan_on_off(strizh.ip2)

                if check_state(strizh.ip1) == 'all_stop' and check_state(strizh.ip2) == 'all_stop':
                    scan_on_off(strizh.ip1)
                    scan_on_off(strizh.ip2)
                    time.sleep(0.5)
                    scan_on_off(strizh.ip1)
                    scan_on_off(strizh.ip2)
                    time.sleep(0.5)
                    for each_apem in apems.filter(strizh_name=strizh.name):
                        ip = each_apem.ip_podavitelya
                        print(ip)
                        jammer_on_off(ip, 'on')

                print(check_state(strizh.ip1))
                print(check_state(strizh.ip2))
                # jammer_on_off(strizh.ip1, 'on')


    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_gps(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('gps dlya strizha #', c.get('chosen_strizh'))
        # TODO action 3 button
    c["action_strizh"] = "GPS: {}".format(', '.join([st for st in c['chosen_strizh'] if st != 'None']))
    # return redirect(request.META['HTTP_REFERER'])
    return render(request, "main.html", context=c)


def butt_ku(request):
    global c
    if c.get("chosen_strizh") != 0:
        print('KU dlya strizha #', c.get('chosen_strizh'))
        # TODO action 4 button
    c["action_strizh"] = "КУ: {}".format(', '.join([st for st in c['chosen_strizh'] if st != 'None']))
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


def collect_logs(log_string):
    global logs, logs_list
    time_obj = datetime.datetime.now().strftime("%Y-%d-%m  %H:%M:%S")
    log_one = time_obj + '   ' + log_string + '\n\t'
    logs_list.append(log_one)
    c['logs_list'] = logs_list
    print(log_one)


def set_correct_temperature(url, strizh_name, temperature_state):
    global c
    if temperature_state != 0:
        while temperature_state != 0:
            temperature_state = check_condition(c['temperature_dict'][strizh_name], low_border=low_t,
                                                high_border=high_t)
            if temperature_state == 1:
                send_line_command(url, 'вентилятор', 1)
                state0 = obtain_state(url, 'датчик потока')
                if state0 != 'вкл':
                    collect_logs('АВАРИЯ! отсутствует вентиляция, возможен перегрев оборудования')
            elif temperature_state == -1:
                send_line_command(url, 'обогрев', 1)
            time.sleep(60)


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


def turn_on_bp(request):
    global c, comlex_state, logs
    c['action_strizh'] = ''
    for striz in c.get('chosen_strizh'):
        if striz != 'None':
            url = c['url_uniping_dict'][striz]

            try:
                requests.get(url, auth=auth, timeout=0.2)
            except:
                result_get = 'ошибка соединения с uniping'
                collect_logs(striz + ': ' + result_get)
                continue

            temperature_state = check_condition(c['temperature_dict'][striz], low_border=low_t, high_border=high_t)
            if temperature_state != 0:
                print('температура не в порядке')
                set_correct_temperature(url, striz, temperature_state)
            elif temperature_state == 0:
                # turn everything on
                state0 = obtain_state(url, 'датчик потока')
                if state0 != 'вкл':
                    send_line_command(url, 'вентилятор', 1)
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

                complex_state = get_complex_state(url)
                c['complex_state'] = complex_state
                str_log = striz + ': ' + complex_state
                collect_logs(str_log)
                c['logs_list'] = logs_list
                # render(request, "main.html", context=c)
                # functioning_loop(request)
    return render(request, "main.html", context=c)


def turn_off_bp(request):
    global c
    c['action_strizh'] = ''
    for striz in c.get('chosen_strizh'):
        if striz != 'None':
            url = c['url_uniping_dict'][striz]

            try:
                requests.get(url, auth=auth, timeout=0.2)
            except:
                result_get = 'ошибка соединения с uniping'
                collect_logs(striz + ': ' + result_get)
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

            send_line_command(url, 'вентилятор', 0)
            time.sleep(1)
            send_impulse(url, 'РЕЗЕТ', time_pulse=6, action='выкл')

            complex_state = 'выкл'
            c['complex_state'] = complex_state
            c['logs'] = logs
            c['logs_list'] = logs_list
    # render(request, "main.html", context=c)
    # functioning_loop(request)

    return render(request, "main.html", context=c)


def show_logs(request):
    global logs
    c['logs'] = logs
    c['logs_list'] = logs_list
    return render(request, "main.html", context=c)


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

# def functioning_loop(request):
#     global c
#     print('loop')
#     is_on = True
#     if c['complex_state'] == 'вкл':
#         while is_on:
#             is_on = check_states_on()
#             render(request, "main.html", context=c)
#             time.sleep(10)
#     elif c['complex_state'] == 'выкл':
#         print('всё выключено')
#         # while True:
#         #     # check_states_off()
#         #     break
