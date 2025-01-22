#!/usr/bin/env python

# -*- coding: utf-8 -*-
"""bgp-viewer.py

Show info on a peer AS number

"""


import napalm
import time
import sys
import getpass


def get_as(asno):
    if len(sys.argv) < 2:
        print('Please supply an AS')
        exit(0)
    asno = sys.argv[1]
    return(int(asno))


def main(rtrname, rtruser, rtrpass, asno):
    localtime = time.asctime(time.localtime(time.time()))
    driver = napalm.get_network_driver('junos')
    j4 = 0
    j6 = 0
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
    i4 = 0
    i6 = 0
    leap = 0
    for k, v in bgpnei['global']['peers'].items():
        if 'is_up' in v:
            if v['remote_as'] == int(asno):
                leap = 1
        if leap:
            print(rtrname)
            print('-' * 80)
            for k, v in bgpnei['global']['peers'].items():
                if 'is_up' in v:
                    if v['remote_as'] == int(asno):
                        if ':' in k:
                            j6 += 1
                            i6 += 1
                        elif '.' in k:
                            j4 += 1
                            i4 += 1
                        print('{:30}{:^10}{:30}'.format(k, v['remote_as'],
                              v['description']))
            leap = 0
            print('-' * 80)
            print('IPv4', i4, 'IPv6', i6)
            print('Router Total', i4 + i6)
            print('-' * 80)
        device.close()
    if j4 > 1:
        print('Total IPv4', j4, 'Total IPv6', j6)
        print('Total Sessions', j4 + j6)
    else:
        print('No sessions with', asno, ':-(')


if __name__ == "__main__":
    rtrname = input("Router hostname: ")
    rtruser = input("Junos OS username: ")
    rtrpass = getpass.getpass(prompt="Junos OS password: ")
    asno = input("AS number to check: ")
    main(rtrname, rtruser, rtrpass, asno)
