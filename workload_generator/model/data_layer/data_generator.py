'''
Created on 30/6/2015

@author: Raul
'''
import sys
import shutil
base_path = '/home/vagrant/workload_generator/'
sys.path.append(base_path)

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
    if type(path) is not list:
        path = path.split(os.path.sep)
    for node in path:
        t = t[node]

def delete_fs_node(t, path):
    if type(path) is not list:
        path = path.split(os.path.sep)
    node = path.pop(0)
    if path == []: del t[node]
    else: return delete_fs_node(t[node], path)

def get_tree_node(t, path):
    if type(path) is not list:
        path = path.split(os.path.sep)
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
                    #print "Activity rate: ", self.activity_rate

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
            top = top.replace("\\", os.path.sep)
            if top[-1] != os.path.sep: top += os.path.sep
            print top, dirs, files
            for dir in dirs:
                add_fs_node(self.file_system, top+dir)
            for file in files:
                add_fs_node(self.file_system, top+file)

    '''Create file at random based on the file type popularity for this stereotype'''
    def create_file(self):
        '''Prior creating a file, we first decide which type of file to create'''
        file_type = self.get_fitness_proportionate_element(self.stereotype_file_types_probabilities)
        '''After choosing the type, we proceed by generating the size of the file'''
        (function, kv_params) = self.file_types_sizes[file_type]
        size = int(get_random_value_from_fitting(function, kv_params))
        '''After generating the file size, we should decide the path for the new file'''
        synthetic_file_base_path = self.get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        '''Create a realistic name'''
        synthetic_file_base_path += get_random_alphanumeric_string(random.randint(1,20)) + \
                                    random.choice(self.stereotype_file_types_extensions[file_type])
        print "CREATING FILE: ", synthetic_file_base_path
        add_fs_node(self.file_system, synthetic_file_base_path)
        '''Invoke SDGen to generate realistic file contents'''
        characterization = DATA_CHARACTERIZATIONS_PATH + file_type
        subprocess.call(['java', '-jar', DATA_GENERATOR_PATH, characterization, str(size), synthetic_file_base_path])
        return synthetic_file_base_path

    def move_file(self):
        src_path = self.get_file_based_on_type_popularity()
        dest_path = self.get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH) 
        if src_path == None or dest_path == None:
            print "WARNING: No files or directories to move!"
            return None, None
        dest_path += src_path.split(os.path.sep)[-1]
        print "MOVE FILE: ", src_path, " TO: ", dest_path
        shutil.move(src_path, dest_path)
        delete_fs_node(self.file_system, src_path)
        add_fs_node(self.file_system, dest_path)
        return src_path, dest_path
    
    def move_directory(self):
        src_path = self.get_empty_directory(self.file_system, FS_SNAPSHOT_PATH)
        if src_path == None:
            print "WARNING: No empty directories to move!"
            return None, None
        dest_path = src_path
        '''Avoid moving a directory to itself'''
        trials = 0
        while src_path in dest_path:
            dest_path = self.get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH) + src_path.split(os.path.sep)[-1]
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
        shutil.move(src_path, dest_path)
        delete_fs_node(self.file_system, src_path)
        add_fs_node(self.file_system, dest_path)
        return src_path, dest_path

    '''Delete a file at random depending on the file type popularity for this stereotype'''
    def delete_file(self):
        to_delete = self.get_file_based_on_type_popularity()
        print "DELETING FILE: ", to_delete
        if to_delete != None:
            os.remove(to_delete)
            delete_fs_node(self.file_system, to_delete)
        '''Delete a random file from the '''
        return to_delete

    '''Create a directory in a random point of the file system'''
    def create_directory(self):
        '''Pick a random position in the fs hierarchy (consider only dirs)'''
        directory_path = self.get_random_fs_directory(self.file_system, FS_SNAPSHOT_PATH)
        to_create = directory_path + get_random_alphanumeric_string()
        print "CREATING DIRECTORY: ", to_create
        add_fs_node(self.file_system, to_create)
        os.makedirs(to_create)
        return to_create

    '''Delete an empty directory from te structure, if it does exist. If not,
    we prefer to do not perform file deletes as they may yield cascade operations'''
    def delete_directory(self):
        dir_path_to_delete = self.get_empty_directory(self.file_system, FS_SNAPSHOT_PATH)
        print "DELETING DIRECTORY: ", dir_path_to_delete
        if dir_path_to_delete != None and os.listdir(dir_path_to_delete) == []:
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
            self.current_updated_file = self.get_file_based_on_type_popularity()
            self.last_update_time = time.time()
                        
        print "FILE TO EDIT: ", self.current_updated_file
        if self.current_updated_file != None: 
            '''3) Select the type of update to be done (Prepend, Middle or Append)'''
            update_type = self.get_fitness_proportionate_element(self.file_update_location_probabilities)
            print "UPDATE TYPE: ", update_type
            '''4) Select the size of the update to be done (1%, 40% of the content)'''
            file_size = os.path.getsize(self.current_updated_file)
            updated_bytes = int(file_size*random.random()) #TODO: This should be changed by a real distribution
            update_type = self.get_fitness_proportionate_element(self.file_update_location_probabilities)
            self.file_update_manager.modify_file(self.current_updated_file, update_type, updated_bytes)
        else: print "WARNING: No files to update!"
        '''5) Return the path to the locally updated file to be transferred to the sandbox'''
        return self.current_updated_file

    '''Pick a file type based on the probabilities of this stereotype'''
    def get_fitness_proportionate_element(self, probabilities_dict):
        file_type = None
        random_trial = random.random()
        start_range = 0.0
        for k in sorted(probabilities_dict.keys()):
            if start_range <= random_trial and random_trial <= start_range+probabilities_dict[k]:
                file_type = k
                break
            else: start_range += probabilities_dict[k]
        return file_type
    
    def get_file_based_on_type_popularity(self):
        tested_file_types = set()
        selected_file = None
        while len(tested_file_types) < len(self.stereotype_file_types_probabilities):
            '''Prior creating a file, we first decide which type of file to create'''
            file_type = self.get_fitness_proportionate_element(self.stereotype_file_types_probabilities)
            if file_type in tested_file_types: continue
            all_files_of_type = self.get_fs_files_of_type(self.file_system, file_type, FS_SNAPSHOT_PATH)
            tested_file_types.add(file_type)
            if all_files_of_type != []:
                selected_file = random.choice(all_files_of_type)
                break
        return selected_file

    def get_random_fs_directory(self, tree, base_path=''):
        '''Get only directories from this tree level'''
        fs_level_directories = [fs_node for fs_node in get_tree_node(tree, base_path) if '.' not in fs_node]
        base_path += os.path.sep
        '''If this level has no more directories, we force this as the random position'''
        if fs_level_directories == []: return base_path
        '''If we can choose among several directories, pick one'''
        fs_node = random.choice(fs_level_directories)
        '''If the trial succeeds, this will be the new location'''
        if  random.random() < DIRECTORY_DEPTH_PROBABILITY:
            return base_path + fs_node + os.path.sep
        '''If not, continue the random navigation'''
        return self.get_random_fs_directory(tree, base_path + fs_node)

    def get_empty_directory(self, tree, base_path=''):
        '''Get only directories from this tree level'''
        this_level_nodes = get_tree_node(tree, base_path)
        fs_level_files = [fs_node for fs_node in this_level_nodes if '.' in fs_node]
        fs_level_directories = [fs_node for fs_node in this_level_nodes if '.' not in fs_node]
        base_path += os.path.sep
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
        this_level_nodes = get_tree_node(tree, base_path)
        base_path += os.path.sep
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
    
    for i in range(10):
        data_generator = DataGenerator()
        data_generator.initialize_from_recipe(STEREOTYPE_RECIPES_PATH + "backupsample")
        data_generator.create_file_system_snapshot()
        data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        for j in range (50):
            data_generator.create_directory()
            data_generator.delete_directory()
            data_generator.create_directory()
            data_generator.create_file()
            data_generator.create_file()
            data_generator.delete_file()
            data_generator.move_file()
            data_generator.move_directory() 
            
        '''DANGER! This deletes a directory recursively!'''    
        shutil.rmtree(FS_SNAPSHOT_PATH)       
        
    #data_generator.create_file_system_snapshot()
    #create_file('/home/user/workspace/BenchBox/external/sdgen_characterizations/text', 
    #                           '10240',
    #                           '/home/user/workspace/BenchBox/external/sdgen_characterizations/synthetic')
