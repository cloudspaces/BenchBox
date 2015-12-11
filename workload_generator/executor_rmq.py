#!/usr/bin/env python
import pika
import os
import sys
import urlparse
import time
import filecmp
import shutil
from threading import Thread
from termcolor import colored

from constants import STEREOTYPE_RECIPES_PATH, FS_SNAPSHOT_PATH
from executor import StereotypeExecutorU1



class Commands(object):
    # singleton class

    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Commands, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, receipt):
        print '[INIT]: rpc commands'
        self.is_warmup = False
        self.is_running = False
        self.stereotype = receipt  # backupsample
        self.stereotype_executor = StereotypeExecutorU1()
        self.fs_abs_target_folder = '/home/vagrant/{}'.format(self.stereotype_executor.ftp_client.ftp_root)  # target ftp_client dir absolute path
        self.execute = None

        # self.data_generator = DataGenerator()

        # start the monitoring stuff. # todo
        # send to impala always...!!!
        # sshpass -p vagrant rsync -rvnc --delete ../output/ vagrant@192.168.56.101:stacksync_folder/

    def hello(self):
        print '[HELLO]: hello world'
        return '[HELLO]: hello world response'

    def warmup(self):
        print '[WARMUP]'
        print FS_SNAPSHOT_PATH
        print STEREOTYPE_RECIPES_PATH
        receipt = STEREOTYPE_RECIPES_PATH + self.stereotype
        print receipt
        print '[WARMUP]: init_stereotype_from_recipe'
        if self.is_warmup is False:
            self.stereotype_executor.initialize_from_stereotype_recipe(receipt)
            print '[WARMUP]: init fs & migrate to sandbox'
            self.stereotype_executor.create_fs_snapshot_and_migrate_to_sandbox()
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
            self.stereotype_executor.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
            # TODO loop
            operations = 0
            while self.is_running:
                operations += 1  # executant de forma indefinida...
                self.stereotype_executor.execute()
                # time.sleep(3)
                print colored("[TEST]: INFO {} --> {} // {}".format(time.ctime(time.time()), operations, self.is_running), 'red')

        else:
            print '[TEST]: WARNING: need warmup 1st!'

    def start(self):
        print '[START_TEST]'
        if not self.is_warmup:
            return '[START_TEST]: WARNING: require warmup!'

        if self.is_running:
            return '[START_TEST]: INFO: already running!'
        else:
            # SELF THREAD START

            print '[START_TEST]: INFO: instance thread'
            self.execute = Thread(target=self._test)
            self.execute.start()
            return '[START_TEST]: SUCCESS: run test response'

    def stop(self):
        if self.is_running:
            print '[STOP_TEST]: stop test'
            self.is_running = False
            self.execute.join()
            return '[STOP_TEST]: SUCCESS: stop test'
        else:
            return '[STOP_TEST]: WARNING: no test is running'




class ExecuteRMQ(object):
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
            # lo ideal es que aixo no sigui un thread per que les peticions s'atenguin fifo
            # t = threading.Thread(target=toExecute)
            output = toExecute()
            # t.start()
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
    print "executor.py is ran when warmup and its queue remains established... WAITING RPC"

    # read the url from path: /vagrant/rmq.url.txt
    rmq_url = None
    with open('/vagrant/rabbitmq','r') as r:
        rmq_url = r.read().splitlines()[0]
    dummyhost = None
    # start the ftp sender
    stereotype_receipt = 'backupsample'

    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost, 'executor')




    if len(sys.argv) == 1:  # means no parameters
        executor = ExecuteRMQ(rmq_url, queue_name, stereotype_receipt)
        executor.listen()
    else:
        profile = "StackSync"
        actions = Commands(receipt=stereotype_receipt)
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


