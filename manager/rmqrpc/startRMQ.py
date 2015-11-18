#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import urlparse
import pika
from manager_constants import RABBIT_MQ_URL

class RabbitMqProxy(object):

    def __init__(self, rmq_url):
        self.rmq_url =rmq_url

    # ACTION CONTROLLER
    def upate_status(self, status):
        print 'update_status_to: {}'.format(status)
        return 'MANAGER-ACKED: {}'.format(status)

    def on_request(self, ch, method, props, body):

        print " [.] status(%s)"  % (body,)

        response = self.update_status(body)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

    def start(self):
        print 'RabbitMQ instance'
        url_str = self.rmq_url
        url = urlparse.urlparse(url_str)

        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
        ))

        # DECLARATION
        channel = connection.channel()
        channel.queue_declare(queue='status_log')

        # CONSUMERS
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.on_request, queue='status_log')

        print " [x] Awaiting RPC requests"
        channel.start_consuming()


# todo : define update rabbitmq task feedback to the manager web-view...


def main():

    print "RMQ : Init"
    rmp = RabbitMqProxy(RABBIT_MQ_URL)
    print "RMQ : start"
    rmp.start()



if __name__ == "__main__":

    main()
