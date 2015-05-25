#!/usr/bin/python
import json
from operator import attrgetter
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
        self.fn_name = self.get_fn_name(oid)
        self.snr = None
        self.description = None

    def get_json(self, **kwargs):
        json = {
            "index": int(self.index),
            "fn_name": self.fn_name,
            "snr": self.snr,
            "type": "fn-%s" % self.fn_name,
            "output": "%s %s snr: %s" % (self.fn_name, self.description, self.snr)
        }
        for key, value in kwargs.iteritems():
            json[key] = value
        return json

    def get_ok_json(self, **kwargs):
        json = {
            "fn_name": self.fn_name,
            "type": "fn-%s" % self.fn_name,
            "output": "%s OK" % self.fn_name
        }
        for key, value in kwargs.iteritems():
            json[key] = value
        return json

    @staticmethod
    def get_fn_name(oid):
        if isinstance(oid, ObjectName):
            oid = oid.prettyPrint().split('.')
        elif isinstance(oid, basestring):
            oid = oid.split('.')

        fn_oid_size = len(CMTS_FIBER_NODES.split('.'))
        name = ""

        i = fn_oid_size + 2
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
        request_fn_oid = ObjectName(CMTS_FIBER_NODES)

        interfaces = {}

        fn_results = self.snmp_requester.do_walk(request_fn_oid)
        if fn_results and len(fn_results) > 0:
            for oid, value in fn_results.items():

                last = oid[len(oid) - 1]
                itf = Interface(last, oid)

                interfaces[itf.index] = itf
        else:
            raise ValueError("didn't get values from the device for oid %s" % request_fn_oid)

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

    @staticmethod
    def get_fn_map(interfaces):
        fn_map = {}

        for itf in interfaces.values():
            if itf.fn_name in fn_map:
                if itf.snr:
                    fn_map[itf.fn_name].append(itf)
            else:
                if itf.snr:
                    fn_map[itf.fn_name] = [itf]

        for fn_name in fn_map:
           fn_map[fn_name] = sorted(fn_map[fn_name], key=attrgetter('snr'))

        return fn_map

    def validate_snr(self, cmts_snr, interfaces):

        status_list = []

        fn_map = self.get_fn_map(interfaces)

        for fn_name in fn_map.keys():
            fn_status_list = []
            for itf in fn_map[fn_name]:
                if itf.snr:
                    status = self.validate_value_gt(itf.snr, cmts_snr)

                    if status != NagiosReturnValues.state_ok:
                        print "!%s" % json.dumps(itf.get_json(
                            nagios_status=NagiosReturnValues.value_to_int(status))
                        )

                    fn_status_list.append(status)
                    status_list.append(status)

            fn_status = self.get_device_status(fn_status_list)
            if fn_status == NagiosReturnValues.state_ok:
                print "!%s" % json.dumps(fn_map[fn_name][0].get_ok_json(
                    nagios_status=NagiosReturnValues.value_to_int(fn_status))
                )

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
