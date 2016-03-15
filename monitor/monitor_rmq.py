#!/usr/bin/env python
import math
import pika
import os
import datetime
import sys
import urlparse
import time
import filecmp
import shutil
import subprocess
import signal
from threading import Thread
import psutil
from termcolor import colored
import socket
import random
import calendar
import json
import fcntl


def singleton(lockfile="monitor_rmq.pid"):
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



class EmitMetric(object):

    def __init__(self, hostname, personal_cloud):
        self.personal_cloud = personal_cloud

        pc_folders = {
            'stacksync': 'stacksync_folder',
            'dropbox': 'Dropbox'
        }

        self.personal_folder = pc_folders[self.personal_cloud.lower()]

        self.hostname = hostname
        self.proc = None
        self.prev_metric = None # keep track of last emited metric
        url_str = None
        with open('rabbitmq','r') as r:
            url_str = r.read().splitlines()[0]

        self.prev_net_counter = psutil.net_io_counters(pernic=True)['eth0']  # 10.0.2.15 static for each sandBox

        url = urlparse.urlparse(url_str)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            heartbeat_interval=10,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='metrics', type='fanout')

    def emit(self, tags='', metrics='', pid='', receipt=''):
        if metrics == '':
            metrics = {'cpu': random.randint(0, 100),
                       'ram': random.randint(0, 100),
                       'net': 0,
                       'bytes_sent': 0,
                       'bytes_recv': 0,
                       'packets_sent': 0,
                       'packets_recv': 0,
                       'errin': 0,
                       'errout': 0,
                       'dropin': 0,
                       'dropout': 0,
                       'disk': 0,
                       'files': 0,
                       'time': calendar.timegm(time.gmtime()) * 1000}
        # psutil read metrics

        if pid == "" or self.proc is None:
            self.proc = psutil.Process(pid)
            print "Sintetic"
        else:
            print "PID: {} [{}]".format(pid, self.personal_cloud.lower())
            try:
                if self.personal_cloud.lower() == "stacksync":
                    #
                    print self.personal_cloud
                    #parent_proc = psutil.Process(pid)
                    # proc = parent_proc.children()[0]
                    #proc = parent_proc
                    proc = self.proc
                    cpu_usage = int(math.ceil(proc.cpu_percent(0)))
                    ram_usage = proc.memory_info().rss
                    metrics['cpu'] = cpu_usage
                    metrics['ram'] = ram_usage
                elif self.personal_cloud.lower() == "owncloud":
                    print "TODO owncloud"
                elif self.personal_cloud.lower() == "dropbox":
                    # how to track dropbox pid???
                    # the pid is contained in a pid file
                    print self.personal_cloud
                    #proc = psutil.Process(pid)
                    proc = self.proc
                    cpu_usage = int(math.ceil(proc.cpu_percent(None)))
                    ram_usage = proc.memory_info().rss
                    metrics['cpu'] = cpu_usage
                    metrics['ram'] = ram_usage
                    print "TODO etc"
            except Exception as e:
                print e.message

        # assign the network usage metric

        if self.prev_metric is not None:
            # do nothing because its the first emit ant there are no previous metric to compare
            # last_net = self.prev_metric['metrics']['net']
            last_time = self.prev_metric['metrics']['time']

            curr_net_counter = psutil.net_io_counters(pernic=True)['eth0']  # read the bytes from somewhere
            curr_time = metrics['time']

            elapsed_time = (curr_time-last_time) / 1000  # segons

            for key, value in curr_net_counter.__dict__.items():
                # print key, value
                # elapsed_net = (curr_net-last_net) # some unit
                metrics[key] = (value - getattr(self.prev_net_counter, key)) / elapsed_time  # unit is seconds
            self.prev_net_counter = curr_net_counter

        # assign hard drive usage metric
        proc = subprocess.Popen(['/usr/bin/du', '-ks', '/home/vagrant/{}'.format(self.personal_folder)], stdout=subprocess.PIPE)
        tmp = proc.stdout.read()
        metrics['disk'] = int(tmp.split('\t')[0])  # kilo bytes cast string to int

        # assign add folder num of files metric
        proc_find = subprocess.Popen('/usr/bin/find /home/vagrant/{} -type f'.format(self.personal_folder).split(), stdout=subprocess.PIPE)
        proc_wc = subprocess.Popen('/usr/bin/wc -l'.split(), stdin=proc_find.stdout, stdout=subprocess.PIPE)
        num_files = proc_wc.communicate()[0]
        metrics['files'] = int(num_files.split('\t')[0])  # count numero of files in the sync directory

        if tags == '':
            tags = {
                'profile': receipt,  # todo @ update this field from the args of rabbitmq
                'credentials': 'pc_credentials',
                'client': self.personal_cloud.lower(),
            }
        data = {
            'metrics': metrics,
            'tags': tags
        }
        self.prev_metric = data  # update the last emited metric

        msg = json.dumps(data)
        print msg

        self.channel.basic_publish(
            exchange='metrics',
            routing_key=self.hostname,
            body=msg)

