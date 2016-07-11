from capture import Capture


class StackSync(Capture):

    def __init__(self, hostname):

        super(self.__class__, self).__init__(hostname)
        self.whoami = (self).__class__.__name__
        print self.whoami

        if self.platform_is_windows:
            self.pc_cmd = "/Users/vagrant/AppData/Roaming/StackSync_client/Stacksync.jar",
            self.proc_name = "javaw.exe"
            self.sync_folder = "/Users/vagrant/stacksync_folder"
            self.sync_folder_cleanup = "/Users/vagrant/stacksync_folder/*"
        else:
            self.pc_cmd = "/usr/bin/stacksync"
            self.proc_name = "java"
            self.sync_folder = "stacksync_folder"
            self.sync_folder_cleanup = "/home/vagrant/stacksync_folder/*"


    def hello(self, body):
        print "{} say hello: {}".format(self.whoami, body)



    # def start(self):
    #     print "{} say start".format(self.whoami)
    #     # self.sync_client = None
    #     # self.monitor = None
    #
    # def stop(self):
    #     print "{} say stop".format(self.whoami)
    #     # self.sync_client = None
    #     # self.monitor = None


