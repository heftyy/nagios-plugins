__author__ = 'szymon'

import json


class NagiosSettings(object):
    def __init__(self, settings_string):
        self.device = json.loads(settings_string, object_hook=self._decode_dict)

        if 'settingsString' in self.device:
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
        if 'nodeId' not in self.device:
            return

        return int(self.device['nodeId'])

    def get_ip_address(self):
        if 'node' not in self.device:
            return

        if 'ipaddr' not in self.device['node']:
            return

        return self.device['node']['ipaddr']

    def get_snmp_config(self):
        if 'node' not in self.device:
            return

        if 'netDevice' not in self.device['node']:
            return

        if 'snmpProfile' not in self.device['node']['netDevice']:
            return

        return self.device['node']['netDevice']['snmpProfile']

    def get_setting(self, itf_type):
        if itf_type not in self.settings:
            print "%s array was missing in the json" % itf_type
            return

        interfaces = self.settings[itf_type]
        if len(interfaces) > 0:
            return interfaces
        else:
            print "%s array was empty" % itf_type
            return

    def get_traffic_interfaces(self):
        return self.get_setting('traffic')

    def get_port_interfaces(self):
        return self.get_setting('port')

    def get_switch_heat(self):
        return self.get_setting('switch_heat')