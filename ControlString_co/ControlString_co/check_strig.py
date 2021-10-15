from ControlString_co.check_uniping import main_check
from ControlString_co.control_trace import check_state
from django.apps import apps


def check_strig():
    srizhes = apps.get_model('geo', 'Strizh').objects.all()
    if len(srizhes) == 0:
        print("Нет стрижей в бд")
    sstrizhes_dict = {}
    for strizh in srizhes:
        sstrizhes_dict[strizh.name] = [strizh.ip1, strizh.ip2, strizh.uniping_ip]
        print(sstrizhes_dict)
    for strizh in sstrizhes_dict:
        Record = apps.get_model('geo', 'Strigstate')
        name = strizh
        ip1_state = check_state(sstrizhes_dict[strizh][0])
        ip2_state = check_state(sstrizhes_dict[strizh][1])
        if ip1_state == 'all_stop':
            ip1_state = 'Все остановлено'
        elif ip1_state == 'scan_on':
            ip1_state = 'Сканирование активно'
        elif ip1_state == 'jammer_on':
            ip1_state = 'Подавление активно'
        elif ip1_state == 'no_connect':
            ip1_state = 'Нет соединения'
        if ip2_state == 'all_stop':
            ip2_state = 'Все остановлено'
        elif ip2_state == 'scan_on':
            ip2_state = 'Сканирование активно'
        elif ip2_state == 'jammer_on':
            ip2_state = 'Подавление активно'
        elif ip2_state == 'no_connect':
            ip2_state = 'Нет соединения'
        check_uni = main_check(sstrizhes_dict[strizh][2])
        # print([name, ip1_state, ip2_state, check_uni])
        record = Record(strig_name=name, ip1_state=ip1_state, ip2_state=ip2_state,
                        temperature=check_uni['temperature'], temperature_state=check_uni['temperature_state'],
                        wetness=check_uni['wetness'], wetness_state=check_uni['wetness_state'],
                        cooler=check_uni['cooler'])
        # apps.get_model('geo', 'Strigstate').objects.all().delete()
        record.save()
