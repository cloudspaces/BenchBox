#!/usr/bin/env python
import pika
import uuid
import urlparse
import sys
import getopt
import socket
import threading
import subprocess
import time
import json
class ActionHandler(object):
    def __init__(self):
        print "vagrant handler"

    ''' executed at the dummyhost '''
    def up(self):
        print 'up'
        print subprocess.check_output(["echo", "Hello World!"])

    def pwd(self):
        print 'up'
        print subprocess.check_output(["pwd", "."])

    def vagrantUp(self):
        print 'vagrantUp'
        print subprocess.check_output(["vagrant", "up"])

    def vagrantProvision(self):
        print 'vagrantProvision'
        print subprocess.check_output(['vagrant', 'provision'])

    def vagrantStatus(self):
        print 'vagrantProvision'
        print subprocess.check_output(['vagrant', 'status'])


    ''' executed at the benchBox '''
    def warmUp(self):
        # warmup the sandBox filesystem running the executor
        print 'warmUp'
        str_cmd = "if [ -d ~/workload_generator ]; then; " \
                  "cd ~/workload_generator; " \
                  "python executor.py -o {} -p {} -t {} -f {} -x {} -w 1; " \
                  "fi; ".format(0, 'backupsample', 0, 'stacksync_folder', 'StackSync')
        print subprocess.check_output(['echo', 'warmup'])

    ''' executed at the sandBox '''
    def tearDown(self):
        # clear the sandBox filesystem and cached files
        print 'tearDown'
        str_cmd = "if [ -d ~/output ]; then " \
                  "rm -R ~/output; " \
                  "fi; "
        print subprocess.check_output(['echo', 'teardown'])

class ProduceStatus(object):
    def __init__(self, rmq_url='localhost', queue_name = 'status_manager'):
        self.rmq_url = rmq_url
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(rmq_url))
        else:
            print 'RabbitMQ instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname,
                virtual_host=url.path[1:],
                credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            print "OK"
            self.response = body
        else:
            print "Not Match corr_id"

    def call(self, message, new_host):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to = self.callback_queue,
                                       correlation_id = self.corr_id,
                                   ),
                                   body=json.dumps({"host": new_host, "status": message}))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

class ConsumeAction(object):
    vagrant_ops = ActionHandler()
    def __init__(self, rmq_url, host_queue):
        print "Dummy Peer Worker"
        self.rmq_url = rmq_url
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(rmq_url))
        else:
            print 'Worker instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.host_queue = host_queue
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.host_queue)

    def on_request(self, ch, method, props, body):
        print " [on_request] {} ".format(body)
        # todo implementar els handler vagrantUp i vagrantDown
        try:
            toExecute = getattr(self.vagrant_ops, body)
            print toExecute
            t = threading.Thread(target=toExecute)
            t.start()
        except AttributeError as e:
            # print e.message
            print "ACK: {}".format(body)

        response = "response from: {}".format(body)
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
        self.channel.basic_consume(self.on_request, queue=self.host_queue)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()


def bash_command(cmd):
    subprocess.Popen(['/bin/bash', '-c', cmd])
    # -c command starts to be read from the first non-option argument

def parse_args(argv):

    print "Arguments: {}".format(argv)
    try:
        opts, args = getopt.getopt(argv, "hm:,t:", ["msg=" , "topic="])
    except getopt.GetoptError:
        print '*.py -m <msg> -t <topic>'
        sys.exit(2)

    msg = None
    top = None
    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-i", "--msg"):
            msg = arg
        elif opt in ("-t", "--topic"):
            top = arg
    print msg, top
    return msg, top



if __name__ == '__main__':
    ''' dummy host says hello to the manager '''
    status_msg, topic = parse_args(sys.argv[1:])

    # rmq_url = 'localhost'  # 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy'
    rmq_url = 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy'
    status_exchanger = 'status_exchanger'

    emit_status_rpc = ProduceStatus(rmq_url)

    hostname = socket.gethostname()

    if status_msg is None:
        status_msg = "Hello from {} ".format(hostname)

    if topic is None:
        topic = hostname

    try:  # this means that its a dummyhost
        with open('./hostname', 'r') as f:
            dummyhost = f.read().splitlines()[0]

    except: # this means that its sandBox or benchBox
        with open('/vagrant/hostname', 'r') as f:
            dummyhost = f.read().splitlines()[0]

    # dummyhost = hostname

    host_queue = "{}.{}".format(dummyhost, hostname)
    # status_msg

    print " [x] emit: emit_status_rpc.call({})".format(host_queue)
    response = emit_status_rpc.call(status_msg, host_queue)
    print " [.] Got %r" % (response,)

    ''' crear una cua amb el propi host name de tipus direct '''
    print "START DummyRabbitStatus Worker"
    consumer_rpc = ConsumeAction(rmq_url, host_queue)
    consumer_rpc.listen()
    ''' dummy host does all the following setup operations '''