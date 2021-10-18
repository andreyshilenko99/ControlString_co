import requests
import re

lines_control_map = {
    'вентилятор_команда': 2,
    'БП ПЭВМ': 4,
    'БП Шелест': 6,
    'БП АПЕМ': 8,
    'ЭВМ1': 9,
    'ЭВМ2': 13,
    'вентилятор': 16,
}
auth = ('user', '555')


# получение состояния одного блока через url запрос
def obtain_state(url, line_name):
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

    return state


# получение состояния всех блоков в комплексе
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
    return complex_state


if __name__ == "__main__":
    url = 'http://192.168.2.51/'
    x = get_complex_state(url)
    print(x)
