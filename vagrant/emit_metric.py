#!/usr/bin/env python
import pika
import random
import uuid
import urlparse
import sys
import time
import json
import calendar
import socket
class EmitMetric(object):
    def __init__(self):
        url_str = None
        with open('rabbitmq','r') as r:
            url_str = r.read().splitlines()[0]

        url = urlparse.urlparse(url_str)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))

        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='metrics', type='fanout')

    def emit(self, key, value):
        # msg = '{} {} {}'.format(key, value, self.tsNow())
        # msg = '{} {} {}'.format(key, value, self.tsNow())
        metrics = {'cpu': random.randint(0, 100),
                'ram': random.randint(0, 100),
                'net': random.randint(0, 100),
                'time': calendar.timegm(time.gmtime()) * 1000}
        tags = {
            'profile': 'backupsample',
            'credentials': 'pc_credentials'
        }
        data = {
            'metrics': metrics,
            'tags': tags
        }

        msg = json.dumps(data)
        print msg

        self.channel.basic_publish(
            exchange='metrics',
            routing_key=socket.gethostname(),
            body=msg)

    def tsNow(self):
        return int(time.time())

if __name__ == '__main__':
    print " [x] emit(key, value)"
    print " [x] emit({}, {})".format(sys.argv[1], sys.argv[2])
    metric_emiter = EmitMetric()
    response = metric_emiter.emit(sys.argv[1], sys.argv[2])
