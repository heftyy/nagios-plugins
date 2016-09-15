#!/usr/bin/python

from pysnmp.proto.rfc1902 import ObjectName
from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues
import requests

LAN_CONTROLLER_IN4 = '1.3.6.1.4.1.17095.3.11.0'
LAN_CONTROLLER_IN6 = '1.3.6.1.4.1.17095.3.13.0'

LAN_CONTROLLER_V2_IN4 = '1.3.6.1.4.1.17095.4.6.0'
LAN_CONTROLLER_V2_IN6 = '1.3.6.1.4.1.17095.5.1.0'

LB487 = '1.3.6.1.4.1.22925.487.3.1.3'


class CheckSensor(CheckPlugin):

    def get_sensor_value(self, oid):
        request_oid = ObjectName(oid)

        result = self.snmp_requester.do_get(request_oid)
        if result and len(result) == 1:
            result = result[request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % request_oid)

        return result

    def validate_status(self, sensor_config, value):

        status = self.validate_value_lt(value, sensor_config)

        return status

    def read_lan_controller(self, sensor_config):
        request_oid = None

        if sensor_config['input'] == 'LAN_CONTROLLER_IN4':
            request_oid = LAN_CONTROLLER_IN4

        elif sensor_config['input'] == 'LAN_CONTROLLER_IN6':
            request_oid = LAN_CONTROLLER_IN6

        # lan controller returns OctetString so we have to turn it into string with pretty print and cast to float
        temperature = float(self.get_sensor_value(request_oid).prettyPrint())

        print "temperatura: %s (%s / %s)" % (temperature, sensor_config['warning'], sensor_config['critical'])

        return self.validate_status(sensor_config, temperature)

    def read_lan_controller2(self, sensor_config):
        request_oid = None

        if sensor_config['input'] == 'LAN_CONTROLLER_V2_IN4':
            request_oid = LAN_CONTROLLER_V2_IN4

        elif sensor_config['input'] == 'LAN_CONTROLLER_V2_IN6':
            request_oid = LAN_CONTROLLER_V2_IN6

        # lan controller returns OctetString so we have to turn it into string with pretty print and cast to float
        temperature = float(self.get_sensor_value(request_oid).prettyPrint())

        print "temperatura: %s (%s / %s)" % (temperature, sensor_config['warning'], sensor_config['critical'])

        return self.validate_status(sensor_config, temperature)

    def read_lb487(self, sensor_config):
        request_oid = "%s.%d.1" % (LB487, sensor_config['id'])

        temperature = float(self.get_sensor_value(request_oid)) / 100

        status = self.validate_status(sensor_config, temperature)

        if status != NagiosReturnValues.state_ok:
            print "temperatura %s: %s (%s / %s)" % (sensor_config['name'], temperature,
                                                    sensor_config['warning'], sensor_config['critical'])

        return status

    @staticmethod
    def read_moniti(node):
        url = "http://%s/data.html?analog=yes&digital=yes" % node['ipaddr']
        resp = requests.get(url, params=None)
        if resp.status_code != 200:
            print resp.content
            return NagiosReturnValues.state_unknown

        json = resp.json()
        statuses = []

        for analog in json['analog']:
            state = int(analog['state'])
            if state != 0:
                print "%s %s %s" % (analog['name'], analog['value'], analog['unit'])

            if state == -2 or state == 2:
                statuses.append(NagiosReturnValues.state_critical)
            elif state == -1 or state == 1:
                statuses.append(NagiosReturnValues.state_warning)
            elif state == 126:
                statuses.append(NagiosReturnValues.state_unknown)
            else:
                statuses.append(NagiosReturnValues.state_ok)

        for digital in json['digital']:
            state = int(digital['state'])
            if state != 0:
                print "%s" % (digital['name'])

            if state == 1:
                statuses.append(NagiosReturnValues.state_critical)
            elif state == 2:
                statuses.append(NagiosReturnValues.state_warning)
            elif state == 3:
                statuses.append(NagiosReturnValues.state_warning)
            else:
                statuses.append(NagiosReturnValues.state_ok)

        return statuses

    def get_sensor_status(self, sensor_config):
        status = NagiosReturnValues.state_ok

        if 'input' in sensor_config:
            if sensor_config['input'] == 'LAN_CONTROLLER_IN4' or sensor_config['input'] == 'LAN_CONTROLLER_IN6':
                status = self.read_lan_controller(sensor_config)

            elif sensor_config['input'] == 'LAN_CONTROLLER_V2_IN4' or sensor_config['input'] == 'LAN_CONTROLLER_V2_IN6':
                status = self.read_lan_controller2(sensor_config)

            elif sensor_config['input'] == 'LB487':
                status = self.read_lb487(sensor_config)

        return status

    def check(self, settings):
        # special case for special device
        if settings.device['node']['netDevice']['type']['name'] == 'Moniti':
            try:
                statuses = self.read_moniti(settings.device['node'])
                status = self.get_device_status(statuses)
                if status == NagiosReturnValues.state_ok:
                    print "Sensor OK"
                return status
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

        sensors = settings.get_sensors()

        statuses = []

        if not sensors:
            return NagiosReturnValues.state_ok

        for sensor in sensors:
            try:
                status = self.get_sensor_status(sensor)
                statuses.append(status)
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

        if len(statuses) == 0:
            print "Sensor OK"
            return NagiosReturnValues.state_ok
        else:
            status = self.get_device_status(statuses)
            if status == NagiosReturnValues.state_ok:
                print "Sensor OK"
            return status


if __name__ == '__main__':
    CheckSensor().start()
