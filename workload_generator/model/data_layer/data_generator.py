'''
Created on 30/6/2015

@author: Raul
'''

import subprocess
import random
import collections
import os

from workload_generator.utils import get_random_value_from_fitting, get_random_alphanumeric_string
from workload_generator.constants import FS_IMAGE_PATH, FS_IMAGE_CONFIG_PATH,\
    DATA_CHARACTERIZATIONS_PATH, DIRECTORY_DEPTH_PROBABILITY, FS_SNAPSHOT_PATH,\
    DATA_GENERATOR_PATH, STEREOTYPE_RECIPES_PATH, DEBUG
import time
from workload_generator.model.data_layer.update_manager import FileUpdateManager

'''Simple tree data structure and utility methods to manipulate the tree'''
def FileSystem():
    return collections.defaultdict(FileSystem)

def add_fs_node(t, path):
    for node in path:
        t = t[node]

def delete_fs_node(t, path):
    node = path.pop(0)
    if path == []: del t[node]
    else: return delete_fs_node(t[node], path)

def get_tree_node(t, path):
    node = path.pop(0)
    if path == []: return t[node]
    else: return get_tree_node(t[node], path)

def print_tree(t, depth = 0):
    """ print a tree """
    for k in t.keys():
        print("%s %2d %s" % ("".join(depth * ["    "]), depth, k))
        depth += 1
        print_tree(t[k], depth)
        depth -= 1

