import boxsdk
from publisher_credentials import CREDENTIALS_BOX

class Box():


    def __init__(self):

        self.whoami = (self).__class__.__name__
        self.client = None

        self.access_token = None
        self.refresh_token = None

        TOKEN = CREDENTIALS_BOX['auth_token']
        CLIENT_ID = CREDENTIALS_BOX['client_id']
        CLIENT_SECRET = CREDENTIALS_BOX['client_secret']
        if self.access_token is None:
            self.access_token = TOKEN
        # if self.refresh_token is None:

        oauth = boxsdk.OAuth2(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            store_tokens=self.store_token_function,
            access_token=self.access_token,
            refresh_token=self.refresh_token
        )
        # create instance of box class

        self.client = boxsdk.Client(oauth)

        print self.whoami

    def hello(self):
        print "{} say hello".format(self.whoami)

        """
        Connect and authenticate with box
        """
        app = self.client.user().get()
        print app.name
        print app.login
        print app.avatar_url





    def publish(self, src, tgt):
        print "{} say publish".format(self.whoami)

        """
        Connect and authenticate with box
        """

        # upload a file to box
        print src, tgt
        f = open(src, 'rb')

        # se requiere buscar o crear el parent folder del path que especifiquemos
        # se tiene que comprobar que el archivo exista o no, no deja overwrite... implicaria hacer un put y get
        # lo que no queremos es el cliente haga un delete + download cuando
        # solo queremos download.

        str = tgt
        path_array = str.split('/')
        print str, path_array
        #  hacer un metodo lookup folder..

        root_folder = self.client.folder('0')
        current_folder = root_folder
        idx = 1
        while idx < len(path_array) - 1:
            print idx, path_array[idx]
            next_folder = path_array[idx]
            item_list = current_folder.get_items(limit=100, offset=0)
            print 'This is the first 100 items in the root folder:'
            for item in item_list:
                if next_folder == item.name:
                    print "folder_found!"
                    current_folder = item
                    break
                else:
                    print "missing_folder!"

            idx += 1


        file_name = path_array.pop()

        # hacer un fectch si se puede subir el archivo...
        try:
            current_folder.preflight_check(name=file_name,size=0)
        except boxsdk.exception.BoxAPIException as ex:
            print ex.message
            item_list = current_folder.get_items(limit=100, offset=0)
            print "try remove file"
            for item in item_list:
                if item.name == file_name:
                    item.delete()
                    print "removed"
                    break
                else:
                    continue
                    # remove the file
        finally:
            print "uploading file again"
            f = current_folder.upload_stream(f, file_name)
            print f.name



    def download(self, remote, local):
        print "{} say download".format(self.whoami)


    def store_token_function(self, access_token, refresh_token):
        self.access_token = access_token
        self.refresh_token = refresh_token
