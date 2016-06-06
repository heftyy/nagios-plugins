import os


class NagiosHost():
    def __init__(self, options):
        self.address = options.host_address
        self.port = options.port
        self.name = options.host_name
        self.output = options.host_output
        self.state = options.host_state

        self.community = options.community
        self.login = options.login
        self.password = options.password

        self.node_id = options.node_id

    def is_reachable(self):
        ret = os.system("ping -c 1 %s" % self.address)
        if ret != 0:
            print "Host is not up"
            return False

        return True

