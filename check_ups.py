#!/usr/bin/python

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues

UPS_BATTERY_VOLTAGE = '1.3.6.1.2.1.33.1.2.5.0'
UPS_BATTERY_TEMPERATURE = '1.3.6.1.2.1.33.1.2.7.0'


class CheckUps(CheckPlugin):

    def get_battery_status(self):
        temp_request_oid = ObjectName(UPS_BATTERY_TEMPERATURE)

        temperature = self.snmp_requester.do_get(temp_request_oid)
        if temperature and len(temperature) == 1:
            temperature = temperature[temp_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % temp_request_oid)

        voltage_request_oid = ObjectName(UPS_BATTERY_VOLTAGE)

        voltage = self.snmp_requester.do_get(voltage_request_oid)
        if voltage and len(voltage) == 1:
            voltage = voltage[voltage_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % voltage_request_oid)

        result = {'temperature': temperature, 'voltage': voltage}

        return result

    def validate_status(self, ups, value):

        temp_valid = voltage_valid = None

        if 'temperature' in ups:
            temp_valid = self.validate_value_lt(value['temperature'], ups['temperature'])

        if 'voltage' in ups:
            voltage_valid = self.validate_value_gt(value['voltage'], ups['voltage'])

        return self.get_device_status(temp_valid, voltage_valid)

    def check(self, settings):
        ups_list = settings.get_ups_list()

        if not ups_list:
            return NagiosReturnValues.state_ok

        for ups in ups_list:
            if 'temperature' not in ups and 'voltage' not in ups:
                return NagiosReturnValues.state_unknown

            try:
                result = self.get_battery_status()
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            validate = self.validate_status(ups, result)
            if validate != NagiosReturnValues.state_ok:
                return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckUps().start()
