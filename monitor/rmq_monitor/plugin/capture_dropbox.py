from capture import Capture
import pwd

class Dropbox(Capture):

    def __init__(self, hostname):

        super(self.__class__, self).__init__(hostname)
        self.whoami = (self).__class__.__name__
        print self.whoami
        if self.platform_is_windows:
            self.pc_cmd = "/Program Files (x86)/Dropbox/Client/Dropbox.exe",
            self.proc_name = "Dropbox.exe"
            self.sync_folder = "/Users/vagrant/Dropbox"
            self.sync_folder_cleanup = "/Users/vagrant/Dropbox/*"

        else:
            # self.pc_cmd = "sudo -H -u {} bash -c '/usr/bin/dropbox start'".format('vagrant')
            session_user = "vagrant"
            self.pc_cmd = "sudo -H -u {} bash -c '/usr/local/bin/dropbox start'".format(session_user)
            try:
                if pwd.getpwnam("milax").pw_uid == 1000:
                    session_user = "milax"
                    self.pc_cmd = "sudo -H -u {} bash -c '/usr/bin/dropbox start'".format(session_user)
            except KeyError:
                pass
            # self.pc_cmd = "sudo -H -u vagrant bash -c '/usr/local/bin/dropbox start'"
            self.proc_name = "dropbox"
            self.sync_folder = "Dropbox"
            self.sync_folder_cleanup = "/home/vagrant/Dropbox/*"

    def hello(self, body):
        print "{} say hello {}".format(self.whoami, body)




