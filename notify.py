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

        for row in output.split('\\n'):
            if row and len(row) > 0 and row[0] == '!':
                entry = json.loads(row[1:], object_hook=_decode_dict)
                result.append(entry)
        return result

    def run(self, options, host):
        print('host address %s' % host.address)
        print('host state %s' % host.state)
        print('host output %s' % host.output)
        print('service output %s' % options.service_output)

        output = None
        if options.service_output is not None:
            output = options.service_output
        else:
            output = host.output

        parsed_output = self.parse_output(output)
        if parsed_output and len(parsed_output) > 0:
            for output_json in parsed_output:
                self.send_notification(host, output_json['nagios_status'], output_json['output'], output_json['type'])
        else:
            self.send_notification(host, options.service_output, options.notification_type)

    def send_notification(self, host, service_state, output, notification_type):
        data = {}
        data['nodeId'] = host.node_id
        data['ip'] = host.address
        data['state'] = host.state
        data['service'] = service_state
        data['output'] = output
        data['type'] = notification_type

        print "data = %s" % json.dumps(data)

        resp = requests.post(self.config.cog_notification_url, params=data)

        print resp

    def add_arguments(self, parser):
        parser.add_argument(
            '--type', action="store", dest="notification_type", help="Notification type")

if __name__ == '__main__':
    NotifyPlugin().start()
