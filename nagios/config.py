import ConfigParser
import os

class PluginConfig:
    def __init__(self):
        print "PATH = %s" % os.path.dirname(__file__)
        print "PATH = %s" % os.getcwd()

        config = ConfigParser.ConfigParser()
        f = open(r'plugins.conf')
        config.readfp(f)
        self.api_ip = config.get('API', 'ip')
        self.api_port = config.get('API', 'port')
        self.api_notification_route = config.get('API', 'notification_route')

        self.api_notification_url = "http://%s:%s/%s" % (self.api_ip, self.api_port, self.api_notification_route)
        print self.api_notification_url