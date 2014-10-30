from pysnmp.proto.api.v2c import NoSuchObject, NoSuchInstance

__author__ = 'szymon'

from enum import Enum
from pysnmp.entity.rfc3413.oneliner import cmdgen


class ConnectionState(Enum):
    offline = 1
    online = 2
    waiting = 3

ping_oid = '1.3.6.1.2.1.1.1.0'


class SnmpRequester(object):

    def __init__(self, address, community, version):
        self.address = address
        self.community = community
        self.version = version

        self.connection_state = ConnectionState.offline

    def init_connection(self):
        if self.check_snmp_alive():
            self.connection_state = ConnectionState.online
            return True
        else:
            return False

    def check_snmp_alive(self):
        if self.do_get(ping_oid):
            return True
        else:
            return False

    def get_snmp_target(self):
        community_data = cmdgen.CommunityData(self.community)
        if self.version == 0:
            community_data.mpModel = 0

        return community_data

    def get_snmp_transport(self):
        return cmdgen.UdpTransportTarget((self.address, 161))

    @staticmethod
    def check_for_errors(error_indication, error_status, error_index, var_binds):
        if error_indication:
            print(error_indication)
        else:
            if error_status:
                print('%s at %s' % (
                    error_status.prettyPrint(),
                    error_index and var_binds[int(error_index)-1] or '?'
                )
                )
            else:
                for name, val in var_binds:
                    if isinstance(val, NoSuchObject) or isinstance(val, NoSuchInstance):
                        var_binds[name] = None
                return var_binds

    @staticmethod
    def check_for_errors_walk(error_indication, error_status, error_index, var_binds):
        if error_indication:
            print(error_indication)
        else:
            if error_status:
                print('%s at %s' % (
                    error_status.prettyPrint(),
                    error_index and var_binds[int(error_index)-1] or '?'
                )
                )
            else:
                for row in var_binds:
                    for name, val in row:
                        if isinstance(val, NoSuchObject) or isinstance(val, NoSuchInstance):
                            row[name] = None
                return var_binds

    def do_get(self, oid):
        cmd_gen = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_gen.getCmd(
            self.get_snmp_target(),
            self.get_snmp_transport(),
            oid
        )

        return self.check_for_errors(error_indication, error_status, error_index, var_binds)

    def do_walk(self, walk_oid):
        cmd_gen = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_gen.bulkCmd(
            self.get_snmp_target(),
            self.get_snmp_transport(),
            0, 25,
            walk_oid
        )

        var_binds = self.check_for_errors_walk(error_indication, error_status, error_index, var_binds)

        result = []

        if var_binds:
            for row in var_binds:
                for oid, value in row:
                    if oid.prettyPrint().startswith(walk_oid):
                        tup2 = (oid, value)
                        result.append(tup2)

        return result

