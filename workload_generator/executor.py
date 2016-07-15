#!/usr/bin/python
'''
Created on 30/6/2015

@author: Raul
'''
import os, sys
import random,json,calendar
import time, urlparse, os, pika
from termcolor import colored
from utils import appendParentDir

'''
HardCode path for each environment, should be dev, debug, production instead...
'''
appendParentDir(1, os.path.dirname(os.path.realpath(__file__)))

from model.user_activity.stereotype_executor import StereotypeExecutor
from communication.actions import UploadDirectory, \
    CreateFile, CreateDirectory, UpdateFile, DeleteFile, DeleteDirectory, MoveFile, MoveDirectory

from communication.ftp_sender import ftp_sender
from constants import DEBUG, FS_SNAPSHOT_PATH, MAX_WAITING_TIME, MIN_WAITING_TIME, \
    FTP_SENDER_IP, FTP_SENDER_PORT, FTP_SENDER_USER, FTP_SENDER_PASS

from py_publish.publisher import Publisher


'''Class that executes remote operations on the Sandbox based on the
data generation and user activity models. The class is tailored for the
available information in the UbuntuOne (U1) trace.'''


class StereotypeExecutorU1(StereotypeExecutor):
    def __init__(self):
        StereotypeExecutor.__init__(self)
        self.rmq_channel = None
        self.ftp_client = None
        self.current_operation = "SYNC"  # assign default initial, current operation
        # AttributeError: 'StereotypeExecutorU1' object has no attribute 'current_operation'
        # el keep alive puede ser por run o por to_wait operation...

    def initialize_rmq_channel(self):
        self.rmq_path = "rabbitmq"
        self.rmq_path_url = None

        with open(self.rmq_path, 'r') as read_file:
            self.rmq_path_url = read_file.read().splitlines()[0]
        self.rmq_url = urlparse.urlparse(self.rmq_path_url)
        self.rmq_connection = None
        try:
            self.rmq_connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=self.rmq_url.hostname,
                    heartbeat_interval=5,
                    virtual_host=self.rmq_url.path[1:],
                    credentials=pika.PlainCredentials(self.rmq_url.username, self.rmq_url.password)
                )
            )
        except Exception as ex:
            print ex.message
            exit(0)
            # failed to create rabbit connection
        self.rmq_channel = self.rmq_connection.channel()


    def initialize_ftp_client_by_directory(self, root_dir, ftp_home):
        # update fto_client_root directory
        print "Init ftp_client and its root directory {}".format(root_dir)
        self.ftp_client = ftp_sender(
                ftp_host=FTP_SENDER_IP,
                ftp_port=FTP_SENDER_PORT,
                ftp_user=FTP_SENDER_USER,
                ftp_pass=FTP_SENDER_PASS,
                ftp_root=root_dir,  # per defecte ...
                ftp_home=ftp_home  # default home directory
        )



    def initialize_from_stereotype_recipe(self, stereotype_recipe):
        StereotypeExecutor.initialize_from_stereotype_recipe(self, stereotype_recipe)

    def create_fs_snapshot_and_migrate_to_sandbox(self):
        '''Initialize the file system in addition to the models'''
        self.data_generator.create_file_system_snapshot()
        self.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        '''Create a set of initial files to populate the file system'''
        for i in range(10):
            self.data_generator.create_file()
            
        '''When the initial file system has been built, migrate it to the sandbox'''
        if not DEBUG:
            # self.data_generator.migrate_file_system_snapshot_to_sandbox("migrate location")
            action = UploadDirectory(FS_SNAPSHOT_PATH, FS_SNAPSHOT_PATH)
            action.perform_action(self.ftp_client.keep_alive())
            print "MoveFileOrDirectory/to/SandBox/DONE"

    '''Do an execution step as a client'''

    def execute(self, personal_cloud=None):
        '''Get the next operation to be done'''
        self.operation_chain.next_step_in_random_navigation()
        to_execute = getattr(self, 'do' + self.operation_chain.current_state)
        return self.operation_chain.current_state,  to_execute(personal_cloud=personal_cloud)


    def doUPLOAD(self, op_name="UPLOAD", personal_cloud=None):
        print colored(op_name, 'cyan')
        synthetic_file_name, isFile = self.data_generator.create_file_or_directory()
        print "{} :>>> NEW ".format(synthetic_file_name)
        if isFile:
            action = CreateFile(synthetic_file_name, FS_SNAPSHOT_PATH)
        else:
            action = CreateDirectory(synthetic_file_name, FS_SNAPSHOT_PATH)
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
        action.perform_action(self.ftp_client.keep_alive())
        return to_wait


    def doSYNC(self, op_name="SYNC", personal_cloud=None):
        print colored(op_name, 'green')
        synthetic_file_name = self.data_generator.update_file()
        print synthetic_file_name
        if synthetic_file_name is None:
            print "no file selected!"
            return 0
        else:
            action = UpdateFile(synthetic_file_name, FS_SNAPSHOT_PATH)
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
            action.perform_action(self.ftp_client.keep_alive())
            return to_wait

    def doDELETE(self, op_name="DELETE", personal_cloud=None):
        print colored(op_name, 'yellow')
        synthetic_file_name, isFile = self.data_generator.delete_file_or_directory()
        if not synthetic_file_name is None:
            if isFile:
                action = DeleteFile(synthetic_file_name, FS_SNAPSHOT_PATH)
            else:
                action = DeleteDirectory(synthetic_file_name, FS_SNAPSHOT_PATH)
            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
            action.perform_action(self.ftp_client.keep_alive())
            return to_wait
        else:
            print "No file selected!"
            return 0

    def doMOVE(self, op_name="MOVE", personal_cloud=None):
        print colored(op_name, 'magenta')
        synthetic_file_name, isFile = self.data_generator.move_file_or_directory()
        print synthetic_file_name
        (src_mov, tgt_mov) = synthetic_file_name
        if src_mov:
            if isFile:
                action = MoveFile(src_mov, FS_SNAPSHOT_PATH, tgt_mov)
            else:
                action = MoveDirectory(src_mov, FS_SNAPSHOT_PATH, tgt_mov)
            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
            action.perform_action(self.ftp_client.keep_alive())
            return to_wait
        else:
            print "No file selected!"
            return 0

    def doDOWNLOAD(self, op_name="DOWNLOAD", personal_cloud=None):
        print colored(op_name, 'blue')
        '''Get the time to wait for this transition in millis'''
        to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
        synthetic_file_name = self.data_generator.create_file()
        print "{} :>>> PUBLISH: ".format(synthetic_file_name)
        publisher = Publisher(personal_cloud=personal_cloud)
        # b.publish('sample/sample.txt', '/aaaa/sample.txt')
        publisher.publish(synthetic_file_name, FS_SNAPSHOT_PATH)  #
        return to_wait

    def doIDLE(self, op_name="IDLE", personal_cloud=None):
        print colored(op_name, 'blue')
        try:
            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
            return to_wait
        except Exception as ex:
            print ex.message
            return 0

    def doSTART(self, op_name="START", personal_cloud=None):
        print colored(op_name, 'blue')
        try:
            '''Get the time to wait for this transition in millis'''
            to_wait = self.inter_arrivals_manager.get_waiting_time(self.current_operation, op_name)
            return to_wait
        except Exception as ex:
            print ex.message
            return 0

    def notify_operation(self, profile="sync-heavy", personal_cloud="dropbox", hostname=None, operation_name=None):
        tags = ''

        if tags == '':
            tags = {
                'profile': profile,
                'hostname': hostname,
                'client': personal_cloud,
            }

        metrics = {
            'operation': operation_name,
            'time': calendar.timegm(time.gmtime()) * 1000,
        }
        data = {
            'metrics': metrics,
            'tags': tags
        }
        msg = json.dumps(data)
        ## setup pika sender settings
        self.rmq_channel.basic_publish(
            exchange='metrics_ops',
            routing_key=hostname,
            body=msg)


