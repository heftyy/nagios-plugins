#!/usr/bin/python

import time
from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues

JUNIPER_HEAT = '1.3.6.1.4.1.2636.3.1.13.1.7'


class CheckSwitchHeat(CheckPlugin):

    def get_switch_heat(self):
        request_oid = JUNIPER_HEAT

        heat_values = []

        heat_result = self.snmp_requester.do_walk(request_oid)
        if heat_result and len(heat_result) > 0:
            for oid, value in heat_result:
                if value is None or value == 0:
                    continue
                else:
                    heat_values.append(value)
        else:
            raise ValueError("didn't get values from the device for oid %s" % request_oid)

        if len(heat_values) == 0:
            raise ValueError("values received from the device could not be used %s" % request_oid)

        return heat_values

    @staticmethod
    def validate_heat(heat_settings, temperatures):
        warning = critical = None

        if 'warning' in heat_settings:
            warning = heat_settings['warning']

        if 'critical' in heat_settings:
            critical = heat_settings['critical']

        if not critical and not warning:
            return NagiosReturnValues.state_unknown

        if critical:
            for temp in temperatures:
                if temp >= critical:
                    print "temperature is above critical, ERROR"
                    return NagiosReturnValues.state_critical

        if warning:
            for temp in temperatures:
                if temp >= warning:
                    print "temperature is above warning, WARNING"
                    return NagiosReturnValues.state_warning

        print "all temperatures are ok"
        return NagiosReturnValues.state_ok

    def check(self, settings):
        switch_heat = settings.get_switch_heat()

        if not switch_heat:
            return NagiosReturnValues.state_ok

        for heat_settings in switch_heat:

            try:
                temperatures = self.get_switch_heat()
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            if not self.validate_heat(heat_settings, temperatures):
                return NagiosReturnValues.state_critical

        return 0


if __name__ == '__main__':
    CheckSwitchHeat().start()
