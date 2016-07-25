from capture import Capture


class GoogleDrive(Capture):

    def __init__(self, hostname):

        super(self.__class__, self).__init__(hostname)
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files (x86)/Google/Drive/googledrivesync.exe",
            self.proc_name = "googledrivesync.exe"
            self.sync_folder = "/Users/vagrant/Google Drive"
            self.sync_folder_cleanup = "/Users/vagrant/Google Drive/*"
        else:
            self.pc_cmd = ""
            self.proc_name = ""
            self.sync_folder = ""

    def hello(self):
        print "{} say hello".format(self.whoami)

