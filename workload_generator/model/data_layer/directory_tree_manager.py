'''
Created on 23/10/2015

@author: Raul
'''
import collections
import os
import random
from workload_generator.constants import DIRECTORY_DEPTH_PROBABILITY,\
    FS_SNAPSHOT_PATH

'''Simple tree data structure and utility methods to manipulate the tree'''
def FileSystem():
    return collections.defaultdict(FileSystem)

def add_fs_node(t, path):
    if type(path) is not list:
        path = path.split(os.sep)
    for node in path:
        t = t[node]

def delete_fs_node(t, path):
    if type(path) is not list:
        path = path.split(os.sep)
    node = path.pop(0)
    if path == []: del t[node]
    else: return delete_fs_node(t[node], path)

def get_tree_node(t, path):
    if type(path) is not list:
        path = path.split(os.sep)
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
        
#Utilities to ease the management and utilization of the logical directory tree        
        
'''Pick a directory element (key) based on its probability (values)'''
def get_fitness_proportionate_element(probabilities_dict):
    file_type = None
    random_trial = random.random()
    start_range = 0.0
    for k in sorted(probabilities_dict.keys()):
        if start_range <= random_trial and random_trial <= start_range+probabilities_dict[k]:
            file_type = k
            break
        else: start_range += probabilities_dict[k]
    return file_type

'''Return an existing file in the directory tree based on the popularity of file types'''
def get_file_based_on_type_popularity(file_system, stereotype_file_types_probabilities, file_type_extensions):
    tested_file_types = set()
    selected_file = None
    while len(tested_file_types) < len(stereotype_file_types_probabilities):
        '''Prior creating a file, we first decide which type of file to create'''
        file_type = get_fitness_proportionate_element(stereotype_file_types_probabilities)
        if file_type in tested_file_types: continue
        all_files_of_type = get_fs_files_of_type(file_system, file_type_extensions[file_type], FS_SNAPSHOT_PATH)
        tested_file_types.add(file_type)
        if all_files_of_type != []:
            selected_file = random.choice(all_files_of_type)
            break
    return selected_file

'''Get a random directory from the whole tree'''
def get_random_fs_directory(tree, base_path=''):
    '''Get only directories from this tree level'''
    fs_level_directories = [fs_node for fs_node in get_tree_node(tree, base_path) if '.' not in fs_node]
    base_path += os.sep
    '''If this level has no more directories, we force this as the random position'''
    if fs_level_directories == []: return base_path
    '''If we can choose among several directories, pick one'''
    fs_node = random.choice(fs_level_directories)
    '''If the trial succeeds, this will be the new location'''
    if  random.random() < DIRECTORY_DEPTH_PROBABILITY:
        return base_path + fs_node + os.sep
    '''If not, continue the random navigation'''
    return get_random_fs_directory(tree, base_path + fs_node)

def get_empty_directory(tree, base_path=''):
    '''Get only directories from this tree level'''
    this_level_nodes = get_tree_node(tree, base_path)
    fs_level_files = [fs_node for fs_node in this_level_nodes if '.' in fs_node]
    fs_level_directories = [fs_node for fs_node in this_level_nodes if '.' not in fs_node]
    base_path += os.sep
    '''If this level has no more directories, we force this as the random position'''
    if fs_level_directories == []:
        print fs_level_files
        if fs_level_files == []: return base_path[:-1]
        else: return None
    random.shuffle(fs_level_directories)
    '''If we can choose among several directories, pick one'''
    for fs_dir in fs_level_directories:
        '''If the trial succeeds, this will be the new location'''
        empty_dir = get_empty_directory(tree, base_path + fs_dir)
        if empty_dir != None: return empty_dir
    '''If not, continue the random navigation'''
    return None

def get_fs_files_of_type(tree, file_type_extensions, base_path=''):
    '''Get all files of the given type at this level'''
    this_level_nodes = get_tree_node(tree, base_path)
    base_path += os.sep
    fs_level_files = [base_path+fs_node for fs_node in this_level_nodes if '.' in fs_node and \
                      matches_file_type(fs_node, file_type_extensions)]
    '''Get all directories at this level'''
    fs_level_directories = [fs_node for fs_node in this_level_nodes if '.' not in fs_node]
    '''If this level has no more directories, return current file list'''
    if fs_level_directories == []: return fs_level_files
    '''Continue exploring the tree'''
    for fs_dir in fs_level_directories:
        '''Get all files of the requested types on lower levels'''
        fs_level_files += get_fs_files_of_type(tree, file_type_extensions, base_path + fs_dir)
    '''Return the aggregated list'''
    return fs_level_files

def matches_file_type(fs_node, file_type_extensions):
    for extension in file_type_extensions: 
        if extension in fs_node: return True
    return False

def get_type_of_file(fs_node, file_type_extensions):
    file_extension = '.' + fs_node.split('.')[-1]
    for file_type in file_type_extensions.keys(): 
        if file_extension in file_type_extensions[file_type]: 
            return file_type
    return None