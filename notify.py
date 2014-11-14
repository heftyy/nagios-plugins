#!/usr/bin/python
import json

import logging
import requests
from nagios.json_dict_decode import _decode_dict
from nagios.nagiosPlugin import NagiosPlugin

_log = logging.getLogger('notifyPlugin')


class NotifyPlugin(NagiosPlugin):

    @staticmethod
    def parse_output(output):
        result = []

        for row in output.split("\n"):
            if row[0] == '!':
                entry = json.loads(row[1:], object_hook=_decode_dict)
                result.append(entry)
        return result

    def run(self, options, host):
        print('host address %s' % host.address)
        print('state %s' % host.state)

        data = {}
        data['nodeId'] = host.node_id
        data['ip'] = host.address
        data['state'] = host.state
        data['output'] = json.dumps(self.parse_output(host.output))
        data['type'] = options.notification_type

        resp = requests.post(self.config.cog_notification_url, params=data)

        print resp

    def add_arguments(self, parser):
        parser.add_argument(
            '--type', action="store", dest="notification_type", help="Notification type")

if __name__ == '__main__':
    NotifyPlugin().start()
