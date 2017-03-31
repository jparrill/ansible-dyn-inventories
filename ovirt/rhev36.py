#!/usr/bin/python

## Ovirt SDK
from ovirtsdk.xml import params
from ovirtsdk.api import API

## Logging
import os
from os.path import realpath
from os.path import dirname
from os.path import exists
import logging

## other
import pprint
import ConfigParser

class Ovirt36Inventory(object):
    """docstring for Ovirt36Inventory"""
    def __init__(self):
        super(Ovirt36Inventory, self).__init__()
        self.get_config()
        self.logger(self.logpath)
        self.read_cfg_groups()
        self.ovirt_get_vms(self.url, self.user, self.passw, self.ssl_insecure)
        self.create_inventory()

    def get_config(self):
        # Configuration catcher
        self.file_path = dirname(realpath(__file__))
        self.config = ConfigParser.ConfigParser()
        try:
            self.config.read(self.file_path + '/ansible.cfg')
        except Exception as err:
            raise Exception('Error reading config file: %s' % err)

        self.host = self.config.get('ovirt', 'host').strip("'")
        self.port = self.config.get('ovirt', 'port')
        self.user = self.config.get('ovirt', 'user').strip("'")
        self.passw = self.config.get('ovirt', 'passw').strip("'")
        self.ssl_insecure = self.config.get('ovirt', 'ssl_insecure')
        self.logfile = self.config.get('ovirt', 'logfile').strip("'")
        self.logpath = self.file_path + '/' + self.logfile
        self.url = '{}:{}/api'.format(self.host, self.port)

        ## Inventory purposes
        self.vnodes = []

    def logger(self, logfile):
        '''
        Function to log all actions
        '''
        log_file = logfile
        logging.getLogger('').handlers = []
        if not os.path.exists(log_file):
            open(log_file, 'a').close()
            logging.basicConfig(
               filename=log_file,
               format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s',
               level=logging.INFO
               )
        else:
            logging.basicConfig(
               filename=log_file,
               format='%(asctime)-15s %(name)-5s %(levelname)-8s %(message)s',
               level=logging.INFO
               )
        logging.info('RHEV/oVirt Dynamic inv started...')

    def read_cfg_groups(self):
        '''
        read all groups to be mapped as ansible groups, also adapt it
        '''
        self.ansible_mapper = {}
        for k, v in self.config.items('ovirt-classifier'):
            key = k.replace('group_','')
            if k == 'basename':
                self.basename = v.strip("'")
            else:
                self.ansible_mapper[key.upper()] = v.strip("'")

    def classify_vm(self, name):
        '''
        add a tuple to vm specs to enrolling into an ansible group
        '''
        for key, value in self.ansible_mapper.iteritems():
            if name[:-2] == self.basename + value:
                return key

    def ovirt_get_vms(self, url, user, passw, ssl_insecure):
        '''
        using sdk to attack ovirt api and getting all the vms to be classfied
        '''
        api = API(url=url, username=user, password=passw, insecure=ssl_insecure)
        logging.info('nodes found:')
        for vm in api.vms.list():
            vnode = {}
            name = vm.get_name()
            group = self.classify_vm(name)
            vnode[group] = {}
            guestinfo = vm.get_guest_info()
            if guestinfo is not None and guestinfo.get_ips() is not None:
                for element in guestinfo.get_ips().get_ip():
                    ip = element.get_address()
            else:
                ip = ['']

            logging.info(vnode)
            vnode[group]['nodes'] = '{}-{}'.format(name, ip[0])

            self.vnodes.append(vnode)

    def create_inventory(self):
        groups = {}
        # Classify nodes by group into an list
        logging.info('Groups')
        for vnode in self.vnodes:
            group_name = vnode.keys()[0]
            node_raw = vnode.values()[0]['nodes']
            # This is the IP if you need it (the first one found)
            ip = node_raw.split('-')[1]
            node = node_raw.split('-')[0]
            if group_name not in groups:
                groups[group_name] = []
                groups[group_name].append(node)
            else:
                groups[group_name].append(node)

        logging.info(groups)

        # Show inventory on stdout
        for group in groups:
            print '[{}]'.format(group)
            for nodes in groups[group]:
                print nodes

        logging.info('finished')

if __name__ == "__main__":
    Ovirt36Inventory()
