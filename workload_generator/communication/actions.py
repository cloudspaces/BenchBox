'''
Created on 30/6/2015

@author: Raul
'''

class Action(object):
    
    def __init__(self, path):
        self.path = path
    
    def get_path(self):
        return self.path
    
    def perform_action(self, sender):
        raise Exception("NotImplementedException")
    
    def to_string(self):
        raise Exception("NotImplementedException")

class CreateFileOrDirectory(Action):

    '''Create file locally and in the remote host'''
    def perform_action(self, sender):
        try:
            sender.send(self.path)
        except Exception as e:
            print e
        return self.size

    def to_string(self):
        return "MakeResponse " + str(self.path) + "\n"

class DeleteFileOrDirectory(Action):

    '''Perform a remove action deleting the file from the FS
    and from the FTP. Return: 0 as no bytes are added or modified'''
    def perform_action(self, sender):       
        try:
            sender.delete(self.name)
        except Exception as e:
            print e.message
        return 0

    def to_string(self):
        return "Unlink "+str(self.name)+"\n"

class MoveFileOrDirectory(Action):

    def __init__(self, origin_path, destination_path):
        Action.__init__(self, origin_path)
        self.destination_path = destination_path

    '''Perform a remove action deleting the file from the FS
    and from the FTP. Return: 0 as no bytes are added or modified'''
    def perform_action(self, sender):        
        try:
            sender.mv(self.path, self.destination_path)
        except Exception as e:
            print e.message
        return 0

    def to_string(self):
        return "MoveResponse "+str(self.name)+"\n"

class GetContentResponse(Action):
    def __init__(self, name, dst, folder):
        Action.__init__(self, name, folder)
        self.dst = dst

    def perform_action(self, sender):
        try:
            sender.get('RETR %s' % self.name, open(self.dst+self.name, 'wb').write)
        except Exception as e:
            print e.message

    def to_string(self):
        return "GetContentResponse "+str(self.name)+"\n"

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