import calendar
import json
import random
import urlparse

import math
import psutil
import pika
import time

import subprocess


class EmitMetric(object):

    def __init__(self, hostname="", personal_cloud="", receipt=""):

        self.personal_cloud = personal_cloud
        self.receipt = receipt
        pc_folders = {
            'stacksync': 'stacksync_folder',
            'dropbox': 'Dropbox',
            'owncloud': 'owncloud_folder'
            'mega:' 'mega_folder'
        }

        self.personal_folder = pc_folders[self.personal_cloud.lower()]

        self.hostname = hostname
        self.proc = None
        self.prev_metric = None  # keep track of last emited metric
        url_str = None

        with open('rabbitmq', 'r') as r:
            url_str = r.read().splitlines()[0]

        self.prev_net_counter = psutil.net_io_counters(pernic=True)['eth0']  # 10.0.2.15 static for each sandBox

        url = urlparse.urlparse(url_str)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname,
                heartbeat_interval=5,
                virtual_host=url.path[1:],
                credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange='metrics', type='fanout')

    def emit(self, pid):
        """
        Lookup for the process pid and emit metric
        if exists emit metric
        otherwise skip emit noop
        :param proc: the syncronization client process.
        :return:
        """
        print "Emit with pid: {}".format(pid)
        if pid is None:
            return False
        metrics = {'cpu': 0,
                   'ram': 1,
                   'net': 2,
                   'bytes_sent': 1,
                   'bytes_recv': 1,
                   'packets_sent': 1,
                   'packets_recv': 1,
                   'errin': 0,
                   'errout': 0,
                   'dropin': 0,
                   'dropout': 0,
                   'disk': 0,
                   'files': 0,
                   'time': calendar.timegm(time.gmtime()) * 1000}
        # psutil read metrics
        try:
            # self.proc = psutil.Process(pid)
            process_name = None

            if self.personal_cloud.lower() == "stacksync":
                self.proc = psutil.Process(pid)
                process_name = "java"
            elif self.personal_cloud.lower() == "dropbox":
                self.proc = psutil.Process(pid)
                process_name = "dropbox"
            elif self.personal_cloud.lower() == "owncloud":
                process_name = "owncloudcmd"
                self.proc = psutil.Process(pid) #.children()[0]
            elif self.personal_cloud.lower() == 'mega':
                process_name = "mega"
                self.proc = psutil.Process(pid)


            if process_name == self.proc.name() or "owncloudcmd" == process_name  or "megacmd" == process_name:
                print "OKEY  match {} == {}".format(self.proc.name(), process_name)
            else:
                print "sync  client does not match: {}".format(process_name)
                return False



        except Exception as ex:
            print "sync client is not running! {}".format(pid)
            print ex.message
            return False  # exit as the process is not alive.

        print "PID: {} [{}]".format(pid, self.personal_cloud.lower())
        try:
            if self.personal_cloud.lower() == "stacksync":
                # todo lookup for stacksync process here => using psutil
                cpu_usage = int(math.ceil(self.proc.cpu_percent(0)))
                ram_usage = self.proc.memory_info().rss
                metrics['cpu'] = cpu_usage
                metrics['ram'] = ram_usage
            elif self.personal_cloud.lower() == "owncloud":
                cpu_usage = int(math.ceil(self.proc.children()[0].cpu_percent(0)))
                ram_usage = self.proc.children()[0].memory_info().rss
                metrics['cpu'] = cpu_usage
                metrics['ram'] = ram_usage
            elif self.personal_cloud.lower() == "mega":
                cpu_usage = int(math.ceil(self.proc.children()[0].cpu_percent(0)))
                ram_usage = self.proc.children()[0].memory_info().rss
                metrics['cpu'] = cpu_usage
                metrics['ram'] = ram_usage
            elif self.personal_cloud.lower() == "dropbox":
                # todo lookup for dropbox process here => using psutil
                cpu_usage = int(math.ceil(self.proc.cpu_percent(0)))
                ram_usage = self.proc.memory_info().rss
                metrics['cpu'] = cpu_usage
                metrics['ram'] = ram_usage
        except Exception as e:
            print e.message

        # assign the network usage metric

        if self.prev_metric is not None:
            # do nothing because its the first emit ant there are no previous metric to compare
            # last_net = self.prev_metric['metrics']['net']
            last_time = self.prev_metric['metrics']['time']

            curr_net_counter = psutil.net_io_counters(pernic=True)['eth0']  # read the bytes from somewhere
            curr_time = metrics['time']
            elapsed_time = (curr_time-last_time) / 1000  # segons
            for key, value in curr_net_counter.__dict__.items():
                metrics[key] = (value - getattr(self.prev_net_counter, key)) / elapsed_time  # unit is seconds
            self.prev_net_counter = curr_net_counter
        # assign hard drive usage metric
        drive_usage_cmd =['/usr/bin/du', '-ks', '/home/vagrant/{}'.format(self.personal_folder)]
        drive_usage_output = subprocess.Popen(drive_usage_cmd, stdout=subprocess.PIPE)
        drive_usage = drive_usage_output.stdout.read()
        try:
            metrics['disk'] = int(drive_usage.split('\t')[0])  # kilo bytes cast string to int
        except:
            print "invalid literal for... memory unit"
            metrics['disk'] = 1
        # assign add folder num of files metric
        find_cmd = '/usr/bin/find /home/vagrant/{} -type f'.format(self.personal_folder).split()
        proc_find = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
        wc_cmd = '/usr/bin/wc -l'.split()
        proc_wc = subprocess.Popen(wc_cmd, stdin=proc_find.stdout, stdout=subprocess.PIPE)
        num_files = proc_wc.communicate()[0]
        metrics['files'] = int(num_files.split('\t')[0])

        tags = ''
        if tags == '':
            tags = {
                'profile': self.receipt,
                'credentials': 'pc_credentials',
                'client': self.personal_cloud.lower(),
            }

        data = {
            'metrics': metrics,
            'tags': tags
        }
        self.prev_metric = data  # update the last emited metric

        msg = json.dumps(data)
        print msg

        self.channel.basic_publish(
                exchange='metrics',
                routing_key=self.hostname,
                body=msg)

        return True

