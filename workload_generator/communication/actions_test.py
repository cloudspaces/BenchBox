

'''
Testing each of the Ftp_sender action
'''
import sys
import time
import os

def appendParentDir(num, currdir):
    print currdir
    if num is 0:
        print 'return value'
        sys.path.append(currdir)
        return currdir
    else:
        dirname, basename = os.path.split(currdir)
        num-=1
        return appendParentDir(num, dirname)
appendParentDir(2, os.getcwd())

from workload_generator.constants import STEREOTYPE_RECIPES_PATH, FS_SNAPSHOT_PATH, DEBUG
from workload_generator.model.data_layer.data_generator import DataGenerator
import filecmp
from workload_generator.communication.ftp_sender import ftp_sender
import shutil
from workload_generator.communication import actions



def print_diff_files(dcmp):
    for name in dcmp.diff_files:
        print "ALERT: diff_file %s found in %s and %s" % (name, dcmp.left,dcmp.right)
    for sub_dcmp in dcmp.subdirs.values():
        print_diff_files(sub_dcmp)

def print_diff_file(path, tgt_path):
    diff = filecmp.cmp(path, tgt_path)
    print "CMP: {} --> {}".format(path, tgt_path)
    time.sleep(1)
    print diff

def print_diff_dir(path, tgt_path):
    diff = filecmp.dircmp(path, tgt_path)
    print "CMP: {} --> {}".format(path, tgt_path)
    time.sleep(1)
    diff.report_full_closure()


number = 1
operations = 1
files = 10
move_dirs = 2
del_files = 3
del_dirs = 2
FS_XXX_FOLDER = '/home/lab144/XXX_folder'
print FS_SNAPSHOT_PATH
print STEREOTYPE_RECIPES_PATH


print 'Clear file system before new test'

if not DEBUG:
    try:
        print "clear output directory!"
        shutil.rmtree(FS_SNAPSHOT_PATH)
        shutil.rmtree(FS_XXX_FOLDER)
        os.makedirs(FS_XXX_FOLDER)
    except:
        os.makedirs(FS_XXX_FOLDER)
        print "directory already clear!"
ftp_folder = 'XXX_folder'
ftp_client = ftp_sender('10.30.103.146', '21','lab144','lab144',ftp_folder)


for i in range(number):
    data_generator = DataGenerator()
    data_generator.initialize_from_recipe(STEREOTYPE_RECIPES_PATH + "backupsample")
    data_generator.create_file_system_snapshot()
    data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
    print "START GENERATING FILES"
    for j in range(operations):

        """ TEST UPLOAD DIRECTORY """
        print 'UPLOAD_DIRECTORY'
        src_path = FS_SNAPSHOT_PATH
        tgt_path = FS_XXX_FOLDER
        actions.UploadDirectory(src_path, FS_SNAPSHOT_PATH).perform_action(ftp_client)
        print_diff_dir(src_path, tgt_path)


        """ TEST CREATE FILE """
        for i in range(files):
            path = data_generator.create_file()
            tgt_path = actions.CreateFile(path, FS_SNAPSHOT_PATH).perform_action(ftp_client)


        """ TEST MOVE FILE """
        path = data_generator.move_file()
        src_path, tgt_path_local = path
        print 'MOVE_FILE: {} ---> {}'.format(src_path, tgt_path_local)
        if not src_path == tgt_path:
            tgt_path_remote = actions.MoveFile(src_path, FS_SNAPSHOT_PATH, tgt_path_local).perform_action(ftp_client)
            print_diff_file(tgt_path_local, tgt_path_remote)

        """ TEST UPDATE FILE """
        path = data_generator.update_file()
        print 'UPDATE_FILE: ' + path
        tgt_path = actions.UpdateFile(path, FS_SNAPSHOT_PATH).perform_action(ftp_client)
        print_diff_file(path, tgt_path)

        """ TEST CREATE DIRECTORY """
        path = data_generator.create_directory()
        print 'CREATE_DIR: ' + path
        tgt_path = actions.CreateDirectory(path, FS_SNAPSHOT_PATH).perform_action(ftp_client)
        print_diff_dir(path, tgt_path)


        """ TEST UPDATE FILE """
        path = data_generator.update_file()
        print 'UPDATE_FILE: ' + path
        tgt_path = actions.UpdateFile(path, FS_SNAPSHOT_PATH).perform_action(ftp_client)
        print_diff_file(path, tgt_path)

        """ TEST MOVE DIRECTORY """
        print "- - - - MOVE DIRECTORY - - - -"
        for i in range(move_dirs):
            path = data_generator.move_directory()
            print 'MOVE_DIRECTORY:::  from {} ----> to {}'.format(src_path, tgt_path)
            src_path, tgt_path = path
            tgt_path = actions.MoveDirectory(src_path, FS_SNAPSHOT_PATH, tgt_path).perform_action(ftp_client)
        #print_diff_dir(src_path, tgt_path)


        """ TEST DELETE FILE """
        for i in range(del_files):
            src_path = data_generator.delete_file()
            print "DELETE FILE:::  at ----> {}".format(src_path)
            actions.DeleteFile(src_path, FS_SNAPSHOT_PATH).perform_action(ftp_client)
            print_diff_dir(FS_XXX_FOLDER, FS_SNAPSHOT_PATH)







        """ TEST DELETE DIRECTORY """
        for i in range(del_dirs):
            src_path = data_generator.delete_directory()
            print "DELETE DIRECTORY:::  at ----> to {}".format(src_path)
            actions.DeleteDirectory(src_path, FS_SNAPSHOT_PATH).perform_action(ftp_client)
            print_diff_dir(FS_XXX_FOLDER, FS_SNAPSHOT_PATH)



        raw_input()



    '''DANGER! This deletes a directory recursively!'''
    '''
    if not DEBUG:
        shutil.rmtree(FS_SNAPSHOT_PATH)
    '''
    # diff -qr BenchBox/output/ XXX_folder/

if ftp_client:
    ftp_client.close()