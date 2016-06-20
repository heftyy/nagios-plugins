#!/usr/bin/python
import json

import logging
import requests
import sys
from nagios.json_dict_decode import _decode_dict
from nagios.nagiosPlugin import NagiosPlugin
from nagios.nagiosSettings import NagiosSettings

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

    def get_ignored_notification_types(self, node_id):
        url = "%s/%s" % (self.config.nagios_settings_url, node_id)
        resp = requests.get(url, params=None)

        if resp.status_code != 200:
            print resp.content
            return []

        settings = NagiosSettings(resp.content)
        ignored_types = settings.get_ignored_types()
        result = []
        if ignored_types is not None:
            for obj in ignored_types:
                result.append(obj['ignored_type'])

        return result

    def run(self, options, host):
        print('host address %s' % host.address)
        print('host state %s' % host.state)
        print('host output %s' % host.output)
        print('service output %s' % options.service_output)

        if options.long_service_output and len(options.long_service_output) > 0:
            service_output = options.long_service_output
        else:
            service_output = options.service_output

        # service notification
        if service_output != '$':
            parsed_output = None
            if service_output is not None:
                output = service_output
                parsed_output = self.parse_output(output)

            if parsed_output and len(parsed_output) > 0:
                for output_json in parsed_output:
                    self.send_notification(host,
                                           output_json['nagios_status'],
                                           output_json['output'],
                                           output_json['type'])
            else:
                self.send_notification(host,
                                       options.service_state,
                                       service_output,
                                       "service-%s" % options.notification_type)

        else:
            self.send_notification(host, None, host.output, options.notification_type)

    def send_notification(self, host, service_state, output, notification_type):
        ignored_types = self.get_ignored_notification_types(host.node_id)
        if notification_type in ignored_types:
            print 'notification type %s is ignored on node %s' % (notification_type, host.node_id)
            return

        data = {
            'nodeId': host.node_id,
            'ip': host.address,
            'state': host.state,
            'service': service_state,
            'output': output,
            'type': notification_type
        }

        print "data = %s" % json.dumps(data)

        resp = requests.post(self.config.notification_url, params=data)

        print resp

    def add_arguments(self, parser):
        parser.add_argument('--type', action="store", dest="notification_type", help="Notification type")

        parser.add_argument('--service_output', action="store", dest="service_output", help="Service output")
        parser.add_argument('--long_service_output', action="store", dest="long_service_output", help="Long output")
        parser.add_argument('--service_state', action="store", dest="service_state", help="Service state")
        parser.add_argument('--service_name', action="store", dest="service_name", help="Service name")


if __name__ == '__main__':
    NotifyPlugin().start()
