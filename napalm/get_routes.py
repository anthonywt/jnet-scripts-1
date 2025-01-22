#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""get_routes.py

Loop thorugh a list of routers listed in rtrlist and check if the route is there and provide
some information to them.

"""

import napalm
import getpass
from sys import exit
from prettytable import PrettyTable


rtrlist = [
"""
List of routers to parse through.
"""
]

split_row = ['—' * x for x in [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]]
BOLD = '\033[1m'
END = '\033[0m'


def initialise_ptable():
    ptable = PrettyTable()
    ptable.align = "l"
    ptable.field_names = [
        "Prefix",
        "Router",
        "Protocol",
        "Active",
        "Selected",
        "Next_hop",
        "Table",
        "AS_Path",
        "Pref",
        "Med",
        "Inactive Reason",
    ]
    ptable.clear_rows()
    return ptable


def main(rtruser, rtrpass, route):
    ptable = initialise_ptable()
    ptable.title = "Searching for " + route
    driver = napalm.get_network_driver("junos")
    for rtr in rtrlist:
        device = driver(hostname=rtr, 
                        username=rtruser, 
                        password=rtrpass)
        try:
            device.open()
            try:
                routes = device.get_route_to(destination=route)
            except Exception as Err:
                print(f"{Err}")
                device.close()
                exit(0)
        except Exception as Err:
            print(f"{Err}")
            exit(0)
        device.close()
        for k, v in routes.items():
            for i in v:
                if ((str(i['current_active']) == "True") and str(i['selected_next_hop']) == "True"):
                    ptable.add_row([BOLD+k+END, rtr, i['protocol'], i['current_active'], i['selected_next_hop'], i['next_hop'], i['routing_table'],
                                    (i['protocol_attributes']['as_path'].replace("\n", "")), i['protocol_attributes']['local_preference'],
                                    i['protocol_attributes']['metric'], i['inactive_reason']])
                else:
                    ptable.add_row([k, rtr, i['protocol'], i['current_active'], i['selected_next_hop'], i['next_hop'], i['routing_table'],
                                    (i['protocol_attributes']['as_path'].replace("\n", "")), i['protocol_attributes']['local_preference'],
                                    i['protocol_attributes']['metric'], i['inactive_reason']])
        ptable.add_row(split_row)
    print(ptable)


if __name__ == "__main__":
    rtruser = input("Router username: ")
    rtrpass = getpass.getpass(prompt="Junos OS password: ")
    route = input("Route to look for: ")
    main(rtruser, rtrpass, route)
