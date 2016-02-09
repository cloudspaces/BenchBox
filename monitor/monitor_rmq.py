#!/usr/bin/env python
import math
import pika
import os
import sys
import urlparse
import time
import filecmp
import shutil
import subprocess

from threading import Thread
import psutil
from termcolor import colored
import socket
import random
import calendar
import json





class EmitMetric(object):

    def __init__(self, hostname, personal_cloud):
        self.personal_cloud = personal_cloud
        self.hostname = hostname

        url_str = None
        with open('rabbitmq','r') as r:
            url_str = r.read().splitlines()[0]

        url = urlparse.urlparse(url_str)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='metrics', type='fanout')

    def emit(self, tags='', metrics='', pid=''):
        if metrics == '':
            metrics = {'cpu': random.randint(0, 100),
                       'ram': random.randint(0, 100),
                       'net': random.randint(0, 100),
                       'time': calendar.timegm(time.gmtime()) * 1000}
        # psutil read metrics

        if pid == "":
            print "Sintetic"
        else:
            print "PID: {} ".format(pid)
            try:
                if self.personal_cloud.lower() == "stacksync":
                    #
                    print self.personal_cloud
                    parent_proc = psutil.Process(pid)
                    proc = parent_proc.children()[0]
                    cpu_usage = math.ceil(proc.cpu_percent(0))
                    ram_usage = proc.memory_info().rss
                    metrics['cpu'] = cpu_usage
                    metrics['ram'] = ram_usage
                elif self.personal_cloud == "owncloud":
                    print "TODO owncloud"
                elif self.personal_cloud == "dropbox":
                    # how to track dropbox pid???
                    # the pid is contained in a pid file

                    print "TODO etc"
            except Exception as e:
                print e.message
        if tags == '':
            tags = {
                'profile': 'backup_sample',
                'credentials': 'pc_credentials'
            }
        data = {
            'metrics': metrics,
            'tags': tags
        }

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
    def __init__(self, hostname, profile, pc=''):
        print '[INIT]: rpc commands'
        self.hostname = hostname
        self.is_warmup = False
        self.is_running = False
        self.stereotype = profile  # backupsample
        self.monitor = None
        self.sync_client = None
        if pc == '':
            self.personal_cloud = 'StackSync'        # its not defined
        else:
            self.personal_cloud = pc
            # todo metric reader class


    def hello(self):
        print '[HELLO]: hello world'
        return '[HELLO]: hello world response'

    '''
     init the target personal client and wait, this stage also defines the metrics that
     are going to be measured
    '''
    def warmup(self):
        print '[WARMUP]'
        print '[WARMUP]: init personal cloud client'
        if self.is_warmup is False:
            print '[WARMUP]: to warmup '
            self.is_warmup = True
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
            # track the sync client pid resources
            metric_reader = EmitMetric(self.hostname, self.personal_cloud)  # start the sync client
            while self.is_running:
                operations += 1  # executant de forma indefinida...
                metric_reader.emit(pid=self.sync_proc_pid)  # send metric to rabbit
                time.sleep(2)  # delay between metric
                print colored("[TEST]: INFO {} --> {} // {}".format(time.ctime(time.time()), operations, self.is_running), 'red')
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
            'dropbox': "/home/vagrant/.dropbox-dist/dropboxd" # launch dropbox
        }

        # en el cas de dropbox arrancar el dropboxd ... legir el /home/vagrant/.dropbox/dropbox.pid
        # instanciar sync_proc
        # create the process
        pc = self.personal_cloud.lower()
        str_cmd = pc_cmd[pc]

        # read the metric may be different for each personal cloud - todo herencia

        # get deamon pid
        if pc == 'dropbox':
            path_to_pidfile = "/home/vagrant/.dropbox/dropbox.pid"
            if os.path.exists(path_to_pidfile):
                pid = int(open(path_to_pidfile).read())
            self.sync_proc_pid = pid
        else:
            self.sync_proc = subprocess.Popen(str_cmd, shell=True)
            self.sync_proc_pid = self.sync_proc.pid

        print "{} --> PID: {}".format(self.personal_cloud, self.sync_proc_pid)


    '''
     start sending metrics
    '''
    def start(self):
        print '[START_TEST]'
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
            return '[START_TEST]: SUCCESS: run test response'

    '''
     halt sending metrics
    '''
    def stop(self):
        if self.is_running:
            print '[STOP_TEST]: stop test'
            self.is_running = False
            self.monitor.join()
            self.sync_client.join()
            print self.sync_proc_pid
            parent = psutil.Process(self.sync_proc_pid)
            for child in parent.children(recursive=True):  # or parent.children() for recursive=False
                print child.kill()
            print parent.kill()
            return '[STOP_TEST]: SUCCESS: stop test'
        else:
            return '[STOP_TEST]: WARNING: no test is running'


class MonitorRMQ(object):
    def __init__(self, rmq_url='', host_queue='', receipt=''):
        print "Executor operation consumer: "
        url = urlparse.urlparse(rmq_url)
        self.profile = receipt
        self.hostname = host_queue.split(".")[0]
        self.actions = Commands(hostname=self.hostname, profile=receipt)
        self.queue_name = host_queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name)

    def on_request(self, ch, method, props, body):
        print " [on_request] {} ".format(body)
        print " [on_request] ch {} meth {} props {} body {}".format(ch, method, props, body)
        # todo implementar els handler vagrantUp i vagrantDown
        output = None
        try:
            toExecute = getattr(self.actions, body)
            print toExecute
            output = toExecute()
        except AttributeError as e:
            print e.message
            print "ACK: {}".format(body)

        response = "{} response: {}: {}".format(self.queue_name, body, output)
        print props.reply_to
        print props.correlation_id
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
        except:
            print "bypass"
        ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index

    def listen(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.queue_name)
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
        monitor = MonitorRMQ(rmq_url=rmq_url, host_queue=queue_name, receipt=stereotype_receipt)
        monitor.listen()
    else:
        profile = "StackSync"
        actions = Commands(profile=stereotype_receipt, hostname=dummyhost)
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
