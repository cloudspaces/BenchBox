#!/usr/bin/python
'''
Created on 30/6/2015

@author: Raul
'''
import os, sys
import random
import time
from termcolor import colored

'''
HardCode path for each environment, should be dev, debug, production instead...
'''


def appendParentDir(num, currdir):
    print currdir
    if num is 0:
        print 'return value'
        sys.path.append(currdir)
        return currdir
    else:
        dirname, basename = os.path.split(currdir)
        num -= 1
        return appendParentDir(num, dirname)


appendParentDir(1, os.path.dirname(os.path.realpath(__file__)))

from workload_generator.model.user_activity.stereotype_executor import StereotypeExecutor
from workload_generator.communication.actions import UploadDirectory, \
    CreateFile, CreateDirectory, UpdateFile, DeleteFile, DeleteDirectory, MoveFile, MoveDirectory

from workload_generator.communication.ftp_sender import ftp_sender
from workload_generator.constants import DEBUG, FS_SNAPSHOT_PATH, TO_WAIT_STATIC_MAX, TO_WAIT_STATIC_MIN, \
    FTP_SENDER_IP, FTP_SENDER_PORT, FTP_SENDER_USER, FTP_SENDER_PASS

'''Class that executes remote operations on the Sandbox based on the
data generation and user activity models. The class is tailored for the
available information in the UbuntuOne (U1) trace.'''


class StereotypeExecutorU1(StereotypeExecutor):
    def __init__(self):
        StereotypeExecutor.__init__(self)
        self.ftp_client = None
        # el keep alive puede ser por run o por to_wait operation...

    """
    benchBox (executor)
    Aquest metode es crida quan hiha un warm up en el cas de executor per que el
    benchbox sapigui a quin directory s'ha sincronitzar els fitchers
    """
    def initialize_ftp_client_by_directory(self, root_dir):
        # update fto_client_root directory
        print "Init ftp_client and its root directory {}".format(root_dir)
        self.ftp_client = ftp_sender(
                FTP_SENDER_IP,
                FTP_SENDER_PORT,
                FTP_SENDER_USER,
                FTP_SENDER_PASS,
                root_dir  # per defecte ...
        )


    def initialize_from_stereotype_recipe(self, stereotype_recipe):
        StereotypeExecutor.initialize_from_stereotype_recipe(self, stereotype_recipe)

    def create_fs_snapshot_and_migrate_to_sandbox(self):
        '''Initialize the file system in addition to the models'''
        self.data_generator.create_file_system_snapshot()
        self.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        '''When the initial file system has been built, migrate it to the sandbox'''
        if not DEBUG:
            # self.data_generator.migrate_file_system_snapshot_to_sandbox("migrate location")
            action = UploadDirectory(FS_SNAPSHOT_PATH, FS_SNAPSHOT_PATH)
            action.perform_action(self.ftp_client.keep_alive())
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
        print colored("doPutContentResponse", 'cyan')

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
        # to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'PutContentResponse')
        to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
        print "Wait: {}s".format(to_wait)
        time.sleep(to_wait)
        action.perform_action(self.ftp_client.keep_alive())

    def doSync(self):
        # TODO: Cheng, you can make use of data_generator.update() to test updating files
        # self.doPutContentResponse()
        print colored("doSync", 'green')
        synthetic_file_name = self.data_generator.update_file()
        print synthetic_file_name
        if synthetic_file_name is None:
            print "no file selected!"
        else:
            action = UpdateFile(synthetic_file_name, FS_SNAPSHOT_PATH)
            # to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'Sync')
            to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(self.ftp_client.keep_alive())

    def doUnlink(self):
        print colored("doUnlink", 'yellow')
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
            # to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'Unlink')
            to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(self.ftp_client.keep_alive())
        else:
            print "No file selected!"

    # TODO: Needs implementation in data generator first
    def doMoveResponse(self):
        print colored("doMoveResponse", 'magenta')
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
            # to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'MoveResponse')
            to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
            print "Wait: {}s".format(to_wait)
            time.sleep(to_wait)
            action.perform_action(self.ftp_client.keep_alive())
        else:
            print "No file selected!"

    # TODO: Let's see how we can solve this
    def doGetContentResponse(self):
        print colored("doGetContentResponse", 'blue')
        '''Get the time to wait for this transition in millis'''
        # to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, 'GetContentResponse')
        to_wait = random.randint(TO_WAIT_STATIC_MIN, TO_WAIT_STATIC_MAX)
        print "Wait: {}s".format(to_wait)
        # action.perform_action(ftp_client)
