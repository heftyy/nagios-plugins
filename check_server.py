#!/usr/bin/python

from pysnmp.proto.rfc1902 import ObjectName

from nagios.checkPlugin import CheckPlugin
from nagios.nagiosReturnValues import NagiosReturnValues


ONE_MINUTE_LOAD_OID = ObjectName("1.3.6.1.4.1.2021.10.1.5.1")
FIVE_MINUTE_LOAD_OID = ObjectName("1.3.6.1.4.1.2021.10.1.5.2")
FIFTEEN_MINUTE_LOAD_OID = ObjectName("1.3.6.1.4.1.2021.10.1.5.3")

USER_CPU = ObjectName(".1.3.6.1.4.1.2021.11.9.0")
SYSTEM_CPU = ObjectName(".1.3.6.1.4.1.2021.11.10.0")
IDLE_CPU = ObjectName(".1.3.6.1.4.1.2021.11.11.0")

SWAP_SIZE = ObjectName(".1.3.6.1.4.1.2021.4.3.0")
SWAP_AVAILABLE = ObjectName(".1.3.6.1.4.1.2021.4.4.0")
MEMORY_TOTAL = ObjectName(".1.3.6.1.4.1.2021.4.5.0")
MEMORY_UNUSED = ObjectName(".1.3.6.1.4.1.2021.4.6.0")
MEMORY_FREE = ObjectName(".1.3.6.1.4.1.2021.4.11.0")
MEMORY_SHARED = ObjectName(".1.3.6.1.4.1.2021.4.13.0")
MEMORY_BUFFERED = ObjectName(".1.3.6.1.4.1.2021.4.14.0")
MEMORY_CACHED = ObjectName(".1.3.6.1.4.1.2021.4.15.0")

STORAGE_INDEX = ObjectName("1.3.6.1.2.1.25.2.3.1.1")
STORAGE_TYPE = ObjectName("1.3.6.1.2.1.25.2.3.1.2")
STORAGE_DESCR = ObjectName("1.3.6.1.2.1.25.2.3.1.3")
STORAGE_ALLOCATION_UNITS = ObjectName("1.3.6.1.2.1.25.2.3.1.4")
STORAGE_SIZE = ObjectName("1.3.6.1.2.1.25.2.3.1.5")
STORAGE_USED = ObjectName("1.3.6.1.2.1.25.2.3.1.6")
STORAGE_ALLOCATION_FAILURES = ObjectName("1.3.6.1.2.1.25.2.3.1.7")

STORAGE_FIXED_DISK_TYPE = ObjectName("1.3.6.1.2.1.25.2.1.4")


class Server():
    def __init__(self, one_minute_load, five_minute_load, fifteen_minute_load, user_cpu, system_cpu, idle_cpu,
                 swap_size, swap_available, memory_total, memory_unused, memory_free, memory_shared, memory_buffered,
                 memory_cached):

        self.one_minute_load = one_minute_load
        self.five_minute_load = five_minute_load
        self.fifteen_minute_load = fifteen_minute_load
        self.user_cpu = user_cpu
        self.system_cpu = system_cpu
        self.idle_cpu = idle_cpu
        self.swap_size = swap_size
        self.swap_available = swap_available
        self.memory_total = memory_total
        self.memory_unused = memory_unused
        self.memory_free = memory_free
        self.memory_shared = memory_shared
        self.memory_buffered = memory_buffered
        self.memory_cached = memory_cached
        if memory_total and memory_buffered and memory_cached and memory_free:
            self.memory_used = self.memory_total - self.memory_buffered - self.memory_cached - self.memory_free

    def __getitem__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]


class Storage():
    def __init__(self, index, storage_type, size, used, description):
        self.index = int(index)
        self.type = storage_type
        self.size = int(size)
        self.used = int(used)
        self.description = description


