from capture import Capture


class OwnCloud(Capture):

    def __init__(self, hostname):

        super(self.__class__, self).__init__(hostname)
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files (x86)/ownCloud/owncloud.exe",
            self.proc_name = "owncloud.exe"
            self.sync_folder = ""
        else:
            self.pc_cmd = "/vagrant/owncloudsync.sh"
            self.proc_name = "owncloudsync"
            self.sync_folder = "owncloud_folder"

    def hello(self, body):
        print "{} say hello".format(self.whoami)
