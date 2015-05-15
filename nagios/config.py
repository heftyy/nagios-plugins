import ConfigParser
import os

class PluginConfig:
    def __init__(self):
        # print "PATH = %s" % os.path.dirname(__file__)
        # print "PATH = %s" % os.getcwd()

        dir_path = "/".join(os.path.dirname(__file__).split('/')[:-1])
        config_path = "%s/%s" % (dir_path, 'plugins.conf')

        config = ConfigParser.ConfigParser()
        f = open(config_path)
        config.readfp(f)
        self.cog_ip = config.get('COG', 'ip')
        self.cog_port = config.get('COG', 'port')

        self.cog_notification_route = config.get('COG', 'notification_route')
        self.cog_notification_url = "http://%s:%s/%s" % (self.cog_ip, self.cog_port, self.cog_notification_route)

        self.cog_nagios_settings_route = config.get('COG', 'nagios_settings_route')
        self.cog_nagios_settings_url = "http://%s:%s/%s" % (self.cog_ip, self.cog_port, self.cog_nagios_settings_route)