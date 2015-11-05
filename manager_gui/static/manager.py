#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import zerorpc
import multiprocessing
from zerorpc import zmq
import subprocess
import json
import urlparse
import urllib
import nmap

# manager import
from ConfigParser import SafeConfigParser

from argparse import ArgumentParser
import shlex
# import psycopg2
import threading
from multiprocessing.pool import ThreadPool
from subprocess import Popen, PIPE
import traceback, time, sys, os
import random, numpy
from multiprocessing import Pool
import csv
import pxssh
import getpass
from manager_constants import SANDBOX_STATIC_IP, BENCHBOX_STATIC_IP, VAGRANT_DEFAULT_LOGIN



# importar el init.py
class ManagerOps():
    # hosts
    # credentials
    # config

    # tenir un fitxer de status, per no torna a repetir proc?s

    HOST_RUN_STATUS = {}
    HOST_STATUS = {}

    def __init__(self):
        print 'ManagerExecutive'

    def setup(self, args):
        print 'ManagerOps {}'.format(args['cmd'][0])

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
        # print h
        hostname = args['hostname'][0]
        # print hostname
        if not self.HOST_STATUS.has_key(hostname):
            # print 'dont have {}'.format(hostname)
            self.HOST_STATUS[hostname] = {}
        else:
            print 'have {}'.format(hostname)

        self.t1downloadBenchBox(h, hostname)
        self.t2installVagrantVBox(h, hostname)
        self.t3downloadVagrantBoxImg(h, hostname)
        self.t4assignStereoTypeToProfile(h, hostname)
        self.t5assignCredentialsToProfile(h, hostname)
        self.t6assignSyncServer(h, hostname)

        return self.HOST_STATUS[hostname]

    def test(self, args):
        # print 'Test args'
        # print args
        # if self.HOST_STATUS[hostname]

        h = {
            'ip': args['ip'][0],
            'passwd': args['login'][0],
            'user': args['login'][0],
            'profile': args['profile'][0],
        }

        # todo choose profile priority default or Execute arguments
        test = {
            'folder': args['test[testFolder]'][0],
            'profile': args['test[testProfile]'][0],
            'operations': args['test[testOps]'][0],
            'client': args['test[testClient]'][0],
            'interval': args['test[testItv]'][0],
        }

        # print test
        # print 'tell benchBox at dummy host to run Test'
        # str_cmd = './monitor/startMonitor.sh'
        str_cmd = 'cd /home/vagrant/workload_generator && ./executor.py -o {} -p {} -t {} -f {} -x {}'.format(test['operations'], test['profile'], test['interval'], test['folder'], test['client'])
        # print str_cmd
        self.rmibenchBox(h['ip'], h['user'], h['passwd'], str_cmd)

    def t1downloadBenchBox(self, h, hostname):  # tell all the hosts to download BenchBox
        if self.HOST_STATUS[hostname].has_key('t1downloadBenchBox'):
            return True
        # print 't1downloadBenchBox'
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
                  "" % h['passwd']
        # # print str_cmd

        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)  # utilitzar un worker del pool
        self.HOST_STATUS[hostname]['t1downloadBenchBox'] = True
        '''
        version pool
        '''
        # print 't1downloadBenchBox/OK: {}'.format(hostname)

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
        # print 't2installVagrantVBox/OK: {}'.format(hostname)

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
        # if self.HOST_STATUS[hostname].has_key('t4assignStereoTypeToProfile'):
        #    # print 'HAS true'
        #    return True
        # print 't4assignStereoTypeToProfile'
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
        # print 't4assignStereoTypeToProfile/OK: {} :: {}'.format(hostname, h['profile'])

    def t5assignCredentialsToProfile(self, h, hostname):
        # if self.HOST_STATUS[hostname].has_key('t5assignCredentialsToProfile'):
        #    # print 'HAS true'
        #    return True
        # print 't5assignCredentialsToProfile'
        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox; " \
                  "git pull; " \
                  "cd vagrant; " \
                  "echo '%s' > ss.stacksync.key; " \
                  "echo '%s' > ss.owncloud.key; " \
                  "echo '%s' > hostname; " \
                  "echo 'Run: clients configuration scripts: '; " \
                  "cd scripts; " \
                  "./config.owncloud.sh; " \
                  "./config.stacksync.sh; " \
                  "echo 'clients configuration files generated'; " \
                  "fi; " % (h['cred_stacksync'], h['cred_owncloud'], hostname)
        # # print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t5assignCredentialsToProfile'] = True
        # print 't5assignCredentialsToProfile/OK: {}'.format(hostname)

    def t6assignSyncServer(self, h, hostname):
        # if self.HOST_STATUS[hostname].has_key('t6assignSyncServer'):
        #    # print 'HAS true'
        #    return True
        # print 't6assignSyncServer'
        # # print 'sserver'
        # # print config
        owncloud_ip = h['owncloud-ip']
        stacksync_ip = h['stacksync-ip']

        str_cmd = "" \
                  "if [ -d BenchBox ]; then " \
                  "cd BenchBox/vagrant; " \
                  "echo '%s' > ss.stacksync.ip; " \
                  "echo '%s' > ss.owncloud.ip; " \
                  "fi; " % (stacksync_ip, owncloud_ip)

        # # print str_cmd
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        self.HOST_STATUS[hostname]['t6assignSyncServer'] = True
        # print 't6assignSyncServer/OK {} '.format(hostname)

    def vagrantDown(self, args):
        # if self.HOST_STATUS[hostname]
        # print "VAGRANT DOWN ..................................................."
        # print args
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
        # print 'run: Call Vagrant DOWN at host: {}'.format(hostname)
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
        # print h
        hostname = args['hostname'][0]
        # print hostname
        """
        if self.HOST_STATUS.has_key(hostname):
            # print 'setup exists'
        else:
            # print 'setup required'

        if len(self.HOST_STATUS[hostname]) == 6:
            for s in self.HOST_STATUS[hostname]:
                if self.HOST_STATUS[hostname][s]:
                    continue
                else:
                    self.HOST_RUN_STATUS[hostname] = 'host setup error';  # use run code...
                    break
        else:
            self.HOST_RUN_STATUS[hostname] = 'host not setup {}'.format(len(self.HOST_STATUS[hostname]));

        self.HOST_RUN_STATUS[hostname] = 'host ready to start!'
        """
        # if not hasattr(self.HOST_STATUS[hostname],'vagrantUp'): return True

        # print 'run: Call Vagrant init at host: {}'.format(hostname)
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
        # # print str_cmd
        # print str_cmd
        # print h
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        #

        # print 'host running!!!'
        self.HOST_RUN_STATUS[hostname] = True
        # print 'run/OK {}/{}'.format(hostname, self.HOST_RUN_STATUS[hostname])

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
        # print h
        hostname = args['hostname'][0]
        # print hostname
        # print 'tell sandBox at dummy host to start SocketListener'
        str_cmd = './monitor/startMonitor.sh'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
        # have session at the dummy host

    def clientStacksyncUp(self, args):

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
        # print h
        hostname = args['hostname'][0]
        # print hostname
        # print 'tell sandBox at dummy host to start client StackSync'
        str_cmd = 'nohup /usr/bin/stacksync &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
        # have session at the dummy host

    def clientStacksyncDown(self, args):

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
        # print h
        hostname = args['hostname'][0]
        # print hostname
        # print 'tell sandBox at dummy host to clear the client StackSync'
        str_cmd = '/usr/bin/stacksync clear &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
        # have session at the dummy host


    def clientOwncloudUp(self, args):

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

        str_cmd = 'nohup /vagrant/owncloud.sh &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
        # have session at the dummy host

    def requestStatus(self, args):
        # print "<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<STATUS"
        # print "request status to sandBox or benchBox"
        # print args
        result = None
        if args['target'] is None:
            print "no target specified"
        else:
            hostname = args['ip'][0]
            username = args['login'][0]
            password = username
            str_cmd = args['status'][0]
            # print username
            # print hostname
            # print password
            # print str_cmd

            result = self.rmiStatus(hostname, username, password, str_cmd, args['target'][0])

        # print "STATUS>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>"
        return result

    def start_node_server(self, h):
        # print 'run the nodejs monitor server at each Dummy Host'

        str_cmd = "cd BenchBox/monitor; " \
                  "nohup /usr/local/bin/npm start & "
        self.rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        # print 'nodeserver running at {}:{}'.format(h['ip'], '5000')


    def rmi(self, hostname, login, passwd, cmd, callback=None):
        while True:
            try:
                # # print 'try'
                # options = {"StrictHostKeyChecking": "no", "UserKnownHostsFile": "/dev/null", "timeout": "3600"}
                s = pxssh.pxssh()
                s.login(hostname, login, passwd)
                s.timeout = 3600  # set timeout to one hour
                s.sendline('who')
                s.prompt()  # match the prompt
                #s.before
                s.sendline(cmd)  # run a command
                s.prompt()
                # s.login('192.168.56.101','vagrant', 'vagrant')
                last_output = s.before  # # # print everyting before the prompt
                s.logout()
                # # print 'end try'
            except pxssh.ExceptionPxssh, e:
                # # print "pxssh failed on login."
                # # print str(e)
                # # print 'error'
                continue
            break
        #print "BEFORE:"
        #s.before
        print "LAST: OUTPUT"
        print last_output
        return last_output

    # relay ssh
    def rmisandBox(self, hostname, login, passwd, cmd, callback=None):
        sandboxIP = SANDBOX_STATIC_IP
        sandboxUser = VAGRANT_DEFAULT_LOGIN
        sandboxPass = VAGRANT_DEFAULT_LOGIN
        str_cmd = " " \
                  'sshpass -p {} ssh -f -n -o StrictHostKeyChecking=no {}@{} "{}"' \
                  " ".format(sandboxPass, sandboxUser, sandboxIP, cmd)

        # return "asdasdf"
        return self.rmi(hostname, login, passwd, str_cmd)


    def rmibenchBox(self, hostname, login, passwd, cmd, callback=None):
        benchboxIP = BENCHBOX_STATIC_IP
        benchboxUser = VAGRANT_DEFAULT_LOGIN
        benchboxPass = VAGRANT_DEFAULT_LOGIN
        str_cmd = " " \
                  'sshpass -p {} ssh -f -n -o StrictHostKeyChecking=no {}@{} "{}"' \
                  " ".format(benchboxPass, benchboxUser, benchboxIP, cmd)

        # return 'asdf'
        return self.rmi(hostname, login, passwd, str_cmd)

    # this is auxiliary rmi function has ssh -f -n unset
    def rmiStatus(self, hostname, login, passwd, cmd, localhost):
        # # print localhost
        if localhost == 'localhost':
            # # print "LOCALHOST_::"
            result = self.rmi(hostname, login, passwd, cmd)
            str = result
            print result
            result = str.split('\n', 1)  # split once
            return result[1]
        elif localhost == 'sandBox':
            # # print "SANDBOX_::"
            boxIP = SANDBOX_STATIC_IP
        elif localhost == 'benchBox':
            # # print "BENCHBOX_::"
            boxIP = BENCHBOX_STATIC_IP


        boxUser = VAGRANT_DEFAULT_LOGIN
        boxPass = VAGRANT_DEFAULT_LOGIN

        str_cmd = " " \
                  'sshpass -p {} ssh -o StrictHostKeyChecking=no {}@{} "{}"' \
                  " ".format(boxPass, boxUser, boxIP, cmd)
        # return 'asdf'
        result = self.rmi(hostname, login, passwd, str_cmd)
        str = result
        # # print result
        result = str.split(cmd, 1)
        # # print "INTO: "
        # # print result[1]
        return result[1]



