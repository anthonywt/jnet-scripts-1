#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""get-interface.py

Script to loop through a router and get interface descriptions, either all or
spcific interface.

"""


import napalm
import sys
import getpass


def main(rtrname, rtruser, rtrpass, interface):
    driver = napalm.get_network_driver('junos')
    device = driver(hostname=rtrname,
                    username=rtruser,
                    password=rtrpass,
                   )
    try:
        device.open()
        interfaces = device.get_interfaces()
    except Exception as Err:
        print(Err)
        sys.exit(0)
    device.close()

    for keys in interfaces:
        if interface in keys:
            print("{} {}".format(keys, interfaces[keys]['description']))
        if 'all' in interface:
            print("{} {}".format(keys, interfaces[keys]['description']))
        if 'desc' in interface:
            if interfaces[keys]['description']:
                print("{} {}".format(keys, interfaces[keys]['description']))


if __name__ == '__main__':
    rtrname = input("Router hostname: ")
    rtruser = input("Junos OS username: ")
    rtrpass = getpass.getpass(prompt="Junos OS password: ")
    interface = input("Specify, desc for description, all for all or specific interface: ")
    main(rtrname, rtruser, rtrpass, interface)
