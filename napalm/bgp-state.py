#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""bgp-state.py

Show a count of down sessions in a loop on a specified router

"""

import napalm
import time
import sys
import getpass


def main(rtrname, rtruser, rtrpass):
    localtime = time.asctime(time.localtime(time.time()))
    driver = napalm.get_network_driver('junos')
    device = driver(hostname=rtrname,
                    username=rtruser,
                    password=rtrpass,
                   )
    try:
        device.open()
    except Exception as Err:
        print('{}'.format(Err))
        sys.exit(1)

    bgpnei = device.get_bgp_neighbors()
    i = 0
    for k, v in bgpnei['global']['peers'].items():
        if 'is_up' in v:
            if not v['is_up'] and v['is_enabled']:
                i += 1
                print('{:30}{:^10}{:30}'.format(k, v['remote_as'],
                       v['description']))
    print('{:25}{:<30}BGP DOWN{:^5}'.format(localtime, rtrname, i))
    device.close()


if __name__ == "__main__":
    rtrname = input("Router hostname: ")
    rtruser = input("Junos OS username: ")
    rtrpass = getpass.getpass(prompt="Junos OS password: ")
    while True:
        end = 0
        try:
            main(rtrname, rtruser, rtrpass)
            if end == 1:
                break
            time.sleep(300)
            print('-' * 60)
        except KeyboardInterrupt:
            break
    print('Done')
