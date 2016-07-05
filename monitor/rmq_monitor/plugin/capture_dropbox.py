from capture import Capture


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
            self.pc_cmd = "sudo -H -u {} bash -c '/usr/bin/dropbox start'".format('milax')
            # self.pc_cmd = "sudo -H -u vagrant bash -c '/usr/local/bin/dropbox start'"
            self.proc_name = "dropbox"
            self.sync_folder = "Dropbox"
            self.sync_folder_cleanup = "/home/vagrant/Dropbox/*"


    def hello(self, body):
        print "{} say hello".format(self.whoami)

    # def start(self, body):
    #
    #     self.personal_cloud = body['msg']['test']['testClient']
    #     self.personal_cloud_ip = body['msg']['{}-ip'.format(self.personal_cloud.lower())]
    #     self.personal_cloud_port = body['msg']['{}-port'.format(self.personal_cloud.lower())]
    #
    #     print "{} say start".format(self.whoami)
    #     # self.sync_client = None
    #     # self.monitor = None
    #
    # def stop(self, body):
    #     print "{} say stop".format(self.whoami)
    #     # self.sync_client = None
    #     # self.monitor = None



