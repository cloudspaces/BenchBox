from capture import Capture


class Box(Capture):

    def __init__(self, hostname):

        super(self.__class__, self).__init__(hostname)
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files/Box/Box Sync/BoxSync.exe",
            self.proc_name = "BoxSync.exe"
            self.sync_folder = "/Users/vagrant/Box Sync"
            self.sync_folder_cleanup = "/Users/vagrant/Box Sync/*"
        else:
            self.pc_cmd = ""
            self.proc_name = ""
            self.sync_folder = ""
            self.sync_folder_cleanup = ""

    def hello(self, body):
        print "{} say hello".format(self.whoami, body)

