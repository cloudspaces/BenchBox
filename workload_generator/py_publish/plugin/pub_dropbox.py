import dropbox
from publisher_credentials import CREDENTIALS_DROPBOX

class Dropbox():
    def __init__(self):

        self.whoami = (self).__class__.__name__
        self.client = None
        print self.whoami

    def hello(self):
        print "{} say hello".format(self.whoami)

        """
        Connect and authenticate with dropbox
        """
        TOKEN = CREDENTIALS_DROPBOX['auth_token']

        # create instance of dropbox class
        self.client = dropbox.Dropbox(TOKEN)

        # check that the access token is valid
        try:
            # print
            self.client.users_get_current_account()
        except dropbox.exceptions.ApiError as ex:
            print ex.message

    def publish(self, src, tgt):
        """

        :param src: relative path from the curr dir
        :param tgt: absolute path at the personal cloud storage
        :return:
        """
        print "{} say publish".format(self.whoami)
        # backup
        """
        Connect and authenticate with dropbox
        """
        TOKEN = CREDENTIALS_DROPBOX['auth_token']

        # create instance of dropbox class
        self.client = dropbox.Dropbox(TOKEN)

        # check that the access token is valid
        try:
            self.client.users_get_current_account()
        except dropbox.exceptions.ApiError as ex:
            print ex.message

        f = open(src, 'r')
        try:
            response = self.client.files_upload(f, tgt, mode=dropbox.files.WriteMode('overwrite'))
        except dropbox.exceptions.ApiError as ex:
            print ex.message

        print 'uploaded: ', response

    def download(self, remote, local):
        print "{} say download".format(self.whoami)
