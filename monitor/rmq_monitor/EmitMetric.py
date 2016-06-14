import calendar
import json
import urlparse

import math
import psutil
import pika
import time
import os

import subprocess
from py_sniffer.TrafficMonitor import TrafficMonitor


class EmitMetric(object):
    def __init__(self, hostname="", personal_cloud="", receipt=""):

        self.personal_cloud_ip = personal_cloud["ip"]
        self.personal_cloud_port = personal_cloud["port"]
        self.personal_cloud = personal_cloud["name"]
        self.receipt = receipt

        if os.name == 'nt':
            pc_folders = {
                'stacksync': '/Users/vagrant/stacksync_folder',
                'dropbox': '/Users/vagrant/Dropbox'
            }
        elif os.name == 'posix':
            pc_folders = {
                'stacksync': 'stacksync_folder',
                'dropbox': 'Dropbox',
                'owncloud': 'owncloud_folder',
                'mega': 'mega_folder'
            }

        # when capturing from private sync server's its server ip must be forwarded
        self.traffic_monitor = TrafficMonitor(client=self.personal_cloud.lower(), server=self.personal_cloud_ip,
                                              port=self.personal_cloud_port)
        self.traffic_monitor.run()  # intermediari que arranca trafficMonitor i permet realitzar get stats sobre la marcha o reiniciar el monitoreig
        self.personal_folder = pc_folders[self.personal_cloud.lower()]

        self.hostname = hostname
        self.proc = None
        self.prev_metric = None  # keep track of last emited metric
        self.url_str = None

        rmq_path = None
        if os.name == "nt":
            rmq_path = '/Users/vagrant/vagrant/rabbitmq'
        elif os.name == "posix":
            rmq_path = 'rabbitmq'

        with open(rmq_path, 'r') as r:
            url_str = r.read().splitlines()[0]

        self.prev_net_counter = psutil.net_io_counters(pernic=True)['eth0']  # 10.0.2.15 static for each sandBox
        # tornar a crear imatge de windows amb el nom del nic 10.. => eth0  &&  192..=> eth1

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
        #return False  # prevent this
        ##########################################################################################################
        # psutil read metrics
        try:
            # self.proc = psutil.Process(pid)
            process_name = None
            if self.personal_cloud.lower() == "stacksync":
                if os.name == 'nt':
                    process_name = "javaw.exe"
                elif os.name == "posix":
                    process_name = "java"

            elif self.personal_cloud.lower() == "dropbox":
                if os.name == 'nt':
                    process_name = "Dropbox.exe"
                elif os.name == "posix":
                    process_name = "dropbox"
            elif self.personal_cloud.lower() == "owncloud":
                process_name = "owncloudcmd"
            elif self.personal_cloud.lower() == 'mega':
                process_name = "megacmd"

            if self.proc is None or self.proc.pid != pid:
                self.proc = psutil.Process(pid)

            if process_name == self.proc.name() or "owncloudcmd" == process_name or "megacmd" == process_name:
                print "OKEY match {} == {}".format(self.proc.name(), process_name)
            else:
                print "sync client does not match: {}".format(process_name)
                return False

        except Exception as ex:
            print "sync client is not running! {}".format(pid)
            print ex.message
            return False  # exit as the process is not alive.

        ##########################################################################################################
        print "PID: {} [{}]".format(pid, self.personal_cloud.lower())
        try:
            if self.personal_cloud.lower() == "stacksync":
                # todo lookup for stacksync process here => using psutil
                cpu_usage = int(math.ceil(self.proc.cpu_percent(0)))
                ram_usage = self.proc.memory_info().rss
                metrics['cpu'] = cpu_usage
                metrics['ram'] = ram_usage
            elif self.personal_cloud.lower() == "owncloud":
                cpu_usage = int(math.ceil(self.proc.children()[0].cpu_percent(interval=1)))
                ram_usage = self.proc.children()[0].memory_info().rss
                metrics['cpu'] = cpu_usage
                metrics['ram'] = ram_usage
            elif self.personal_cloud.lower() == "mega":
                cpu_usage = int(math.ceil(self.proc.children()[0].cpu_percent(interval=1)))
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
            elapsed_time = (curr_time - last_time) / 1000  # segons
            for key, value in curr_net_counter.__dict__.items():
                metrics[key] = (value - getattr(self.prev_net_counter, key)) / elapsed_time  # unit is seconds
            self.prev_net_counter = curr_net_counter
        # assign hard drive usage metric

        if os.name == "nt":
            drive_usage = "1234"
        elif os.name == "posix":
            drive_usage_cmd = ['/usr/bin/du', '-ks', '/home/vagrant/{}'.format(self.personal_folder)]
            drive_usage_output = subprocess.Popen(drive_usage_cmd, stdout=subprocess.PIPE)
            drive_usage = drive_usage_output.stdout.read()
        try:
            metrics['disk'] = int(drive_usage.split('\t')[0])  # kilo bytes cast string to int
        except Exception as ex:
            print "invalid literal for... memory unit"
            metrics['disk'] = 1
        # assign add folder num of files metric

        if os.name == "nt":
            num_files = "123"
        elif os.name == "posix":
            find_cmd = '/usr/bin/find /home/vagrant/{} -type f'.format(self.personal_folder).split()
            proc_find = subprocess.Popen(find_cmd, stdout=subprocess.PIPE)
            wc_cmd = '/usr/bin/wc -l'.split()
            proc_wc = subprocess.Popen(wc_cmd, stdin=proc_find.stdout, stdout=subprocess.PIPE)
            num_files = proc_wc.communicate()[0]
        try:
            metrics['files'] = int(num_files.split('\t')[0])
        except Exception as ex:
            print "invalid literal for... file counter"

        net_stats = self.traffic_monitor.notify_stats()
        # z = dict(x.items() + y.items()) => metrics
        # envez de esto dict join
        metrics['data_rate_size_up'] = net_stats['data_rate']['size_up']
        metrics['data_rate_size_down'] = net_stats['data_rate']['size_down']
        metrics['data_rate_pack_up'] = net_stats['data_rate']['pack_up']
        metrics['data_rate_pack_down'] = net_stats['data_rate']['pack_down']
        metrics['meta_rate_size_up'] = net_stats['meta_rate']['size_up']
        metrics['meta_rate_size_down'] = net_stats['meta_rate']['size_down']
        metrics['meta_rate_pack_up'] = net_stats['meta_rate']['pack_up']
        metrics['meta_rate_pack_down'] = net_stats['meta_rate']['pack_down']

        '''
        {'data_rate':
             {'size_up': 0.471, 'pack_down': 0.00175, 'pack_up': 0.00225, 'size_down': 0.612},
         'meta_rate':
             {'size_up': 0.0, 'pack_down': 0.0, 'pack_up': 0.0, 'size_down': 0.0},
         'time': 1461065156000
        }
        '''

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
