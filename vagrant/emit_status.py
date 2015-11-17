#!/usr/bin/env python
import pika
import uuid
import urlparse
import sys


class FibonacciRpcClient(object):
    def __init__(self):

        url_str = 'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy'
        url = urlparse.urlparse(url_str)

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
        ))
        #'amqp://vvmlshzy:UwLCrV2bep7h8qr6k7WhbsxY7kA9_nas@moose.rmq.cloudamqp.com/vvmlshzy'))

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
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to = self.callback_queue,
                                       correlation_id = self.corr_id,
                                   ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

if __name__ == '__main__':
    ''' dummy host says hello to the server '''
    print "Arguments: "
    args = str(sys.argv)
    fibonacci_rpc = FibonacciRpcClient()
    print " [x] Requesting fib(30)"
    response = fibonacci_rpc.call(args)
    print " [.] Got %r" % (response,)


    ''' dummy host does all the following setup operations '''