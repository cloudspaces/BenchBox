'''
Created on 30/6/2015

@author: Raul
'''
import sys
import shutil
import getpass
import subprocess
import random
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
appendParentDir(3, os.path.dirname(os.path.realpath(__file__)))


from workload_generator.utils import get_random_value_from_fitting, get_random_alphanumeric_string
from workload_generator.constants import FS_IMAGE_PATH, FS_IMAGE_CONFIG_PATH, \
    DATA_CHARACTERIZATIONS_PATH, FS_SNAPSHOT_PATH, \
    DATA_GENERATOR_PATH, STEREOTYPE_RECIPES_PATH, DEBUG, DATA_GENERATOR_PROPERTIES_DIR
import time
from workload_generator.model.data_layer.update_manager import FileUpdateManager
from workload_generator.model.data_layer.directory_tree_manager import delete_fs_node, \
    add_fs_node, FileSystem, get_file_based_on_type_popularity, \
    get_random_fs_directory, get_empty_directory, \
    get_fitness_proportionate_element, get_type_of_file

class DataGenerator(object):

    def __init__(self):
        self.debug_mode = DEBUG
        self.file_system = FileSystem()
        self.file_update_manager = FileUpdateManager()
        '''Parameters to model files and directories'''
        self.stereotype_file_types_probabilities = dict()
        self.stereotype_file_types_extensions = dict()
        self.file_types_sizes = dict()  #Bytes
        self.directory_count_distribution = None
        '''Parameters to model files updates'''
        self.file_update_location_probabilities = dict() #Extracted from Tarasov paper, Home dataset
        self.current_updated_file = None
        self.last_update_time = -1

    def initialize_from_recipe(self, stereotype_recipe):
        for l in open(stereotype_recipe, "r"):
            model_attribute = l.split(',')[0]
            if model_attribute in dir(self):
                if model_attribute == "directory_count_distribution":
                    fitting = l.split(',')[1]
                    kw_params = eval(l[l.index('{'):])
                    setattr(self, model_attribute, (fitting, kw_params))
                else:
                    setattr(self, model_attribute, eval(l[l.index('{'):]))

    '''Initialize the file system of the user (delegated to Impressions benchmark)'''
    def create_file_system_snapshot(self):
        '''Get initial number of directories for this user'''
        (function, kv_params) = self.directory_count_distribution
        num_dirs = get_random_value_from_fitting(function, kv_params)
        '''Change config file of Impressions'''
        fs_config = ''
        for line in open(FS_IMAGE_CONFIG_PATH, 'r'):
            if "Parent_Path: " in line:
                line = "Parent_Path: " + FS_SNAPSHOT_PATH + " 1\n"
                if not DEBUG and not os.path.exists(FS_SNAPSHOT_PATH):
                    os.makedirs(FS_SNAPSHOT_PATH)
            if "Numdirs" in line:
                line = "Numdirs: " + str(num_dirs) + " N\n"
            fs_config = ''.join([fs_config, line])
        fs_config_file = open(FS_IMAGE_CONFIG_PATH, 'w')
        print >> fs_config_file, fs_config[:-1]
        fs_config_file.close()
        '''Create the file system'''
        time.sleep(1)
        if not DEBUG:
            subprocess.call([FS_IMAGE_PATH, FS_IMAGE_CONFIG_PATH])

    '''Generate the logical structure of the initial snapshot before migration to sandbox'''
    def initialize_file_system_tree(self, fs_snapshot_path):
        for top, dirs, files in os.walk(fs_snapshot_path):
            top = top.replace("\\", os.sep)
            if top[-1] != os.sep: top += os.sep
            print top, dirs, files
            for dir in dirs:
                add_fs_node(self.file_system, top+dir)
            for file in files:
                add_fs_node(self.file_system, top+file)

    '''Create file at random based on the file type popularity for this stereotype'''
    # todo create files with realistic file size
    def create_file(self):
        '''Prior creating a file, we first decide which type of file to create'''
        file_type = get_fitness_proportionate_element(self.stereotype_file_types_probabilities)
        '''After choosing the type, we proceed by generating the size of the file'''
        (function, kv_params) = self.file_types_sizes[file_type]
        size = int(get_random_value_from_fitting(function, kv_params))
        '''After generating the file size, we should decide the path for the new file'''
        synthetic_file_base_path = get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        '''Create a realistic name'''
        synthetic_file_base_path += get_random_alphanumeric_string(random.randint(1,20)) + \
                                    random.choice(self.stereotype_file_types_extensions[file_type])
        print "CREATING FILE: ", synthetic_file_base_path
        # se tiene que realizar los cdf en un nivel mas bajo
        add_fs_node(self.file_system, synthetic_file_base_path)
        '''Invoke SDGen to generate realistic file contents'''
        characterization = DATA_CHARACTERIZATIONS_PATH + file_type

        if not DEBUG:
            os.chdir(DATA_GENERATOR_PROPERTIES_DIR)
            subprocess.call(['java', '-jar', DATA_GENERATOR_PATH, characterization, str(size), synthetic_file_base_path])
        return synthetic_file_base_path

    def move_file(self):
        src_path = get_file_based_on_type_popularity(self.file_system, self.stereotype_file_types_probabilities, self.stereotype_file_types_extensions)
        dest_path = get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        if src_path == None or dest_path == None:
            print "WARNING: No files or directories to move!"
            return None, None
        dest_path += src_path.split(os.sep)[-1]
        print "MOVE FILE: ", src_path, " TO: ", dest_path
        if not DEBUG:
            shutil.move(src_path, dest_path)
        delete_fs_node(self.file_system, src_path)
        add_fs_node(self.file_system, dest_path)
        return src_path, dest_path

    def move_directory(self):
        src_path = get_empty_directory(self.file_system, FS_SNAPSHOT_PATH)
        if src_path == None:
            print "WARNING: No empty directories to move!"
            return None, None
        dest_path = src_path
        '''Avoid moving a directory to itself'''
        trials = 0
        while src_path in dest_path:
            dest_path = get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH) + src_path.split(os.sep)[-1]
            trials +=1
            '''Avoid infinite loops'''
            if trials > 5:
                dest_path = None
                break

        if dest_path == None:
            print "WARNING: Not enough distinct directories to move!"
            return None, None

        '''If things are ok, do the move operation'''
        print "MOVE DIRECTORY: ", src_path, " TO: ", dest_path
        if not DEBUG:
            shutil.move(src_path, dest_path)
        delete_fs_node(self.file_system, src_path)
        add_fs_node(self.file_system, dest_path)
        return src_path, dest_path

    '''Delete a file at random depending on the file type popularity for this stereotype'''
    def delete_file(self):
        to_delete = get_file_based_on_type_popularity(self.file_system, self.stereotype_file_types_probabilities, self.stereotype_file_types_extensions)
        print "DELETING FILE: ", to_delete
        if to_delete != None:
            if not DEBUG:
                os.remove(to_delete)
            delete_fs_node(self.file_system, to_delete)
        '''Delete a random file from the '''
        return to_delete

    '''Create a directory in a random point of the file system'''
    def create_directory(self):
        '''Pick a random position in the fs hierarchy (consider only dirs)'''
        directory_path = get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        to_create = directory_path + get_random_alphanumeric_string()
        print "CREATING DIRECTORY: ", to_create
        if not DEBUG:
            os.makedirs(to_create)
        add_fs_node(self.file_system, to_create)
        return to_create

    '''Delete an empty directory from te structure, if it does exist. If not,
    we prefer to do not perform file deletes as they may yield cascade operations'''
    def delete_directory(self):
        dir_path_to_delete = get_empty_directory(self.file_system, FS_SNAPSHOT_PATH)
        print "DELETING DIRECTORY: ", dir_path_to_delete
        if dir_path_to_delete != None and (DEBUG or os.listdir(dir_path_to_delete) == []):
            if not DEBUG:
                os.rmdir(dir_path_to_delete)
            delete_fs_node(self.file_system, dir_path_to_delete)
        return dir_path_to_delete

    def update_file(self):
        '''We have to respect both temporal and spatial localities, as well as to model updates themselves'''
        '''Make use of the UpdateManager for the last aspect'''
        '''1) If there is a file that has been updated, check if we should continue editing it'''
        if self.current_updated_file != None or time.time()-self.last_update_time > 10: #TODO: This threshold should be changed by a real distribution
            '''2) Select a random file of the given type to update (this is a simple approach, which can be
            sophisticated, if necessary, by adding individual "edit probabilities" to files based on distributions)'''
            self.current_updated_file = get_file_based_on_type_popularity(self.file_system, \
                                                                          self.stereotype_file_types_probabilities, self.stereotype_file_types_extensions)
            self.last_update_time = time.time()

        print "FILE TO EDIT: ", self.current_updated_file
        if self.current_updated_file != None:
            '''3) Select the type of update to be done (Prepend, Middle or Append)'''
            update_type = get_fitness_proportionate_element(self.file_update_location_probabilities)
            '''4) Select the size of the update to be done (1%, 40% of the content)'''
            if not DEBUG:
                file_size = os.path.getsize(self.current_updated_file)
                updated_bytes = int(file_size*random.random()) #TODO: This should be changed by a real distribution            
                print "UPDATE TYPE: ", update_type, " UPDATE SIZE: ", updated_bytes
                content_type = DATA_CHARACTERIZATIONS_PATH + get_type_of_file(self.current_updated_file, self.stereotype_file_types_extensions)
                self.file_update_manager.modify_file(self.current_updated_file, update_type, content_type, updated_bytes)
        else: print "WARNING: No files to update!"
        '''5) Return the path to the locally updated file to be transferred to the sandbox'''
        return self.current_updated_file

