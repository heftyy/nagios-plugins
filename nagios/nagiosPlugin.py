import argparse
import sys
from host import NagiosHost
from config import PluginConfig

# _log = logging.getLogger('nagiosPlugin')


class NagiosPlugin(object):
    def __init__(self):
        self.config = PluginConfig()

    def create_parser(self):
        parser = argparse.ArgumentParser(description="Parameters for a nagios plugin")

        parser.add_argument('-V', '--version', action="store_true", dest="version", help="Show plugin version")
        parser.add_argument('-t', '--timeout', action="store", dest="timeout", help="Timeout in seconds")
        parser.add_argument('-w', '--warning', action="store", dest="warning_threshold", help="Warning threshold"),
        parser.add_argument('-c', '--critical', action="store", dest="critical_threshold", help="Critical threshold"),
        parser.add_argument('-v', '--verbose', action="count", dest="verbose", help="Increase verbosity level"),

        parser.add_argument('-H', '--host_address', action="store", dest="host_address", help="Host address"),
        parser.add_argument('-N', '--host_name', action="store", dest="host_name", help="Host name"),
        parser.add_argument('-O', '--host_output', action="store", dest="host_output", help="Host output"),
        parser.add_argument('-S', '--host_state', action="store", dest="host_state", help="Host state")
        parser.add_argument('-p', '--port', action="store", dest="port", help="Port")

        parser.add_argument('-C', '--community', action="store", dest="community", help="SNMP community"),
        parser.add_argument('-L', '--login', action="store", dest="login", help="Authentication login"),
        parser.add_argument('-P', '--password', action="store", dest="password", help="Authentication password"),

        parser.add_argument('--phone', action="store", dest="phone_number", help="Send text message if webservice fails")
        parser.add_argument('--email', action="store", dest="email", help="Send email if webservice fails")
        parser.add_argument('--node_id', action="store", dest="node_id", help="Id of the node")

        self.add_arguments(parser)

        return parser

    def start(self):
        parser = self.create_parser()
        options = parser.parse_args()

        host = NagiosHost(options)

        if not options.host_address:
            parser.error('You must specify a host address.')

        try:
            self.run(options, host)
            sys.exit()
        except Exception, e:
            print e.message
            sys.exit(e)

    def run(self):
        raise NotImplementedError("Please implement your plugin (run method).")

    def add_arguments(self, parser):
        print("No additional parameters")