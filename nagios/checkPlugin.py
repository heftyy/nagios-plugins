#!/usr/bin/python

import requests

from nagios.nagiosPlugin import NagiosPlugin
from nagios.nagiosSettings import NagiosSettings
from nagios.snmpRequester import SnmpRequester


class CheckPlugin(NagiosPlugin):

    def __init__(self):
        super(CheckPlugin, self).__init__()
        self.snmp_requester = {}

    def run(self, options, host):

        if not host.node_id:
            print "Error, host node_id is missing"
            return 1

        url = "%s/%s" % (self.config.api_nagios_settings_url, host.node_id)
        resp = requests.get(url, params=None)

        settings = NagiosSettings(resp.content)

        snmp_config = settings.get_snmp_config()
        self.snmp_requester = SnmpRequester(
            settings.get_ip_address(),
            snmp_config['communityRo'],
            snmp_config['snmpVersion']
        )

        if self.snmp_requester.init_connection():
            self.check(settings)

    def check(self, settings):
        raise NotImplementedError("Please implement your plugin (check method).")

