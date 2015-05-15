#!/usr/bin/python
import json
import re

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


CMTS_SNR = '1.3.6.1.2.1.10.127.1.1.4.1.5'
CMTS_FIBER_NODES = '1.3.6.1.4.1.4998.1.1.105.1.1.2.1.4'

IF_DESCRIPTION = '1.3.6.1.2.1.2.2.1.2'


class Interface():
    def __init__(self, index, oid):
        self.index = index
        self.fb_name = self.get_fb_name(oid)
        self.snr = None
        self.description = None

    def get_json(self, **kwargs):
        json = {
            "index": int(self.index),
            "fb_name": self.fb_name,
            "snr": self.snr,
            "type": "itf-%d" % int(self.index),
            "output": "%s %s snr: %s" % (self.fb_name, self.description, self.snr)
        }
        for key, value in kwargs.iteritems():
            json[key] = value
        return json

    @staticmethod
    def get_fb_name(oid):
        if isinstance(oid, ObjectName):
            oid = oid.prettyPrint().split('.')
        elif isinstance(oid, basestring):
            oid = oid.split('.')

        fb_oid_size = len(CMTS_FIBER_NODES.split('.'))
        name = ""

        i = fb_oid_size + 2
        while i < len(oid) - 1:
            char = int(oid[i])
            name += chr(char)
            i += 1

        return name


class CheckCmtsSnr(CheckPlugin):

    p = re.compile('[0-9/\\.]+')

    def get_if_description(self, index):
        if_description_request_oid = ObjectName("%s.%s" % (IF_DESCRIPTION, index))

        if_description = self.snmp_requester.do_get(if_description_request_oid)
        if if_description and len(if_description) == 1:
            if_description = if_description[if_description_request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % if_description_request_oid)

        return re.search(r'([0-9/\\.]+)', if_description.prettyPrint()).group(0)

    def get_cmts_snr_values(self):
        request_fb_oid = ObjectName(CMTS_FIBER_NODES)

        interfaces = {}

        fb_results = self.snmp_requester.do_walk(request_fb_oid)
        if fb_results and len(fb_results) > 0:
            for oid, value in fb_results.items():

                last = oid[len(oid) - 1]
                itf = Interface(last, oid)

                interfaces[itf.index] = itf
        else:
            raise ValueError("didn't get values from the device for oid %s" % request_fb_oid)

        request_snr_oid = ObjectName(CMTS_SNR)

        snr_results = self.snmp_requester.do_walk(request_snr_oid)
        if snr_results and len(snr_results) > 0:
            for oid, value in snr_results.items():
                if value > 0:
                    last = oid[len(oid) - 1]

                    if last in interfaces:
                        interfaces[last].snr = float(value) / 10
                        interfaces[last].description = self.get_if_description(last)
        else:
            raise ValueError("didn't get values from the device for oid %s" % request_snr_oid)

        if len(interfaces) == 0:
            raise ValueError("values received from the device could not be used %s" % request_snr_oid)

        return interfaces

    def validate_snr(self, cmts_snr, interfaces):

        status_list = []

        for itf in interfaces.values():
            if itf.snr:
                status = self.validate_value_gt(itf.snr, cmts_snr)

                print "!%s" % json.dumps(itf.get_json(nagios_status=NagiosReturnValues.value_to_int(status)))
                # if status != NagiosReturnValues.state_ok:
                #     print "!%s" % itf.get_json(nagios_status=status)

                status_list.append(status)

        return self.get_device_status(status_list)

    def check(self, settings):
        cmts_snrs = settings.get_cmts_snr()

        if not cmts_snrs:
            return NagiosReturnValues.state_ok

        for cmts_snr in cmts_snrs:
            try:
                interfaces = self.get_cmts_snr_values()
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            validate = self.validate_snr(cmts_snr, interfaces)
            if validate != NagiosReturnValues.state_ok:
                return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckCmtsSnr().start()
