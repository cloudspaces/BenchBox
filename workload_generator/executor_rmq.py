#!/usr/bin/env python
import fcntl
import pika
import os
import sys
import urlparse
import time
import signal
import json
import datetime

from threading import Thread
from constants import STEREOTYPE_RECIPES_PATH, FS_SNAPSHOT_PATH
from executor import StereotypeExecutorU1
from termcolor import colored
import shutil
import glob


def singleton(lockfile="executor_rmq.pid"):
    if os.path.exists(lockfile):
        # read the pid
        with open(lockfile, 'r') as f:
            first_line = f.readline()
            print first_line
        last_pid = first_line
        print "kill_last_pid: {}".format(last_pid)
        print last_pid
        try:
            # kill last pid
            os.kill(int(last_pid), signal.SIGTERM)  # kill previous if exists
        except Exception as e:
            print e.message
            print "warning not valid pid"
    # update/store current pid
    with open(lockfile, 'w') as f:
        f.write(str(os.getpid()))


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


class Commands(object):
    # singleton class
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Commands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, receipt, hostname):
        print '[INIT_EXECUTOR_RMQ]: rpc commands'
        self.hostname = hostname  # the name of the dummyHost
        self.is_warmup = False
        self.is_running = False
        self.sync_directory = None  # stacksync_folder, Dropbox, ....
        self.target_ftp_target = None
        self.target_personal_cloud = None # Dropbox, Box, GoogleDrive
        self.stereotype = receipt  # backupsample
        self.stereotype_executor = None
        self.monitor_state = "Unknown"
        # update ftp_root_directory
        self.fs_abs_target_folder = None
        self.execute = None
        # self.data_generator = DataGenerator()

        # start the monitoring stuff. # todo
        # send to impala always...!!!
        # sshpass -p vagrant rsync -rvnc --delete ../output/ vagrant@192.168.56.101:stacksync_folder/

    def hello(self, body=None):
        if body is None:
            body = {
                "cmd": "hello",
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }

        print '[HELLO]: hello world {}'.format(body['cmd'])
        return '[HELLO]: hello world response'

    def warmup(self, body=None):

        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testTarget": "linux",
                        "testFolder": "Dropbox",
                        "testProfile": "download-heavy",
                        "testClient": "dropbox"
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }

        print '[WARMUP]: {} '.format(body)
        print FS_SNAPSHOT_PATH
        print STEREOTYPE_RECIPES_PATH

        print '[WARMUP]: init_stereotype_from_recipe'
        if self.is_warmup is False:
            self.sync_directory = body['msg']['test']['testFolder']
            self.stereotype_executor = StereotypeExecutorU1()  # tornar a assignar

            self.target_personal_cloud = body['msg']['test']['testClient']
            self.target_ftp_target = body['msg']['test']['testTarget']
            self.target_ftp_home = None

            if self.target_ftp_target == "windows":
                self.target_ftp_home = "/Users/vagrant"
            elif self.target_ftp_target == "linux":
                self.target_ftp_home = "/home/vagrant"
            else:
                print "Unhandled sandbox target host"

            self.stereotype_executor.initialize_rmq_channel()
            self.stereotype_executor.initialize_ftp_client_by_directory(root_dir=self.sync_directory, ftp_home=self.target_ftp_home)

            self.fs_abs_target_folder = '{}/{}'.format(self.target_ftp_home, self.sync_directory)  # target ftp_client dir absolute path

            self.stereotype = body['msg']['test']['testProfile']  # add benchbox switch stereotype profile at warmup
            receipt = STEREOTYPE_RECIPES_PATH + self.stereotype
            print receipt
            self.stereotype_executor.initialize_from_stereotype_recipe(receipt)
            print '[WARMUP]: init fs & migrate to sandbox'
            # always
            self.stereotype_executor.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
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
            # TODO loop
            operations = 0

            while self.is_running:
                operations += 1  # executant de forma indefinida...
                operation_executed, to_wait = self.stereotype_executor.execute(personal_cloud=self.target_personal_cloud)
                self.stereotype_executor.notify_operation(
                    operation_name=operation_executed,
                    profile=self.stereotype,
                    personal_cloud=self.target_personal_cloud,
                    hostname=self.hostname)
                print to_wait, operation_executed
                time.sleep(10)
                print colored("[TEST]: INFO {} --> {} // {} // {} // {}({})s".format(time.ctime(time.time()), operations, self.is_running, self.sync_directory, operation_executed, to_wait), 'red')
        else:
            print '[TEST]: WARNING: need warmup 1st!'

    def start(self, body=None):

        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }

        print '[START_TEST]: {}'.format(body)
        if not self.is_warmup:
            return '[START_TEST]: WARNING: require warmup!'
        if self.is_running:
            return '[START_TEST]: INFO: already running!'
        else:
            # SELF THREAD START
            time.sleep(2)  # para que el
            print '[START_TEST]: INFO: instance thread'
            self.execute = Thread(target=self._test)
            self.execute.start()
            self.monitor_state = "executor Running!"
            return '[START_TEST]: SUCCESS: run test response'

    def stop(self, body=None):

        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }
        print body

        print "clear the content of the sintetic workload generator filesystem"
        remove_inner_path('/home/vagrant/output/*')  # clear the directory after stoping the workload_generator

        if self.is_running:
            print '[STOP_TEST]: stop test {}'.format(body)
            self.is_running = False
            self.is_warmup = False
            self.execute.join()
            exit(0) # , prevents the monitor being killed
            self.monitor_state = "executor Stopped!"
            response_msg = '[STOP_TEST]: SUCCESS: stop test'
        else:
            response_msg = '[STOP_TEST]: WARNING: no test is running'

        self.is_warmup = False

        return response_msg

    def keepalive(self, body=None):
        if body is None:
            body = {
                "msg": {
                    "test": {
                        "testClient": "dropbox",
                    },
                    "dropbox-ip": "",
                    "dropbox-port": ""
                }
            }
        return "{} -> {}".format(datetime.datetime.now().isoformat(), self.monitor_state)


