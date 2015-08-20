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

        self.notification_route = config.get('COG', 'notification_route')
        self.notification_url = "http://%s:%s/%s" % (config.get('COG', 'ip'),
                                                     config.get('COG', 'port'),
                                                     config.get('COG', 'notification_route'))

        self.nagios_settings_route = config.get('API', 'nagios_settings_route')
        self.nagios_settings_url = "http://%s:%s/%s" % (config.get('API', 'ip'),
                                                        config.get('API', 'port'),
                                                        config.get('API', 'nagios_settings_route'))