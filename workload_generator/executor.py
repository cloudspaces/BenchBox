#!/usr/bin/python
'''
Created on 30/6/2015

@author: Raul
'''
from ConfigParser import SafeConfigParser
from argparse import ArgumentParser

import os, sys
import random
import time
import getpass
from termcolor import colored
from metrics.cpu_monitor import CPUMonitor


'''
HardCode path for each environment, should be dev, debug, production instead...
'''
curr_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = os.path.expanduser("~")
hard_dir = '/home/anna/CloudSpaces/Dev/BenchBox'
print curr_dir
print home_dir
print hard_dir

username = getpass.getuser()

dev_dir = {
    'anna': hard_dir,
    'vagrant': home_dir,
    'milax': curr_dir
}

sys.path.append(dev_dir[username])



from workload_generator.model.user_activity.markov_chain import SimpleMarkovChain
from workload_generator.model.user_activity.inter_arrivals_manager import InterArrivalsManager
from workload_generator.model.data_layer.data_generator import DataGenerator

from workload_generator.communication.ftp_sender import ftp_sender
from workload_generator.communication.actions import CreateFileOrDirectory, UpdateFile, DeleteFileOrDirectory, MoveFileOrDirectory

from workload_generator.constants import DEBUG, FS_SNAPSHOT_PATH, STEREOTYPE_RECIPES_PATH


def process_opt():
    parser = ArgumentParser()

    parser.add_argument("-p", dest="profile", default=None, help="Option: profile sync|cdn|backup|idle|regular"
                                                               "example: ./executor.py -p sync")

    parser.add_argument("-o", dest="ops", default=10, help="Option: ops #"
                                                             "example: ./executor.py -o 5")

    parser.add_argument("-t", dest="itv", default=1, help="Option: itv #"
                                                             "example: ./executor.py -t 5")

    parser.add_argument("-w", dest="warmup", default=0, help="Option: warmup #"
                                                             "example: ./executor.py -w 1")

    parser.add_argument("-f", dest="folder", default='stacksync_folder', help="Option: ftp folder, folder owncloud_folder|stacksync_folder "
                                                          "example: ./executor.py -f owncloud_folder")

    parser.add_argument("-x", dest="pid", default='StackSync', help="Option: ProcedureName, "
                                                                              "pid StackSync|OwnCloud "
                                                                              "example: ./executor.py -x OwnCloud")

    parser.add_argument("--out", dest="output", default='output', help="Folder for output files")
    opt = parser.parse_args()

    if not opt.itv:
        parser.print_help()
        print 'Example: ./executor.py -o 100 -p sync -t 1 -f owncloud_folder -x OwnCloud'
        sys.exit(1)

    opt = parser.parse_args()

    print opt.profile
    print opt.ops
    print opt.itv

    return opt




class StereotypeExecutor(object):

    def __init__(self):
        self.markov_chain = SimpleMarkovChain()
        self.markov_current_state = 'PutContentResponse' # there should be an initial state @ can be random
        self.inter_arrivals_manager = InterArrivalsManager()
        self.data_generator = DataGenerator()

    def initialize_from_stereotype_recipe(self, stereotype_recipe):
        '''Initialize the Markov Chain states'''
        self.markov_chain.initialize_from_recipe(stereotype_recipe)
        self.markov_chain.calculate_chain_relative_probabilities()
        '''Initialize the inter-arrival times'''
        self.inter_arrivals_manager.initialize_from_recipe(stereotype_recipe)
        '''Initialize data generation layer'''
        self.data_generator.initialize_from_recipe(stereotype_recipe)

    def get_waiting_time(self):
        return self.inter_arrivals_manager.get_waiting_time(self.markov_chain.previous_state,
                                                            self.markov_chain.current_state)
    '''Get the next operation to be done'''
    def next_operation(self):
        self.markov_chain.next_step_in_random_navigation()

    '''Do an execution step as a client'''
    def execute(self):
        raise NotImplemented
    
