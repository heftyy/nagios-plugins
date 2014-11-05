#!/usr/bin/python

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


JUNIPER_HEAT = '1.3.6.1.4.1.2636.3.1.13.1.7'


class CheckSwitchHeat(CheckPlugin):

    def get_switch_heat(self):
        request_oid = ObjectName(JUNIPER_HEAT)

        heat_values = []

        heat_result = self.snmp_requester.do_walk(request_oid)
        if heat_result and len(heat_result) > 0:
            for oid, value in heat_result.items():
                if value is None or value == 0:
                    continue
                else:
                    heat_values.append(value)
        else:
            raise ValueError("didn't get values from the device for oid %s" % request_oid)

        if len(heat_values) == 0:
            raise ValueError("values received from the device could not be used %s" % request_oid)

        return heat_values

    def validate_heat(self, heat_settings, temperatures):

        temp_results = []
        for temp in temperatures:
            temp_results.append(self.validate_value_gt(temp, heat_settings))

        return self.get_device_status(temp_results)

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

            validate = self.validate_heat(heat_settings, temperatures)
            if validate != NagiosReturnValues.state_ok:
                return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckSwitchHeat().start()
