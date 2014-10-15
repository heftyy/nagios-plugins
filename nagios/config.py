import ConfigParser
import os

class PluginConfig:
    def __init__(self):
        print "PATH = %s" % os.path.dirname(__file__)
        print "PATH = %s" % os.getcwd()

        dir_path = "/".join(os.path.dirname(__file__).split('/')[:-1])
        config_path = "%s/%s" % (dir_path, 'plugins.conf')

        config = ConfigParser.ConfigParser()
        f = open(config_path)
        config.readfp(f)
        self.api_ip = config.get('API', 'ip')
        self.api_port = config.get('API', 'port')
        self.api_notification_route = config.get('API', 'notification_route')

        self.api_notification_url = "http://%s:%s/%s" % (self.api_ip, self.api_port, self.api_notification_route)
        print self.api_notification_url