'''Dummy class to emulate the calls of the real one, for simulation purposes'''
class SimulatedStereotypeExecutorU1(StereotypeExecutor):
    
    '''Do an execution step as a client'''
    def execute(self):    
        to_execute = getattr(self, 'do' + self.markov_chain.current_state)
        to_execute()

    '''Operations that should connect to the Cristian's Benchmarking Framework'''        
    def doMakeResponse(self):
        '''Get the time to wait for this transition in millis'''
        
    def doPutContentResponse(self):
        '''Get the time to wait for this transition in millis'''
        
    def doSync(self):
        self.doPutContentResponse()
        
    def doUnlink(self):
        '''Get the time to wait for this transition in millis'''
        
    def doMoveResponse(self):
        '''Get the time to wait for this transition in millis'''
        
    def doGetContentResponse(self):
        '''Get the time to wait for this transition in millis'''

'''Class that executes remote operations on the Sandbox based on the
data generation and user activity models. The class is tailored for the
available information in the UbuntuOne (U1) trace.'''
class StereotypeExecutorU1(StereotypeExecutor):

    def __init__(self, ftp_client):
        StereotypeExecutor.__init__(self)
        self.ftp_client = ftp_client


    def initialize_from_stereotype_recipe(self, stereotype_recipe):
        StereotypeExecutor.initialize_from_stereotype_recipe(self, stereotype_recipe)
        
    def create_fs_snapshot_and_migrate_to_sandbox(self, ftp_client):
        '''Initialize the file system in addition to the models'''
        self.data_generator.create_file_system_snapshot()
        self.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        '''When the initial file system has been built, migrate it to the sandbox'''
        if not DEBUG:
            # self.data_generator.migrate_file_system_snapshot_to_sandbox("migrate location")
            action = MoveFileOrDirectory(FS_SNAPSHOT_PATH, FS_SNAPSHOT_PATH)
            action.perform_action(ftp_client)
            print "MoveFileOrDirectory/to/SandBox/DONE"
    '''Do an execution step as a client'''
    def execute(self):
        '''Get the next operation to be done'''
        self.markov_chain.next_step_in_random_navigation()
        to_execute = getattr(self, 'do' + self.markov_chain.current_state)
        to_execute()

    """
    def doMakeResponse(self):
        print "do create" 
        #TODO: We have to define the operations correctly, because we cannot distinguish
        #between creating/deleting/moving files and directories
        synthetic_file_name = None
        if random.random() > 0.25:        
            synthetic_file_name = self.data_generator.create_file()
        else: synthetic_file_name = self.data_generator.create_directory()
        action = CreateFileOrDirectory(synthetic_file_name)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'MakeResponse')
        action.perform_action(ftp_client)
    """
    
    def doPutContentResponse(self):
        print colored("doPutContentResponse",'cyan')
        synthetic_file_name = self.data_generator.create_file()
        print "{} :>>> NEW ".format(synthetic_file_name)
        action = CreateFileOrDirectory(synthetic_file_name, FS_SNAPSHOT_PATH)
        print "{} :>>> ACTION".format(action)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'PutContentResponse')
        to_wait = random.randint(1, 10)
        print "Wait: {}s".format(to_wait)
        time.sleep(to_wait)
        action.perform_action(ftp_client)

    def doSync(self):
        # TODO: Cheng, you can make use of data_generator.update() to test updating files
        # self.doPutContentResponse()
        print colored("doSync",'green')
        synthetic_file_name = self.data_generator.update_file()
        print synthetic_file_name
        if synthetic_file_name is None:
            print "no file selected!"
        else:
            action = UpdateFile(synthetic_file_name,FS_SNAPSHOT_PATH)
            #to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'Sync')
            to_wait = random.randint(1, 10)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)

            action.perform_action(ftp_client)

    def doUnlink(self):
        print colored("doUnlink",'yellow')
        synthetic_file_name = None
        #if random.random() > 0.25:
        #    synthetic_file_name = self.data_generator.delete_file()
        #else:
        synthetic_file_name = self.data_generator.delete_directory()
        if synthetic_file_name:
            action = DeleteFileOrDirectory(synthetic_file_name, FS_SNAPSHOT_PATH)
            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'Unlink')
            to_wait = random.randint(1, 10)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(ftp_client)
        else:
            print "No file selected!"

    #TODO: Needs implementation in data generator first
    def doMoveResponse(self):
        print colored("doMoveResponse",'magenta')
        #if random.random() > 0.25:
         #   synthetic_file_name = self.data_generator.move_file()
        #else:
        synthetic_file_name = self.data_generator.move_directory()
        print synthetic_file_name
        (src_mov, tgt_mov) = synthetic_file_name
        if src_mov:
            action = MoveFileOrDirectory(src_mov, FS_SNAPSHOT_PATH, tgt_mov)
            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'MoveResponse')
            to_wait = random.randint(1, 10)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(ftp_client)
        else:
            print "No file selected!"

    #TODO: Let's see how we can solve this
    def doGetContentResponse(self):
        print colored("doGetContentResponse",'blue')

        #action = get_action(["GetContentResponse", 'sampleMake.txt', 'files/get/'], ftp_files)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'GetContentResponse')
        to_wait = random.randint(1, 10)
        print "Wait: {}s".format(to_wait)
        #action.perform_action(ftp_client)


