import ConfigParser


class PluginConfig:
    def __init__(self):
        config = ConfigParser.ConfigParser()
        config.readfp(open(r'plugins.conf'))
        self.api_ip = config.get('API', 'ip')
        self.api_port = config.get('API', 'port')
        self.api_notification_route = config.get('API', 'notification_route')

        self.api_notification_url = "http://%s:%s/%s" % (self.api_ip, self.api_port, self.api_notification_route)
        print self.api_notification_url