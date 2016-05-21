#!/usr/bin/python -v
# -*- coding: iso-8859-1 -*-
__author__ = 'anna'

import zerorpc
from manager_rpc import ManagerRpc


class ZeroRpcServer():

    def __init__(self, server_address="tcp://0.0.0.0:4242", pool_size = 50):
        print 'ZeroRPC instance'
        self.s = zerorpc.Server(ManagerRpc(), pool_size=pool_size)  # numero de cpu
        print 'ZeroRPC bind'
        self.s.bind(server_address)

    def start(self):
        print 'ZeroRPC run'
        self.s.run()
        print 'ZeroRPC running'

if __name__ == "__main__":
    print "Start RPC"
    process = ZeroRpcServer()
    process.start()
