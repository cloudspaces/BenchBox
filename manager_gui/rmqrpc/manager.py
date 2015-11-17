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

from manager_gui.rmqrpc.manager_constants import SANDBOX_STATIC_IP, BENCHBOX_STATIC_IP, VAGRANT_DEFAULT_LOGIN, RABBIT_MQ_URL




# importar el init.py
class ManagerOps():

    HOST_RUN_STATUS = {}
    HOST_STATUS = {}

    def __init__(self):
        print 'ManagerExecutive'

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
        self.t1downloadBenchBox(host_settings, hostname)


        '''
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
        # print 't6assignSyncServer/OK {} '.format(hostname)




    def warmUp(self, args):
        print 'warmUP'
        # run execute only prepare directories
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
        # clear benchBox output directory
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
        # print h
        hostname = args['hostname'][0]
        # print hostname
        # print 'tell sandBox at dummy host to start client StackSync'
        str_cmd = 'nohup /usr/bin/stacksync &'
        self.rmisandBox(h['ip'], h['user'], h['passwd'], str_cmd)
        # have session at the dummy host

    def clientStackSyncDown(self, args):

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


    def clientOwnCloudUp(self, args):

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
                s.sendline('whoami')
                s.prompt()  # match the prompt
                s.sendline(cmd)  # run a command
                s.prompt() # true
                last_output = s.before  # # # print everyting before the prompt
                print colored(last_output, 'blue')
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
        # "handle only the last two lines"
        replace_n = last_output.replace('\n', '')
        replace_r = replace_n.replace('\r', '')
        whole_cmd = replace_r.split(' ')
        print "JOIN COMMAND: "
        join_cmd = ''.join(whole_cmd[-2:])
        print "AFTER JOIN "
        print join_cmd
        return join_cmd
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
            print "RMI LOCALHOST RESULT {}: {}".format(localhost, result)
            """
            str = result
            print result
            result = str.split('\n', 1)  # split once
            """
            return result
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

        print "RMI RESULT {}: {}".format(localhost, result)

        return result

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
        print str
        print 'Request: -> cmd {}'.format(name)
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


def startZeroRPC():
    '''
    process = multiprocessing.Process(target=ManagerRPC())
    process.start()
    '''
    # print 'ManagerRPC instance'
    s = zerorpc.Server(Manager(), pool_size=10)  # numero de cpu
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
    # startZeroRPC()
    startRabbitMQ(RABBIT_MQ_URL) # status Feedback queue
    # startRabbitMQ(RABBIT_MQ_URL) # queue
    # print "Finish manager"
