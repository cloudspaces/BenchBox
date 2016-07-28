#!/usr/bin/env python
import pika
import uuid
import urlparse
import sys
import getopt
import socket
import subprocess
import json
import glob, shutil
import os
import signal

def check_kill_process(pstring):
    for line in os.popen("ps ax | grep " + pstring + " | grep -v grep"):
        fields = line.split()
        pid = fields[0]
        os.kill(int(pid), signal.SIGKILL)


def remove_inner_path(path):
    files = glob.glob(path)
    try:
        for f in files:
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.remove(f)
    except Exception as ex:
        print ex.message


def run_command(cmd, dir):
    output = subprocess.check_output(cmd.split(" "), cwd=dir)
    return output


class ActionHandler(object):
    def __init__(self, target='windows', is_dummy=False):
        print "vagrant handler"
        self.hostname = socket.gethostname()
        self.target = target
        self.working_dir = None
        home = os.path.expanduser('~')  # milax or vagrant

        # tell the dummy host which benchbox virtual machines to emit
        # if is_dummy:
        #     print "Not a dummy host"
        #     self.working_dir = "{}\{}".format(home,'BenchBox/vagrant')
        # else:

        if is_dummy:  # llamadas tipo vagrant up
            if target == 'windows':  # para lanzar dentro de prod_status windows
                self.working_dir = "{}/{}".format(home,'BenchBox/windows')
                # aqui quizas haya un fork de 4 tipo
            elif target == 'linux':  # para apuntar dentro de prod_status linux
                self.working_dir = "{}/{}".format(home,'BenchBox/vagrant')
        else: # cuando es lanzado dentro del sandBox de windows
            self.working_dir = os.getcwd()

        print "TARGET DIRECTORY!!! [{}]".format(self.working_dir)

    ''' executed at the dummyhost '''
    def up(self):
        print 'up'
        output =  subprocess.check_output(["echo", "Hello World!"], cwd=self.working_dir)
        return output
        # subprocess.check_output(["vagrant", "status"], cwd="/home/milax/BenchBox/windows")

    def pwd(self):
        print 'up'
        return subprocess.check_output(["pwd", "."], cwd=self.working_dir)

    def vagrantStart(self):
        print 'vagrantStart'
        #
        # change directory to the target provisioning directory
        #
        self.vagrantUp()
        self.vagrantProvision()
        print 'vagrantStart/OK'

    def vagrantUp(self):
        print 'vagrantUp'
        while True:
            try:
                print subprocess.check_output(["vagrant", "up"], cwd=self.working_dir)
                break
            except:
                print "try again vagrant up"
                pass
        return 'vagrantUp/OK'

    def vagrantProvision(self):
        print 'vagrantProvision'
        print subprocess.check_output(['vagrant', 'provision'], cwd=self.working_dir)
        return 'vagrantProvision/OK'

    def vagrantStatus(self):
        print 'vagrantProvision'
        print subprocess.check_output(['vagrant', 'status'], cwd=self.working_dir)
        return 'vagrantProvision/OK'

    def vagrantDestroy(self):
        print 'vagrantDestroy'
        print subprocess.check_output(['vagrant', 'destroy', '-f'],cwd=self.working_dir) # vagrant destroy -f # force yes
        return 'vagrantDestroy/OK'


    # fins aqui els vagrant operations
    # todo: caracteritzar el warmup del sandBox en el cas de windows o linux
    # este

    ''' executed at the benchBox, nota: el script esta en el directorio root /vagrant'''
    def warmUp(self):  # unchanged only windows
        # warmup the sandBox filesystem booting the executor.py
        output = ""
        try:
            print 'warmUp'
            str_cmd = "nohup python ~/workload_generator/executor_rmq.py &> nohup_executor_rmq.out& "
            # output = subprocess.check_output(['echo', 'warmup'])
            output = bash_command(str_cmd)
        except:
            print "something failed"
        finally:
            return output




    "este script es compartido entre sandBox y benchBox"
    def tearDown(self):  #
        # clear the sandBox filesystem and cached files
        print 'tearDown'
        if self.target == "windows":
            if self.hostname == "sandBox":
                remove_inner_path('/Users/vagrant/Dropbox/*')
                remove_inner_path('/Users/vagrant/stacksync_folder/*')
            elif self.hostname == "benchBox":
                remove_inner_path('/home/vagrant/output/*')

            return None  # noop unimplemented exception
        try:
            output = ''
            if self.hostname == 'sandBox':              # todo if sandbox

                # tambien hace falta limpiar las carpetas de sincronizacion
                '''
                /home/vagrant/Dropbox
                /home/vagrant/Dropbox
                /home/vagrant/stacksync_folder
                /home/vagrant/owncloud_folder
                /home/vagrant/XXXX ...
                '''

                remove_inner_path('/home/vagrant/Dropbox/*')
                remove_inner_path('/home/vagrant/stacksync_folder/*')

                check_kill_process("monitor_rmq.py")

            elif self.hostname == 'benchBox':           # todo if benchBox
                check_kill_process("executor_rmq.py")
                # aprovechar el metodo que habia en github
                # hace falta limpiar la carpeta de ficheros sinteticos
                # /home/vagrant/output/*

                remove_inner_path('/home/vagrant/output/*')
                '''
                /home/vagrant/output
                '''
            else:
                return 'unhandled hostname: {}'.format(self.hostname)
        except:
            print "something failed"
        finally:
            return output

    ''' executed at the sandBox '''
    def monitorUp(self):
        # start the metrics listener for monitoring
        output = ""
        if self.target == "linux":
            try:
                print 'monitorUp'
                str_cmd = "sudo nohup python ~/monitor/monitor_rmq.py &> nohup_monitor_rmq.out& "
                output = bash_command(str_cmd)
            except:
                print "something failed"
            finally:
                return output
        elif self.target == "windows":
            # when the virtual machine is windows how can my local machine tell my windows(sandBox) guest to launch executor_rmq_py???
            print "how to warmup windows operating sandBox ??"
            # todo lanzar el executor_rmq.py
            output = power_command("python", "/Users/vagrant/monitor/monitor_rmq.py")

            try:
                print "warmUp windows sandBox "

            except Exception as ex:
                print ex.message
                print "something failed"

            finally:
                return output

        else:
            print "unhandled operating system"


    def execute(self):
        print 'execute'
        return bash_command('whoami')


