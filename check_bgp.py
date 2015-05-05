#!/usr/bin/python

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


BGP_OID = '1.3.6.1.2.1.15.3.1'
BGP_REMOTE_ADDRESS_END = 7
BGP_REMOTE_PORT_END = 8
BGP_IN_MESSAGES_END = 12
BGP_OUT_MESSAGES_END = 13


class BgpSession():
    def __init__(self, remote_address=None, remote_port=None, in_messages=None, out_messages=None):
        self.remote_address = remote_address
        self.remote_port = remote_port
        self.in_messages = in_messages
        self.out_messages = out_messages


class CheckBGP(CheckPlugin):
    def get_bgp_data(self):
        request_bgp_oid = ObjectName(BGP_OID)

        bgp_dict = {}

        bgp_walk_results = self.snmp_requester.do_walk(request_bgp_oid)
        if bgp_walk_results and len(bgp_walk_results) > 0:
            for oid, value in bgp_walk_results.items():
                ident = oid[len(oid) - 4:len(oid)].prettyPrint()

                if ident not in bgp_dict:
                    bgp_dict[ident] = BgpSession()

                if oid[len(request_bgp_oid)] == BGP_IN_MESSAGES_END:
                    bgp_dict[ident].in_messages = value

                if oid[len(request_bgp_oid)] == BGP_OUT_MESSAGES_END:
                    bgp_dict[ident].out_messages = value

                if oid[len(request_bgp_oid)] == BGP_REMOTE_ADDRESS_END:
                    bgp_dict[ident].remote_address = value

                if oid[len(request_bgp_oid)] == BGP_REMOTE_PORT_END:
                    bgp_dict[ident].remote_port = value

        else:
            raise ValueError("didn't get values from the device for oid %s" % request_bgp_oid)

        if len(bgp_dict) == 0:
            raise ValueError("values received from the device could not be used %s" % request_bgp_oid)

        return bgp_dict

    def validate_bgp(self, bgp_settings, bgp_data):

        status_list = []

        for bgp in bgp_settings:
            if 'remote_ip' in bgp:
                ip = bgp['remote_ip']
                if ip in bgp_data:
                    in_messages = bgp_data[ip].in_messages

                    status = self.validate_value_gt(in_messages, bgp)
                    print "bgp: %s" % in_messages
                    status_list.append(status)
                else:
                    status_list.append(NagiosReturnValues.state_unknown)

        return self.get_device_status(status_list)

    def check(self, settings):
        bgp_list = settings.get_bgp()

        if not bgp_list:
            return NagiosReturnValues.state_ok

        try:
            bgp_data = self.get_bgp_data()
        except ValueError as e:
            print "ValueError %s" % e
            return NagiosReturnValues.state_unknown

        validate = self.validate_bgp(bgp_list, bgp_data)
        if validate != NagiosReturnValues.state_ok:
            return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckBGP().start()
