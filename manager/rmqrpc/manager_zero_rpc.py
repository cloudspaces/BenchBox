#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import pxssh
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
            'profile': args['profile'][0],
            'stacksync-ip': args['stacksync-ip'][0],
            'owncloud-ip': args['owncloud-ip'][0],
            'impala-ip': args['impala-ip'][0],
            'graphite-ip': args['graphite-ip'][0],
            'hostname': args['hostname'][0]
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
    str_cmd = "" \
              "echo 'check if Git is installed...'; " \
              "echo '{}' | sudo -S apt-get install git; " \
              "echo 'check if BenchBox is installed...'; " \
              "if [ -d BenchBox ]; then " \
              "cd BenchBox;" \
              "git pull; " \
              "else " \
              "git clone --recursive https://github.com/CloudSpaces/BenchBox.git; " \
              "fi; " \
              "" \
              "cd vagrant; " \
              "" \
              "echo '{}' > profile; " \
              "" \
              "echo '{}' > ss.stacksync.key; " \
              "echo '{}' > ss.owncloud.key; " \
              "echo '{}' > hostname; " \
              "" \
              "echo '{}' > ss.stacksync.ip; " \
              "echo '{}' > ss.owncloud.ip; " \
              "echo '{}' > log.impala.ip; " \
              "echo '{}' > log.graphite.ip; " \
              "" \
              "echo '{}' | sudo -S ./setup.sh; " \
              "" \
              "".format(
                        h['passwd'],  h['profile'],
                        h['cred_stacksync'], h['cred_owncloud'],  h['hostname'],
                        h['owncloud-ip'], h['stacksync-ip'], h['impala-ip'], h['graphite-ip'],
                        h['passwd']
                        )
    return rmi(h['ip'], h['user'], h['passwd'], str_cmd)  # utilitzar un worker del pool


def rmi(hostname, login, passwd, cmd, callback=None):
        while True:
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
        print "LAST: OUTPUT"
        print colored(last_output, 'blue')
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

