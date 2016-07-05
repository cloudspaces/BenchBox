import requests
import json
import pprint
from oauthlib import oauth1
from oauthlib.common import urlencode, urldecode
from oauthlib.oauth1 import SIGNATURE_PLAINTEXT, SIGNATURE_TYPE_AUTH_HEADER, SIGNATURE_TYPE_BODY, SIGNATURE_TYPE_QUERY
import keystoneclient


class StackSync():
    def __init__(self):

        self.whoami = (self).__class__.__name__
        print self.whoami

        headers = {
            'Content-Type': 'application/json',
        }

        data = CREDENTIALS_STACKSYNC['access_token_credentials']

        response = requests.post('http://130.206.36.143:5000/v2.0/tokens', headers=headers, data=data)
        access_token = json.loads(response.content)  # json...
        access_token_id = access_token['access']['token']['id']
        print access_token_id

        headers = {
            'X-Auth-Token': access_token_id,
        }

        user_swift_account = CREDENTIALS_STACKSYNC['user']['swift_account']
        print user_swift_account
        response = requests.get('http://130.206.36.143:8080/v1/{}'.format(user_swift_account), headers=headers)
        # print response.content



        self.client = oauth1.Client(
            client_key=CREDENTIALS_STACKSYNC['client_key'],
            client_secret=CREDENTIALS_STACKSYNC['client_secret'],
            signature_type=SIGNATURE_TYPE_AUTH_HEADER,
            signature_method=SIGNATURE_PLAINTEXT,
            # resource_owner_key=CREDENTIALS_STACKSYNC['resource_owner_key'],
            # resource_owner_secret=CREDENTIALS_STACKSYNC['resource_owner_secret'],
            callback_uri='oob'
        )

        # try

        url = "{}{}{}{}".format(CREDENTIALS_STACKSYNC['swift_url'],
                            CREDENTIALS_STACKSYNC['swift_port'],
                            CREDENTIALS_STACKSYNC['oauth_endpoint'],
                            CREDENTIALS_STACKSYNC['request_token_endpoint'])

        uri, headers, _ = self.client.sign(url, http_method='GET')
        headers['StackSync-API'] = 'v2'

        print uri, headers, _  # _ : deroberately ignored.

        r = requests.get(uri, headers=headers)

        print r.content
        if r.status_code != 200:
            assert False

        decoded_data = urldecode(r.text)
        oauth_response = dict(decoded_data)
        print oauth_response['oauth_token_secret']
        print oauth_response['oauth_token']

        '''
        {u'oauth_token_secret'  : u'Y1qur0rrxkvPyDw2YnF6DKo1c2rNeQ',
         u'oauth_token'         : u'eZhaQ1Z3EZGOH5l4DFpY4xL6QqFpZt',
         u'oauth_callback_confirmed': u'true'}

        '''
        self.oauth_token_secret = oauth_response['oauth_token_secret']
        self.oauth_token = oauth_response['oauth_token']

        # headers = {
        #     'X-Auth-Token': access_token_id,
        #     'stacksync-api': 'true',
        #     'list': 'true',
        # }

        #
        # file_name = 'file_name_here'
        # requests.get('https://130.206.36.143:8080/v1/{}/stacksync/files?file_name={}&overwrite=true'.format(user_swift_account, file_name)
        #              , headers=headers)
        # self.server_base_url = "{}{}{}".format(
        #     CREDENTIALS_STACKSYNC['swift_url'],
        #     CREDENTIALS_STACKSYNC['swift_port'],
        #     CREDENTIALS_STACKSYNC['swift_api_version'],
        # )
        #
        # self.server_auth_url = "{}{}{}{}".format(
        #     CREDENTIALS_STACKSYNC['swift_url'],
        #     CREDENTIALS_STACKSYNC['swift_port'],
        #     CREDENTIALS_STACKSYNC['oauth_endpoint'],
        #     CREDENTIALS_STACKSYNC['authorize_endpoint'],
        # )
        # print self.server_base_url
        # print self.server_auth_url
        # headers = {
        #     "STACKSYNC_API":"v2"
        # }
        #
        # # response = requests.post(
        #     url=self.server_auth_url,
        #     auth=self.oauth,
        #     headers=headers,
        #     verify=False
        # )
        #
        # print response.content

        self.username = CREDENTIALS_STACKSYNC['login']['username']
        self.password = CREDENTIALS_STACKSYNC['login']['password']

    def hello(self):
        print "{} say hello".format(self.whoami)

        # headers = {}
        # folder_id = 0
        # if folder_id and folder_id != 0:
        #     url = self.server_base_url + '/folder/' + str(folder_id) + '/contents'
        # else:  # if no folder_id provided -> list root
        #     url = self.server_base_url + '/folder/0'
        #
        # headers['StackSync-API'] = "v2"
        #
        # r = requests.get(url, headers=headers, auth=self.oauth)
        # print 'response status', r
        # print 'response', r.text
        #
        # # list root folder content list

    def publish(self, src, tgt):
        print "{} say publish".format(self.whoami)
        ###########
        ###PUT_File
        ###########
        # curl
        # -XPUT
        # -i
        # -k
        # -H "X-Auth-Token: 63bdc8aaa0ac4a2394482d203ba09713"
        # -H "stacksync-api: true"
        # -H "list: true" "https://10.30.239.228:8080/v1/AUTH_e26e8353dbd043ae857ad6962e02f5cc/stacksync/files?file_name=blabla&overwrite=true"
        # -T Path_file

        # lookup a file parent folder and create file.
        headers = {}

        # parent = raw_input("Parent id:  ")

        # parse file name from tgt

        file_name = tgt.split('/')[-1]

        # parse
        if len(tgt.split('/')) == 2:
            # lookup for the target parent folder file_id
            pass
        else:
            parent = None

        if parent:
            url = self.server_base_url + "/file?name=" + file_name + "&parent=" + parent
        else:
            url = self.server_base_url + "/file?name=" + file_name
        # uri, headers, _ = client.sign(url, http_method='GET')
        with open(src, "r") as myfile:
            data = myfile.read()
        headers['StackSync-API'] = "v2"
        r = requests.post(url, data=data, headers=headers, auth=self.oauth)
        print 'response', r
        print 'response', r.text

    def download(self, remote, local):
        print "{} say download".format(self.whoami)

# https://github.com/stacksync/swift-API/blob/3fe1d66ab94237cfc184b6275bd6576003f75aeb/tests/api_test_menu_v2.py
