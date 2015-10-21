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
from workload_generator.communication.actions import CreateFileOrDirectory, DeleteFileOrDirectory, MoveFileOrDirectory

from workload_generator.constants import DEBUG, FS_SNAPSHOT_PATH, STEREOTYPE_RECIPES_PATH


def process_opt():
    parser = ArgumentParser()

    parser.add_argument("-p", dest="profile", default=None, help="Option: profile sync|cdn|backup|idle|regular"
                                                               "example: ./executor.py -p sync")

    parser.add_argument("-o", dest="ops", default=10, help="Option: ops #"
                                                             "example: ./executor.py -o 5")

    parser.add_argument("-t", dest="itv", default=1, help="Option: itv #"
                                                             "example: ./executor.py -t 5")

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
        self.debug_mode = DEBUG
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
        
    def create_fs_snapshot_and_migrate_to_sandbox(self):
        '''Initialize the file system in addition to the models'''
        self.data_generator.create_file_system_snapshot()
        self.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        '''When the initial file system has been built, migrate it to the sandbox'''
        if not self.debug_mode:
            # self.data_generator.migrate_file_system_snapshot_to_sandbox("migrate location")
            action = MoveFileOrDirectory(FS_SNAPSHOT_PATH, '/')

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
        print "do update"
        synthetic_file_name = self.data_generator.create_file()
        print synthetic_file_name
        action = CreateFileOrDirectory(synthetic_file_name)
        print action
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'PutContentResponse')
        print to_wait
        action.perform_action(ftp_client)

    def doSync(self ):
        self.doPutContentResponse()

    def doUnlink(self):
        print "do delete"
        synthetic_file_name = None
        if random.random() > 0.25:        
            synthetic_file_name = self.data_generator.delete_file()
        else: synthetic_file_name = self.data_generator.delete_directory()
        action = DeleteFileOrDirectory(synthetic_file_name)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'Unlink')
        action.perform_action(ftp_client)

    #TODO: Needs implementation in data generator first
    def doMoveResponse(self):
        print "do move"
        #action = get_action(["MoveResponse", 'files', 'ReSampleMake.txt'], ftp_files)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'MoveResponse')
        #action.perform_action(ftp_client)

    #TODO: Let's see how we can solve this
    def doGetContentResponse(self):
        print "do download"
        #action = get_action(["GetContentResponse", 'sampleMake.txt', 'files/get/'], ftp_files)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.markov_current_state, 'GetContentResponse')
        #action.perform_action(ftp_client)


if __name__ == '__main__':

    # Root permissions are needed, and some checks to save existing files
    # if not os.geteuid() == 0:
    #     print "Only root can run this script"  # exit()
    # else:
    #     print 'Config/OK'


    # read hostname
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

    # print parser.options('executor')
    #log = logger(parser.get('executor', 'output') + os.sep + "metadata.log", dict(parser._sections['executor']) )
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


    stereotype_executor.create_fs_snapshot_and_migrate_to_sandbox()
    # stereotype_executor.doMakeResponse()
    stereotype_executor.doPutContentResponse()
    # read the line /vagrant/profile and use it

    if opt.profile is not None:
        profile_type = opt.profile
    else:
        with open('/vagrant/profile') as f:
            profile_type= f.read().split('\n')[0]
    #profile = '/home/vagrant/simulator/data/xl_markov_{}_all_ms.csv'.format(profile_type)




    stereotype_executor.markov_chain.calculate_chain_relative_probabilities()

    print 'IPTables/OK'
    # os.system('sudo ./pcb/scripts/firewall start')
    # os.system('sudo iptables -L')

    print 'FTP/OK'
    worker = None
    print "Start executing/****************************"
    # start monitoring
    #sandBoxSocketIpPort = '192.168.56.101',11000
    #monitor = CPUMonitor('192.168.56.101',11000)
    interval = int(opt.itv)
    log_filename = 'local.csv'
    proc_name = opt.pid # if its stacksync
    print interval
    #monitor.start_monitor(interval, log_filename, proc_name, opt.ops, opt.profile, hostname)
    #  operations = 100
    #  operations = 10000
    for i in range(operations):
        # stereotype_executor.execute(sender, parser.get('executor','files_folder'))
        stereotype_executor.execute()
    # stop monitoring
    #monitor.stop_monitor()
    print "Finish executing/****************************"

    print "ClearingProcess/..."


    MoveFileOrDirectory('../output','/').perform_action(ftp_client)


    if ftp_client:
        print "close sender"
        ftp_client.close()
    #os.system('sudo ./pcb/scripts/firewall stop')

    print "ClearingProcess/OK"
