import datetime
from plugin.capture_box import Box as box
from plugin.capture_dropbox import Dropbox as dropbox
from plugin.capture_googledrive import GoogleDrive as googledrive
from plugin.capture_owncloud import OwnCloud as ownloud
from plugin.capture_stacksync import StackSync as stacksync


# this class will be invoked by monitor_rmq
# this class has an instance monitor_py and sniffer_py

class Monitor(object):
    # singleton class
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Monitor, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    # name of the current dummyhost => the physical machine => ast10,ast12,ast13
    def __init__(self, personal_cloud=None, hostname=None):
        print "constructor"
        self.hostname = hostname
        self.sync_client = None
        if personal_cloud is None:
            raise NotImplemented
        else:
            self.sync_client = eval("{}".format(personal_cloud))(hostname)

        self.monitor_state = "Unknown"
        self.traffic_monitor = None  # variable that holds the sniffer
        # instance a sniffer here

        # holds the rmq outgoing

    def emit(self, body=None):
        print "[Emit]: metric emission"
        self.sync_client.notify_status()


    def hello(self, body=None):
        #try:
        print "[Hello]: Hello World"

        body = {
            "msg": {
                "test": {
                    "testClient": "dropbox",
                },
                "dropbox-ip": "",
                "dropbox-port": ""
            }
        }

        self.sync_client.hello(body)
        return 0, "[Hello]: response"
        #    return 0  # successfully logged to personal cloud service
        # except Exception as ex:
        #     print ex.message
        #     print traceback.print_tb(None)
        #     return 1

    """
    RMQ request to start personal cloud client
    """
    def start(self, body=None):
        #try:

        body = {
            "msg": {
                "test": {
                    "testClient": "dropbox",
                },
                "dropbox-ip": "",
                "dropbox-port": ""
            }
        }

        self.monitor_state = "start_monitor"
        if not self.sync_client.is_monitor_capturing:  # if not capturing start otherwise noop
            self.sync_client.start(body)
        return 0, "[Start]: response"

    '''
    RMQ request to warmup the dummyhost=>[sandbox|benchbox]
    '''
    def warmup(self, body=None):
        body = {
            "msg": {
                "test": {
                    "testClient": "dropbox",
                },
                "dropbox-ip": "",
                "dropbox-port": ""
            }
        }

        self.monitor_state = "warmup_monitor"
        self.sync_client.warmup(body)
        return 0, "[Warmup]: response"

    '''
    RMQ request to stop personal cloud client
    '''
    def stop(self, body=None):

        body = {
            "msg": {
                "test": {
                    "testClient": "dropbox",
                },
                "dropbox-ip": "",
                "dropbox-port": ""
            }
        }

        self.monitor_state = "stop_monitor"
        if self.sync_client.is_monitor_capturing:  # if its capturing, stop it to capture
            self.sync_client.stop(body)
        # else:
        #     self.client.stop(body)  # remove this

        return 0, "[Stop]: response"

    '''
    RMQ request to display the executor status
    '''
    def keepalive(self, body=None):

        body = {
            "msg": {
                "test": {
                    "testClient": "dropbox",
                },
                "dropbox-ip": "",
                "dropbox-port": ""
            }
        }

        # self.monitor_state = ""
        return "{} -> {}".format(datetime.datetime.now().isoformat(), self.executor_state)