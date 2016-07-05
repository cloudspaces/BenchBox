import httplib2
import os
import apiclient
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools


class GoogleDrive():
    def __init__(self):

        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/drive_credentials.json
        # https://developers.google.com/drive/v3/web/about-auth#OAuth2Authorizing
        SCOPES = 'https://www.googleapis.com/auth/drive'
        CLIENT_SECRET_FILE = 'client_secret_oauth.json'
        APPLICATION_NAME = 'BenchBox upload file to drive'
        CACHED_CREDENTIAL_FILE = 'drive_credentials.json'
        # inserting file to certain folder id ... lookup required, none transactional operation error prone..*[]:

        self.whoami = (self).__class__.__name__
        print self.whoami
        curr_dir = os.path.expanduser('.')
        credential_dir = os.path.join(curr_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, CACHED_CREDENTIAL_FILE)
        self.store = oauth2client.file.Storage(credential_path)
        self.credentials = self.store.get()

        if not self.credentials or self.credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            self.credentials = tools.run(flow, self.store)
            print 'New credentials Storing to ' + credential_path
        else:
            print "Credentials already cached!"
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http)

        self.root_folder = self.service.files().get(fileId='root').execute()
        print self.root_folder

    def hello(self):
        print "{} say hello".format(self.whoami)

        # self.oauth = Gauth(settings_file="../quickstart/settings.yaml")
        # self.oauth = Gauth(settings_file="quickstart/settings.yaml")
        # self.oauth.LocalWebserverAuth()
        # self.drive = Gdrive(self.oauth)


        print "QUERY:"
        #
        results = self.service.files().list(
            q="'{}' in parents".format(self.root_folder['id']),
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print('{0} ({1})'.format(item['name'], item['id']))

    def publish(self, src, tgt):
        print "{} say publish".format(self.whoami)
        # given a certain file path => move forward and try to upload the file
        print src, tgt
        f = open(src, 'rb')
        str = tgt
        path_array = str.split('/')
        print str, path_array
        #  hacer un metodo lookup folder..

        current_folder = self.root_folder
        idx = 1
        while idx < len(path_array) - 1:
            print idx, path_array[idx]
            next_folder = path_array[idx]
            results = self.service.files().list(
                q="'{}' in parents and name = '{}'".format(current_folder['id'], next_folder),
                pageSize=1,
                fields="files(id, name)").execute()
            items = results.get('files', [])
            if not items:
                print 'No files found.'
            else:
                for item in items:
                    if next_folder == item['name']:
                        print "Next folder: ", item
                        current_folder = item
                        break
                    else:
                        print "missing_folder!"
            idx += 1

        file_name = path_array.pop()
        print file_name
        # check if the file already exists:
        check_file_exists = self.service.files().list(
            q="'{}' in parents and name = '{}'".format(current_folder['id'], file_name),
            pageSize=1,
            fields="files(id, name)"
        ).execute()
        items = check_file_exists.get('files', [])
        print items
        # https://developers.google.com/drive/v3/web/folder#creating_a_folder
        if not items:
            # upload file
            print "Upload file"

            # https://developers.google.com/drive/v2/web/appdata#inserting_a_file_into_the_application_data_folder
            media = apiclient.http.MediaFileUpload(filename=src)
            metadata = {
                'name': file_name,
                'title': file_name,
                'parents': [ current_folder['id']]
            }
            try:
                file = self.service.files().create(body=metadata, media_body=media).execute()
                print "upload success: {}".format(file)
                print file
            except apiclient.errors.HttpError, error:
                print "an error occured: %s" % error

        else:
            print "Update file"
            for item in items:
                print "Update the item!"
                try:
                    media_body = apiclient.http.MediaFileUpload(filename=src)
                    updated_file = self.service.files().update(
                        fileId=item['id'],
                        media_body=media_body).execute()
                    print "update success: {}".format(updated_file)
                except apiclient.errors.HttpError, error:
                    print 'An error occurred: %s' % error

    def download(self, remote, local):
        print "{} say download".format(self.whoami)
