#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""get_routes2.py

check if route is in routing table of specified router

"""

import napalm
import getpass
from sys import exit
from pprint import pprint


def main(rtrname, rtruser, rtrpass, rtrroute):
    driver = napalm.get_network_driver("junos")
    device = driver(hostname=rtrname, 
                    username=rtruser, 
                    password=rtrpass)
    try:
        device.open()
        try:
            routes = device.get_route_to(destination=rtrroute)
        except Exception as Err:
            print(f"{Err}")
            exit(0)
    except Exception as Err:
            print(f"{Err}")
            exit(0)
    device.close()
    pprint(routes)


if __name__ == "__main__":
    rtrname = input("Router hostname: ")
    rtruser = input("Junos OS username: ")
    rtrpass = getpass.getpass(prompt="Junos OS password: ")
    rtrroute = input("Route to check: ")
    main(rtrname, rtruser, rtrpass, rtrroute)
