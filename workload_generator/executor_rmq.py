#!/usr/bin/env python
import pika
import os
import sys
import urlparse
import filecmp
import shutil
from termcolor import colored


def appendParentDir(num, currdir):
    print currdir
    if num is 0:
        print 'return value'
        sys.path.append(currdir)
        return currdir
    else:
        dirname, basename = os.path.split(currdir)
        num-=1
        return appendParentDir(num, dirname)
appendParentDir(1, os.path.dirname(os.path.realpath(__file__)))



from workload_generator.constants import STEREOTYPE_RECIPES_PATH, FS_SNAPSHOT_PATH, \
    FTP_SENDER_IP, FTP_SENDER_PASS, FTP_SENDER_PORT, FTP_SENDER_USER, DEBUG
from workload_generator.model.data_layer.data_generator import DataGenerator
from workload_generator.communication.ftp_sender import ftp_sender
from workload_generator.communication import actions
from workload_generator.executor import StereotypeExecutorU1






class Commands(object):


    def __init__(self, ftp_sender, profile):
        print 'rpc commands'
        self.ftp_sender = ftp_sender
        self.stereotype = profile  # backupsample
        self.fs_abs_target_folder = '/home/vagrant/{}'.format(ftp_sender.ftp_root) # target ftp_client dir absolute path
        self.stereotype_executor = StereotypeExecutorU1(self.ftp_sender)
        # self.data_generator = DataGenerator()

        # start the monitoring stuff. # todo
        # send to impala always...!!!

    def hello(self):
        print 'hello world'
        return 'hello world response'

    def warmup(self):
        print 'warm up'
        print FS_SNAPSHOT_PATH
        print STEREOTYPE_RECIPES_PATH
        receipt = STEREOTYPE_RECIPES_PATH + self.stereotype
        print receipt
        print 'init markov chain'
        self.stereotype_executor.operation_chain.initialize_from_recipe(receipt)
        print 'init data gen'
        self.stereotype_executor.data_generator.initialize_from_recipe(receipt)
        print 'init interarrival'
        self.stereotype_executor.inter_arrivals_manager.initialize_from_recipe(receipt)

        # self.data_generator.initialize_from_recipe(receipt)
        # self.data_generator.create_file_system_snapshot()
        print 'init fs & migrate to sandbox'
        self.stereotype_executor.create_fs_snapshot_and_migrate_to_sandbox(ftp_client)
        return 'warm up response'

    def runtest(self):
        print 'run test'
        self.stereotype_executor.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        # TODO loop
        operations = 10
        for i in range(operations):
            self.stereotype_executor.execute()
            print colored("doOps {}/{}".format(i, operations), 'red')
        return 'run test response'

    def uploadir(self):
        """ TEST UPLOAD DIRECTORY | root directory """
        print 'UPLOAD_DIRECTORY'
        actions.UploadDirectory(FS_SNAPSHOT_PATH, FS_SNAPSHOT_PATH).perform_action(self.ftp_sender)
        return 'UPLOAD_DIRECTORY: {} '.format(FS_SNAPSHOT_PATH)

    def createfile(self):
        """ TEST CREATE FILE """
        path = self.data_generator.create_file()
        print 'CREATE_FILE: {}'.format(path)
        tgt_path = actions.CreateFile(path, FS_SNAPSHOT_PATH).perform_action(self.ftp_sender)
        return 'CREATE_FILE: {} ---> {}'.format(path, tgt_path)

    def createdir(self):
        """ TEST CREATE DIR """


    def movefile(self):
        """ TEST MOVE FILE """
        path = self.data_generator.move_file()
        print 'MOVE_FILE: {}'.format(path)
        src_path, tgt_path_local = path
        if not src_path == tgt_path_local: # not None == None
            tgt_path_remote = actions.MoveFile(src_path, FS_SNAPSHOT_PATH, tgt_path_local).perform_action(self.ftp_sender)
        return 'MOVE_FILE: {} ---> {} | {}'.format(src_path, tgt_path_local, tgt_path_remote)

    def movedir(self):
        """ TEST MOVE DIRECTORY """
        src_path = self.data_generator.delete_file()
        print "DELETE FILE:::  at ----> {}".format(src_path)
        actions.DeleteFile(src_path, FS_SNAPSHOT_PATH).perform_action(self.ftp_sender)
        return "DELETE FILE:::  at ----> {}".format(src_path)

    def updatefile(self):
        """ TEST UPDATE FILE """
        path = self.data_generator.update_file()
        print "UPDATE FILE: {}".format(path)
        tgt_path = actions.UpdateFile(path, FS_SNAPSHOT_PATH).perform_action(self.ftp_sender)
        return 'UPDATE_FILE: {} ---> {}'.format(path, tgt_path)

    def delfile(self):
        """ TEST DELETE FILE """
        src_path = self.data_generator.delete_file()
        print "DELETE FILE:::  at ----> {}".format(src_path)
        actions.DeleteFile(src_path, FS_SNAPSHOT_PATH).perform_action(self.ftp_sender)
        return "DELETE FILE:::  at ----> {}".format(src_path)



    def deldir(self):
        """ TEST DELETE DIRECTORY """
        src_path = self.data_generator.delete_directory()
        print "DELETE DIRECTORY:::  at ----> to {}".format(src_path)
        actions.DeleteDirectory(src_path, FS_SNAPSHOT_PATH).perform_action(self.ftp_sender)
        return "DELETE DIRECTORY:::  at ----> to {}".format(src_path)





