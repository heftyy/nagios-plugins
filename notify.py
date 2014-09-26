#!/usr/bin/python

import logging
import requests
from nagios.nagiosPlugin import NagiosPlugin

_log = logging.getLogger('notifyPlugin')


class NotifyPlugin(NagiosPlugin):
    def run(self, options, host):
        print('host address %s' % host.address)
        print('state %s' % host.state)

        data = {}
        data['node_id'] = host.node_id
        data['ip'] = host.address
        data['state'] = host.state

        resp = requests.post(self.config.api_notification_url, params=data)

        print resp

    def add_arguments(self, parser):
        parser.add_argument('--type', action="store", dest="notification_type", help="Notification type")

if __name__ == '__main__':
    NotifyPlugin().start()