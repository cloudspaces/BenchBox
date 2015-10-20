'''
Created on Oct 20, 2015

@author: user
'''
import random
import tempfile

class FileUpdateManager(object):
    
    def modify_file(self, file_path, starting_point, num_bytes):    
        rand_bytes = bytearray(random.getrandbits(8) for _ in range(num_bytes))        
        if starting_point == 0: # Prepend
            with tempfile.TemporaryFile() as f:
                f.write(rand_bytes)
                f.write(open(file_path).read())
                f.seek(0)
                dest_file = open(file_path, 'wb+')
                dest_file.write(f.read())
                dest_file.close()
        elif starting_point == -1: # Append
            with open(file_path, 'ab+') as dest_file:
                dest_file.write(rand_bytes)  
        else: # Modification in the middle
            with open(file_path, 'r+b') as dest_file:
                dest_file.seek(starting_point)
                dest_file.write(rand_bytes)
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