class CheckServer(CheckPlugin):

    def get_server_data(self):
        server = None

        request_oids = [
            ONE_MINUTE_LOAD_OID, FIVE_MINUTE_LOAD_OID, FIFTEEN_MINUTE_LOAD_OID,
            USER_CPU, SYSTEM_CPU, IDLE_CPU,
            SWAP_SIZE, SWAP_AVAILABLE,
            MEMORY_TOTAL, MEMORY_UNUSED, MEMORY_FREE, MEMORY_SHARED, MEMORY_BUFFERED, MEMORY_CACHED
        ]

        server_data = self.snmp_requester.do_get(*request_oids)
        if server_data and len(server_data) > 0:
            server = Server(
                float(server_data[ONE_MINUTE_LOAD_OID]) / 100,
                float(server_data[FIVE_MINUTE_LOAD_OID]) / 100,
                float(server_data[FIFTEEN_MINUTE_LOAD_OID]) / 100,
                server_data[USER_CPU],
                server_data[SYSTEM_CPU],
                server_data[IDLE_CPU],
                server_data[SWAP_SIZE],
                server_data[SWAP_AVAILABLE],
                server_data[MEMORY_TOTAL],
                server_data[MEMORY_UNUSED],
                server_data[MEMORY_FREE],
                server_data[MEMORY_SHARED],
                server_data[MEMORY_BUFFERED],
                server_data[MEMORY_CACHED]
            )

            # for oid, value in server_data.items():
            #   print "%s = %s" % (oid.prettyPrint(), value.prettyPrint())

        else:
            raise ValueError("didn't get any values from the server")

        if not server:
            raise ValueError("didn't get any values from the server")

        storage = self.get_storage()
        server.storage = storage

        return server

    def get_storage(self):
        storage_dict = {}

        storage_type = self.snmp_requester.do_walk(STORAGE_TYPE)
        if storage_type and len(storage_type) > 0:
            for oid, value in storage_type.items():
                storage_index = oid[len(oid) - 1]
                storage_type = value

                if storage_type != STORAGE_FIXED_DISK_TYPE:
                    continue

                request_storage_size_oid = ObjectName("%s.%s" % (STORAGE_SIZE, storage_index))
                request_storage_used_oid = ObjectName("%s.%s" % (STORAGE_USED, storage_index))
                request_storage_desc_oid = ObjectName("%s.%s" % (STORAGE_DESCR, storage_index))

                storage_size = self.snmp_requester.do_get(request_storage_size_oid)[request_storage_size_oid]
                storage_used = self.snmp_requester.do_get(request_storage_used_oid)[request_storage_used_oid]
                storage_desc = self.snmp_requester.do_get(request_storage_desc_oid)[request_storage_desc_oid]

                if storage_index not in storage_dict:
                    storage_dict[storage_index] = Storage(
                        storage_index,
                        storage_type,
                        storage_size,
                        storage_used,
                        storage_desc
                    )

        return storage_dict

    def validate_server(self, server_settings, server_data):
        status_list = []

        for key, settings in server_settings.items():
            if key == 'storage_used':
                continue

            if key in server_data.__dict__:
                status = self.validate_value(server_data[key], settings)
                print "%s: %s" % (key, server_data[key])
                status_list.append(status)
            else:
                status_list.append(NagiosReturnValues.state_unknown)

        if 'storage_used' in server_settings:
            if 'storage' in server_data.__dict__:
                storage_list = server_data['storage']
                for storage in storage_list.values():
                    storage_used_percent = int((float(storage.used) / storage.size) * 100)
                    status = self.validate_value_lt(storage_used_percent, server_settings['storage_used'])
                    print "zajetosc dysku %s: %s" % (storage.description, storage_used_percent)
                    status_list.append(status)
            else:
                status_list.append(NagiosReturnValues.state_unknown)

        return self.get_device_status(status_list)

    def check(self, settings):
        server_list = settings.get_server()

        if not server_list:
            return NagiosReturnValues.state_ok

        for server in server_list:
            try:
                server_data = self.get_server_data()
            except ValueError as e:
                print "ValueError %s" % e
                return NagiosReturnValues.state_unknown

            validate = self.validate_server(server, server_data)
            if validate != NagiosReturnValues.state_ok:
                return validate

        return NagiosReturnValues.state_ok


if __name__ == '__main__':
    CheckServer().start()
