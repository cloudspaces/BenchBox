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
from manager_rmq import manager_rmq



class manager_rpc(object):
    hosts = None
    config = None

    ops = manager_rmq()

    def loadHosts(self):
        print 'loadHosts'

    def loadConfig(self):
        print 'loadConfig'

    def cmd(self, name):
        str = urllib.quote_plus(name)
        print str
        print 'Request: -> cmd {}'.format(name)
        output = subprocess.check_output(['bash', '-c', urllib.unquote_plus(name)])
        return output.split('\n')


    def list(self, name):
        bashCommand = "ls {}".format(name)
        output = subprocess.check_output(['bash', '-c', bashCommand])
        return output.split('\n')

    def bad(self):
        raise Exception('xD')

    def nmap(self, port, ip):
        output = subprocess.check_output(['nmap', '-p', port, ip])

        result = output.split('\n')
        if len(result) > 5:
            if result[5].split()[1] == 'open':
                return True
        return False


    def rpc(self, url):
        str = urlparse.urlparse(url)
        argslist = urlparse.parse_qs(str.query)
        toExecute = getattr(self.ops, argslist['cmd'][0])
        t = threading.Thread(target=toExecute, args=(argslist,))
        t.start()
        result = None # None Blocking
        argslist['result'] = result;
        return argslist


    def status(self, url):
        str = urlparse.urlparse(url)
        argslist = urlparse.parse_qs(str.query)
        toExecute = self.ops.requestStatus
        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(toExecute, (argslist,))
        try:
            result = async_result.get()
        except:
            raise

        argslist['result'] = result;
        return result