if __name__ == '__main__':
    # import random
    test_iterations=1
    for i in range(test_iterations):
        data_generator = DataGenerator()
        data_generator.initialize_from_recipe(STEREOTYPE_RECIPES_PATH + "receipt/receipt_sample_backup")
        # data_generator.initialize_from_recipe(STEREOTYPE_RECIPES_PATH + "backupsample")
        data_generator.create_file_system_snapshot()
        data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        do_list = {
            0: data_generator.update_file,
            1: data_generator.create_directory,
            2: data_generator.delete_directory,
            3: data_generator.create_directory,
            4: data_generator.create_file,
            5: data_generator.delete_file,
            6: data_generator.move_file,
            7: data_generator.move_directory,
            8: data_generator.update_file,
            9: data_generator.update_file,
        }
        number_of_ops = 50
        for j in range (number_of_ops):
            todo = random.randint(0, 9)
            do_list[todo]()

        '''DANGER! This deletes a directory recursively!'''
        if not DEBUG:
            shutil.rmtree(FS_SNAPSHOT_PATH)

            #data_generator.create_file_system_snapshot()
            #create_file('/home/user/workspace/BenchBox/external/sdgen_characterizations/text',
            #                           '10240',
            #                           '/home/user/workspace/BenchBox/external/sdgen_characterizations/synthetic')