class ProduceStatus(object):
    def __init__(self, rmq_url='localhost', queue_name = 'status_manager', target_os = 'linux', is_dummyHost=False):
        print 'prod: {}'.format(rmq_url)
        self.is_dummyHost = is_dummyHost
        self.rmq_url = rmq_url
        if rmq_url == 'localhost':
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=rmq_url,
                    heartbeat_interval=0
            ))
        else:
            print 'RabbitMQ instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname,
                heartbeat_interval=0,
                virtual_host=url.path[1:],
                credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        result = self.channel.queue_declare(durable=False, auto_delete=True)

        self.callback_queue = result.method.queue
        self.channel.basic_consume(self.on_response,
                                   no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            print "OK"
            self.response = body
        else:
            print "Not Match corr_id"

    def call(self, message, new_host):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                       reply_to = self.callback_queue,
                                       correlation_id = self.corr_id,
                                   ),
                                   body=json.dumps({"host": new_host, "status": message}))
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def close(self):
        print 'close connection'
        self.connection.close()


class ConsumeAction(object):
    def __init__(self, rmq_url, host_queue, target_os, is_dummy):
        print "Dummy Peer Worker"
        self.vagrant_ops = ActionHandler(target=target_os, is_dummy=is_dummy)
        self.rmq_url = rmq_url
        if rmq_url == 'localhost':
            """
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=rmq_url,
                    heartbeat_interval=5
            ))
            """
            # Async consumer

        else:
            print 'Worker instance'
            url_str = self.rmq_url
            url = urlparse.urlparse(url_str)
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(
                host=url.hostname,
                    heartbeat_interval=0,
                    virtual_host=url.path[1:],
                    credentials=pika.PlainCredentials(url.username, url.password)
            ))

        self.host_queue = host_queue
        self.channel = self.connection.channel()
        self.channel.basic_qos(prefetch_count=1)
        self.channel.queue_declare(queue=self.host_queue)

    def on_request(self, ch, method, props, data):
        body = json.loads(data)
        print " [on_request] {} => {}".format(body['cmd'], self.host_queue)
        # todo implementar els handler vagrantUp i vagrantDown
        try:
            toExecute = getattr(self.vagrant_ops, body['cmd'])
            print toExecute
            # lo ideal es que aixo no sigui un thread per que les peticions s'atenguin fifo
            # t = threading.Thread(target=toExecute)
            output = toExecute()
            # t.start()
        except AttributeError as e:
            # print e.message
            print "ACK: {}".format(body['cmd'])

        response = "{} response: {}: {}".format(self.host_queue, body['cmd'], output)
        print props.reply_to
        print props.correlation_id
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,

                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
        except:
            print "bypass"

        try:
            ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index
        except:
            print "the sender has been rebooted, so the response will never reach as their id are dynamically changing every time the node server reboots"

    def listen(self):
        self.channel.basic_consume(self.on_request,
                                   queue=self.host_queue,
                                   no_ack=True)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()




