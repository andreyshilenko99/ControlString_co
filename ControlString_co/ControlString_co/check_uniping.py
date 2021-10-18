from pysnmp.hlapi import *
from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto import rfc1902
# import multiprocessing
from pythonping import ping

community_string = 'SWITCH'  # From file
ip_address_host = '192.168.2.51'  # From file
port_snmp = 161
OID_sysName = '.1.3.6.1.4.1.25728.8900.1.1.3.1'  # From SNMPv2-MIB hostname/sysname
temperature = '.1.3.6.1.4.1.25728.8400.2.4.0'
wet = '.1.3.6.1.4.1.25728.8400.2.5.0'
check_oids = {'npThermoValue.n': '.1.3.6.1.4.1.25728.8800.1.1.2.1',
              'npThermoStatus.n': '.1.3.6.1.4.1.25728.8800.1.1.3.1',
              'npRelHumSensorValueT': '.1.3.6.1.4.1.25728.8400.2.4.0',
              'npRelHumSensorStatusH': '.1.3.6.1.4.1.25728.8400.2.5.0'}

control_oids = {'warm': '.1.3.6.1.4.1.25728.8900.1.1.3.1', 'wind': '.1.3.6.1.4.1.25728.8900.1.1.3.2',
                'control_wind': '.1.3.6.1.4.1.25728.8900.1.1.2.9', 'check_heater': '.1.3.6.1.4.1.25728.8900.1.1.2.1'}


def snmp_get(community, ip, port, oid):  # опрос uniping
    getcmd = getCmd(SnmpEngine(),
                    CommunityData(community),
                    UdpTransportTarget((ip, port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid)))

    error_indication, error_status, error_index, var_binds = next(getcmd)
    for name, val in var_binds:
        # print(val.prettyPrint())
        return val.prettyPrint()


# code section

# name = (snmp_get(community_string, ip_address_host, port_snmp, temperature))
# print('answer= ' + name)


# посмотреть errors во вкладке

def snmp_send(community, ip, port, oid):
    cmdGen = cmdgen.CommandGenerator()
    cmdGen.setCmd(
        cmdgen.CommunityData(community, mpModel=1),
        cmdgen.UdpTransportTarget((ip, port)),
        (oid, rfc1902.Integer(-1)),
    )


def main_check(host):
    dict_state = {'cooler': 'Нет данных', 'temperature_state': 'Нет данных', 'wetness_state': 'Нет данных',
                  'heater_state': 'Нет данных', 'temperature': 'Нет данных',
                  'wetness': 'Нет данных'}
    ip_address_host = host
    try:
        # name = (snmp_get(community_string, ip_address_host, port_snmp, temperature))
        # # print('answer= ' + name)
        # # print(int(snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npThermoStatus.n'))))
        # dict_state['wetness'] = str(
        #     snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npRelHumSensorValueT')))
        # dict_state['temperature'] = str(
        #     snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npThermoValue.n')))
        # if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('wind'))) == 0:
        #     snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('wind'))
        # if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('control_wind'))) == 1:
        #     dict_state['cooler'] = 'works'
        # else:
        #     dict_state['cooler'] = 'error'
        #     temp = int(snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npThermoStatus.n')))
        #     wetness = int(
        #         snmp_get(community_string, ip_address_host, port_snmp, check_oids.get('npRelHumSensorStatusH')))
        #     print(wetness)
        #     if temp == 0:
        #         dict_state['temperature'] = 'no_tempo_sense'
        #     elif temp == 1:
        #         if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('check_heater'))) == 0:
        #             snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
        #     elif temp == 3:
        #         if int(snmp_get(community_string, ip_address_host, port_snmp, control_oids.get('check_heater'))) == 1:
        #             snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
        #             dict_state['temperature_state'] = 'tempe_not_ok'
        #     elif temp == 2:
        #         dict_state['temperature_state'] = 'temp_is_ok'
        #         if wetness == 0:
        #             dict_state['wetness_state'] = 'no_wetness_sense'
        #             print("no wetness sense")
        #         elif wetness == 3:
        #             if int(snmp_get(community_string, ip_address_host, port_snmp,
        #                             control_oids.get('check_heater'))) == 0:
        #                 dict_state['wetness_state'] = 'wetness_not_ok'
        #                 snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
        #         elif wetness == 2:
        #             if int(snmp_get(community_string, ip_address_host, port_snmp,
        #                             control_oids.get('check_heater'))) == 1:
        #                 dict_state['wetness_state'] = 'wetness_is_ok'
        #                 snmp_send(community_string, ip_address_host, port_snmp, control_oids.get('warm'))
        return dict_state
    except TypeError:
        return dict_state
