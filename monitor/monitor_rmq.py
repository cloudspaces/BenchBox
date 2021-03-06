#!/usr/bin/env python
import pika
import os
import sys
import urlparse
import signal
import json
import getopt
import time
# from rmq_monitor.Commands import Commands
from rmq_monitor.monitor import Monitor as Commands

def singleton(lockfile="monitor_rmq.pid"):
    if os.path.exists(lockfile):
        with open(lockfile, 'r') as f:
            first_line = f.readline()
            print first_line
        last_pid = first_line
        print "kill_last_pid: {}".format(last_pid)
        print last_pid
        try:
            os.kill(int(last_pid), signal.SIGTERM)  # kill previous if exists
        except Exception as e:
            print e.message
            print "warning not valid pid"
    with open(lockfile, 'w') as f:
        f.write(str(os.getpid()))


class MonitorRMQ(object):
    """
    Instance a RMQ monitor server
    """
    def __init__(self, rmq_url='', host_queue=''):
        """

        :param rmq_url: location of the rmq server
        :param host_queue: monitor queue name @ [hostname].monitor
        :return:
        """
        url = urlparse.urlparse(rmq_url)
        self.hostname = host_queue.split(".")[0]
        self.actions = Commands(hostname=self.hostname)
        self.queue_name = host_queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            heartbeat_interval=0,
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        print 'Joined to queue: {}'.format(self.queue_name)
        self.channel.queue_declare(queue=self.queue_name)

    def on_request(self, ch, method, props, data):
        """
        Handling rabbitmq incomming messages
        :param ch: message channel
        :param method: message method
        :param props: message properties
        :param data: message content {object}
        :return:
        """
        body = json.loads(data)
        output = None
        try:
            toExecute = getattr(self.actions, body['cmd'])
            print "Monitoring Request  : {} ".format(body['cmd'])
            output = toExecute(body)
            print "Monitoring Output : {} ".format(output)
        except AttributeError as ex:
            print ex.message

        response = "Queue[{}] Cmd[{}] Out[{}]".format(self.queue_name, body['cmd'], output)
        print props.reply_to
        print props.correlation_id
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             # properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
        except ex:
            print ex.message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def listen(self):
        self.channel.basic_consume(self.on_request,
                                   no_ack=False,
                                   queue=self.queue_name)
        print "[Consumer] Awaiting RPC requests"
        self.channel.start_consuming()


def parse_args(argv):

    print "Arguments: {}".format(argv)
    try:
        opts, args = getopt.getopt(argv, "hc:,s:,i:", ["client=" , "stereo=", "id="])
    except getopt.GetoptError:
        print '*.py -c <client> -s <stereo> -i <id> '
        sys.exit(2)

    client = None
    stereo = None
    test_idx = None
    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-c", "--client"):
            client = arg
        elif opt in ("-s", "--stereo"):
            stereo = arg
        elif opt in ("-i", "--id"):
            test_idx = int(arg)

    print client, stereo, test_idx
    return client, stereo, test_idx


if __name__ == '__main__':
    print "Monitor_rmq.py [START] {}".format(sys.argv)
    rmq_url = None
    try:
        with open('/vagrant/rabbitmq', 'r') as r:
            rmq_url = r.read().splitlines()[0]
    except Exception as ex:
        print ex.message
        with open('../vagrant/rabbitmq', 'r') as r:
            rmq_url = r.read().splitlines()[0]

    dummyhost = None
    stereotype_receipt = 'backup-heavy'
    try:
        with open('/vagrant/hostname', 'r') as f:
            dummyhost = f.read().splitlines()[0]
    except Exception as ex:
        print ex.message
        with open('../vagrant/hostname', 'r') as r:
            dummyhost = r.read().splitlines()[0]

    queue_name = '{}.{}'.format(dummyhost, 'monitor')
    if len(sys.argv) == 1:
        singleton()  # apply singleton
        connection_try = 0
        while True:
            connection_try += 1
            time.sleep(2)

            print "Try connect to monitor through RabbitMQ "
            print rmq_url, queue_name
            monitor = MonitorRMQ(rmq_url=rmq_url, host_queue=queue_name)
            monitor.listen()
            connection_try = 0
            # try:
            #     print "Try connect to monitor through RabbitMQ "
            #     print rmq_url, queue_name
            #     monitor = MonitorRMQ(rmq_url=rmq_url, host_queue=queue_name)
            #     monitor.listen()
            #     connection_try = 0
            # except Exception as ex:
            #     print "Some connection exception happened... [{}]".format(connection_try)
            #     print ":: {} ::".format(ex.message)
            # finally:
            #     if connection_try > 2:
            #         break  # exit the infinit loop

    else:  # con parametros


        # personal cloud
        # receta
        #

        personal_cloud, stereo_recipe, test_id = parse_args(sys.argv[1:])

        # print "monitor_rmq.OLD.py"
        #
        # dummyhost = None
        # stereotype_receipt = 'backup-heavy'
        # try:
        #     with open('/vagrant/hostname', 'r') as f:
        #         dummyhost = f.read().splitlines()[0]
        # except Exception as ex:
        #     print ex.message
        #     with open('../vagrant/hostname', 'r') as r:
        #         dummyhost = r.read().splitlines()[0]

        actions = Commands(personal_cloud=personal_cloud, hostname=dummyhost)
        body = {
            "msg": {
                "test": {
                    "testClient": personal_cloud,
                    "testProfile": stereo_recipe
                },
                "test_id": test_id,
                "{}-ip".format(personal_cloud.lower()): "",
                "{}-box-port".format(personal_cloud.lower()): ""
            }
        }
        while True:
            print 'write command: hello|warmup|start|stop'
            teclat = raw_input()
            print teclat
            try:
                toExecute = getattr(actions, teclat)
                print toExecute

                output = toExecute(body)
            except AttributeError as e:
                print e.message
                print "ACK: {}".format(teclat)
            time.sleep(1)