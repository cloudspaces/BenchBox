#!/usr/bin/env python
import pika
import os
import sys
import urlparse
import time
import filecmp
import shutil
import subprocess

from threading import Thread
from termcolor import colored
# from py_monitor import SocketListener

'''

launch the sync client from here and use psutil to track the personal client resource usage.
stacksync: /usr/lib/stacksync/StackSync.jar -etc

java -jar Stacksync.jar -d -c /vagrant & echo $!


owncloud: ./owncloud_sync.sh

while true; do
echo 'DoSync'
    owncloudcmd --httpproxy http://10.30.235.91 -u Xen -p Xen /home/vagrant/owncloud_folder/ http://10.30.235.91
    echo 'SyncingComplete'
     sleep $delay
    # ls -l
done

'''

class Commands(object):
    # singleton class

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Commands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, profile):
        print '[INIT]: rpc commands'
        self.is_warmup = False
        self.is_running = False
        self.stereotype = profile  # backupsample
        self.monitor = None
        self.sync_client = None
        self.personale_cloud = 'StackSync'

        # self.data_generator = DataGenerator()

        # start the monitoring stuff. # todo
        # send to impala always...!!!
        # sshpass -p vagrant rsync -rvnc --delete ../output/ vagrant@192.168.56.101:stacksync_folder/

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

            while self.is_running:
                operations += 1  # executant de forma indefinida...
                time.sleep(3)
                print colored("[TEST]: INFO {} --> {} // {}".format(time.ctime(time.time()), operations, self.is_running), 'red')
        else:
            print '[TEST]: WARNING: need warmup 1st!'


    def _pc_client(self):
        '''
        This thread will get track the personal client process id
        '''
        print "Start: {} ".format(self.personale_cloud)
        proc = subprocess.Popen("/usr/bin/du folder", stdout=file("1.txt", "ab"))
        print "PID:", proc.pid
        print "Return code:", proc.wait()

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
            return '[STOP_TEST]: SUCCESS: stop test'
        else:
            return '[STOP_TEST]: WARNING: no test is running'


class MonitorRMQ(object):
    def __init__(self, rmq_url='', host_queue='', profile=''):
        print "Executor operation consumer: "
        url = urlparse.urlparse(rmq_url)
        self.profile = profile
        self.actions = Commands(profile)

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

    dummyhost = None
    stereotype_receipt = 'backupsample'
    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost, 'monitor')
    monitor = MonitorRMQ(rmq_url, queue_name, stereotype_receipt)
    monitor.listen()