"""
Run bash command and return output
"""
def bash_command(cmd):
    child = subprocess.Popen(['/bin/bash', '-c', cmd])
    child.communicate()[0]
    rc = child.returncode
    return rc

    # -c command starts to be read from the first non-option argument
'''
cmd : command
cwd : directory
'''
def power_command(cmd, script):
    print cmd
    print script
    request = "{} {}".format(cmd, script)
    child = subprocess.Popen(request)
    child.communicate()[0]
    rc = child.returncode
    print "Return code from cmd: [{}] -> {}".format(cmd, rc)
    # print "power shell command through winrm"
    # simple python to launch the provider
    return rc


def parse_args(argv):

    print "Arguments: {}".format(argv)
    try:
        opts, args = getopt.getopt(argv, "hm:,t:", ["msg=" , "topic="])
    except getopt.GetoptError:
        print '*.py -m <msg> -t <topic> '
        sys.exit(2)

    msg = None
    top = None
    for opt, arg in opts:
        if opt == '-h':
            sys.exit()
        elif opt in ("-i", "--msg"):
            msg = arg
        elif opt in ("-t", "--topic"):
            top = arg

    print msg, top
    return msg, top


class ProdStatusService():

    def __init__(self):

        print "Noop"

    def start(self):
        print "Start ..."

    def stop(self):
        print "Stop ..."
        sys.exit(0)
        #raise SystemExit, "Some message here :D"

    def main(self, status_msg, topic):
        ''' dummy host says hello to the manager '''
        # target
        is_dummy_host = None  # significa que es una maquina fisica
        target_os = None
        rmq_url = None

        try:
            with open('/vagrant/rabbitmq', 'r') as r:
                rmq_url = r.read().splitlines()[0]
            with open('/vagrant/target', 'r') as r:
                target_os = r.read().splitlines()[0]
            with open('/vagrant/hostname', 'r') as f:
                dummy_hostname = f.read().splitlines()[0]
        except Exception as ex:
            print ex.message
            print "This is a Physical machine, no vagrant folder found! "
            with open('./rabbitmq', 'r') as r:
                rmq_url = r.read().splitlines()[0]
            with open('./target', 'r') as r:
                target_os = r.read().splitlines()[0]
            with open('./hostname', 'r') as f:
                dummy_hostname = f.read().splitlines()[0]

        hostname = socket.gethostname()

        if hostname == 'benchBox' or hostname == 'sandBox':
            is_dummy_host = False
        else:
            is_dummy_host = True

        emit_status_rpc = ProduceStatus(rmq_url=rmq_url, target_os=target_os, is_dummyHost=is_dummy_host)

        if status_msg is None:
            status_msg = "Hello from {} ".format(hostname)

        # if topic is None:
        #     hostname = topic

        if is_dummy_host:
            host_queue = "{}.{}".format(hostname.lower(), hostname.lower())  # es maquina fisica
        else:
            host_queue = "{}.{}".format(dummy_hostname, hostname.lower())  # es maquina virtual
            # this is the format, that rmq.js target_queue needs!

        print " [Out] emit: emit_status_rpc.call({})".format(host_queue)
        response = emit_status_rpc.call(status_msg, host_queue)
        emit_status_rpc.close()  # emit setup done response
        print " [In] recv: Got response from manager: %r" % (response,)

        ''' crear una cua amb el propi host name de tipus direct '''
        while True:
            # try:
            consumer_rpc = ConsumeAction(rmq_url, host_queue, target_os, is_dummy_host)
            consumer_rpc.listen()
            # except Exception as ex:
            #    print "{} prod_status Consumer exception".format(ex.message)

        ''' dummy host does all the following setup operations '''

if __name__ == '__main__':
    status_msg, topic = parse_args(sys.argv[1:])
    ps = ProdStatusService()
    ps.main(status_msg, topic)
