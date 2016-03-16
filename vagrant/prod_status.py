#!/usr/bin/env python
import pika
import uuid
import urlparse
import sys
import getopt
import socket
import subprocess
import json

import os
import signal

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)

class ActionHandler(object):
    def __init__(self):
        print "vagrant handler"
        self.hostname = socket.gethostname()

    ''' executed at the dummyhost '''
    def up(self):
        print 'up'
        output =  subprocess.check_output(["echo", "Hello World!"])
        return output

    def pwd(self):
        print 'up'
        return subprocess.check_output(["pwd", "."])

    def vagrantStart(self):
        print 'vagrantStart'
        self.vagrantUp()
        self.vagrantProvision()
        print 'vagrantStart/OK'

    def vagrantUp(self):
        print 'vagrantUp'
        print subprocess.check_output(["vagrant", "up"])
        return 'vagrantUp/OK'

    def vagrantProvision(self):
        print 'vagrantProvision'
        print subprocess.check_output(['vagrant', 'provision'])
        return 'vagrantProvision/OK'

    def vagrantStatus(self):
        print 'vagrantProvision'
        print subprocess.check_output(['vagrant', 'status'])
        return 'vagrantProvision/OK'

    def vagrantDestroy(self):
        print 'vagrantDestroy'
        print subprocess.check_output(['vagrant', 'destroy', '-f']) # vagrant destroy -f # force yes
        return 'vagrantDestroy/OK'


    ''' executed at the benchBox, nota: el script esta en el directorio root /vagrant'''
    def warmUp(self):
        # warmup the sandBox filesystem booting the executor.py
        output =  ""
        try:
            print 'warmUp'
            str_cmd = "nohup python ~/workload_generator/executor_rmq.py &> nohup_executor_rmq.out& "
            # output = subprocess.check_output(['echo', 'warmup'])
            output = bash_command(str_cmd)
        except:
            print "something failed"
        finally:
            return output
    def tearDown(self):
        # clear the sandBox filesystem and cached files
        print 'tearDown'
        try:
            output = ''
            if self.hostname == 'sandBox':              # todo if sandbox
                check_kill_process("monitor_rmq.py")
            elif self.hostname == 'benchBox':           # todo if benchBox
                check_kill_process("executor_rmq.py")
                # aprovechar el metodo que habia en github
            else:
                return 'unhandled hostname: {}'.format(self.hostname)
        except:
            print "something failed"
        finally:
            return output

    ''' executed at the sandBox '''
    def monitorUp(self):
        # start the metrics listener for monitoring
        output = ""
        try:
            print 'monitorUp'
            str_cmd = "nohup python ~/monitor/monitor_rmq.py &> nohup_monitor_rmq.out& "
            output = bash_command(str_cmd)
        except:
            print "something failed"
        finally:
            return output
    def execute(self):
        print 'execute'
        return bash_command('whoami')


class ProduceStatus(object):
    def __init__(self, rmq_url='localhost', queue_name = 'status_manager'):
        print 'prod: {}'.format(rmq_url)
        self.rmq_url = rmq_url
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=rmq_url,
                    heartbeat_interval=5
            ))
        else:
            print 'RabbitMQ instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname,
                heartbeat_interval=5,
                virtual_host=url.path[1:],
                credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        result = self.channel.queue_declare()

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

    def close(self):
        print 'close connection'
        self.connection.close()


class ConsumeAction(object):
    vagrant_ops = ActionHandler()
    def __init__(self, rmq_url, host_queue):
        print "Dummy Peer Worker"
        self.rmq_url = rmq_url
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=rmq_url,
                    heartbeat_interval=5
            ))
        else:
            print 'Worker instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname,
                    heartbeat_interval=5,
                    virtual_host=url.path[1:],
                    credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.host_queue = host_queue
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_declare(queue=self.host_queue)

    def on_request(self, ch, method, props, data):
        body = json.loads(data)
        print " [on_request] {} => {}".format(body['cmd'], self.host_queue)
        # todo implementar els handler vagrantUp i vagrantDown
        try:
            toExecute = getattr(self.vagrant_ops, body['cmd'])
            print toExecute
            # lo ideal es que aixo no sigui un thread per que les peticions s'atenguin fifo
            # t = threading.Thread(target=toExecute)
            output = toExecute()
            # t.start()
        except AttributeError as e:
            # print e.message
            print "ACK: {}".format(body['cmd'])

        response = "{} response: {}: {}".format(self.host_queue, body['cmd'], output)
        print props.reply_to
        print props.correlation_id
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,

                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
        except:
            print "bypass"

        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index
        except:
            print "the sender has been rebooted, so the response will never reach as their id are dynamically changing every time the node server reboots"

    def listen(self):
        self.channel.basic_consume(self.on_request, queue=self.host_queue)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()

"""
Run bash command and return output
"""
def bash_command(cmd):
    child = subprocess.Popen(['/bin/bash', '-c', cmd])
    child.communicate()[0]
    rc = child.returncode
    return rc

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

    rmq_url = None
    with open('rabbitmq','r') as r:
        rmq_url = r.read().splitlines()[0]

    status_exchanger = 'status_exchanger'
    emit_status_rpc = ProduceStatus(rmq_url)

    hostname = socket.gethostname()

    if status_msg is None:
        status_msg = "Hello from {} ".format(hostname)

    if topic is None:
        hostname = topic

    try:  # this means that its a dummyhost
        with open('./hostname', 'r') as f:
            dummyhost = f.read().splitlines()[0]

    except: # this means that its sandBox or benchBox
        with open('/vagrant/hostname', 'r') as f:
            dummyhost = f.read().splitlines()[0]

    # dummyhost = hostname

    host_queue = "{}.{}".format(dummyhost, hostname.lower())  # this is the format, that rmq.js target_queue needs!
    # status_msg

    print " [x] emit: emit_status_rpc.call({})".format(host_queue)
    response = emit_status_rpc.call(status_msg, host_queue)
    emit_status_rpc.close()
    print " [.] Got %r" % (response,)

    ''' crear una cua amb el propi host name de tipus direct '''
    print "START DummyRabbitStatus Worker"
    consumer_rpc = ConsumeAction(rmq_url, host_queue)
    consumer_rpc.listen()
    ''' dummy host does all the following setup operations '''