class Commands(object):
    # singleton class
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Commands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    """
    profile == receipt
    personal_cloud: stacksync.
    receipt: backupsample
    """
    def __init__(self, hostname):
        print '[INIT_MONITOR_RMQ]: rpc commands'
        self.hostname = hostname
        self.is_warmup = False
        self.is_running = False
        self.stereotype = None      # backupsample # todo @ update this to load profiles dynamically
        self.monitor = None         # monitor_process => experimento
        self.sync_client = None     # sync_client process
        self.sync_proc_pid = None
        self.sync_proc = None
        self.personal_cloud = None  # personal cloud
        self.executor_state = "Unknown"  # state +  time

    def hello(self, body):
        print '[HELLO]: hello world {}'.format(body['cmd'])
        return '[HELLO]: hello world response'

    '''
     init the target personal client and wait, this stage also defines the metrics that
     are going to be measured
    '''
    def warmup(self, body):
        print '[WARMUP] {}'.format(body)
        print '[WARMUP]: init personal cloud client'
        if self.is_warmup is False:  # or the personal cloud has changed
            self.personal_cloud = body['msg']['test']['testClient']
            self.stereotype = body['msg']['test']['testProfile']  # if its defined then this will be loaded
            self.is_warmup = True
            print '[WARMUP]: to warmup {}'.format(self.personal_cloud)
            self.executor_state = "monitor Warmup Done!"

            # todo @ kill existing java process
        else:
            # if self.personal_cloud == personal_cloud_candidate: todo @ sino tornar a arrancar
            print '[WARMUP]: already warmed-up as {}'.format(self.personal_cloud)

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
            # track the sync client pid resources
            metric_reader = EmitMetric(hostname=self.hostname, personal_cloud=self.personal_cloud)  # start the sync client
            while self.is_warmup and self.is_running and self.sync_proc_pid is not None:
                operations += 1  # executant de forma indefinida...
                metric_reader.emit(pid=self.sync_proc_pid, receipt=self.stereotype)  # send metric to rabbit
                time.sleep(2)  # delay between metric
                print colored("[TEST]: INFO {} --> {} // {} // {}".format(time.ctime(time.time()), operations, self.is_running, self.sync_proc_pid), 'red')
        else:
            print '[TEST]: WARNING: need warmup 1st!'

    def _pc_client(self):
        '''
        This thread will get track the personal client process id
        '''
        print "Start: {} ".format(self.personal_cloud)
        # start the personal cloud client process and register its pid
        pc_cmd = {
            'stacksync': "/usr/bin/java -jar /usr/lib/stacksync/Stacksync.jar -d -c /vagrant",
            'owncloud': "",
            'dropbox': "/home/vagrant/.dropbox-dist/dropboxd"  # launch dropbox
        }

        # en el cas de dropbox arrancar el dropboxd ... legir el /home/vagrant/.dropbox/dropbox.pid
        # instanciar sync_proc
        # create the process
        pc = self.personal_cloud.lower()
        str_cmd = pc_cmd[pc]

        # read the metric may be different for each personal cloud - todo herencia

        # get deamon pid
        if pc == 'dropbox':
            self.sync_proc = subprocess.Popen(str_cmd, shell=True) # forgot tu lauch dropbox

            pid = None
            while pid == None or pid == '':
                try:
                    pid = int(subprocess.check_output(['pidof','dropbox']).replace('\n',''))
                except Exception as e:
                    print e.message
            # do until a pid is found otherwise read dropbox.pid and check if the pid is running...
            # and dont continue until the pid from dropbox.pid is found, match...

            """
            path_to_pidfile = "/home/vagrant/.dropbox/dropbox.pid"
            if os.path.exists(path_to_pidfile):
                pid = int(open(path_to_pidfile).read())
            """
            self.sync_proc_pid = pid
        else:
            ## if its already running what do i do?
            self.sync_proc = subprocess.Popen(str_cmd, shell=True) # executar el process
            pid = None
            while pid == None or pid == '':
                try:
                    pid = int(subprocess.check_output(['pidof','java']).replace('\n',''))
                except Exception as e:
                    time.sleep(3)  # wait stacksync to quit or start
                    print e.message
            self.sync_proc_pid = pid

        print "{} --> PID: {}".format(self.personal_cloud, self.sync_proc_pid)


    '''
     start sending metrics
    '''
    def start(self, body):
        print '[START_TEST] {}'.format(body)
        if not self.is_warmup:
            return '[START_TEST]: WARNING: require warmup!'

        if self.is_running:
            return '[START_TEST]: INFO: already running!'
        else:
            # SELF THREAD START

            print '[START_TEST]: INFO: instance thread'
            self.sync_client = Thread(target=self._pc_client)
            self.sync_client.start()
            # self.sync_client.start()
            self.monitor = Thread(target=self._test)
            self.monitor.start()
            self.executor_state = "monitor Capturing... "
            return '[START_TEST]: SUCCESS: run test response'

    '''
     halt sending metrics
    '''
    def stop(self, body):
        if self.is_running:
            print '[STOP_TEST]: stop test {}'.format(body)
            self.is_running = False
            self.monitor.join()
            self.sync_client.join()
            print self.sync_proc_pid
            parent = psutil.Process(self.sync_proc_pid)
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                print child.kill()
            print parent.kill()
            self.is_warmup = False
            self.executor_state = "monitor stop Capturing... "
            return '[STOP_TEST]: SUCCESS: stop test'
        else:
            return '[STOP_TEST]: WARNING: no test is running'

    def keepalive(self, body):
        return "{} -> {}".format(datetime.datetime.now().isoformat(), self.executor_state)

