'''
Created on 18/11/2015

@author: Raul
'''
from workload_generator.model.user_activity.markov_chain import SimpleMarkovChain
from workload_generator.model.user_activity.inter_arrivals_manager import InterArrivalsManager
from workload_generator.model.data_layer.data_generator import DataGenerator

class StereotypeExecutor(object):

    def __init__(self):
        '''This markov chain describes the state of the client, which can be ONLINE, OFFLINE AND ACTIVE'''
        self.state_chain = SimpleMarkovChain()
        '''This markov chain guides the actions (UPLOAD, UPDATE, MOVE,...) that the client will do when ACTIVE'''
        self.operation_chain = SimpleMarkovChain()
        '''Class to manage the waiting time between actions in ACTIVE state and between OFFLINE, ONLINE and ACTIVE states'''
        self.inter_arrivals_manager = InterArrivalsManager()
        '''Class for managing the data layer of the client'''
        self.data_generator = DataGenerator()
        '''Waiting time until the next action'''
        self.session_duration = 0
        self.inter_operation_time = 0
        self.current_time = 0
        self.next_action = ''

    def initialize_from_stereotype_recipe(self, stereotype_recipe):
        '''Initialize the Markov Chain states'''
        self.state_chain.initialize_from_recipe(stereotype_recipe, 'state_chain')
        self.state_chain.calculate_chain_relative_probabilities()
        '''Initialize the Markov Chain actions'''
        self.operation_chain.initialize_from_recipe(stereotype_recipe, 'operation_chain')
        self.operation_chain.calculate_chain_relative_probabilities()
        '''Initialize the inter-arrival times'''
        self.inter_arrivals_manager.initialize_from_recipe(stereotype_recipe)
        '''Initialize data generation layer'''
        self.data_generator.initialize_from_recipe(stereotype_recipe)

    def get_waiting_time(self):
        '''If we are in Active state, let's do operations'''
        if self.state_chain.previous_state == 'Active':  
            if (self.active_session_start + self.session_duration) < (self.current_time + self.inter_operation_time):
                self.inter_operation_time = (self.active_session_start + self.session_duration) - self.current_time
            return self.inter_operation_time
        else: return self.session_duration
        
            
    '''Get the next operation to be done'''
    def next_operation(self):
        '''Update current time, the time of the process after waiting'''
        self.update_current_time()
        if self.state_chain.previous_state == 'Active' and (self.active_session_start + self.session_duration) > self.current_time:
            self.operation_chain.next_step_in_random_navigation()
            self.next_action = self.operation_chain.previous_state
            self.inter_operation_time = self.inter_arrivals_manager.get_waiting_time(
                self.operation_chain.previous_state, self.operation_chain.current_state)
        else:
            self.state_chain.next_step_in_random_navigation()
            self.next_action = self.state_chain.previous_state
            self.session_duration = self.inter_arrivals_manager.get_waiting_time(
                self.state_chain.previous_state, self.state_chain.current_state) 
            if self.next_action == 'Active':
                self.active_session_start = self.current_time            
            
    def update_current_time(self):
        raise NotImplemented

    '''Do an execution step as a client'''
    def execute(self):
        raise NotImplemented
    
