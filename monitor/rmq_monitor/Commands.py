import os
import time
import subprocess
import signal
from threading import Thread
import datetime
import psutil
from termcolor import colored
from rmq_monitor.EmitMetric import EmitMetric
import glob
import shutil


class Commands(object):
    # singleton class
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Commands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, hostname):
        """
        This script contains the thread operations of a monitor process contained in the sandBox.
        :param hostname: Name of the current dummy host
        :return:
        """
        print '[INIT_MONITOR_RMQ]: rpc commands'
        self.hostname = hostname
        self.is_running = False     # state flag
        self.client_running = False
        self.stereotype = None      # backupsample
        self.monitor = None         # monitor_process => experimento
        self.sync_client = None     # sync_client process
        self.sync_proc_pid = None   # GATHER THE SYNC PID FROM SYNC PROC, actively updated by _pc_client
        self.sync_proc = None
        self.personal_cloud = None  # personal cloud
        self.personal_cloud_ip = None
        self.personal_cloud_port = None
        self.executor_state = "Unknown"  # state +  time

    def hello(self, body):
        print '[HELLO]: hello world {}'.format(body['cmd'])
        return '[HELLO]: hello world response'

    def warmup(self, body):
        """
        This stage can be avoided, todo refactor this into start&stop
        where start will automatically manage
        - the syncronization client state [it periodically checks if the client is running]
        - the syncronization client to use [it actively swaps between sincronization client]
        :param body: contains the configuration and settings emited by the manager node
        :return:
        """
        print '[WARMUP]: init personal cloud client'
        return '[WARMUP]: warm up response'

    def _test(self):
        '''
        Aixo ha d'executarse en un thread com a bucle infinit
        :return:
        '''
        operations = 0
        metric_reader = EmitMetric(
                hostname=self.hostname,
                personal_cloud={
                    "name": self.personal_cloud,
                    "ip": self.personal_cloud_ip,
                    "port": self.personal_cloud_port
                },
                receipt=self.stereotype)

        # define metric reader with [hostname & sync client name]
        while self.is_running:
            operations += 1
            self.client_running = metric_reader.emit(self.sync_proc_pid)  # send metric to rabbit
            time.sleep(2)  # delay between metric
            print colored("[TEST]: INFO {} --> {} // {} //"
                          "".format(time.ctime(time.time()), operations, self.is_running), 'red')
        print "QUIT emit metrics!!!"


    def _pc_client(self):
        """
        This thread will get track the personal client process id, and actively
        keep the pc client running {self.sync_proc_pid}
        :return:
        """

        pc_cmd = {
            #'stacksync': "/usr/bin/java -jar /usr/lib/stacksync/Stacksync.jar -d -c /vagrant",
            # owncloudcmd --httpproxy http://10.30.232.183 -u demo10 -p demo10 /home/vagrant/owncloud_folder/ http://10.30.232.183
            'stacksync': "/usr/bin/stacksync",
            'owncloud': "/vagrant/owncloudsync.sh",
            # 'dropbox': "/home/vagrant/.dropbox-dist/dropboxd",  # launch dropbox
            'dropbox': "sudo -H -u vagrant bash -c '/usr/local/bin/dropbox start'",  # launch dropbox
            'mega': "/vagrant/megasync.sh"
        }

        pc_cmd_win = {
            #'dropbox': " subprocess.call(['C:\Program Files (x86)\Dropbox\Client\Dropbox.exe'])"
            'dropbox': "/Program Files (x86)/Dropbox/Client/Dropbox.exe",
            'mega': "/Users/vagrant/AppData/Local/MEGAsync/MEGAsync.exe",
            'stacksync': "/Users/vagrant/AppData/Roaming/StackSync_client/Stacksync.jar",
            'sugarsync': "/Program Files (x86)/SugarSync/SugarSync.exe",
            'owncloud': "/Program Files (x86)/ownCloud/owncloud.exe",
            'googledrive': "/Program Files (x86)/Google/Drive/googledrivesync.exe",

        }

        if os.name == "nt":
            str_cmd = pc_cmd_win[self.personal_cloud.lower()]
        elif os.name == "posix":
            str_cmd = pc_cmd[self.personal_cloud.lower()]
        else:
            # unimplemented operating system
            return None

        print "TARGET: client == {}".format(str_cmd)
        pc_pid = {
            'stacksync': "java",
            'owncloud': "owncloudsync",
            'dropbox': "dropbox",
            'mega': "megasync"
        }
        pc_pid_win = {
            #'dropbox': " subprocess.call(['C:\Program Files (x86)\Dropbox\Client\Dropbox.exe'])"
            'dropbox': "Dropbox.exe",
            'mega': "MEGAsync.exe",
            'stacksync': "javaw.exe",
            'sugarsync': "SugarSync.exe",
            'owncloud': "owncloud.exe",
            'googledrive': "googledrivesync.exe",

        }

        if os.name == "nt":
            proc_name = pc_pid_win[self.personal_cloud.lower()]
        elif os.name == "posix":
            proc_name = pc_pid[self.personal_cloud.lower()]  # get the process name to be tracked
        else:
            return None
        while self.is_running:
            # check if client is running
            time.sleep(5)
            if self.client_running is False:
                # call client && update pid
                try_start = 10
                while self.client_running is False:
                    self.sync_proc = subprocess.Popen(str_cmd, shell=True)
                    try_start-=1
                    if try_start == 0:
                        print "Unable to start {}".format(self.personal_cloud)
                        break
                    time.sleep(3)
                    try: # pid lookup
                        if os.name == "nt":
                            # each case handle
                            print "Monitoring windows client"
                            print self.sync_proc
                            is_running = False
                            client_pid = None
                            for proc in psutil.process_iter():
                                if proc.name() == proc_name:
                                    is_running = True
                                    client_pid = proc.pid
                                    break
                            if is_running:
                                self.client_running = True
                                self.sync_proc_pid = client_pid
                                print "Process running as {}".format(self.sync_proc_pid)
                            else:
                                print "Process idle"

                        elif os.name == "posix":
                            if proc_name == "owncloudsync":
                                self.client_running = True
                                self.sync_proc_pid = psutil.Process(self.sync_proc.pid).children()[0].pid
                                # cojer el pid del script
                                # elif proc_name == "boxsync":
                                # psutil.Process(self.sync_proc_pid).children()[0].children()[0]
                                # el primer children es el script
                                # el segundo children corresponde lo que hay en el bucle infinito del script
                                # sleep/owncloudcmd
                            elif proc_name == "megasync":
                                self.client_running = True
                                self.sync_proc_pid = psutil.Process(self.sync_proc.pid).children()[0].pid
                            else:
                                # en caso de dropbox y stacksync van aqui dentro. # quizas es porque los han arrancado con interfaz visual i no xuta nada...
                                for proc in psutil.process_iter():
                                    if proc.name() == proc_name:
                                        self.client_running = True
                                        self.sync_proc_pid = proc.pid
                                        break
                        ps_client = psutil.Process(self.sync_proc_pid)
                        print "[INFO]: {} => {}".format(ps_client.pid, ps_client.name())
                    except Exception as ex:
                        print ex.message
                        print "couldn't load the pc"
            # every 5 seconds checks if the target personal cloud client is running

    def start(self, body):
        """
        Start sending metrics
        :param body:
        :return:
        """
        print '[START_TEST] {}'.format(body)

        if self.is_running:
            return '[START_TEST]: INFO: already running!'
        else:
            self.is_running = True
            # SELF THREAD START
            self.personal_cloud = body['msg']['test']['testClient']
            try:
                self.personal_cloud_ip = body['msg']['{}-ip'.format(self.personal_cloud.lower())]
                self.personal_cloud_port = body['msg']['{}-port'.format(self.personal_cloud.lower())]
            except:
                print "Its not private cloud"
            self.stereotype = body['msg']['test']['testProfile']  # if its defined then this will be loaded
            print '[START_TEST]: INFO: instance thread'
            self.sync_client = Thread(target=self._pc_client)
            self.sync_client.start()
            # self.sync_client.start()
            self.monitor = Thread(target=self._test)
            self.monitor.start()
            return '[START_TEST]: SUCCESS: run test response'

    def stop(self, body):
        # clear the shared folder content and wait
        print "clear the content of all the shared folders and wait"
        self.personal_cloud = body['msg']['test']['testClient']
        try:
            self.personal_cloud_ip = body['msg']['{}-ip'.format(self.personal_cloud.lower())]
            self.personal_cloud_port = body['msg']['{}-port'.format(self.personal_cloud.lower())]
        except KeyError:
            print "[INFO] Its a public cloud, none ip:port available"
        if os.name == "nt":
            "This is windows, remove the content of windows shared folder"
            remove_inner_path('/Users/vagrant/OneDrive/*')
            remove_inner_path('/Users/vagrant/stacksync_folder/*')

            #time.sleep(10)

        elif os.name == "posix":
            remove_inner_path('/home/vagrant/Dropbox/*')
            remove_inner_path('/home/vagrant/stacksync_folder/*')

            #time.sleep(10)

        if self.is_running:
            print '[STOP_TEST]: stop test {}'.format(body)
            self.is_running = False
            self.sync_proc_pid = None
            self.sync_proc = None
            self.monitor.join()
            self.sync_client.join()
            """
            parent = psutil.Process(self.sync_proc_pid)
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                print child.kill()
            print parent.kill()
            """
            self.executor_state = "monitor stop Capturing... "
            return '[STOP_TEST]: SUCCESS: stop test'

        else:


            if os.name == "posix":
                pc_cmd = {
                    'stacksync': "java",
                    'owncloud': "owncloudsync.sh",
                    'dropbox': "dropbox",
                    'mega': "megasync.sh"
                }
                print "this is posix: {}".format(self.personal_cloud)

                str_cmd = pc_cmd[self.personal_cloud.lower()]
                pstring = str_cmd
                for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
                    fields = line.split()
                    proc_pid = fields[0]
                    os.kill(int(proc_pid), signal.SIGKILL)
                return '[STOP_TEST]: WARNING: no test is running'



            elif os.name == "nt":

                print "this is nt: {}".format(self.personal_cloud)
                print "check for process is running in windows... {}".format(self.personal_cloud.lower())
                pc_cmd = {
                    'box': "BoxSync",
                    'stacksync': "javaw.exe",
                    'owncloud': "owncloud.exe",
                    'sugarsync': "SugarSync.exe",
                    'dropbox': "Dropbox.exe",
                    'mega': "MEGAsync.exe",
                    'googledrive': "googledrivesync.exe",
                    'amazondrive': "AmazonDrive.exe",
                }
                was_running = 0
                for proc in psutil.process_iter():
                    if proc.name() == pc_cmd[self.personal_cloud.lower()]:
                        was_running+=1
                        # proc.terminate() # kill()
                        proc.kill() # ProcessTerminate in windows => asinc
                print "Running Process Cleaned: {}".format(was_running)

    def keepalive(self, body):
        return "{} -> {}".format(datetime.datetime.now().isoformat(), self.executor_state)


def remove_inner_path(path):
    files = glob.glob(path)
    try:
        for f in files:
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.remove(f)
    except Exception as ex:
        print ex.message

