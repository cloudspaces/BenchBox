import os
import time
import subprocess
import signal
from threading import Thread
import datetime
import psutil
from termcolor import colored
from rmq_monitor.EmitMetric import EmitMetric


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
                personal_cloud=self.personal_cloud,
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
            'dropbox': "/home/vagrant/.dropbox-dist/dropboxd",  # launch dropbox
            'mega': "/vagrant/megasync.sh"
        }
        str_cmd = pc_cmd[self.personal_cloud.lower()]

        pc_pid = {
            'stacksync': "java",
            'owncloud': "owncloudsync",
            'dropbox': "dropbox",
            'mega': "megasync"
        }
        proc_name = pc_pid[self.personal_cloud.lower()]  # get the process name to be tracked

        while self.is_running:
            # check if client is running
            time.sleep(5)
            if self.client_running is False:
                # call client && update pid
                while self.client_running is False:
                    self.sync_proc = subprocess.Popen(str_cmd, shell=True)
                    time.sleep(3)
                    try:
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
                            for proc in psutil.process_iter():
                                if proc.name() == proc_name:
                                    self.client_running = True
                                    self.sync_proc_pid = proc.pid
                                    break
                            psutil.Process(self.sync_proc_pid)
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
            self.stereotype     = body['msg']['test']['testProfile']  # if its defined then this will be loaded
            print '[START_TEST]: INFO: instance thread'
            self.sync_client = Thread(target=self._pc_client)
            self.sync_client.start()
            # self.sync_client.start()
            self.monitor = Thread(target=self._test)
            self.monitor.start()
            return '[START_TEST]: SUCCESS: run test response'

    def stop(self, body):
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
            pc_cmd = {
                'stacksync': "java",
                'owncloud': "owncloudsync.sh",
                'dropbox': "dropbox",
                'mega': "megasync.sh"
            }
            str_cmd = pc_cmd[self.personal_cloud.lower()]
            pstring = str_cmd
            for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
                fields = line.split()
                proc_pid = fields[0]
                os.kill(int(proc_pid), signal.SIGKILL)
            return '[STOP_TEST]: WARNING: no test is running'

    def keepalive(self, body):
        return "{} -> {}".format(datetime.datetime.now().isoformat(), self.executor_state)
