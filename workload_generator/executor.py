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
from workload_generator.model.user_activity.stereotype_executor import StereotypeExecutor


'''
HardCode path for each environment, should be dev, debug, production instead...
'''
curr_dir = os.path.dirname(os.path.realpath(__file__))
home_dir = os.path.expanduser("~")
hard_dir = '/home/x/Code/BenchBox'
print curr_dir
print home_dir
print hard_dir

username = getpass.getuser()

dev_dir = {
    'x': hard_dir,
    'vagrant': home_dir,
    'milax': curr_dir
}

sys.path.append(dev_dir[username])



from workload_generator.model.user_activity.markov_chain import SimpleMarkovChain
from workload_generator.model.user_activity.inter_arrivals_manager import InterArrivalsManager
from workload_generator.model.data_layer.data_generator import DataGenerator

from workload_generator.communication.ftp_sender import ftp_sender
from workload_generator.communication.actions import UploadDirectory,\
    CreateFile, CreateDirectory, UpdateFile, DeleteFile, DeleteDirectory, MoveFile, MoveDirectory

from workload_generator.constants import DEBUG, FS_SNAPSHOT_PATH, STEREOTYPE_RECIPES_PATH, \
    BENCHBOX_IP, CPU_MONITOR_PORT, TO_WAIT_STATIC_MAX, TO_WAIT_STATIC_MIN,\
    FTP_SENDER_IP, FTP_SENDER_PASS, FTP_SENDER_PORT, FTP_SENDER_USER


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
            action = UploadDirectory(FS_SNAPSHOT_PATH, FS_SNAPSHOT_PATH)
            action.perform_action(ftp_client)
            print "MoveFileOrDirectory/to/SandBox/DONE"
    '''Do an execution step as a client'''
    def execute(self):
        '''Get the next operation to be done'''
        self.operation_chain.next_step_in_random_navigation()
        to_execute = getattr(self, 'do' + self.operation_chain.current_state)
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
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'MakeResponse')
        action.perform_action(ftp_client)
    """
    
    def doPutContentResponse(self):
        print colored("doPutContentResponse",'cyan')

        if random.random() > 0.25:
            synthetic_file_name = self.data_generator.create_file()
            isFile = True
        else:
            synthetic_file_name = self.data_generator.create_directory()
            isFile = False

        print "{} :>>> NEW ".format(synthetic_file_name)

        if isFile:
            action = CreateFile(synthetic_file_name, FS_SNAPSHOT_PATH)
        else:
            action = CreateDirectory(synthetic_file_name, FS_SNAPSHOT_PATH)

        print "{} :>>> ACTION".format(action)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'PutContentResponse')
        to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
        print "Wait: {}s".format(to_wait)
        time.sleep(to_wait)
        action.perform_action(self.ftp_client)

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
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'Sync')
            to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)

            action.perform_action(self.ftp_client)

    def doUnlink(self):
        print colored("doUnlink",'yellow')
        if random.random() > 0.25:
            synthetic_file_name = self.data_generator.delete_file()
            isFile = True
        else:
            synthetic_file_name = self.data_generator.delete_directory()
            isFile = False
        if not synthetic_file_name == None:
            if isFile:
                action = DeleteFile(synthetic_file_name, FS_SNAPSHOT_PATH)
            else:
                action = DeleteDirectory(synthetic_file_name, FS_SNAPSHOT_PATH)

            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'Unlink')
            to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(self.ftp_client)
        else:
            print "No file selected!"

    #TODO: Needs implementation in data generator first
    def doMoveResponse(self):
        print colored("doMoveResponse",'magenta')
        if random.random() > 0.25:
            synthetic_file_name = self.data_generator.move_file()
            isFile = True
        else:
            synthetic_file_name = self.data_generator.move_directory()
            isFile = False
        print synthetic_file_name
        (src_mov, tgt_mov) = synthetic_file_name
        if src_mov:
            if isFile:
                action = MoveFile(src_mov, FS_SNAPSHOT_PATH, tgt_mov)
            else:
                action = MoveDirectory(src_mov, FS_SNAPSHOT_PATH, tgt_mov)

            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'MoveResponse')
            to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(self.ftp_client)
        else:
            print "No file selected!"

    #TODO: Let's see how we can solve this
    def doGetContentResponse(self):
        print colored("doGetContentResponse",'blue')
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'GetContentResponse')
        to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
        print "Wait: {}s".format(to_wait)
        #action.perform_action(ftp_client)




class Execute:
    def __init__(self, args):
        print "Executor operation consumer: "

    def start(self):
        print 'start'
        idx = 0
        while True:
            idx+=1
            print idx
            time.sleep(1)

if __name__ == '__main__':

    print "executor.py is ran when warmup and its queue remains established... WAITING RPC"
    opt = process_opt()
    executor = Execute(opt)
    Execute.start()



