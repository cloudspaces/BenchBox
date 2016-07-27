#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

from pexpect import pxssh
from termcolor import colored


class ManagerZeroRpc:

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
            'cred_dropbox': args['cred_dropbox'][0],
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'stacksync-port': args['stacksync-port'][0],
            'owncloud-ip': args['owncloud-ip'][0],
            'impala-ip': args['impala-ip'][0],
            'graphite-ip': args['graphite-ip'][0],
            'rabbit-url': args['rabbitmq-amqp'][0],
            'box-url': None,
            'hostname': args['hostname'][0],
            'target': args['target'][0], # target operating system
        }
        print "Start Initial Task"


        return setup_benchbox(host_settings)


'''
t2installVagrantVBox(host_settings)
t3downloadVagrantBoxImg(host_settings)
t4assignStereoTypeToProfile(host_settings)
t5assignCredentialsToProfile(host_settings)
t6assignSyncServer(host_settings)
return 0
'''

def setup_benchbox(h):  # tell all the hosts to download BenchBox
    print 'setupBenchBox'
    # todo append rabbit.mq.url link and as ip file and also vagrant.box.url
    # "git clone -b development --recursive https://github.com/CloudSpaces/BenchBox.git; " \
    # "git clone -b development --recursive https://github.com/CloudSpaces/BenchBox.git; " \

    print ""
    print "Start setup benchbox: WINDOWS"
    print ""
    str_cmd_win = " " \
              "" \
              "cd ~/BenchBox; " \
              "cd windows; " \
              "echo '{}' > rabbitmq; " \
              "echo '{}' > profile; " \
              "echo 'Forward keys'; " \
              "echo '{}' > ss.stacksync.key; " \
              "echo '{}' > ss.owncloud.key; " \
              "echo '{}' > ss.dropbox.key; " \
              "echo '{}' > hostname; " \
              "" \
              "echo '{}' > ss.stacksync.ip; " \
              "echo '{}' > ss.stacksync.port; " \
              "echo '{}' > ss.owncloud.ip; " \
              "echo '{}' > log.impala.ip; " \
              "echo '{}' > log.graphite.ip; " \
              "".format(h['rabbit-url'], h['profile'],
                        h['cred_stacksync'],
                        h['cred_owncloud'],
                        h['cred_dropbox'], h['hostname'],
                        h['stacksync-ip'], h['stacksync-port'],
                        h['owncloud-ip'], h['impala-ip'], h['graphite-ip'])
    print str_cmd_win
    print ""
    print "Start setup benchbox: LINUX"
    print ""
    str_cmd = " " \
          "echo 'check if Git is installed...'; " \
          "echo '{}' | sudo -S apt-get install git; " \
          "echo 'check upgrade pip'; " \
          "echo '{}' | sudo pip install --upgrade pip; " \
          "echo 'check if BenchBox is installed...'; " \
          "" \
          "if [ -d ~/BenchBox ]; then " \
          "cd ~/BenchBox; " \
          "" \
          "git pull; " \
          "else " \
          "git clone --recursive https://github.com/CloudSpaces/BenchBox.git; " \
          "cd BenchBox; " \
          "fi; " \
          "echo '{}' > target; " \
          "cd vagrant; " \
          "echo '{}' > target; " \
          "echo '{}' > rabbitmq; " \
          "echo '{}' > profile; " \
          "" \
          "echo '{}' > ss.stacksync.key; " \
          "echo '{}' > ss.owncloud.key; " \
          "echo '{}' > ss.dropbox.key; " \
          "echo '{}' > hostname; " \
          "" \
          "echo '{}' > ss.stacksync.ip; " \
          "echo '{}' > ss.stacksync.port; " \
          "echo '{}' > ss.owncloud.ip; " \
          "echo '{}' > log.impala.ip; " \
          "echo '{}' > log.graphite.ip; " \
          "" \
          "echo '{}' | sudo -S ./setup.sh; " \
          "echo '----------------------------------'; " \
          "nohup ./startPeerConsumer.sh & " \
          "" \
          "" \
          "".format(h['passwd'],
                    h['passwd'],
                    h['target'],
                    h['target'],
                    h['rabbit-url'], h['profile'],
                    h['cred_stacksync'], h['cred_owncloud'], h['cred_dropbox'], h['hostname'],
                    h['stacksync-ip'], h['stacksync-port'],
                    h['owncloud-ip'], h['impala-ip'], h['graphite-ip'],
                    h['passwd'])
    print str_cmd
    print ""
    print 'sendQuery...: '
    print ""
    if h["target"] == "windows":
        print "TARGET IS WINDOWS: {}".format(h["target"])
        print rmi(h['ip'], h['user'], h['passwd'], str_cmd)
        return rmi(hostname=h['ip'], login=h['user'], passwd=h['passwd'], cmd=str_cmd_win, target=h["target"])
    else:
        print "TARGET IS LINUX: {}".format(h["target"])
        return rmi(hostname=h['ip'], login=h['user'], passwd=h['passwd'], cmd=str_cmd, target=h["target"])


def rmi(hostname, login, passwd, cmd, target=None):
    print "sendQuery to: "+hostname, login, passwd, target
    print "-----------------------------------------------"
    print cmd
    rmiTry = 0
    while True:
        rmiTry += 1
        print rmiTry
        try:
            s = pxssh.pxssh()
            s.login(hostname, login, passwd)
            s.timeout = 3600  # set timeout to one hour
            s.sendline('whoami')
            s.prompt()  # match the prompt
            s.sendline(cmd)  # run a command
            s.prompt()  # true
            last_output = s.before  # # # print everyting before the prompt

            s.logout()
        except pxssh.ExceptionPxssh, e:
            continue
        break
    # print "LAST: OUTPUT"
    # print colored(last_output, 'blue')
    print "------------------------------------------------"
    return last_output

'''
replace_n = last_output.replace('\n', '')
replace_r = replace_n.replace('\r', '')
whole_cmd = replace_r.split(' ')
print "JOIN COMMAND: "
join_cmd = ''.join(whole_cmd[-2:])
print "AFTER JOIN "
print join_cmd
return join_cmd
'''

