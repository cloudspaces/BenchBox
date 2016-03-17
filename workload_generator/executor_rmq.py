#!/usr/bin/env python
import fcntl
import pika
import os
import sys
import urlparse
import time
import signal
import json

from rmq_executor.Commands import Commands


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

class ExecuteRMQ(object):
    def __init__(self, rmq_url='', host_queue='', profile=''):
        print "Executor operation consumer: "
        url = urlparse.urlparse(rmq_url)
        self.profile = profile
        self.actions = Commands(profile)
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
        # print " [on_request] ch {} meth {} props {} body {}".format(ch, method, props, body['cmd'])
        # todo implementar els handler vagrantUp i vagrantDown
        output = None
        try:
            toExecute = getattr(self.actions, body['cmd'])
            # print toExecute # la comanda que s'executara
            # lo ideal es que aixo no sigui un thread per que les peticions s'atenguin fifo
            # t = threading.Thread(target=toExecute)
            print "ExecuteIn  : {}".format(body['cmd'])
            output = toExecute(body)
            print "ExecuteOut : {}".format(output)
            # t.start()
        except AttributeError as e:
            print e.message
            print "ACK: {}".format(body['cmd'])

        response = "{} response: {}: {}".format(self.queue_name, body['cmd'], output)
        print props.reply_to
        print props.correlation_id
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
    stereotype_receipt = 'backupsample'

    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost, 'executor')




    if len(sys.argv) == 1:  # means no parameters
        # DEFAULT: dummy

        # use file look
        singleton()


        executor = ExecuteRMQ(rmq_url, queue_name, stereotype_receipt)
        # todo fer que stereotype_receipt y personal cloud sigui dinamic
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


