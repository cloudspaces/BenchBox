#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import urlparse
import pika
from manager_constants import RABBIT_MQ_URL

class RabbitMqProxy(object):

    def __init__(self, rmq_url = 'localhost'):
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
        # DECLARATION
        self.channel = self.connection.channel()


    def update_status(self, status):
        print 'update_status_to: {}'.format(status)
        hname, vname, queue = status.split('.')
        AckStatus().ack(hname, queue)
        return 'MANAGER-ACKED: {}'.format(status)


    def on_request(self, ch, method, props, body):
        print "channel, method, props "
        print ch
        print method
        print props
        print body

        response = self.update_status(body)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index

    def start(self):
        self.channel.queue_declare(queue='status_log')
        # CONSUMERS
        # self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue='status_log')
        print " [x] Awaiting RPC requests"
        self.channel.start_consuming()

class AckStatus:

    def __init__(self, rmq_url = 'localhost'):
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
        # DECLARATION
        self.channel = self.connection.channel()
    # todo : define update rabbitmq task feedback to the manager web-view...
    def ack(self, queue, msg):
        print "ack {} ".format(queue)
        self.channel.queue_declare(queue=queue)
        self.channel.basic_publish(exchange='',
                                    routing_key=queue,
                                    body=msg)
        self.connection.close()


def main():

    print "RMQ : StatusManager Instance"
    rmp = RabbitMqProxy(RABBIT_MQ_URL)
    print "RMQ : start"
    rmp.start()



if __name__ == "__main__":

    main()
