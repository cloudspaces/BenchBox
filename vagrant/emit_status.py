#!/usr/bin/env python
import pika
import uuid
import urlparse
import sys
import getopt
import socket

class EmitStatusRpcClient(object):
    def __init__(self, rmq_url):

        url_str = rmq_url
        url = urlparse.urlparse(url_str)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
        ))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
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
        return self.response

    def close(self):
        self.connection.close()

class DummyRabbitHandler(object):
    def __init__(self, rmq_url, topic):
        print "Dummy Rabbit Handler"

        self.url_str = rmq_url
        url = urlparse.urlparse(self.url_str)
        self.topic = topic
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))


        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.topic)

    def on_request(self, ch, method, props, body):
        n = body
        print " [on_request] {} ".format(n)
        response = "response from: {}".format(n)
        ch.basic_publish(exchange='',
                         routing_key=n,
                         body=response)

    def listen(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.topic)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()

if __name__ == '__main__':
    ''' dummy host says hello to the server '''
    argv = sys.argv[1:]
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
        with open('/vagrant/hostname','r') as f:
            dummyhost = f.read().splitlines()[0]
    except:
        dummyhost = hostname
    composite_msg="{}.{}.{}".format(dummyhost, hostname, status_msg)

    print " [x] emit: emit_status_rpc.call({})".format(composite_msg)
    response = emit_status_rpc.call(composite_msg)
    print " [.] Got %r" % (response,)

    rmq_status_server = DummyRabbitHandler(rmq_url, topic)
    rmq_status_server.listen()
    ''' dummy host does all the following setup operations '''