'''
Created on 30/6/2015

@author: Raul
'''
import os

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

class CreateFileOrDirectory(Action):

    def __init__(self, origin_path, fs_rel_path):
        self.fs_rel_path = fs_rel_path
        Action.__init__(self, origin_path)
    '''Create file locally and in the remote host'''
    def perform_action(self, sender):
        try:
            # os.path.basename('/home/vagrant/output/2/12/36/2205FC054D7BD409BF59.jpg') -> 2205FC054D7BD409BF59.jpg
            # sender.send(os.path.basename(self.path), os.path.dirname(self.path))
            print "send: {} -> to: {}".format(self.path, os.path.relpath(os.path.dirname(self.path), self.fs_rel_path))
            #sender.send(self.path, os.path.dirname(self.path))
            sender.send(self.path, None, os.path.relpath(os.path.dirname(self.path), self.fs_rel_path))
        except Exception as e:
            print e
        # TODO return self.size
        return 0

    def to_string(self):
        return "MakeResponse " + str(self.path) + "\n"

class DeleteFileOrDirectory(Action):

    '''Perform a remove action deleting the file from the FS
    and from the FTP. Return: 0 as no bytes are added or modified'''
    def __init__(self, origin_path, fs_rel_path):
        self.fs_rel_path = fs_rel_path
        Action.__init__(self, origin_path)

    def perform_action(self, sender):
        try:
            print "delete: -> to: {}".format(self.path)
            sender.rm(os.path.basename(self.path), os.path.relpath(os.path.dirname(self.path), self.fs_rel_path))
        except Exception as e:
            print e.message
        return 0

    def to_string(self):
        return "Unlink "+str(self.path)+"\n"

class MoveFileOrDirectory(Action):

    def __init__(self, origin_path, fs_rel_path):
        self.fs_rel_path = fs_rel_path
        Action.__init__(self, origin_path)

    '''Perform a remove action deleting the file from the FS
    and from the FTP. Return: 0 as no bytes are added or modified'''
    def perform_action(self, sender):
        try:
            # sender.mv(self.path, self.destination_path)
            self.uploadFolder(sender, self.path, self.fs_rel_path) # self.path is the source path of the folder
        except Exception as e:
            print e.message
        return 0


    def uploadFolder(self, sender, tgt_path, src_path):
        #print "Push files to target: {}".format(path)
        # http://www.programmerinterview.com/index.php/general-miscellaneous/ftp-command-to-transfer-a-directory/
        files = os.listdir(src_path) # list the files at the source directory
        #print files
        #print "Currdir: {}".format(os.getcwd())
        os.chdir(src_path) # goto the directory
        for f in files:

            target_file = '{}/{}'.format(tgt_path, f)

            #print os.path.isfile(target_file)
            #print os.path.isdir(target_file)

            print(target_file)
            if os.path.isfile(target_file):
                print "{} is file".format(target_file)
                if(tgt_path == src_path):
                    sender.send(f)
                else:
                    print "mv from: {} -> {}".format(f,os.path.relpath(tgt_path, src_path))
                    sender.mv(f, os.path.relpath(tgt_path, src_path))
            elif os.path.isdir(target_file):
                print "{} is dir".format(target_file)
                sender.mkd(f)
                sender.cwd(f)
                self.uploadFolder(sender, target_file, target_file)
        sender.cwd('..')
        os.chdir('..')
        #print "Finish Moving"


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
