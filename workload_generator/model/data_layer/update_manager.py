'''
Created on Oct 20, 2015

@author: user
'''
import random
import tempfile
import os
from workload_generator.utils import split_list_into_chunks
from workload_generator.constants import DATA_GENERATOR_PATH, DEBUG,\
    UPDATES_CONTENT_GENERATION_PATH, DATA_GENERATOR_PROPERTIES_DIR
import subprocess
import uuid

class FileUpdateManager(object):
    
    def __init__(self):
        if not os.path.exists(UPDATES_CONTENT_GENERATION_PATH):
            os.makedirs(UPDATES_CONTENT_GENERATION_PATH)
    
    def modify_file(self, file_path, update_type, content_type, num_bytes):    
        #'B':0.38, 'E': 0.03, 'M': 0.08, 'BE': 0.1, 'BM': 0.11, 'ME': 0.01, 'BEM': 0.29
        new_content = None        
        if not DEBUG:
            os.chdir(DATA_GENERATOR_PROPERTIES_DIR)
            generated_update_content_file = UPDATES_CONTENT_GENERATION_PATH + str(uuid.uuid4())
            subprocess.call(['java', '-jar', DATA_GENERATOR_PATH, content_type, str(num_bytes), generated_update_content_file])
            in_file = open(generated_update_content_file, "rb") 
            new_content = in_file.read() 
            in_file.close()
            os.remove(generated_update_content_file)
        else: new_content = bytearray(random.getrandbits(8) for _ in range(num_bytes)) 
        if update_type == 'B': # Prepend
            self.do_prepend(file_path, new_content)
        elif update_type == 'E': # Append
            self.do_append(file_path, new_content)
        elif update_type == 'M': # Modification in the middle
            self.do_middle_update(file_path, new_content)
        elif update_type == 'BE':
            content_parts = split_list_into_chunks(new_content, 2)
            self.do_prepend(file_path, content_parts[0])
            self.do_append(file_path, content_parts[1])
        elif update_type == 'BM':
            content_parts = split_list_into_chunks(new_content, 2)
            self.do_prepend(file_path, content_parts[0])
            self.do_middle_update(file_path, content_parts[1])
        elif update_type == 'ME':
            content_parts = split_list_into_chunks(new_content, 2)
            self.do_middle_update(file_path, content_parts[0])
            self.do_append(file_path, content_parts[1])
        elif update_type == 'BEM':
            content_parts = split_list_into_chunks(new_content, 3)
            self.do_prepend(file_path, content_parts[0])
            self.do_middle_update(file_path, content_parts[1])
            self.do_append(file_path, content_parts[2])
        else:
            raise NotImplementedError("NOT IMPLEMENTED UPDATE TYPE: " + update_type)
    
    def do_prepend(self, file_path, content):
        with tempfile.TemporaryFile() as f:
            f.write(content)
            f.write(open(file_path).read())
            f.seek(0)
            dest_file = open(file_path, 'wb+')
            dest_file.write(f.read())
            dest_file.close()
            
    def do_append(self, file_path, content):
        with open(file_path, 'ab+') as dest_file:
            dest_file.write(content) 
    
    def do_middle_update(self, file_path, content):
        file_size = os.path.getsize(file_path)
        starting_point = 0
        if file_size > 1:
            starting_point = int(file_size/2)
        with open(file_path, 'r+b') as dest_file:
            dest_file.seek(starting_point)
            dest_file.write(content)
            dest_file.close()
    
    def add_content_file(self, file_path, starting_point, num_bytes):        
        rand_bytes = bytearray(random.getrandbits(8) for _ in range(num_bytes))        
        with open(file_path, 'r+b') as dest_file:
            dest_file.seek(starting_point)
            final_content = dest_file.read()
            dest_file.seek(starting_point)
            dest_file.write(rand_bytes)
            dest_file.write(final_content)
            dest_file.close()