#!/usr/bin/python
import unittest
import os
from sniffer import Sniffer
from hashlib import md5
import sys
# import pdb;


# execute single test
# nosetests publisher_test.py -- single test
# nosetests /path/to/folder -- suit of test


class SnifferTest(unittest.TestCase):

    personal_cloud = "StackSync"
    # la plataforma se comprueba por script no por parametro

    def test_hello(self):
        print ""
        print "TEST HELLO"
        print ""
        config_client = {
            "sync_server_ip": "stacksync.urv.cat",
            "sync_server_port": 8080,
            "packet_limit": -1,
            "max_bytes": 65535,
            "promiscuous": False,
            "read_timeout": 100
        }
        print config_client
        sniff = Sniffer(self.personal_cloud,  config_client)
        result = sniff.hello()
        self.assertEqual(result, 0)

    def test_capture(self):
        print ""
        print "TEST CAPTURE"
        print ""
        config_client = {
            "sync_server_ip": "stacksync.urv.cat",
            "sync_server_port": 8080,
            "packet_limit": -1,
            "max_bytes": 65535,
            "promiscuous": False,
            "read_timeout": 100
        }
        print config_client
        sniff = Sniffer(self.personal_cloud,  config_client)
        result = sniff.run()
        print result
        result = sniff.rage_quit()

        # pdb.set_trace()
        self.assertEqual(0, 0)
