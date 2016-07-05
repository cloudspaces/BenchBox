
class OwnCloud():

    def __init__(self):

        self.whoami = (self).__class__.__name__
        print self.whoami

    def hello(self):
        print "{} say hello".format(self.whoami)

    def publish(self, src, tgt):
        print "{} say publish".format(self.whoami)

    def download(self, remote, local):
        print "{} say download".format(self.whoami)