class MonitorRMQ(object):
    def __init__(self, rmq_url='', host_queue=''):
        print "Executor operation consumer: "
        url = urlparse.urlparse(rmq_url)
        self.hostname = host_queue.split(".")[0]
        self.actions = Commands(hostname=self.hostname)
        self.queue_name = host_queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            heartbeat_interval=10,
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_declare(queue=self.queue_name)

    def on_request(self, ch, method, props, data):
        body = json.loads(data)
        print " [on_request] {} ".format(body['cmd'])
        # print " [on_request] ch {} meth {} props {} body {}".format(ch, method, props, body['cmd'])
        # todo implementar els handler vagrantUp i vagrantDown
        output = None
        try:
            toExecute = getattr(self.actions, body['cmd'])
            print "ExecuteIn  : {}".format(body['cmd'])
            output = toExecute(body)
            print "ExecuteOut : {}".format(output)
        except AttributeError as e:
            print e.message
            print "ACK: {}".format(body['cmd'])

        response = "{} response: {}: {}".format(self.queue_name, body['cmd'], output)
        print props.reply_to
        print props.correlation_id
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             # properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
        except:
            print "bypass"
        ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index

    def listen(self):
        # self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request,
                                   no_ack=False,
                                   queue=self.queue_name)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()



if __name__ == '__main__':
    print "monitor.py is ran at sandBox to dump metrics... WAITING RPC"
    rmq_url = None
    with open('/vagrant/rabbitmq','r') as r:
        rmq_url = r.read().splitlines()[0]
    print len(sys.argv)

    dummyhost = None
    stereotype_receipt = 'backupsample'
    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost, 'monitor')

    if len(sys.argv) == 1:  # means no parameters
        # use file look
        singleton()

        monitor = MonitorRMQ(rmq_url=rmq_url, host_queue=queue_name)
        monitor.listen()
    else:
        profile = "StackSync"
        actions = Commands(hostname=dummyhost)
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
            time.sleep(1)
