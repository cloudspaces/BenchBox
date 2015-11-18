'''
Created on 18/11/2015

@author: Raul
'''
from workload_generator.model.user_activity.markov_chain import SimpleMarkovChain
from workload_generator.model.user_activity.inter_arrivals_manager import InterArrivalsManager
from workload_generator.model.data_layer.data_generator import DataGenerator




class StereotypeExecutor(object):

    def __init__(self):
        self.markov_chain = SimpleMarkovChain()
        self.markov_current_state = 'PutContentResponse' # there should be an initial state @ can be random
        self.inter_arrivals_manager = InterArrivalsManager()
        self.data_generator = DataGenerator()

    def initialize_from_stereotype_recipe(self, stereotype_recipe):
        '''Initialize the Markov Chain states'''
        self.markov_chain.initialize_from_recipe(stereotype_recipe)
        self.markov_chain.calculate_chain_relative_probabilities()
        '''Initialize the inter-arrival times'''
        self.inter_arrivals_manager.initialize_from_recipe(stereotype_recipe)
        '''Initialize data generation layer'''
        self.data_generator.initialize_from_recipe(stereotype_recipe)

    def get_waiting_time(self):
        return self.inter_arrivals_manager.get_waiting_time(self.markov_chain.previous_state,
                                                            self.markov_chain.current_state)
    '''Get the next operation to be done'''
    def next_operation(self):
        self.markov_chain.next_step_in_random_navigation()

    '''Do an execution step as a client'''
    def execute(self):
        raise NotImplemented
    
'''Dummy class to emulate the calls of the real one, for simulation purposes'''
class SimulatedStereotypeExecutorU1(StereotypeExecutor):
    
    '''Do an execution step as a client'''
    def execute(self):    
        to_execute = getattr(self, 'do' + self.markov_chain.current_state)
        to_execute()

    '''Operations that should connect to the Cristian's Benchmarking Framework'''        
    def doMakeResponse(self):
        '''Get the time to wait for this transition in millis'''
        
    def doPutContentResponse(self):
        '''Get the time to wait for this transition in millis'''
        
    def doSync(self):
        self.doPutContentResponse()
        
    def doUnlink(self):
        '''Get the time to wait for this transition in millis'''
        
    def doMoveResponse(self):
        '''Get the time to wait for this transition in millis'''
        
    def doGetContentResponse(self):
        '''Get the time to wait for this transition in millis'''