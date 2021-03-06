import boxsdk
try:
    import bottle
except Exception as ex:
    print ex.message
import os
from threading import Thread, Event
import webbrowser
from py_publish.publisher_credentials import CREDENTIALS_BOX
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler, make_server
from boxsdk import OAuth2


class Box():

    def __init__(self):

        self.whoami = (self).__class__.__name__
        self.client = None

        self.access_token = None
        self.refresh_token = CREDENTIALS_BOX['refresh_token']

        TOKEN = CREDENTIALS_BOX['auth_token']

        CLIENT_ID = CREDENTIALS_BOX['client_id']
        CLIENT_SECRET = CREDENTIALS_BOX['client_secret']

        oauth, self.access_token, self.refresh_token = self.authenticate(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)

        if self.access_token is None:
            self.access_token = TOKEN
        # if self.refresh_token is None:
        # oauth = boxsdk.OAuth2(
        #     client_id=CLIENT_ID,
        #     client_secret=CLIENT_SECRET,
        #     store_tokens=self.store_token_function,
        #     access_token=self.access_token,
        #     refresh_token=self.refresh_token
        # )
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
            try:
                item_list = current_folder.get_items(limit=100, offset=0)
            except boxsdk.exception.BoxOAuthException as ex:
                print ex.message

                # try refreash token

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

    def authenticate(self, client_id="", client_secret=""):

        oauth_class = boxsdk.OAuth2

        class StoppableWSGIServer(bottle.ServerAdapter):
            def __init__(self, *args, **kwargs):
                super(StoppableWSGIServer, self).__init__(*args, **kwargs)
                self._server = None

            def run(self, app):
                server_cls = self.options.get('server_class', WSGIServer)
                handler_cls = self.options.get('handler_class', WSGIRequestHandler)
                self._server = make_server(self.host, self.port, app, server_cls, handler_cls)
                self._server.serve_forever()

            def stop(self):
                self._server.shutdown()

        auth_code = {}
        auth_code_is_available = Event()

        local_oauth_redirect = bottle.Bottle()

        @local_oauth_redirect.get('/')
        def get_token():
            auth_code['auth_code'] = bottle.request.query.code
            auth_code['state'] = bottle.request.query.state
            auth_code_is_available.set()

        local_server = StoppableWSGIServer(host='localhost', port=8080)
        server_thread = Thread(target=lambda: local_oauth_redirect.run(server=local_server))
        server_thread.start()

        oauth = oauth_class(
            client_id=client_id,
            client_secret=client_secret,
        )
        auth_url, csrf_token = oauth.get_authorization_url('http://localhost:8080')
        webbrowser.open(auth_url)

        auth_code_is_available.wait()
        local_server.stop()
        assert auth_code['state'] == csrf_token
        access_token, refresh_token = oauth.authenticate(auth_code['auth_code'])

        print('access_token: ' + access_token)
        print('refresh_token: ' + refresh_token)

        return oauth, access_token, refresh_token