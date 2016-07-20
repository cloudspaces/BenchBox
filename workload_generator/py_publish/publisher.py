import publisher_credentials
import traceback, os
from plugin.pub_box import Box as box
from plugin.pub_clouddrive import CloudDrive as clouddrive
from plugin.pub_dropbox import Dropbox as dropbox
from plugin.pub_googledrive import GoogleDrive as googledrive
from plugin.pub_mega import Mega as mega
from plugin.pub_onedrive import OneDrive as onedrive
from plugin.pub_owncloud import OwnCloud as ownloud
# from plugin.pub_stacksync import StackSync as stacksync
from plugin.pub_sugarsync import SugarSync as sugarsync


class Publisher(object):
    '''
    this is the base object file publisher
    '''

    def __init__(self, personal_cloud=None):
        print "Constructor"

        self.action = None
        if personal_cloud is None:
            raise NotImplemented
        else:
            self.action = eval("{}".format(personal_cloud.lower()))()

    def publish(self, local_file_path, dst_remote_path = "/"):
        """
        upload a local file to the personal cloud storage
        :param local_file_path:
        :param remote_path:
        :return:
        """
        send_output_to = os.path.relpath(local_file_path, dst_remote_path)  # / == output
        send_to_remote = "/{}".format(send_output_to)
        print local_file_path, "Send to remote: ", send_to_remote

        # try:
        self.action.publish(local_file_path, send_to_remote)
        # while True:
        #     # try download the uploaded file
        #     # not try download check if exists.
        #     pass
        return 0
        # except Exception as ex:
        #     print ex.message
        #     return 1

    def download(self, remote_file_path, dst_local_path = "sample_response"):
        """
        retrieve a file hosted at personal cloud storage
        :param remote_file_path:
        :param dst_local_path:
        :return:
        """
        try:
            self.action.download(remote_file_path, dst_local_path)
            return 0
        except Exception as ex:
            print ex.message
            return 1

    def hello(self):
        #try:
        self.action.hello()
        return 0
        #    return 0  # successfully logged to personal cloud service
        # except Exception as ex:
        #     print ex.message
        #     print traceback.print_tb(None)
        #     return 1


if __name__ == "__main__":

    b = dropbox()
    b.hello()
    b.publish('sample/sample.txt', '/aaaa/sample.txt')