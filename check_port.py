#!/usr/bin/python

import time
from nagios.checkPlugin import CheckPlugin

IF_IN_OCTETS = '1.3.6.1.2.1.2.2.1.10'
IF_OUT_OCTETS = '1.3.6.1.2.1.2.2.1.16'

IF_HC_IN_OCTETS = '1.3.6.1.2.1.31.1.1.1.6'
IF_HC_OUT_OCTETS = '1.3.6.1.2.1.31.1.1.1.10'

#wait between checking octets for seconds
TRANSFER_UPDATE_INTERVAL = 10


class CheckPort(CheckPlugin):

    @staticmethod
    def bytes_to_mb(transfer_in_bytes):
        return float(transfer_in_bytes) / (1000 * 1000)

    def get_transfer(self, itf, snmp_version):
        itf_index = itf['itfIndex']

        itf_oid = "%s.%s" % (IF_IN_OCTETS, itf_index)

        octets_start = self.snmp_requester.do_get(itf_oid)
        if octets_start and len(octets_start) == 1:
            octets_start = octets_start[0][1]
        else:
            return 0

        time.sleep(TRANSFER_UPDATE_INTERVAL)
        octets_end = self.snmp_requester.do_get(itf_oid)
        if octets_end and len(octets_end) == 1:
            octets_end = octets_end[0][1]
        else:
            return 0

        octets_diff = octets_end - octets_start
        transfer = octets_diff / TRANSFER_UPDATE_INTERVAL

        return transfer

    @staticmethod
    def validate_transfer(itf, transfer):
        if int(itf['min']) <= transfer <= int(itf['max']):
            print "transfer: %d is valid" % transfer
            return True
        else:
            print "transfer: %d is invalid" % transfer
            return False

    def check(self, settings):
        interfaces = settings.get_interfaces()
        snmp_settings = settings.get_snmp_config()
        for itf in interfaces:
            transfer = self.get_transfer(itf, snmp_settings['snmpVersion'])
            if not self.validate_transfer(itf, transfer):
                return 1

            print "transfer on itf: %s = %d B" % (itf['itfIndex'], transfer)
            print "transfer on itf: %s = %f MB" % (itf['itfIndex'], self.bytes_to_mb(transfer))

        return 0


if __name__ == '__main__':
    CheckPort().start()
