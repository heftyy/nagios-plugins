#!/usr/bin/python
import json

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues

UPS_BATTERY_VOLTAGE = '1.3.6.1.2.1.33.1.2.5.0'
UPS_INPUT_VOLTAGE = '1.3.6.1.2.1.33.1.3.3.1.3.1'

UPS_SEC_ON_BATTERY = '1.3.6.1.2.1.33.1.2.2.0'
UPS_EST_CH_REM = '1.3.6.1.2.1.33.1.2.4.0'
UPS_OUT_PERCENT_LOAD = '1.3.6.1.2.1.33.1.4.4.1.5.1'

UPS_BATTERY_TEMPERATURE = '1.3.6.1.2.1.33.1.2.7.0'


class CheckUps(CheckPlugin):

    def get_battery_status(self):
        temp_request_oid = ObjectName(UPS_BATTERY_TEMPERATURE)

        temperature = self.snmp_requester.do_get(temp_request_oid)
        if temperature and len(temperature) == 1:
            temperature = temperature[temp_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % temp_request_oid)

        voltage_request_oid = ObjectName(UPS_INPUT_VOLTAGE)

        voltage = self.snmp_requester.do_get(voltage_request_oid)
        if voltage and len(voltage) == 1:
            voltage = float(voltage[voltage_request_oid])
        else:
            raise ValueError("didn't get a value from the device for oid %s" % voltage_request_oid)

        sec_on_battery_request_oid = ObjectName(UPS_SEC_ON_BATTERY)

        sec_on_battery = self.snmp_requester.do_get(sec_on_battery_request_oid)
        if sec_on_battery and len(sec_on_battery) == 1:
            sec_on_battery = sec_on_battery[sec_on_battery_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % sec_on_battery_request_oid)

        est_ch_rem_request_oid = ObjectName(UPS_EST_CH_REM)

        est_ch_rem = self.snmp_requester.do_get(est_ch_rem_request_oid)
        if est_ch_rem and len(est_ch_rem) == 1:
            est_ch_rem = est_ch_rem[est_ch_rem_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % est_ch_rem_request_oid)

        out_percent_load_request_oid = ObjectName(UPS_OUT_PERCENT_LOAD)

        out_percent_load = self.snmp_requester.do_get(out_percent_load_request_oid)
        if out_percent_load and len(out_percent_load) == 1:
            out_percent_load = out_percent_load[out_percent_load_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % out_percent_load_request_oid)

        result = {'temperature': temperature, 'voltage': voltage, 'sec_on_battery': sec_on_battery,
                  'est_ch_rem': est_ch_rem, 'out_percent_load': out_percent_load}

        return result

    def validate_status(self, ups_settings, value):

        temp_valid = voltage_valid = None

        if 'temperature' in ups_settings:
            temp_valid = self.validate_value_lt(value['temperature'], ups_settings['temperature'])
            if temp_valid != NagiosReturnValues.state_ok:
                print "Temperatura na baterii: %s C" % value['temperature']

        if 'voltage' in ups_settings:
            voltage_valid = self.validate_value_gt(value['voltage'], ups_settings['voltage'])
            if voltage_valid != NagiosReturnValues.state_ok:
                print "napiecie: %s V, praca na baterii: %s, stan baterii: %s %%, obciazenie: %s %%" % \
                      (value['voltage'], value['sec_on_battery'], value['est_ch_rem'], value['out_percent_load'])

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
            else:
                print "UPS OK"

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckUps().start()
