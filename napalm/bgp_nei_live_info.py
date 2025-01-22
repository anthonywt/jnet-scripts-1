#!/usr/bin/env python3

# -*- coding: utf-8 -*-
"""bgp_nei_live_info.py

Simple script to either parse through peering routers or a specified router with a provided AS number
and get some info on the state.

"""

import napalm
import argparse
import os
import datetime
import getpass

from prettytable import PrettyTable
from sys import platform, exit


parser = argparse.ArgumentParser()
parser.add_argument("-a", "--asno", type=int, help="AS number", required=True)
parser.add_argument("-b", "--brief", action="store_true", help="Display briefer output with less table columns")
parser.add_argument("-r", "--router", help="Provide a router name, else I will parse all peering routers")
parser.add_argument("-u", "--username", default="USER", help="Username to login with, default USER")
parser.add_argument("--html", action="store_true", help="Write out a html file, will also open in default browser")

args = parser.parse_args()

rtrlist = [
    """
    List of routers to parse and match, if not specifed with -r/--router
    """
]


def main(password):
    if args.brief:
        ptable = initialise_ptable_brief()
    else:
        ptable = initialise_ptable()
    driver = napalm.get_network_driver("junos")
    for rtr in rtrlist:
        if args.router and args.router in rtr:
            device = driver(hostname=rtr, username=args.username, password=password)
        elif args.router:
            continue
        else:
            device = driver(hostname=rtr, username=args.username, password=password)
        try:
            device.open()
            try:
                bgpneis = device.get_bgp_neighbors()
            except Exception as Err:
                print(f"{rtr} get_bgp_neighs error: {Err}")
                continue
            try:
                bgpnei = device.get_bgp_neighbors_detail()
            except Exception as Err:
                print(f"{rtr} get_bgp_neigh_detail error: {Err}")
                continue
            try:
                bgpgroup = device.get_bgp_config()
            except Exception as Err:
                print(f"{rtr} get_bgp_config error: {Err}")
                continue
            device.close()
            if args.asno in bgpnei["global"]:
                output = bgpnei["global"][args.asno]
                filloutput(rtr, output, ptable, bgpgroup, bgpneis)
        except Exception as Err:
            print(f"{rtr} error: {Err}")
    if args.html and args.router:
        print_html_out(ptable, args.asno, args.router)
    elif args.html:
        print_html_out(ptable, args.asno, False)
    else:
        print(ptable)


def print_html_out(ptable, asno, router):
    if router:
        filename = router + "AS" + str(asno) + "-" + str(datetime.date.today()) + ".html"
    else:
        filename = "AS" + str(asno) + "-" + str(datetime.date.today()) + ".html"
    file_to_write = "/tmp/" + filename
    with open(file_to_write, "w+") as fileh:
        fileh.write("<html><head></head><body>")
        fileh.write(ptable.get_html_string(format=True))
        fileh.write("</body></html>")
    if platform == "darwin":
        cmd = "open " + file_to_write
        os.system(cmd)


def initialise_ptable():
    ptable = PrettyTable()
    ptable.align = "l"
    ptable.field_names = [
        "Router",
        "Group",
        "Local Address",
        "Neighbor",
        "AS",
        "Description",
        "State",
        "Uptime",
        "Rcv",
        "Adv",
        "Import",
        "Export",
        "Hold",
        "Prev State",
        "Last Event",
        "Prefix Limit",
        "Remote ID",
    ]
    ptable.clear_rows()
    return ptable


def initialise_ptable_brief():
    ptable = PrettyTable()
    ptable.align = "l"
    ptable.field_names = [
        "Router",
        "Local Address",
        "Neighbor",
        "AS",
        "Description",
        "State",
        "Uptime",
        "Rcv",
        "Adv",
        "Prev State",
        "Last Event",
    ]
    ptable.clear_rows()
    return ptable


def splitprefixlimit(prefix_limit_dir):
    if prefix_limit_dir.get("inet"):
        return prefix_limit_dir["inet"]["unicast"]["limit"]
    elif prefix_limit_dir.get("inet6"):
        return prefix_limit_dir["inet6"]["unicast"]["limit"]
    else:
        return "No pfx limit"


def filloutput(rtr, output, ptable, bgpgroup, bgpneis):
    for peer_config in output:
        uptime = 0
        for nei in bgpneis["global"]["peers"].keys():
            if peer_config["remote_address"] in nei:
                uptime_secs = bgpneis["global"]["peers"][nei]["uptime"]
                uptime = str(datetime.timedelta(seconds=uptime_secs))
                rid = str(bgpneis["global"]["peers"][nei]["remote_id"])
        for groups in bgpgroup.keys():
            if peer_config["remote_address"] in bgpgroup[groups]["neighbors"]:
                description = bgpgroup[groups]["neighbors"][peer_config["remote_address"]]["description"]
                group = groups
                if bgpgroup[groups]["neighbors"][peer_config["remote_address"]]["prefix_limit"]:
                    prefix_limit = splitprefixlimit(
                        bgpgroup[groups]["neighbors"][peer_config["remote_address"]]["prefix_limit"]
                    )
                else:
                    prefix_limit = splitprefixlimit(bgpgroup[groups]["prefix_limit"])
        if args.brief:
            ptable.add_row(
                [
                    rtr,
                    peer_config["local_address"],
                    peer_config["remote_address"],
                    peer_config["remote_as"],
                    description,
                    peer_config["connection_state"],
                    uptime,
                    peer_config["accepted_prefix_count"],
                    peer_config["advertised_prefix_count"],
                    peer_config["previous_connection_state"],
                    peer_config["last_event"],
                ]
            )
        else:
            ptable.add_row(
                [
                    rtr,
                    group,
                    peer_config["local_address"],
                    peer_config["remote_address"],
                    peer_config["remote_as"],
                    description,
                    peer_config["connection_state"],
                    uptime,
                    peer_config["accepted_prefix_count"],
                    peer_config["advertised_prefix_count"],
                    peer_config["import_policy"],
                    peer_config["export_policy"],
                    peer_config["holdtime"],
                    peer_config["previous_connection_state"],
                    peer_config["last_event"],
                    prefix_limit,
                    rid,
                ]
            )
    return ptable


if __name__ == "__main__":
    try:
        password = getpass.getpass(prompt='Enter password: ')
    except Exception as Err:
        print("ERROR", Err)
        exit(0)
    main(password)
