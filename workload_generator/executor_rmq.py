#!/usr/bin/env python
import pika
import os
import sys
import urlparse
import filecmp
import shutil
from termcolor import colored


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

from workload_generator.constants import STEREOTYPE_RECIPES_PATH, FS_SNAPSHOT_PATH
from workload_generator.executor import StereotypeExecutorU1




class Commands(object):
    def __init__(self, profile):
        print 'rpc commands'
        self.is_warmup = False
        self.stereotype = profile  # backupsample
        self.stereotype_executor = StereotypeExecutorU1()
        self.fs_abs_target_folder = '/home/vagrant/{}'.format(self.stereotype_executor.ftp_client.ftp_root)  # target ftp_client dir absolute path

        # self.data_generator = DataGenerator()

        # start the monitoring stuff. # todo
        # send to impala always...!!!

    def hello(self):
        print 'hello world'
        return 'hello world response'

    def warmup(self):
        print 'warm up'
        print FS_SNAPSHOT_PATH
        print STEREOTYPE_RECIPES_PATH
        receipt = STEREOTYPE_RECIPES_PATH + self.stereotype
        print receipt
        print 'init_stereotype_from_recipe'
        if self.is_warmup is False:
            self.stereotype_executor.initialize_from_stereotype_recipe(receipt)
            print 'init fs & migrate to sandbox'
            self.stereotype_executor.create_fs_snapshot_and_migrate_to_sandbox()
            self.is_warmup = True
        else:
            print 'already warmed-up'
        return 'warm up response'

    def runtest(self):
        print 'run test'
        if self.is_warmup:
            self.stereotype_executor.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
            # TODO loop
            operations = 10
            for i in range(operations):
                self.stereotype_executor.execute()
                print colored("doOps {}/{}".format(i, operations), 'red')
        else:
            return 'need warmup 1st!'
        return 'run test response'



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

    rmq_url = 'amqp://benchbox:benchbox@10.30.236.141/'
    dummyhost = None

    # start the ftp sender


    #
    stereotype_receipt = 'backupsample'

    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost, 'executor')
    executor = ExecuteRMQ(rmq_url, queue_name, stereotype_receipt)
    executor.listen()
