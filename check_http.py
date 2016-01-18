#!/usr/bin/python

import requests

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


class CheckWebsite(CheckPlugin):

    def check_snmp(self, settings):
        # ignore snmp check
        return True

    @staticmethod
    def make_request(url, request_type):
        if not url.startswith("http://"):
            url = 'http://' + url

        if request_type == 'GET' or request_type == '' or request_type is None:
            result = requests.get(url)
        elif request_type == 'POST':
            result = requests.post(url)
        else:
            return NagiosReturnValues.state_unknown

        if result.status_code == 200:
            return NagiosReturnValues.state_ok
        else:
            print '%s, Status: %d' % (url, result.status_code)
            return NagiosReturnValues.state_critical

    def check_website(self, host_address, website_settings):
        if 'port' in website_settings:
            port = website_settings['port']
            host_address = '%s:%d' % (host_address, port)

        if 'url' in website_settings:
            request_url = website_settings['url']
            request_method = website_settings['method']

            if not request_url.startswith('/'):
                request_url = '/' + request_url

            return self.make_request(host_address + request_url, request_method)
        else:
            return self.make_request(host_address, 'GET')

    def check(self, settings):
        websites = settings.get_http()
        statuses = []
        device_status = NagiosReturnValues.state_ok

        host_address = settings.device['node']['ipaddr']

        if not websites:
            return NagiosReturnValues.state_ok

        for website_settings in websites:
            status = self.check_website(host_address, website_settings)
            statuses.append(status)

        if len(statuses) > 0:
            device_status = self.get_device_status(statuses)

        if device_status == NagiosReturnValues.state_ok:
            print 'HTTP OK'

        return device_status

if __name__ == '__main__':
    CheckWebsite().start()
