#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import subprocess
import urlparse
import urllib
import threading
from multiprocessing.pool import ThreadPool
import pxssh

import zerorpc
import pika
from termcolor import colored

from manager_constants import SANDBOX_STATIC_IP, BENCHBOX_STATIC_IP, VAGRANT_DEFAULT_LOGIN, RABBIT_MQ_URL
from manager_rpc import manager_rpc
from manager_rmq import manager_rmq


def startZeroRPC():
    # print 'ManagerRPC instance'
    s = zerorpc.Server(manager_rpc(), pool_size=10)  # numero de cpu
    server_address = "tcp://0.0.0.0:4242"
    s.bind(server_address)
    s.run()

def startRabbitMQ(rmq_url):


    url_str = rmq_url
    url = urlparse.urlparse(url_str)

    connection = pika.BlockingConnection(pika.ConnectionParameters(
        host=url.hostname, virtual_host=url.path[1:], credentials=pika.PlainCredentials(url.username, url.password)
    ))

    ## DECLARATION
    channel = connection.channel()
    channel.queue_declare(queue='status_log')


    ## ACTION CONTROLLER
    def fib(n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            return fib(n-1) + fib(n-2)
    def update_status(status):
        print 'update_status_to: {}'.format(status)







        return 'MANAGER-ACKED: {}'.format(status)
    def on_request(ch, method, props, body):
        # body

        print " [.] status(%s)"  % (body,)
        # response = fib(n)

        response = update_status(body)

        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id = \
                                                             props.correlation_id),
                         body=str(response))
        ch.basic_ack(delivery_tag = method.delivery_tag)

    ## CONSUMERS
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(on_request, queue='status_log')

    print " [x] Awaiting RPC requests"
    channel.start_consuming()



if __name__ == "__main__":
    # print "Start manager"
    '''
    Start handling the initial stage of the chain, this starts the emit_status.py at the dummy machines which
    tells the dummy machines to join its routing:key
    '''
    # startZeroRPC()
    startRabbitMQ(RABBIT_MQ_URL)  # status Feedback queue
    # startRabbitMQ(RABBIT_MQ_URL) # queue
    # print "Finish manager"