class DataGenerator(object):

    def __init__(self):
        self.debug_mode = DEBUG
        self.file_system = FileSystem()
        self.file_update_manager = FileUpdateManager()
        self.stereotype_file_types = dict()
        self.stereotype_file_types_extensions = dict()
        self.file_types_sizes = dict()  #KB
        #Extracted from Tarasov paper, Home dataset
        self.file_update_location_probabilities = dict()
        self.current_updated_file = None
        self.initial_num_directories = None
        self.last_update_time = -1

    def initialize_from_recipe(self, stereotype_recipe):
        for l in open(stereotype_recipe, "r"):
            model_attribute = l.split(',')[0]
            if model_attribute in dir(self):
                if model_attribute == "initial_num_directories":
                    fitting = l.split(',')[1]
                    kw_params = eval(l[l.index('{'):])
                    setattr(self, model_attribute, (fitting, kw_params))
                else:
                    setattr(self, model_attribute, eval(l[l.index('{'):]))
                    #print "Activity rate: ", self.activity_rate

    '''Initialize the file system of the user (delegated to Impressions benchmark)'''
    def create_file_system_snapshot(self):
        '''Get initial number of directories for this user'''
        (function, kv_params) = self.initial_num_directories
        num_dirs = get_random_value_from_fitting(function, kv_params)
        '''Change config file of Impressions'''
        fs_config = ''
        for line in open(FS_IMAGE_CONFIG_PATH, 'r'):
            if "Parent_Path: " in line:
                line = "Parent_Path: " + FS_SNAPSHOT_PATH + " 1\n"
                if not os.path.exists(FS_SNAPSHOT_PATH):
                    os.makedirs(FS_SNAPSHOT_PATH)
            if "Numdirs" in line:
                line = "Numdirs: " + str(num_dirs) + " N\n"
            fs_config = ''.join([fs_config, line])
        fs_config_file = open(FS_IMAGE_CONFIG_PATH, 'w')
        print >> fs_config_file, fs_config[:-1]
        fs_config_file.close()
        '''Create the file system'''
        time.sleep(1)
        subprocess.call([FS_IMAGE_PATH, FS_IMAGE_CONFIG_PATH])

    '''Generate the logical structure of the initial snapshot before migration to sandbox'''
    def initialize_file_system_tree(self, fs_snapshot_path):
        for top, dirs, files in os.walk(fs_snapshot_path):
            top = top.replace("\\", "/")
            if top[-1] != '/': top += '/'
            print top, dirs, files
            for dir in dirs:
                add_fs_node(self.file_system, (top+dir).split('/'))
            for file in files:
                add_fs_node(self.file_system, (top+file).split('/'))

    #TODO: After initializing the file system, we need to move it to the sandbox
    def migrate_file_system_snapshot_to_sandbox(self, to_migrate):
        print "move the whole fs to the sandbox via ftp during warm-up"

    '''Create file at random based on the file type popularity for this stereotype'''
    def create_file(self):
        '''Prior creating a file, we first decide which type of file to create'''
        file_type = self.get_fitness_proportionate_file_type()
        '''After choosing the type, we proceed by generating the size of the file'''
        (function, kv_params) = self.file_types_sizes[file_type]
        size = int(get_random_value_from_fitting(function, kv_params))
        '''After generating the file size, we should decide the path for the new file'''
        synthetic_file_base_path = self.get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        '''Create a realistic name'''
        synthetic_file_base_path += get_random_alphanumeric_string(random.randint(1,20)) + \
                                    random.choice(self.stereotype_file_types_extensions[file_type])
        print "CREATING FILE: ", synthetic_file_base_path
        add_fs_node(self.file_system, synthetic_file_base_path.split('/'))
        '''Invoke SDGen to generate realistic file contents'''
        characterization = DATA_CHARACTERIZATIONS_PATH + file_type
        subprocess.call(['java', '-jar', DATA_GENERATOR_PATH, characterization, str(size), synthetic_file_base_path])
        return synthetic_file_base_path

    #TODO: MISSING!
    def move_file(self):
        print "MOVE FILE"

    #TODO: MISSING!
    def move_directory(self):
        print "MOVE DIRECTORY"

    '''Delete a file at random depending on the file type popularity for this stereotype'''
    def delete_file(self):
        tested_file_types = set()
        to_delete = None
        while len(tested_file_types) < len(self.stereotype_file_types):
            '''Prior creating a file, we first decide which type of file to create'''
            file_type = self.get_fitness_proportionate_file_type()
            if file_type in tested_file_types: continue
            all_files_of_type = self.get_fs_files_of_type(self.file_system, file_type, FS_SNAPSHOT_PATH)
            tested_file_types.add(file_type)
            if all_files_of_type != []:
                to_delete = random.choice(all_files_of_type)
                break

        print "DELETING FILE: ", to_delete
        if to_delete != None:
            delete_fs_node(self.file_system, to_delete.split('/'))
        '''Delete a random file from the '''
        return to_delete

    '''Create a directory in a random point of the file system'''
    def create_directory(self):
        '''Pick a random position in the fs hierarchy (consider only dirs)'''
        directory_path = self.get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        to_create = directory_path + get_random_alphanumeric_string()
        print "CREATING DIRECTORY: ", to_create
        add_fs_node(self.file_system, to_create.split('/'))
        os.makedirs(to_create)
        return to_create

    '''Delete an empty directory from te structure, if it does exist. If not,
    we prefer to do not perform file deletes as they may yield cascade operations'''
    def delete_directory(self):
        dir_path_to_delete = self.get_empty_directory(self.file_system, FS_SNAPSHOT_PATH)
        print "DELETING DIRECTORY: ", dir_path_to_delete
        if dir_path_to_delete != None and os.listdir(dir_path_to_delete) == []:
            os.rmdir(dir_path_to_delete)
            delete_fs_node(self.file_system, dir_path_to_delete.split('/'))
        return dir_path_to_delete

    #TODO: Updates are missing, and will we somewhat complex to do
    def update_file(self):
        '''We have to respect both temporal and spatial localities, as well as to model updates themselves'''
        '''Make use of the UpdateManager for the last aspect'''
        '''1) If there is a file that has been updated, check if we should continue editing it'''
        if self.current_updated_file != None or time.time()-self.last_update_time > 10:
            '''2) If we select a new file, do it based on popularity'''
            self.current_updated_file = 'Select new file to update'
            self.last_update_time = time.time()
        '''3) Select the type of update to be done (Prepend, Middle or Append)'''

        '''4) Select the size of the update to be done (1%, 40% of the content)'''

        return "text.txt"

    '''Pick a file type based on the probabilities of this stereotype'''
    def get_fitness_proportionate_file_type(self):
        file_type = None
        random_trial = random.random()
        start_range = 0.0
        for k in sorted(self.stereotype_file_types.keys()):
            if start_range <= random_trial and random_trial <= start_range+self.stereotype_file_types[k]:
                file_type = k
                break
            else: start_range += self.stereotype_file_types[k]
        return file_type

    def get_random_fs_directory(self, tree, base_path=''):
        '''Get only directories from this tree level'''
        fs_level_directories = [fs_node for fs_node in get_tree_node(tree, base_path.split('/')) if '.' not in fs_node]
        base_path += '/'
        '''If this level has no more directories, we force this as the random position'''
        if fs_level_directories == []: return base_path
        '''If we can choose among several directories, pick one'''
        fs_node = random.choice(fs_level_directories)
        '''If the trial succeeds, this will be the new location'''
        if  random.random() < DIRECTORY_DEPTH_PROBABILITY:
            return base_path + fs_node + '/'
        '''If not, continue the random navigation'''
        return self.get_random_fs_directory(tree, base_path + fs_node)

    def get_empty_directory(self, tree, base_path=''):
        '''Get only directories from this tree level'''
        this_level_nodes = get_tree_node(tree, base_path.split('/'))
        fs_level_files = [fs_node for fs_node in this_level_nodes if '.' in fs_node]
        fs_level_directories = [fs_node for fs_node in this_level_nodes if '.' not in fs_node]
        base_path += '/'
        '''If this level has no more directories, we force this as the random position'''
        if fs_level_directories == []:
            print fs_level_files
            if fs_level_files == []: return base_path[:-1]
            else: return None
        random.shuffle(fs_level_directories)
        '''If we can choose among several directories, pick one'''
        for fs_dir in fs_level_directories:
            '''If the trial succeeds, this will be the new location'''
            empty_dir = self.get_empty_directory(tree, base_path + fs_dir)
            if empty_dir != None: return empty_dir
        '''If not, continue the random navigation'''
        return None

    def get_fs_files_of_type(self, tree, file_type, base_path=''):
        '''Get all files of the given type at this level'''
        this_level_nodes = get_tree_node(tree, base_path.split('/'))
        base_path += '/'
        fs_level_files = [base_path+fs_node for fs_node in this_level_nodes if '.' in fs_node and \
                          self.matches_file_type(fs_node, file_type)]
        '''Get all directories at this level'''
        fs_level_directories = [fs_node for fs_node in this_level_nodes if '.' not in fs_node]
        '''If this level has no more directories, return current file list'''
        if fs_level_directories == []: return fs_level_files
        '''Continue exploring the tree'''
        for fs_dir in fs_level_directories:
            '''Get all files of the requested types on lower levels'''
            fs_level_files += self.get_fs_files_of_type(tree, file_type, base_path + fs_dir)
        '''Return the aggregated list'''
        return fs_level_files

    def matches_file_type(self, fs_node, file_type):
        for extension in self.stereotype_file_types_extensions[file_type]:
            if extension in fs_node: return True
        return False

if __name__ == '__main__':
    data_generator = DataGenerator()
    data_generator.initialize_from_recipe(STEREOTYPE_RECIPES_PATH + "backupsample")
    data_generator.create_file_system_snapshot()
    data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
    for i in range (50):
        data_generator.create_directory()
        data_generator.delete_directory()
        data_generator.create_file()
        data_generator.create_file()
        data_generator.delete_file()

    print_tree(data_generator.file_system)
    #data_generator.create_file_system_snapshot()
    #create_file('/home/user/workspace/BenchBox/external/sdgen_characterizations/text', 
    #                           '10240',
    #                           '/home/user/workspace/BenchBox/external/sdgen_characterizations/synthetic')