if __name__ == '__main__':


    hostname = None
    try:
        f = open('/vagrant/hostname', 'r')
        hostname = f.read().splitlines()[0]
    except Exception as ex:
        print ex


    opt = process_opt()
    operations = int(opt.ops)


    parser = SafeConfigParser()


    parser.read('./config.ini')
    print parser.get('executor', 'interface')   # eth0
    print parser.get('executor', 'ftp')         # 192.168.56.2
    print parser.get('executor', 'port')        # 21
    print parser.get('executor', 'user')        # cotes -> vagrant
    print parser.get('executor', 'passwd')      # lab144 -> vagrant

    print 'Logger/OK'
    # log experiment metadata

    print parser.options('executor')
    # log = logger(parser.get('executor', 'output') + os.sep + "metadata.log", dict(parser._sections['executor']) )
    ftp_client = ftp_sender(parser.get('executor','ftp'),
                        parser.get('executor','port'),
                        parser.get('executor','user'),
                        parser.get('executor','passwd'),
                        opt.folder)
    # parser.get('executor','folder')) # root path ftp_client directory :: ~/stacksync_folder
    # ftp_files = parser.get('executor','files_folder') # relative path to local files :: ./files/demoFiles.txt
    print 'Markov/OK'
    stereotype_executor = StereotypeExecutorU1(ftp_client)

    receipt = STEREOTYPE_RECIPES_PATH + opt.profile
    print receipt
    stereotype_executor.markov_chain.initialize_from_recipe(receipt)
    stereotype_executor.data_generator.initialize_from_recipe(receipt)
    stereotype_executor.inter_arrivals_manager.initialize_from_recipe(receipt)


    print "Syntetic File System Path:".format(FS_SNAPSHOT_PATH)
    if opt.warmup is not 0:
        print "only warming up"
        stereotype_executor.create_fs_snapshot_and_migrate_to_sandbox(ftp_client)
    else:
        stereotype_executor.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)

        if opt.profile is not None:
            profile_type = opt.profile
        else:
            with open('/vagrant/profile') as f:
                profile_type = f.read().split('\n')[0]

        stereotype_executor.markov_chain.calculate_chain_relative_probabilities()

        print 'FTP/OK'
        worker = None
        print "Start executing/****************************"
        try:
            monitor = CPUMonitor('192.168.56.101',11000)
            interval = int(opt.itv)
            log_filename = 'local.csv'
            proc_name = opt.pid  # if its stacksync
            print interval
            monitor.start_monitor(interval, log_filename, proc_name, opt.ops, opt.profile, hostname)
        except:
            print "Could not connect to SocketListener at sandBox".format(Exception)

        #  operations = 100
        for i in range(operations):
        # stereotype_executor.execute(sender, parser.get('executor','files_folder'))
            stereotype_executor.execute()
            print colored("doOps {}/{}".format(i, operations),'red')
            # stop monitoring

        if monitor:
            monitor.stop_monitor()
        print "Finish executing/****************************"


        """
        print "Test do operations"
        loops = 10
        for ops in range(loops):
            print "loop {}/{}".format(ops, loops)
            stereotype_executor.doMoveResponse()
            stereotype_executor.doSync()
            stereotype_executor.doPutContentResponse()
            stereotype_executor.doSync()
            '''
            stereotype_executor.doPutContentResponse()
            stereotype_executor.doSync()
            stereotype_executor.doUnlink()
            stereotype_executor.doMoveResponse()
            stereotype_executor.doPutContentResponse()
            '''
        print "Test do operations/DONE"

        print "ClearingProcess/..."
        """
        # WarmUp move the output directory to the target


    if ftp_client:
        print "close ftp_client"
        ftp_client.close()

    print "ClearingProcess/OK"