class ExecuteRMQ(object):


    def __init__(self, rmq_url='', host_queue='', ftp_client='', profile=''):
        print "Executor operation consumer: "
        url = urlparse.urlparse(rmq_url)
        self.profile = profile
        self.ftp_client = ftp_client
        self.actions = Commands(ftp_client, profile)
        # ftp_client.ftp_root = 'stacksync_folder'


        self.queue_name = host_queue
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=url.hostname,
            virtual_host=url.path[1:],
            credentials=pika.PlainCredentials(url.username, url.password)
        ))
        self.channel = self.connection.channel()

        self.channel.queue_declare(queue=self.queue_name)

    def on_request(self, ch, method, props, body):
        print " [on_request] {} ".format(body)
        # todo implementar els handler vagrantUp i vagrantDown
        output = None
        try:
            toExecute = getattr(self.actions, body)
            print toExecute
            # lo ideal es que aixo no sigui un thread per que les peticions s'atenguin fifo
            # t = threading.Thread(target=toExecute)
            output = toExecute()
            # t.start()
        except AttributeError as e:
            print e.message
            print "ACK: {}".format(body)

        response = "{} response: {}: {}".format(self.queue_name, body, output)
        print props.reply_to
        print props.correlation_id
        try:
            ch.basic_publish(exchange='',
                             routing_key=props.reply_to,
                             properties=pika.BasicProperties(correlation_id=props.correlation_id),
                             body=response)
        except:
            print "bypass"
        ch.basic_ack(delivery_tag=method.delivery_tag)  # comprar que l'ack coincideix, # msg index

    def listen(self):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.on_request, queue=self.queue_name)
        print " [Consumer] Awaiting RPC requests"
        self.channel.start_consuming()


if __name__ == '__main__':

    print "executor.py is ran when warmup and its queue remains established... WAITING RPC"

    rmq_url = 'amqp://benchbox:benchbox@10.30.236.141/'
    dummyhost = None

    # start the ftp sender
    ftp_client = ftp_sender(
        FTP_SENDER_IP,
        FTP_SENDER_PORT,
        FTP_SENDER_USER,
        FTP_SENDER_PASS,
        'stacksync_folder'
    )

    #
    stereotype_receipt = 'backupsample'

    with open('/vagrant/hostname', 'r') as f:
        dummyhost = f.read().splitlines()[0]
    queue_name = '{}.{}'.format(dummyhost,'executor')
    executor = ExecuteRMQ(rmq_url, queue_name, ftp_client, stereotype_receipt)
    executor.listen()