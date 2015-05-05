#!/usr/bin/python

import time
from pysnmp.proto.rfc1902 import ObjectName
from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues

IF_OPERATIONAL_STATUS = '1.3.6.1.2.1.2.2.1.8'


class CheckPort(CheckPlugin):

    def get_port_status(self, itf):
        itf_index = itf['itfIndex']

        request_oid = ObjectName("%s.%s" % (IF_OPERATIONAL_STATUS, itf_index))

        itf_operational_status = self.snmp_requester.do_get(request_oid)
        if itf_operational_status and len(itf_operational_status) == 1:
            itf_operational_status = itf_operational_status[request_oid]
        else:
            raise ValueError("didn't get a value from the device for oid %s" % request_oid)

        return itf_operational_status

    @staticmethod
    def validate_status(itf, status):
        port_status_string = 'wlaczony' if itf['oper_status'] == 0 else 'wylaczony'
        print 'port %s jest %s' % (itf['itfIndex'], port_status_string)

        if itf['oper_status'] == status:
            return True
        else:
            return False

    def check(self, settings):
        interfaces = settings.get_port_interfaces()

        if not interfaces:
            return NagiosReturnValues.state_ok

        for itf in interfaces:
            try:
                status = self.get_port_status(itf)
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            if not self.validate_status(itf, status):
                return NagiosReturnValues.state_critical

            # print "status on itf: %s = %d" % (itf['itfIndex'], status)

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckPort().start()