class Manager(object):
    hosts = None
    config = None

    ops = ManagerOps()

    def loadHosts(self):
        print 'loadHosts'

    def loadConfig(self):
        print 'loadConfig'


    def hello(self, name):
        print "Request: -> hello {}".format(name)
        return "Response: -> client: Hello from manager, %s" % name

    def goodbye(self, name):
        # # print 'Request: -> goodbye {}'.format(name)
        return "Response: -> client: Goodbye from manager, %s" % name

    def start(self, name):
        # # print 'Request: -> start {}'.format(name)
        return "Response: -> client: Start from manager, %s" % name

    def cmd(self, name):
        str = urllib.quote_plus(name)
        # # print name
        # # print str
        # # print 'Request: -> cmd {}'.format(name)
        output = subprocess.check_output(['bash', '-c', urllib.unquote_plus(name)])
        return output.split('\n')


    def list(self, name):
        # # print 'Request: -> list {}'.format(name)
        bashCommand = "ls {}".format(name)
        output = subprocess.check_output(['bash', '-c', bashCommand])
        return output.split('\n')

    def bad(self):
        raise Exception('xD')

    def nmap(self, port, ip):
        # # print 'Request: -> ping {}:{}'.format(ip, port)
        output = subprocess.check_output(['nmap', '-p', port, ip])

        result = output.split('\n')
        # # print result
        if len(result) > 5:
            if result[5].split()[1] == 'open':
                # # print result[5]
                # # print result[5].split()[1]
                return True
        return False


    def rpc(self, url):
        # # print 'Request: -> rpc to dummyhost'
        # # # print url # full url

        str = urlparse.urlparse(url)
        argslist = urlparse.parse_qs(str.query)
        toExecute = getattr(self.ops, argslist['cmd'][0])

        # # print argslist['cmd'][0]
        # # print getattr(self.ops, argslist['cmd'][0])
        t = threading.Thread(target=toExecute, args=(argslist,))
        t.start()
        result = None # None Blocking
        # # print 'command {}/--->FINISH'.format(argslist['cmd'][0])
        argslist['result'] = result;
        return argslist


    def status(self, url):
        # # print 'Request: -> rpc to dummyhost'
        str = urlparse.urlparse(url)
        argslist = urlparse.parse_qs(str.query)
        toExecute = self.ops.requestStatus
        # print argslist['status'][0]

        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(toExecute, (argslist,))
        # print "ASYNC_RESULT: ", async_result
        try:
            #async_result.join()

            # print async_result
            result = async_result.get()
            # print result
        except:
            # # print "got indexError"
            #result = "1 indexError"
            raise
        # print result

        #result = toExecute(argslist)

        # print 'command {}/--->FINISH'.format(argslist['cmd'][0])
        argslist['result'] = result;
        return result


def ManagerRPC():
    # print 'ManagerRPC instance'
    s = zerorpc.Server(Manager(), pool_size=4)  # numero de cpu
    server_address = "tcp://0.0.0.0:4242"
    s.bind(server_address)
    s.run()


def main():
    '''
    process = multiprocessing.Process(target=ManagerRPC())
    process.start()
    '''
    # print 'ManagerRPC instance'
    s = zerorpc.Server(Manager(), pool_size=10)  # numero de cpu
    server_address = "tcp://0.0.0.0:4242"
    s.bind(server_address)
    s.run()


if __name__ == "__main__":
    # print "Start manager"
    main()
    # print "Finish manager"
