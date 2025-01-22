#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""router-snmp-ids.py

Script to show interface descriptions and snmp-ids on specifed router

"""

from jnpr.junos import Device
from jnpr.junos.exception import ConnectError
from prettytable import PrettyTable
import sys
import getpass


def main(rtrname, rtruser, rtrpass):
    x = PrettyTable()
    x.field_names = ["Interface", "Description", "SNMP ID"]
    x.align = 'l'
    dev = Device(host=rtrname,
                 user=rtruser,
                 password=rtrpass,
                 gather_facts=False)
    try:
        dev.open()
    except ConnectError as err:
        print ("Cannot connect to device: {0}".format(err))
        sys.exit(1)
    except Exception as err:
        print (err)
        sys.exit(1)    

    interfaces_json = dev.rpc.get_interface_information({'format':'json'})
    dev.close()

    x.clear_rows()
        
    for interfaces in interfaces_json['interface-information'][0]['physical-interface']:
        if 'description' in interfaces:
            x.add_row([interfaces['name'][0]['data'], interfaces['description'][0]['data'], interfaces['snmp-index'][0]['data']])
        else:
            x.add_row([interfaces['name'][0]['data'], "No description", interfaces['snmp-index'][0]['data']])
        if 'logical-interface' in interfaces:
            for i in interfaces['logical-interface']:
                if 'description' in i:
                    x.add_row([i['name'][0]['data'], i['description'][0]['data'], i['snmp-index'][0]['data']])
                else:
                    x.add_row([i['name'][0]['data'], "No Description", i['snmp-index'][0]['data']])

    filetowrite = rtrname + '-snmp.txt'
    with open(filetowrite, 'w') as f:
        f.write(x.get_string())


if __name__ == '__main__':
    rtrname = input("Device hostname: ")
    rtruser = input("Junos OS username: ")
    rtrpass = getpass.getpass(prompt="Junos OS or SSH key password: ")
    main(rtrname, rtruser, rtrpass)
