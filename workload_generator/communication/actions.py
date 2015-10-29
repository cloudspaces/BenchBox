'''
Created on 30/6/2015

@author: Raul
'''
import os
from termcolor import colored

class Action(object):
    
    def __init__(self, path):
        print path
        self.path = path
    
    def get_path(self):
        return self.path
    
    def perform_action(self, sender):
        raise Exception("NotImplementedException")
    
    def to_string(self):
        raise Exception("NotImplementedException")


# OK
class CreateFileOrDirectory(Action):

    def __init__(self, output_src, output_root):
        self.output_root = output_root
        Action.__init__(self, output_src)
    '''Create file locally and in the remote host'''
    def perform_action(self, sender):
        try:
            send_output_to = os.path.relpath(os.path.dirname(self.path), self.output_root)  # / == output
            print "send: {} -> to: {}".format(self.path, send_output_to)
            sender.send(self.path, None, send_output_to)
        except Exception as e:
            print e
        # TODO return self.size
        return 0

    def to_string(self):
        return "MakeResponse " + str(self.path) + "\n"


# OK
class DeleteFileOrDirectory(Action):

    '''Perform a remove action deleting the file from the FS
    and from the FTP. Return: 0 as no bytes are added or modified'''
    def __init__(self, output_src, output_root):
        self.output_root = output_root
        Action.__init__(self, output_src)

    def perform_action(self, sender):
        try:
            print "delete: -> to: {}".format(self.path)
            delete_output_at = os.path.relpath(os.path.dirname(self.path), self.output_root)
            delete_output_filename = os.path.basename(self.path)
            sender.rm(delete_output_filename, delete_output_at)
        except Exception as e:
            print "removed a folder "  # e.message
        return 0

    def to_string(self):
        return "Unlink "+str(self.path)+"\n"

#
class MoveFileOrDirectory(Action):
    def __init__(self, output_src, output_root, output_tgt=None):
        self.output_root = output_root
        if output_tgt is None:  # if output_tgt == None upload to remote
            self.is_upload = True
            self.output_tgt = output_root
        else:
            self.is_upload = False
            self.output_tgt = output_tgt
        Action.__init__(self, output_src)

    def perform_action(self, sender):
        print "MOVE PATH source path:::::"
        print self.path
        print "MOVE PATH Target path-----"
        print self.output_tgt
        try:
            # look if the file at the target location is a file or directory
            if os.path.isfile(self.output_tgt):
                print "is file"+self.output_tgt
                print colored("move a FILE","cyan")
                ftp_rel_src_path = os.path.relpath(self.path, self.output_root)
                ftp_rel_tgt_path = os.path.relpath(self.output_tgt, self.output_root)
                sender.mv(ftp_rel_src_path, ftp_rel_tgt_path) # rename the file at sandBox ftp_folder from # ftp_root
            else:
                print "is not file"+self.output_tgt

            if os.path.isdir(self.output_tgt):
                print "is dir"+self.output_tgt
                print self.is_upload
                if self.is_upload:
                    print colored("upload a folder",'green')
                    self.uploadFolder(sender, self.path, self.output_tgt) # self.path is the source path of the folder at sandBox
                else:
                    print colored("move a folder","red")
                    self.moveFolder(sender, self.path, self.output_tgt)
                    print colored(" REMOVE FOLDER AFTER moving all the files",'red')
                    #delete_output_at = os.path.relpath(os.path.dirname(self.path), self.output_root)
                    #delete_output_filename = os.path.basename(self.path)
                    #sender.rm(delete_output_filename, delete_output_at)

                    print "just move the folder"
                    print sender.ftp.pwd()
                    sender.mkd(os.path.join(sender.ftp_root, os.path.relpath(self.output_tgt, self.output_root)))
                    print "remove the folder"
                    sender.rm(self.path, os.path.dirname(os.path.relpath(self.path, self.output_root)))
                    # remove folder after move the directories
            else:
                print "is not dir"+self.output_tgt
        except Exception as e:
            print e.message
        return 0

    def moveFolder(self, ftp_client, src_path, tgt_path):
        print "move folder from {} -> {}".format(src_path, tgt_path)
        print src_path
        print tgt_path

        files = os.listdir(tgt_path) # list the files at the source directory
        print "files to move: {}".format(files)
        os.chdir(tgt_path) # goto the directory

        if len(files) == 0:
            print "no files to move"

        for f in files:
            print "moving file {}".format(f)

            source_file = '{}/{}'.format(source_file, f)
            target_file = '{}/{}'.format(tgt_path, f)

            print(target_file)
            if os.path.isfile(target_file):
                print "{} -> {}".format(source_file, target_file)
                print colored("move a FILE","cyan")
                ftp_rel_src_path = os.path.relpath(self.source_file, self.output_root)
                ftp_rel_tgt_path = os.path.relpath(self.target_file, self.output_root)
                ftp_client.mv(ftp_rel_src_path, ftp_rel_tgt_path) # rename the file at sandBox ftp_folder from # ftp_root

            elif os.path.isdir(target_file):
                print "{} is dir".format(target_file)
                ftp_client.mkd(f)
                ftp_client.cwd(f)
                self.moveFolder(ftp_client, target_file, target_file)
        ftp_client.cwd('..')
        os.chdir('..')

    # move files at the remote fs, src_path to tgt_path
    def uploadFolder(self, ftp_client, src_path, tgt_path):
        files = os.listdir(src_path)  # list the files at the source directory
        os.chdir(src_path)  # goto the directory
        for f in files:

            target_file = '{}/{}'.format(tgt_path, f)
            print colored(target_file, 'yellow')
            if os.path.isfile(target_file):
                print "{} is file".format(target_file)
                 #if tgt_path == src_path:
                ftp_client.send(f)
                """
                else:
                    file_remote_abs_path = os.path.relpath(tgt_path, src_path)
                    print "mv from: {} -> {}".format(f, file_remote_abs_path)
                    ftp_client.mv(f, os.path.relpath(tgt_path, src_path))
                """
            elif os.path.isdir(target_file):
                print "{} is dir".format(target_file)
                ftp_client.mkd(f)
                ftp_client.cwd(f)
                self.uploadFolder(ftp_client, target_file, target_file)
        ftp_client.cwd('..')
        os.chdir('..')


    def to_string(self):
        return "MoveResponse "+str(self.path)+"\n"

