#!/usr/bin/python

import dns.resolver

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


class CheckDns(CheckPlugin):

    def check_snmp(self, settings):
        # ignore snmp check
        return True

    def check(self, settings):
        addresses = settings.get_dns()

        if not addresses:
            return NagiosReturnValues.state_ok

        my_resolver = dns.resolver.Resolver()
        my_resolver.nameservers = [settings.device['node']['ipaddr']]

        for address in addresses:
            answers = my_resolver.query(address['domain'])

            results = []
            for answer in answers:
                results.append(answer.address)

            if address['expected_answer'] not in results:
                print 'DNS CRITICAL - results [ %s ], expected %s' % (', '.join(results), address['expected_answer'])
                return NagiosReturnValues.state_critical

        print 'DNS OK'
        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckDns().start()
