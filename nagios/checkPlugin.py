#!/usr/bin/python

import sys

import requests

from nagios.nagiosPlugin import NagiosPlugin
from nagios.nagiosReturnValues import NagiosReturnValues
from nagios.nagiosSettings import NagiosSettings
from nagios.snmpRequester import SnmpRequester


class CheckPlugin(NagiosPlugin):

    def __init__(self):
        super(CheckPlugin, self).__init__()
        self.snmp_requester = {}

    @staticmethod
    def is_number(text):
        try:
            float(text)
            return True
        except ValueError:
            return False

    def validate_value(self, value, settings):
        if "check_type" in settings:
            validate_type = settings["check_type"]
            if validate_type == "lt":
                return self.validate_value_lt(value, settings)
            elif validate_type == "gt":
                return self.validate_value_gt(value, settings)

        return NagiosReturnValues.state_unknown


    @staticmethod
    def validate_value_lt(value, settings):
        warning = critical = None

        if 'warning' in settings:
            warning = settings['warning']

        if 'critical' in settings:
            critical = settings['critical']

        if not critical and not warning:
            return NagiosReturnValues.state_ok

        if CheckPlugin.is_number(value):
            number = float(value)
            if critical:
                if number >= critical:
                    # print 'value %s is above critical' % number
                    return NagiosReturnValues.state_critical

            if warning:
                if number >= warning:
                    # print 'value %s is above warning' % number
                    return NagiosReturnValues.state_warning

        else:
            if critical:
                if value == critical:
                    # print 'value %s is critical' % value
                    return NagiosReturnValues.state_critical

            if warning:
                if value == warning:
                    # print 'value %s is warning' % value
                    return NagiosReturnValues.state_warning

        # print 'value %s is ok' % value
        return NagiosReturnValues.state_ok

    @staticmethod
    def validate_value_gt(value, settings):
        warning = critical = None


        if 'warning' in settings:
            warning = settings['warning']

        if 'critical' in settings:
            critical = settings['critical']

        if not critical and not warning:
            return NagiosReturnValues.state_ok

        if CheckPlugin.is_number(value):
            number = float(value)
            if critical:
                if number <= critical:
                    # print 'value %s is below critical' % number
                    return NagiosReturnValues.state_critical
            if warning:
                if number <= warning:
                    # print 'value %s is below warning' % number
                    return NagiosReturnValues.state_warning
        else:
            if critical:
                if value == critical:
                    # print 'value %s is critical' % value
                    return NagiosReturnValues.state_critical

            if warning:
                if value == warning:
                    # print 'value %s is warning' % value
                    return NagiosReturnValues.state_warning

        # print 'value %s is ok' % value
        return NagiosReturnValues.state_ok

    @staticmethod
    def get_device_status(*args):
        if len(args) == 1 and isinstance(args[0], list):
            args = args[0]

        for arg in args:
            if arg and arg == NagiosReturnValues.state_critical:
                return NagiosReturnValues.state_critical

        for arg in args:
            if arg and arg == NagiosReturnValues.state_warning:
                return NagiosReturnValues.state_warning

        for arg in args:
            if arg and arg == NagiosReturnValues.state_unknown:
                return NagiosReturnValues.state_unknown

        return NagiosReturnValues.state_ok

    def run(self, options, host):

        if not host.node_id:
            print "Error, host node_id is missing"
            return 1

        url = "%s/%s" % (self.config.api_nagios_settings_url, host.node_id)
        resp = requests.get(url, params=None)

        if resp.status_code != 200:
            print resp.content
            sys.exit(0)

        settings = NagiosSettings(resp.content)

        snmp_config = settings.get_snmp_config()
        self.snmp_requester = SnmpRequester(
            settings.get_ip_address(),
            snmp_config['communityRo'],
            snmp_config['snmpVersion']
        )

        if self.snmp_requester.init_connection():
            script_return_value = self.check(settings)

            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"
            print "fix_nagios"

            sys.exit(NagiosReturnValues.value_to_int(script_return_value))

        print "Error, snmp connection failed."

    def check(self, settings):
        raise NotImplementedError("Please implement your plugin (check method).")

