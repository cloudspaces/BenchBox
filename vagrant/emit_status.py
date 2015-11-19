#!/usr/bin/env python
import pika
import uuid
import urlparse
import sys
import getopt
import socket
import threading
import subprocess

class VagrantHandlers(object):
    def __init__(self):
        print "vagrant handler"

    def up(self):
        print 'up'
        print subprocess.check_output(["echo", "Hello World!"])

    """
    def halt(self):
        print 'halt'

    def status(self):
        print 'status'

    def destroy(self):
        print 'destroy'
    """

class EmitStatusRpcClient(object):
    def __init__(self, rmq_url = 'localhost'):
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(rmq_url))
            self.rmq_url =rmq_url
        else:
            print 'RabbitMQ instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='status_log',
                                   properties=pika.BasicProperties(
                                       reply_to = self.callback_queue,
                                       correlation_id = self.corr_id,
                                   ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        self.connection.close()
        return self.response


class DummyRabbitHandler(object):

    vagrant_ops = VagrantHandlers()

    def __init__(self, rmq_url, topic):
        print "Dummy Rabbit Handler"
        self.rmq_url =rmq_url
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(rmq_url))
        else:
            print 'RabbitMQ instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.topic = topic
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.topic)

    def on_request(self, ch, method, props, body):
        print " [on_request] {} ".format(body)


        # todo implementar els handler vagrantUp i vagrantDown
        try:
            toExecute = getattr(self.vagrant_ops, body)
            print toExecute
            t = threading.Thread(target=toExecute)
            # exemple peticion up, al final de vagrant up fer que es executi emit status dins del sandBox i del benchBox
            # enlloc de que la queue sigui parcial fer que sigui completa dins del sandBox | benchBox, a fora es nomes hostname
            t.start()
        except AttributeError as e:
            # print e.message
            print "ACK: {}".format(body)
        # t.join()
        response = "response from: {}".format(body)
        ch.basic_publish(exchange='',
                         routing_key=body,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=response)
        ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index

    def listen(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.topic)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()

if __name__ == '__main__':
    ''' dummy host says hello to the server '''
    argv = sys.argv[1:]
    # rmq_url = 'localhost'  # 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy'
    rmq_url = 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy'
    routing_key = 'rpc_queue'

    print "Arguments: {}".format(argv)
    try:
        opts,args = getopt.getopt(argv, "hm:,t:", ["msg=" , "topic="])
    except getopt.GetoptError:
        print '*.py -m <message> -t <topic>'
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-i", "--msg"):
            status_msg = arg
        elif opt in ("-t", "--topic"):
            topic = arg

    emit_status_rpc = EmitStatusRpcClient(rmq_url)
    hostname = socket.gethostname()
    try:
        with open('hostname','r') as f:
            dummyhost = f.read().splitlines()[0]
    except:
        dummyhost = hostname
    composite_msg="{}.{}.{}".format(dummyhost, hostname, status_msg)

    print " [x] emit: emit_status_rpc.call({})".format(composite_msg)
    response = emit_status_rpc.call(composite_msg)
    print " [.] Got %r" % (response,)

    ''' crear una cua amb el propi host name de tipus direct '''
    print "START DummyRabbitStatus Worker"
    rmq_status_server = DummyRabbitHandler(rmq_url, dummyhost)
    rmq_status_server.listen()
    ''' dummy host does all the following setup operations '''