class ExecuteRMQ(object):
    def __init__(self, rmq_url='', host_queue='', profile='', hostname="TEST"):
        """
        This class contains the rabbitmq request handlers, that will call Commands contained in Commands class
        :param rmq_url: url where the rabbitmq server is hosted
        :param host_queue: queue name of the benchbox.executor
        :param profile: refers to the user stereotype to use
        :return:
        """
        print "Executor operation consumer: "
        url = urlparse.urlparse(rmq_url)
        self.profile = profile
        self.actions = Commands(receipt=profile, hostname=hostname)
        self.queue_name = host_queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            heartbeat_interval=5,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_declare(queue=self.queue_name)

    def on_request(self, ch, method, props, data):
        body = json.loads(data)
        print " [on_request] {} ".format(body['cmd'])
        executor_output = None
        try:
            executor_requested_command = getattr(self.actions, body['cmd'])
            # convertir en executor threads, simular multiples ediciones de manera simultanea
            # print toExecute # la comanda que s'executara
            # lo ideal es que aixo no sigui un thread per que les peticions s'atenguin fifo
            # t = threading.Thread(target=toExecute)
            print "requestCommand  : {}".format(body['cmd'])
            executor_output = executor_requested_command(body)
            print "requestCommand : {}".format(executor_output)
            # t.start()
        except AttributeError as ex:
            print ex.message
            print "ACK: {}".format(body['cmd'])
        response = "{} response: {}: {}".format(self.queue_name, body['cmd'], executor_output)
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             body=response)
        except:
            print "bypass"
        ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index

    def listen(self):
        self.channel.basic_consume(self.on_request,
                                   no_ack=False,
                                   queue=self.queue_name)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()


if __name__ == '__main__':
    print "executor.py is ran when warmup and its queue remains established... WAITING RPC"
    # read the url from path: /vagrant/rmq.url.txt
    rmq_url = None
    with open('/vagrant/rabbitmq','r') as r:
        rmq_url = r.read().splitlines()[0]
    dummyhost = None
    # start the ftp sender
    stereotype_receipt = 'download-heavy'
    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost, 'executor')
    singleton()
    if len(sys.argv) == 1:  # means no parameters
        # DEFAULT: dummy
        # use file look
        while True:
            # try:
            executor = ExecuteRMQ(rmq_url=rmq_url, host_queue=queue_name, profile=stereotype_receipt, hostname=dummyhost)
            # todo fer que stereotype_receipt y personal cloud sigui dinamic
            executor.listen()
            # except Exception as ex:
            #     print ex.message
            #     print "Some connection exception happened..."

    else:
        profile = "StackSync"
        actions = Commands(receipt=stereotype_receipt, hostname=dummyhost)
        while True:
            print 'write command: hello|warmup|start|stop'
            teclat = raw_input()
            print teclat
            try:
                toExecute = getattr(actions, teclat)
                print toExecute
                output = toExecute()
            except AttributeError as e:
                print e.message
                print "ACK: {}".format(teclat)
            time.sleep(5)



