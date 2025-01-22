#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""environment.py

go through router and show high temperatures, looping every 5 minutes

"""


import napalm
import time
import os
import sys
import getpass


def main(rtrname, rtruser, rtrpass):
    driver = napalm.get_network_driver('junos')
    os.system('clear')
    localtime = time.asctime(time.localtime(time.time()))
    print("Local current time :", localtime)
    rtenvironment = {}
    device = driver(hostname=rtrname,
                    username=rtruser,
                    password=rtrpass,
                    )
    try:
        device.open()
        rtenvironment = device.get_environment()
        device.close()
        print(rtrname)
        for k, v in rtenvironment['temperature'].items():
            if int(v['temperature']) > 60:
                print('{:30} {}'.format(k, v['temperature']))
    except Exception as Err:
        print(Err)
        sys.exit("Error")
    print('-' * 30)


if __name__ == '__main__':
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
        except KeyboardInterrupt:
            break
    print('Done')