class GetContentResponse(Action):
    def __init__(self, name, dst, folder):
        Action.__init__(self, name, folder)
        self.dst = dst

    def perform_action(self, sender):
        try:
            sender.get('RETR %s' % self.path, open(self.dst+self.path, 'wb').write)
        except Exception as e:
            # print e.message
            print ""

    def to_string(self):
        return "GetContentResponse "+str(self.path)+"\n"

# def get_action(args, folder):
#     
#     action_str = args[0]
#     name = args[1]
#     print action_str
# 
#     if action_str == "MakeResponse":
#         size = int(args[2])
#         action = MakeResponse(name, size, folder)
#     elif action_str == "GetContentResponse":
#         dst = args[2]
#         action = GetContentResponse(name, dst, folder)
#     elif action_str == "PutContentResponse":
#         updates = []
#         modifications = args[2]
#         i = 0
#         while i < len(modifications):
#             start = int(modifications[i])
#             end = int(modifications[i+1])
#             updates.append((start, end))
#             i += 2
#         action = PutContentResponse(name, updates, folder)
#     elif action_str == "Unlink":
#         action = Unlink(name, folder)
#     elif action_str == "MoveResponse":
#         tgt = args[2]
#         action = MoveResponse(name, tgt, folder)
#     else:
#         print 'Action Not Found!'
#     return action
#         
### ------------------------- ###
### ------------------------- ###

if __name__ == '__main__':
    print 'This is the main Program'

    #ftp_client = ftp_sender("192.168.56.2",'21',"vagrant","vagrant","stacksync_folder")
    #MoveFileOrDirectory('../../ouput','').perform_action(ftp_client)
    from ftp_sender import ftp_sender

    server = '192.168.56.101'
    username = 'vagrant'
    password = 'vagrant'
    path = 'stacksync_folder'
    ftp_client = ftp_sender(server, "21", username, password, path)
    MoveFileOrDirectory('/home/vagrant/output', '').perform_action(ftp_client)
