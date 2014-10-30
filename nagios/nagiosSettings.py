__author__ = 'szymon'

import json


class NagiosSettings(object):
    def __init__(self, settings_string):
        self.device = json.loads(settings_string, object_hook=self._decode_dict)
        self.settings = json.loads(self.device['settingsString'], object_hook=self._decode_dict)

    def _decode_list(self, data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = self._decode_list(item)
            elif isinstance(item, dict):
                item = self._decode_dict(item)
            rv.append(item)
        return rv

    def _decode_dict(self, data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = self._decode_list(value)
            elif isinstance(value, dict):
                value = self._decode_dict(value)
            rv[key] = value
        return rv

    def get_node_id(self):
        return int(self.device['nodeId'])

    def get_ip_address(self):
        if not self.device['node']:
            return

        return self.device['node']['ipaddr']

    def get_snmp_config(self):
        if not self.device['node']:
            return

        if not self.device['node']['netDevice']:
            return

        if not self.device['node']['netDevice']['snmpProfile']:
            return

        return self.device['node']['netDevice']['snmpProfile']

    def get_interfaces(self):
        if not self.settings['port']:
            print "ports array was missing in the json"
            return

        interfaces = self.settings['port']
        if len(interfaces) > 0:
            return interfaces
        else:
            print "ports array was empty"
            return