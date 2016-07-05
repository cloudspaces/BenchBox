#!/usr/bin/python
import unittest
import os
from publisher import Publisher
from hashlib import md5
import sys

# test methods from publisher.py

# execute single test
# nosetests publisher_test.py -- single test
# nosetests /path/to/folder -- suit of test


class PublisherTest(unittest.TestCase):

    personal_cloud = "dropbox"
    test_file = "sample.txt"
    test_file_path = "sample/{}".format(test_file)
    down_file_path = "sample_response/{}".format(test_file)
    remote_dir = "/aaaa/"
    remote_file_path = "{}{}".format(remote_dir, test_file)

    def test_hello(self):
        pp = Publisher(self.personal_cloud)
        result = pp.hello()
        self.assertEqual(result, 0)

    def test_publish(self):
        pp = Publisher(self.personal_cloud)
        result = pp.publish(self.test_file_path, self.remote_file_path)
        self.assertEqual(result, 0)  # 0 means published successfully

    # @unittest.skipUnless(sys.platform.startswith("win"), "requires Windows")
    # def test_publish_exists(self):
    #     pp = Publisher(self.personal_cloud)
    #     os.remove(self.down_file_path)
    #
    #     result = pp.download(self.remote_file_path, self.down_file_path)
    #     self.assertEqual(result, 0)
    #     response_hash = md5(open(self.down_file_path, 'rb').read()).hexdigest()
    #     original_hash = md5(open(self.test_file_path, 'rb').read()).hexdigest()
    #     self.assertEqual(response_hash, original_hash)
        # python check if md5 of [sample/sample.txt] [sample_response/sample.txt] match


