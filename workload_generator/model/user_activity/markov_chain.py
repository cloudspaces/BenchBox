'''
Created on 19/6/2015

@author: Raul

This class implements a graph of a certain number of nodes
with bidirectional transitions among them. Moreover, after
the probabilities among states are set, it also provides
random walk on that graph.
'''
import random

class SimpleMarkovChain(object):
    
    def __init__(self):
        self.chain = dict()
        self.result_chain = dict()
        self.previous_state = None
        self.current_state = None
        self.activity_rate = None
        
    def add_transition(self, state1, state2, probability):
        #If there is no entry for this transition, create one
        if state1 not in self.chain:
            self.chain[state1] = dict()     
        self.chain[state1][state2] = probability
        
    def add_result(self, state1, state2):
        #If there is no entry for this transition, create one
        if state1 not in self.result_chain:
            self.result_chain[state1] = dict()     
        if state2 not in self.result_chain[state1]:
            self.result_chain[state1][state2] = 0
            
        self.result_chain[state1][state2] += 1
        
    def calculate_chain_relative_probabilities(self):
        self.calculate_relative_probabilities(self.chain)
        
    def calculate_results_relative_probabilities(self):
        self.calculate_relative_probabilities(self.result_chain)
        
    def calculate_relative_probabilities(self, chain):
        for k1 in chain.keys():
            all_transitions = float(sum(chain[k1].values()))
            
            for k2 in chain[k1].keys():
                chain[k1][k2] = chain[k1][k2]/all_transitions
            if float(sum(chain[k1].values())) > 1.001 or float(sum(chain[k1].values())) < 0.999:
                print "WARNING: Sum of transitions does not sum 1! ", float(sum(chain[k1].values()))

    def next_step_in_random_navigation(self):
        #Initialize the navigation cursor to a random state
        if self.current_state == None:
            #TODO:Select this from an initial probability distribution
            self.current_state = "START"
            
        #Fitness proportionate selection of next state
        random_trial = random.random()
        start_range = 0.0
        self.previous_state = self.current_state
        for k in sorted(self.chain[self.current_state].keys()):
            if start_range <= random_trial and random_trial <= start_range+self.chain[self.current_state][k]:
                self.add_result(self.current_state, k)
                self.current_state = k
                break
            else: start_range += self.chain[self.current_state][k]      
            
    def initialize_from_recipe(self, file_name, discriminator):
        for l in open(file_name, "r"):
            model_attribute = l.split(',')[0]
            if model_attribute == discriminator:
                state1, state2, num_transitions  = l.split(",")[1:4]
                self.add_transition(state1, state2, float(num_transitions))

    def print_states(self):  
        self.printChain(self.chain)
        
    def print_results(self):  
        self.printChain(self.result_chain)
        
    def print_chain(self, chain):    
        for k1 in sorted(chain.keys()):
            for k2 in sorted(chain[k1].keys()):
                print chain[k1][k2]
