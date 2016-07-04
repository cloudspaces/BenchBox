from target.sniff_box import Box as box
from target.sniff_dropbox import Dropbox as dropbox
from target.sniff_googledrive import GoogleDrive as googledrive
from target.sniff_owncloud import OwnCloud as ownloud
from target.sniff_stacksync import StackSync as stacksync
from threading import Thread
import psutil, os, time, sys, getopt

class Sniffer(Thread):

    def __init__(self, personal_cloud=None, config={}):
        super(Sniffer, self).__init__()
        print "constructor"
        self.target = None
        if personal_cloud is None:
            raise NotImplemented
        else:
            self.target = eval("{}".format(personal_cloud.lower()))(config)

    def run(self, interval=5):
        self.register = True
        return self.target.capture()

    def rage_quit(self):
        self.register = False
        parent_pid = os.getpid()
        print "Quiting"
        parent_process = psutil.Process(parent_pid)
        for child in parent_process.children(recursive=True):
            child.kill()
        self.target.capture_quit()
        # time.sleep(5)
        print "Quit parent.kill()"
        parent_process.kill()


        # print "Quited"

    def cancel(self):
        '''
        Cancels this thread class
        :return:
        '''
        self.cancelled = True

    def hello(self):
        #try:
        self.target.hello()
        return 0

    def notify_stats(self):
        return self.target.notify_stats()

def parseArgs(argv):
    personal_cloud = ''
    random_variable = ''
    try:
        opts, args = getopt.getopt(argv,"hc:x:",["pclient="])
        #opts, args = getopt.getopt(argv,"hc:x:",["pclient=","xrand="])
    except getopt.GetoptError:
        print 'test.py -c <personal_cloud> -x <random_variable>'
        # sys.exit(2)
        return None
    for opt, arg in opts:
        if opt == '-h':
            print 'test.py -c <personal_cloud> -x <random_variable>'
            sys.exit()
        elif opt in ("-c", "--pclient"):
            personal_cloud = arg
        elif opt in ("-x", "--xrand"):
            random_variable = arg
    print 'Personal_Cloud is %s ' % personal_cloud
    print 'Random_Variable is %s' % random_variable
    return personal_cloud



if __name__ == '__main__':

    # todo refactoring arguments?
    config_client = {
        "sync_server_ip": "stacksync.urv.cat",
        "sync_server_port": 8080,
        "packet_limit": -1,
        "max_bytes": 65535,
        "promiscuous": False,
        "read_timeout": 100
    }

    personal_cloud = parseArgs(sys.argv[1:])
    if personal_cloud is None:
        personal_cloud = "dropbox"

    tm = Sniffer(personal_cloud=personal_cloud, config=config_client)
    tm.run()
    # idx = 0
    while True:
        # idx += 1
        # print "Notify status... {}".format(idx)
        time.sleep(5)
        print tm.notify_stats()
    print "end"
