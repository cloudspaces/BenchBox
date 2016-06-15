from threading import Thread
from constants import STEREOTYPE_RECIPES_PATH, FS_SNAPSHOT_PATH
from executor import StereotypeExecutorU1
import datetime
from termcolor import colored
import os
import time

class Commands(object):

    # singleton class
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Commands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, receipt):
        print '[INIT_EXECUTOR_RMQ]: rpc commands'
        self.is_warmup = False
        self.is_running = False
        self.sync_directory = None  # stacksync_folder, Dropbox, ....
        self.stereotype = receipt  # backupsample
        self.stereotype_executor = StereotypeExecutorU1()

        self.monitor_state = "Unknown"

        # update ftp_root_directory

        self.fs_abs_target_folder = None
        self.execute = None

        # self.data_generator = DataGenerator()

        # start the monitoring stuff. # todo
        # send to impala always...!!!
        # sshpass -p vagrant rsync -rvnc --delete ../output/ vagrant@192.168.56.101:stacksync_folder/

    def hello(self, body):
        print '[HELLO]: hello world {}'.format(body['cmd'])
        return '[HELLO]: hello world response'

    def warmup(self, body):
        print '[WARMUP]: {} '.format(body)
        print FS_SNAPSHOT_PATH
        print STEREOTYPE_RECIPES_PATH

        print '[WARMUP]: init_stereotype_from_recipe'
        if self.is_warmup is False:
            self.sync_directory = body['msg']['test']['testFolder']
            self.stereotype_executor.initialize_ftp_client_by_directory(root_dir=self.sync_directory)
            if os.name == "nt":
                self.fs_abs_target_folder = '/Users/vagrant/{}'.format(self.sync_directory)  # target ftp_client dir absolute path
            elif os.name == "posix":
                self.fs_abs_target_folder = '/home/vagrant/{}'.format(self.sync_directory)  # target ftp_client dir absolute path
            self.stereotype = body['msg']['test']['testProfile']  # add benchbox switch stereotype profile at warmup
            receipt = STEREOTYPE_RECIPES_PATH + self.stereotype
            print receipt
            self.stereotype_executor.initialize_from_stereotype_recipe(receipt)
            print '[WARMUP]: init fs & migrate to sandbox'
            # always
            self.stereotype_executor.create_fs_snapshot_and_migrate_to_sandbox()
            self.is_warmup = True
            self.monitor_state = "executor Warmup Done!"
        else:
            print '[WARMUP]: already warmed-up'
        return '[WARMUP]: warm up response'

    def _test(self):
        '''
        Aixo ha d'executarse en un thread com a bucle infinit
        :return:
        '''
        print '[TEST]: run'
        if self.is_warmup:
            print '[TEST]: run test'
            self.is_running = True
            self.stereotype_executor.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
            # TODO loop
            operations = 0
            while self.is_running:
                operations += 1  # executant de forma indefinida...
                self.stereotype_executor.execute()
                # time.sleep(3)
                print colored("[TEST]: INFO {} --> {} // {} // {} ".format(time.ctime(time.time()), operations, self.is_running, self.sync_directory), 'red')

        else:
            print '[TEST]: WARNING: need warmup 1st!'

    def start(self, body):
        print '[START_TEST]: {}'.format(body)
        if not self.is_warmup:
            return '[START_TEST]: WARNING: require warmup!'

        if self.is_running:
            return '[START_TEST]: INFO: already running!'
        else:
            # SELF THREAD START
            print '[START_TEST]: INFO: instance thread'
            self.execute = Thread(target=self._test)
            self.execute.start()
            self.monitor_state = "executor Running!"
            return '[START_TEST]: SUCCESS: run test response'

    def stop(self, body):
        if self.is_running:
            print '[STOP_TEST]: stop test {}'.format(body)
            self.is_running = False
            self.is_warmup = False
            self.execute.join()
            self.monitor_state = "executor Stopped!"
            return '[STOP_TEST]: SUCCESS: stop test'
        else:
            return '[STOP_TEST]: WARNING: no test is running'

    def keepalive(self, body):
        return "{} -> {}".format(datetime.datetime.now().isoformat(), self.monitor_state)

