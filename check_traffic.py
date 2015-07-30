#!/usr/bin/python

import time
from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


IF_IN_OCTETS = '1.3.6.1.2.1.2.2.1.10'
IF_OUT_OCTETS = '1.3.6.1.2.1.2.2.1.16'

IF_HC_IN_OCTETS = '1.3.6.1.2.1.31.1.1.1.6'
IF_HC_OUT_OCTETS = '1.3.6.1.2.1.31.1.1.1.10'

IF_DESCRIPTION = '1.3.6.1.2.1.2.2.1.2'
IF_ALIAS = '1.3.6.1.2.1.31.1.1.1.18'

# wait between checking octets for seconds
TRAFFIC_UPDATE_INTERVAL = 10


class CheckTraffic(CheckPlugin):

    @staticmethod
    def bytes_to_megabytes(traffic_in_bytes):
        return float(traffic_in_bytes) / (1000 * 1000)

    @staticmethod
    def bytes_to_megabits(traffic_in_bytes):
        return float(8 * traffic_in_bytes) / (1000 * 1000)

    @staticmethod
    def kilobits_to_megabits(traffic_in_kbits):
        return float(traffic_in_kbits / 1000)

    def get_traffic(self, itf, snmp_version):
        itf_index = itf['itfIndex']

        traffic_oid = None

        # snmp version 1
        if snmp_version == 0:
            if itf['type'] == 'IN':
                traffic_oid = IF_IN_OCTETS
            elif itf['type'] == 'OUT':
                traffic_oid = IF_OUT_OCTETS

        else:
            if itf['type'] == 'IN':
                traffic_oid = IF_HC_IN_OCTETS
            elif itf['type'] == 'OUT':
                traffic_oid = IF_HC_OUT_OCTETS

        if not traffic_oid:
            raise ValueError("error, the correct oid for request could not be found for itf: %s" % itf['itfIndex'])

        request_oid = ObjectName("%s.%s" % (traffic_oid, itf_index))

        octets_start = self.snmp_requester.do_get(request_oid)
        if octets_start and len(octets_start) == 1:
            octets_start = octets_start[request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % request_oid)

        time.sleep(TRAFFIC_UPDATE_INTERVAL)
        octets_end = self.snmp_requester.do_get(request_oid)
        if octets_end and len(octets_end) == 1:
            octets_end = octets_end[request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % request_oid)

        if octets_end == octets_start == 0:
            raise ValueError("counter was 0, no traffic on this interface")

        octets_diff = octets_end - octets_start
        traffic = octets_diff / TRAFFIC_UPDATE_INTERVAL

        # convert to kbps
        traffic = traffic * 8 / 1000

        request_oid = ObjectName("%s.%s" % (IF_DESCRIPTION, itf_index))

        itf_description = self.snmp_requester.do_get(request_oid)
        if itf_description and len(itf_description) == 1:
            itf_description = itf_description[request_oid]
        else:
            itf_description = ''

        request_oid = ObjectName("%s.%s" % (IF_ALIAS, itf_index))

        itf_alias = self.snmp_requester.do_get(request_oid)
        if itf_alias and len(itf_alias) == 1:
            itf_alias = itf_alias[request_oid]
        else:
            itf_alias = ''

        print "transfer na interfejse %s (%s) = %d Mbit/s" % (itf_description, itf_alias, self.kilobits_to_megabits(traffic))

        return traffic

    @staticmethod
    def validate_traffic(itf, traffic):
        traffic_min = traffic_max = traffic_min_warning = traffic_max_warning = None

        if 'min' and 'max' in itf:
            traffic_min = int(itf['min'])
            traffic_max = int(itf['max'])

        if 'warning_min' and 'warning_max' in itf:
            traffic_min_warning = int(itf['warning_min'])
            traffic_max_warning = int(itf['warning_max'])

        if traffic_min is not None and traffic_max is not None:
            # don't return in the first if because it could still be in the warning range
            if traffic_min <= traffic <= traffic_max:
                if traffic_min_warning is None and traffic_max_warning is None:
                    # print "traffic: %d OK" % traffic
                    return NagiosReturnValues.state_ok
            else:
                # print "traffic: %d ERROR" % traffic
                return NagiosReturnValues.state_critical

        if traffic_min_warning is not None and traffic_max_warning is not None:
            if traffic_min_warning <= traffic <= traffic_max_warning:
                # print "traffic: %d OK" % traffic
                return NagiosReturnValues.state_ok
            else:
                # print "traffic: %d WARNING" % traffic
                return NagiosReturnValues.state_warning

        return NagiosReturnValues.state_unknown

    def check(self, settings):
        interfaces = settings.get_traffic_interfaces()

        if not interfaces:
            return 0

        snmp_settings = settings.get_snmp_config()

        if not snmp_settings:
            return 1

        statuses = []

        for itf in interfaces:
            try:
                traffic = self.get_traffic(itf, snmp_settings['snmpVersion'])
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            status = self.validate_traffic(itf, traffic)

            statuses.append(status)

            # print "traffic on itf: %s = %f MB" % (itf['itfIndex'], self.bytes_to_mb(traffic))

        if len(statuses) == 0:
            return NagiosReturnValues.state_ok
        else:
            return self.get_device_status(statuses)


if __name__ == '__main__':
    CheckTraffic().start()
