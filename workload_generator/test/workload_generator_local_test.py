'''
Created on Jul 14, 2016

@author: raul
'''
from workload_generator.model.user_activity.stereotype_executor import StereotypeExecutor
from workload_generator.constants import FS_SNAPSHOT_PATH,\
    STEREOTYPE_RECIPES_PATH

import time

'''Dummy class to emulate the calls of the real one, for simulation purposes'''
class TestExecutor(StereotypeExecutor):
    
    def __init__(self):
        super(TestExecutor, self).__init__()
    
    '''Do an execution step as a client'''
    def execute(self): 
        '''Get the next operation to be done'''
        self.next_operation()
        to_execute = getattr(self, 'do_' + self.next_action.lower())
        result = to_execute()
        return result
        
    def do_online(self):
        print '''do_online'''      
        return self.get_waiting_time()
        
    def do_offline(self):
        print '''do_offline'''       
        return self.get_waiting_time()
        
    def do_start(self):
        print '''do_start'''
        return self.get_waiting_time()
        
    '''Operations that should connect to the Cristian's Benchmarking Framework'''        
    def do_upload(self):
        '''Get the time to wait for this transition in millis''' 
        print '''do_upload'''   
        self.data_generator.create_file_or_directory()
        return self.get_waiting_time()
        
    def do_sync(self):
        print '''do_sync'''
        self.data_generator.update_file()
        return self.get_waiting_time()
        
    def do_delete(self):
        '''Get the time to wait for this transition in millis'''  
        print '''do_delete'''
        self.data_generator.delete_file_or_directory()
        return self.get_waiting_time()
        
    def do_move(self):
        '''Get the time to wait for this transition in millis'''        
        print '''do_move'''
        self.data_generator.move_file_or_directory()
        return self.get_waiting_time()
        
    def do_download(self):
        '''Get the time to wait for this transition in millis'''  
        print '''do_download'''  
        return self.get_waiting_time()
            
    def create_fs_snapshot(self):
        '''Initialize the file system in addition to the models'''
        self.data_generator.create_file_system_snapshot()
        self.data_generator.initialize_file_system_tree(FS_SNAPSHOT_PATH)
        '''Create a set of initial files to populate the file system'''
        for i in range(10):
            self.data_generator.create_file()
            
    def update_current_time(self):
        self.current_time = time.time()
        
if __name__ == '__main__':
    
    executor = TestExecutor()
    executor.initialize_from_stereotype_recipe(STEREOTYPE_RECIPES_PATH + "backup-heavy")
    executor.create_fs_snapshot()
    
    for i in range(10):
        to_sleep = executor.execute()
        print "Sleep for: ", to_sleep
        time.sleep(to_sleep)
    
    
    
    
    