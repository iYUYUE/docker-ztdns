#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# (c) 2019, Brian Clemens <brian@tiuxo.com>
#
# This file is part of Ansible.
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible. If not, see <http://www.gnu.org/licenses/>.

######################################################################
"""
ZeroTier external inventory script
==================================

Generates Ansible inventory from a ZeroTier network.  This script takes configuration from a file named zerotier.ini or the following environmental variables:
    ZT_CONTROLLER - String, URL to the ZeroTier controller
    ZT_NETWORK - String, ZeroTier network ID
    ZT_TOKEN - String, ZeroTier authentication token
    ZT_INCLUDEOFFLINE - Boolean, include offline hosts in generated inventory

usage: zerotier.py [--list]
"""

# Standard imports
import os
import sys
import argparse

import json
import requests
import configparser

class ZeroTierInventory(object):
    def __init__(self):
        """ Main execution path """
        self.inventory = []
        self.local_hosts = self.get_local_hosts()

        # Read settings and parse CLI arguments
        self.read_settings()
        self.parse_cli_args()

        # Get host information and populate inventory
        self.get_hosts()

        if self.args.list:
            print('\n'.join(self.inventory))

        if self.args.refresh:
            hosts_file = self.get_hosts_file()
            if hosts_file and not set(self.inventory) ^ set(hosts_file):
                sys.exit("hosts are up-to-date")
            else:
                self.dump_hosts_file()
                print("hosts updated")

    def dump_hosts_file(self):
        with open(self.hosts, 'w') as fh:
            for item in self.inventory:
                fh.write('%s\n' % item)          

    def get_hosts_file(self):
        try:
            return [line.rstrip('\n') for line in open(self.hosts)]
        except FileNotFoundError:
            return None

    def get_local_hosts(self):
        ret = []
        local_hosts = open('/etc/hosts','r')
        for line in local_hosts:
            ret += line.split()[1:]
        return ret

    def add_host(self, host):
        """Adds a host to the inventory"""
        host_vars = []
        names = []
        if host['name'] not in self.local_hosts:
            names += [host['name']]
        for n in host['description'].split(';'):
            if n:
                if ':' in n:
                    nn = n.split(':')
                    if nn[0] not in self.local_hosts:
                        self.inventory.append(self._get_host_info([nn[0]], nn[1]))
                else:
                    if n not in self.local_hosts:
                        names.append(n)
        if len(host['config']['ipAssignments']) == 1:
            self.inventory.append(self._get_host_info(names, host['config']['ipAssignments'][0]))

    def _get_host_info(self, names, ip):
        
        ext_names = []
        for name in names:
            if not '.' in name:
                ext_names.append(name+'.'+self.domain)
            ext_names.append(name)
        record = ip + '\t' + ' '.join(ext_names)

        return record

    def get_hosts(self):
        """Make API call and add hosts to inventory"""
        r = requests.get(
            self.controller + '/api/network/' + self.network + '/member',
            headers={'Authorization': 'bearer ' + self.token})

        for host in r.json():
            if host['config']['authorized'] and (host['online'] or self.include_offline):
                self.add_host(host)

    def parse_cli_args(self):
        """Command line argument processing"""
        parser = argparse.ArgumentParser(
            description='Produce an Ansible inventory from a ZeroTier network')
        parser.add_argument(
            '--list',
            action='store_true',
            default=False,
            help='List hosts (default: True)')
        parser.add_argument(
            '--refresh',
            action='store_true',
            default=False,
            help='Refresh hosts file (default: True)')
        self.args = parser.parse_args()

    def push(self, my_dict, key, element):
        """Pushed an element onto an array that may not have been defined in the dict."""
        if key in my_dict:
            my_dict[key].append(element)
        else:
            my_dict[key] = [element]

    def read_settings(self):
        """Reads the settings from the .ini file and environment"""
        config_file = os.path.dirname(
            os.path.realpath(__file__)) + '/zerotier.ini'

        if os.path.isfile(config_file):
            config = configparser.ConfigParser()
            config.read(config_file)

            self.controller = config.get('zerotier', 'controller')
            self.network = config.get('zerotier', 'network')
            self.domain = config.get('zerotier', 'domain')
            self.hosts = config.get('zerotier', 'hosts')
            self.token = config.get('zerotier', 'token')
            self.include_offline = config.getboolean('zerotier',
                                                     'include_offline')

        if os.environ.get('ZT_CONTROLLER'):
            self.controller = os.environ.get('ZT_CONTROLLER')
        if os.environ.get('ZT_NETWORK'):
            self.network = os.environ.get('ZT_NETWORK')
        if os.environ.get('ZT_TOKEN'):
            self.token = os.environ.get('ZT_TOKEN')
        if os.environ.get('ZT_INCLUDEOFFLINE'):
            self.include_offline = os.environ.get('ZT_INCLUDEOFFLINE')
            if self.include_offline in ('False', 'false', '0'):
                self.include_offline = False


if __name__ == '__main__':
    ZeroTierInventory()
