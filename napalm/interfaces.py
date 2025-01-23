#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""interfaces.py

Simple script to show interface rates and flag those
over 50% utilised for juniper ethernet interfaces (ge-, xe- and et-)

"""

from collections import defaultdict
import napalm
import time
import datetime
import sys
import getpass


def main(h, rtrname, rtruser, rtrpass):
    now = datetime.datetime.now().strftime("%d-%m-%y %H:%M")
    driver = napalm.get_network_driver('junos')
    print(now)
    print('{:25}|{:10}|{:5}|{:5}|{}'.format('Host', 'Interface', 'RX %',
          'TX %', 'Description'))
    device = driver(hostname=rtrname,
                    username=rtruser,
                    password=rtrpass,
                    )
    try:
        device.open()
        interfaces = device.get_interfaces()
        int_counters = device.get_interfaces_counters()
        device.close()
    except Exception as Err:
        print(Err)
        sys.exit(1)

    for keys in interfaces:
        line = rtrname + '-' + keys
        if interfaces[keys]['is_up'] is True:
            if "xe-" in keys or "ge-" in keys or "et-" in keys:
                if keys in int_counters:
                    rxbits = int_counters[keys]['rx_octets'] * 8
                    txbits = int_counters[keys]['tx_octets'] * 8
                    speed = interfaces[keys]['speed'] * 10000
                    desc = interfaces[keys]['description']
                    if 'rx' in h[line]:
                        tdiff = int(time.time() - h[line]['time'])
                        rxdiff = int((rxbits - h[line]['rx']) / tdiff)
                        txdiff = int((txbits - h[line]['tx']) / tdiff)
                        h[line]['rx'] = rxbits
                        h[line]['tx'] = txbits
                        h[line]['time'] = time.time()
                        if txdiff > 0 and rxdiff > 0:
                            if ((float(rxdiff / speed) > 50.0) or
                                (float(txdiff / speed) > 50.0)):
                                print('{:25}|{:10}|{:<5}|{:<5}|{}'.format(
                                      rtrname, keys,
                                      (float(rxdiff / speed)),
                                      (float(txdiff / speed)),
                                      desc))
                            else:
                                h[line]['rx'] = rxbits
                                h[line]['tx'] = txbits
                                h[line]['time'] = time.time()


if __name__ == '__main__':
    h = defaultdict(dict)
    rtrname = input("Router hostname: ")
    rtruser = input("Junos OS username: ")
    rtrpass = getpass.getpass(prompt="Junos OS password: ")
    while True:
        end = 0
        try:
            main(h, rtrname, rtruser, rtrpass)
            if end == 1:
                break
            time.sleep(300)
            print('-' * 40)
        except KeyboardInterrupt:
            break
    print('Done')
