#!/usr/bin/python

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


class CheckSensor(CheckPlugin):

    def get_sensor_value(self, oid):
        request_oid = ObjectName(oid)

        result = self.snmp_requester.do_get(request_oid)
        if result and len(result) == 1:
            result = result[request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % request_oid)

        return result

    def validate_status(self, sensor, value):

        return self.validate_value_gt(value, sensor)

    def check(self, settings):
        sensors = settings.get_sensors()

        if not sensors:
            return NagiosReturnValues.state_ok

        for sensor in sensors:
            try:
                result = self.get_sensor_value(sensor['oid'])
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            validate = self.validate_status(sensor, result)
            if validate != NagiosReturnValues.state_ok:
                return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckSensor().start()
