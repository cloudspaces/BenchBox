#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import subprocess
import urllib
from manager_zero_rpc import ManagerZeroRpc
import urlparse
import threading

class ManagerRpc(object):

    hosts = None
    config = None

    ops = ManagerZeroRpc()

    def cmd(self, name):
        str = urllib.quote_plus(name)
        print str
        print 'Request: -> cmd {}'.format(name)
        output = subprocess.check_output(['bash', '-c', urllib.unquote_plus(name)])
        return output.split('\n')

    def nmap(self, port, ip):
        output = subprocess.check_output(['nmap', '-p', port, ip])
        result = output.split('\n')
        print result
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
        result = "CMD {} Send!".format(argslist['cmd'][0])  # None Blocking
        argslist['result'] = result;
        return argslist

'''
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
'''
