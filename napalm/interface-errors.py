#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""interface-errors.py

Simple python script to retrieve interface errors
using napalm, printing it out and writing to log file

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
    device = driver(hostname=rtrname,
                    username=rtruser,
                    password=rtrpass)
    try:
        device.open()
        interfaces = device.get_interfaces_counters()
    except Exception as Err:
        print(Err)
        sys.exit(1)
        
    device.close()

    filename = rtrname + '-log.txt'
    with open(filename, 'a+') as file:
        for keys in interfaces:
            line = rtrname + '-' + keys
            for k, v in interfaces[keys].items():
                if 'discards' in k or 'errors' in k:
                    diff = 0
                    if v > 0:
                        if k in h[line]:
                            diff = int(v) - int(h[line][k])
                            h[line][k] = v
                            if diff > 0:
                                print('{} {} {} {} {} {}'.format(now, rtrname,
                                      keys, k, v, diff))
                                towrite = '%s,%s,%s,%s,%s,%s\n' % \
                                          (str(now), str(rtrname), str(keys),
                                          str(k), str(v), str(diff))
                                file.write(towrite)
                        else:
                            h[line][k] = v


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
