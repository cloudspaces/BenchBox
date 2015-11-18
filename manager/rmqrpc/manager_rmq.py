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



# importar el init.py
class manager_rmq():

    HOST_RUN_STATUS = {}
    HOST_STATUS = {}

    def __init__(self):
        print 'manager_rmq instance'






























    def setup(self, args):
        print 'ManagerOps {}'.format(args['cmd'][0])

        host_settings = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0],
            'impala-ip': args['impala-ip'][0],
            'graphite-ip': args['graphite-ip'][0]
        }
        print host_settings
        hostname = args['hostname'][0]
        # print hostname
        if not self.HOST_STATUS.has_key(hostname):
            # print 'dont have {}'.format(hostname)
            self.HOST_STATUS[hostname] = {}
        else:
            print 'have {}'.format(hostname)

        print "Start Initial Task"


        '''

        self.t1downloadBenchBox(host_settings, hostname)



        self.t2installVagrantVBox(host_settings, hostname)
        self.t3downloadVagrantBoxImg(host_settings, hostname)
        self.t4assignStereoTypeToProfile(host_settings, hostname)
        self.t5assignCredentialsToProfile(host_settings, hostname)
        self.t6assignSyncServer(host_settings, hostname)
        '''
        return self.HOST_STATUS[hostname]

    def t1downloadBenchBox(self, h, hostname):  # tell all the hosts to download BenchBox
        print 't1downloadBenchBox'
        '''
        Descarregar el repositori de BenchBox i inicialitzar un bootstrap service

        '''
        str_cmd = "" \
                  "echo 'check if Git is installed...'; " \
                  "echo '%s' | sudo -S apt-get install git; " \
                  "echo 'check if BenchBox is installed...'; " \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox;" \
                  "git pull; " \
                  "else " \
                  "git clone --recursive https://github.com/CloudSpaces/BenchBox.git; " \
                  "fi;" \
                  "python vagrant/emit_status.py; " \
                  "" \
                  "" % h['passwd']

        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)  # utilitzar un worker del pool
        print 't1downloadBenchBox/OK: {}'.format(hostname)

    def t2installVagrantVBox(self, h, hostname):  # tell all the hosts to install VirtualBox and Vagrant
        if self.HOST_STATUS[hostname].has_key('t2installVagrantVBox'):
            # print 'HAS true'
            return True
        # print 't2installVagrantVBox'
        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox;" \
                  "git pull; " \
                  "cd vagrant/scripts; " \
                  "echo '%s' | sudo -S ./installVagrantVBox.sh; " \
                  "fi;" \
                  "" % h['passwd']
        # # print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t2installVagrantVBox'] = True

    def t3downloadVagrantBoxImg(self, h, hostname):  # tell the hosts to download Vagrant box to use
        if self.HOST_STATUS[hostname].has_key('t3downloadVagrantBoxImg'):
            # print 'HAS true'
            return True
        # print 't3downloadVagrantBoxImg'
        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox;" \
                  "git pull; " \
                  "cd vagrant/scripts; " \
                  "./installDependencies.sh; " \
                  "fi;" \
                  ""
        # # print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t3downloadVagrantBoxImg'] = True
        # print 't3downloadVagrantBoxImg/OK: {}'.format(hostname)

    def t4assignStereoTypeToProfile(self, h, hostname):
        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox;" \
                  "git pull; " \
                  "cd vagrant; " \
                  "echo '%s' > profile; " \
                  "fi; " % h['profile']

        ## print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t4assignStereoTypeToProfile'] = True

    def t5assignCredentialsToProfile(self, h, hostname):
        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox; " \
                  "git pull; " \
                  "cd vagrant; " \
                  "echo '%s' > ss.stacksync.key; " \
                  "echo '%s' > ss.owncloud.key; " \
                  "echo '%s' > hostname; " \
                  "echo '' > logfile; " \
                  "echo '' > logfile.b; " \
                  "echo '' > logfile.s; " \
                  "echo 'Run: clients configuration scripts: '; " \
                  "cd scripts; " \
                  "./config.owncloud.sh; " \
                  "./config.stacksync.sh;  '%s'" \
                  "echo 'clients configuration files generated'; " \
                  "fi; " % (h['cred_stacksync'], h['cred_owncloud'],  hostname, h['stacksync-ip'])
        # # print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t5assignCredentialsToProfile'] = True

    def t6assignSyncServer(self, h, hostname):
        owncloud_ip = h['owncloud-ip']
        stacksync_ip = h['stacksync-ip']
        impala_ip = h['impala-ip']
        graphite_ip = h['graphite-ip']

        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox/vagrant; " \
                  "echo '%s' > ss.stacksync.ip; " \
                  "echo '%s' > ss.owncloud.ip; " \
                  "echo '%s' > log.impala.ip; " \
                  "echo '%s' > log.graphite.ip; " \
                  "fi; " % (stacksync_ip, owncloud_ip, impala_ip, graphite_ip)

        print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t6assignSyncServer'] = True




    def warmUp(self, args):
        print 'warmUP'
        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        str_cmd = "if [ -d ~/workload_generator ]; then; " \
                  "cd ~/workload_generator; " \
                  "python executor.py -o {} -p {} -t {} -f {} -x {} -w 1; " \
                  "fi; ".format(0, 'backupsample', 0, 'stacksync_folder', 'StackSync')
        print str_cmd
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

    def tearDown(self, args):
        print 'TEARDOWN'
        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        str_cmd = "if [ -d ~/output ]; then " \
                  "rm -R ~/output; " \
                  "fi; "

        self.rmibenchBox(h['ip'], h['user'], h['passwd'], str_cmd)

    def vagrantDown(self, args):
        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        hostname = args['hostname'][0]
        str_cmd = "kill -9 $(pgrep ruby); " \
                  "kill -9 $(pgrep vagrant); " \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox; " \
                  "cd vagrant; " \
                  "vagrant halt; " \
                  "fi; "
        # print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)

    def vagrantUp(self, args):
        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        hostname = args['hostname'][0]
        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox;" \
                  "git pull; " \
                  "cd vagrant; " \
                  "echo '-------------------------------'; " \
                  "ls -l *.box; " \
                  "vagrant -v; " \
                  "VBoxManage --version; " \
                  "echo '-------------------------------'; " \
                  "VBoxManage list runningvms | wc -l > running; " \
                  "vagrant up sandBox; " \
                  "vagrant provision sandBox; " \
                  "vagrant up benchBox; " \
                  "vagrant provision benchBox; " \
                  "else " \
                  "echo 'Vagrant Project not Found!??'; " \
                  "fi;" \
                  ""
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_RUN_STATUS[hostname] = True

    def monitorUp(self, args):

        # if self.HOST_STATUS[hostname]
        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        hostname = args['hostname'][0]
        str_cmd = './monitor/startMonitor.sh'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

    def clientStackSyncUp(self, args):

        # if self.HOST_STATUS[hostname]
        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        hostname = args['hostname'][0]
        str_cmd = 'nohup /usr/bin/stacksync &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

    def clientStackSyncDown(self, args):

        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }
        hostname = args['hostname'][0]
        str_cmd = '/usr/bin/stacksync clear &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)

    def clientOwnCloudUp(self, args):

        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'cred_stacksync': args['cred_stacksync'][0],
            'cred_owncloud': args['cred_owncloud'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0]
        }

        hostname = args['hostname'][0]

        str_cmd = 'nohup /vagrant/owncloud.sh &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
        # have session at the dummy host

    def requestStatus(self, args):
        result = None
        if args['target'] is None:
            print "no target specified"
        else:
            hostname = args['ip'][0]
            username = args['login'][0]
            password = username
            str_cmd = args['status'][0]

            result = self.rmiStatus(hostname, username, password, str_cmd, args['target'][0])

        return result

    def start_node_server(self, h):

        str_cmd = "cd BenchBox/monitor; " \
                  "nohup /usr/local/bin/npm start & "
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)

