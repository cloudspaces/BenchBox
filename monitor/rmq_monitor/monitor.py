import datetime
from plugin.capture_box import Box as box
from plugin.capture_dropbox import Dropbox as dropbox
from plugin.capture_googledrive import GoogleDrive as googledrive
from plugin.capture_owncloud import OwnCloud as ownloud
from plugin.capture_stacksync import StackSync as stacksync
import psutil

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
        print "constructor: {}[{}]".format(hostname, personal_cloud)
        self.test_id = None
        self.hostname = hostname
        self.sync_client = None
        print personal_cloud
        if personal_cloud is None:
            # raise NotImplemented
            pass
        else:
            self.sync_client = eval("{}".format(personal_cloud.lower()))(hostname)

        self.monitor_state = "Unknown"
        self.traffic_monitor = None  # variable that holds the sniffer
        # instance a sniffer here

        # holds the rmq outgoing

    def emit(self, body=None):
        print "[Emit]: metric emission"
        personal_cloud = body['msg']['test']['testClient']
        if personal_cloud is None:
            # raise NotImplemented
            return 0 # if no personal cloud is forwarded
        elif self.sync_client is None:
            self.sync_client = eval("{}".format(personal_cloud))(self.hostname)
        else:
            return 0
        self.sync_client.notify_status()


    def hello(self, body=None):
        #try:
        print "[Hello]: Hello World"
        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }
        self._sync_client_selector(request=body)
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
        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                        "testProfile": "sync-occasional"
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }

        self._sync_client_selector(request=body)
        self.monitor_state = "start_monitor"
        result = None
        if not self.sync_client.is_monitor_capturing:  # if not capturing start otherwise noop
            result = self.sync_client.start(body)
        return 0, "[Start]: response {}".format(result)

    '''
    RMQ request to warmup the dummyhost=>[sandbox|benchbox]
    '''
    def warmup(self, body=None):

        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }
        self._sync_client_selector(request=body)
        self.monitor_state = "warmup_monitor"
        self.sync_client.warmup(body)
        return 0, "[Warmup]: response"

    '''
    RMQ request to stop personal cloud client
    '''
    def stop(self, body=None):

        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }

        print body
        self._sync_client_selector(request=body)
        self.monitor_state = "stop_monitor"
        result = None
        if self.sync_client.is_monitor_capturing:  # if its capturing, stop it to capture
            result = self.sync_client.stop(body)
        # else:
        #     self.client.stop(body)  # remove this

        return 0, "[Stop]: response {}".format(result)

    '''
    RMQ request to display the executor status
    '''
    def keepalive(self, body=None):
        if body is None:
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

    def exit(self):
        exit(0)

    """
    Personal Cloud
    """
    def _sync_client_selector(self, request=None):
        personal_cloud = request['msg']['test']['testClient']
        if self.sync_client is None:
                self.sync_client = eval("{}".format(personal_cloud.lower()))(self.hostname)
        #     # raise NotImplemented
        #     return 0  # if no personal cloud is forwarded
        #