from nagios.json_dict_decode import _decode_dict

__author__ = 'szymon'

import json


class NagiosSettings(object):
    def __init__(self, settings_string):
        self.device = json.loads(settings_string, object_hook=_decode_dict)

        if 'settingsString' in self.device:
            self.settings = json.loads(self.device['settingsString'], object_hook=_decode_dict)

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

        result = self.settings[itf_type]
        if len(result) > 0:
            return result
        else:
            print "%s array was empty" % itf_type
            return

    def get_traffic_interfaces(self):
        return self.get_setting('traffic')

    def get_port_interfaces(self):
        return self.get_setting('port')

    def get_switch_heat(self):
        return self.get_setting('switch_heat')

    def get_sensors(self):
        return self.get_setting('sensor')

    def get_ups_list(self):
        return self.get_setting('ups')

    def get_cmts_cards(self):
        return self.get_setting('cmts_card')

    def get_cmts_snr(self):
        return self.get_setting('cmts_snr')

    def get_cmts_utilization(self):
        return self.get_setting('cmts_utilization')

    def get_bgp(self):
        return self.get_setting('bgp')

    def get_server(self):
        return self.get_setting('server')