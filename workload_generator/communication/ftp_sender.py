#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

from ftplib import FTP
import traceback
import sys, os

#-------------------------------------------------------------------------------
# Upload a file to a remove ftp server
#-------------------------------------------------------------------------------
class ftp_sender():
    def __init__(self, ftp_host, ftp_port, ftp_user, ftp_pass, ftp_root):
        self.ftp = FTP()
        self.ftp.connect(ftp_host, ftp_port, 604800)  # socket set timeout 1 week timeout
        self.ftp.login(ftp_user, ftp_pass)
        print "......................................Going to root"
        print self.ftp.pwd()
        print "current directory"
        self.ftp.cwd(ftp_root)
        print self.ftp.pwd()

        self.ftp_host = ftp_host
        self.ftp_root = ftp_root

    def send(self, fname, new_name=None, sub_folder=None):
        print ">> {} <<  ".format(self.ftp.pwd())

        if sub_folder:
            self.ftp.cwd("~")  # move to home
            if self.ftp_root:
                print "move to "+self.ftp_root
                self.ftp.cwd(self.ftp_root)
            print "move to "+sub_folder
            self.ftp.cwd(sub_folder)


        # Remove any path component
        remote_name = ""
        if new_name:
            remote_name = os.path.basename(new_name)
        else:
            remote_name = os.path.basename(fname)
        remote_dir = self.ftp.pwd()
        remote_abs_path = os.path.join(remote_dir, remote_name)
        # fname, local file name path
        self.ftp.storbinary('STOR ' + remote_name, open(fname,'rb'))

        return remote_abs_path

    def mkdir(self, ftp_rel_path):
        print ">> {} <<  ".format(self.ftp.pwd())

        sub_folder = os.path.dirname(ftp_rel_path)

        self.ftp.cwd("~")  # move to home
        if self.ftp_root:
            print "move to "+self.ftp_root
            self.ftp.cwd(self.ftp_root)
        print "move to "+sub_folder
        self.ftp.cwd(sub_folder)

        # Remove any path component
        remote_name = os.path.basename(ftp_rel_path)
        remote_dir = self.ftp.pwd()
        remote_abs_path = os.path.join(remote_dir, remote_name)
        # fname, local file name path
        print remote_abs_path
        print self.ftp.pwd()
        self.ftp.mkd(remote_name)

        if sub_folder:
            self.ftp.cwd("..")
        return remote_abs_path

    def mkd(self, path):
        try:
            self.ftp.mkd(path)
        except Exception as e:
            print e.message


    def rm(self, fname, sub_folder=None):

        if sub_folder:
            self.ftp.cwd("~")  # move to home
            if self.ftp_root:
                print "move to "+self.ftp_root
                self.ftp.cwd(self.ftp_root)
            print "move to "+sub_folder
            self.ftp.cwd(sub_folder)
            # self.ftp.delete(sub_folder + "/" + os.path.basename(fname))
        print self.ftp.pwd()

        try:
            self.ftp.delete(os.path.basename(fname))
        except Exception as e:
            print "rm folder >> {}".format(fname)
            self.ftp.rmd(os.path.basename(fname))
            #traceback.print_exc(file=sys.stderr)

            # yes, there was an error...

    def rmd(self, fname, sub_folder=None):

        if sub_folder:
            self.ftp.cwd("~")  # move to home
            if self.ftp_root:
                print "move to "+self.ftp_root
                self.ftp.cwd(self.ftp_root)
            print "move to "+sub_folder
            self.ftp.cwd(sub_folder)
            # self.ftp.delete(sub_folder + "/" + os.path.basename(fname))
        print self.ftp.pwd()

        print "rm folder >> {}".format(fname)
        self.ftp.rmd(os.path.basename(fname))

            # yes, there was an error...
    def get(self, src, tgt):
        return self.ftp.retrbinary(src, tgt)

    def ls(self):
        return self.ftp.nlst()

    def close(self):
        self.ftp.close()

    def mv(self, src, tgt):
        #
        self.ftp.cwd("~")  # move to home
        if self.ftp_root:
            print "move to "+self.ftp_root
            self.ftp.cwd(self.ftp_root)

        self.ftp.rename(src, tgt)
        return os.path.join(self.ftp.pwd(), tgt)

    def move_down(self):
        self.ftp.cwd('..')
        
    def move_up(self, folder):
        self.ftp.cwd(folder)

    def cwd(self, folder):
        self.ftp.cwd(folder)
    
    def get_ftp_host(self):
        return self.ftp_host


if __name__ == '__main__':

    print 'testing ftp operations'
    ftp_client = ftp_sender('10.30.103.145', '21','milax','milax','ftpdir')


    print 'do operations'


    '''def doMakeResponse(self): '''

    '''def doPutContentResponse(self): '''

    '''def doSync(self):'''

    '''def doUnlink(self):'''

    '''def doMoveResponse(self):'''



    if ftp_client:
        print "close ftp_client"
        ftp_client.close()
