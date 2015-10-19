'''
Created on 19/10/2015

@author: Raul
'''
import os
from workload_generator.constants import SIMULATION_OUTPUT, SIMULATION_TIME_SLOT

class StatisticsManager(object):
    
    def __init__(self):
        self.operations_per_user = dict()
        self.operations_per_timeslot = dict()
        self.inter_arrivals_per_transition = dict()
        if not os.path.exists(SIMULATION_OUTPUT):
            os.makedirs(SIMULATION_OUTPUT)        
        
    def trace_operations_per_user(self, stereotype, user, operation, timestamp):
        current_timeslot = int(timestamp/SIMULATION_TIME_SLOT)
        
        '''Time-series operations per stereotype'''
        if stereotype not in self.operations_per_timeslot:
            self.operations_per_timeslot[stereotype] = dict()              
        if current_timeslot not in self.operations_per_timeslot[stereotype]:
            self.operations_per_timeslot[stereotype][current_timeslot] = dict()             
        if operation not in self.operations_per_timeslot[stereotype][current_timeslot]:
            self.operations_per_timeslot[stereotype][current_timeslot][operation] = 0      
            
        self.operations_per_timeslot[stereotype][current_timeslot][operation] += 1
        
        '''User-based operations'''
        if stereotype not in self.operations_per_user:
            self.operations_per_user[stereotype] = dict()   
            
        if user not in self.operations_per_user[stereotype]:
            self.operations_per_user[stereotype][user] = 0
        self.operations_per_user[stereotype][user] += 1
        
    def trace_operation_transitions_and_interarrivals(self, stereotype, previous_state, current_state, interarrival):
        if stereotype not in self.inter_arrivals_per_transition:
            self.inter_arrivals_per_transition[stereotype] = dict()            
        transition = previous_state + "_" + current_state        
        if transition not in self.inter_arrivals_per_transition[stereotype]:
            self.inter_arrivals_per_transition[stereotype][transition] = open(SIMULATION_OUTPUT + stereotype + "_" + transition + ".dat", "w")            
        print >> self.inter_arrivals_per_transition[stereotype][transition], interarrival 
        
    def finish_statistics(self):
        for stereotype in self.inter_arrivals_per_transition.keys():
            for transition in self.inter_arrivals_per_transition[stereotype].keys():
                self.inter_arrivals_per_transition[stereotype][transition].close()
        
        for stereotype in sorted(self.operations_per_timeslot.keys()):
            stereotype_file = open(SIMULATION_OUTPUT + stereotype + "_ops_per_timeslot.dat", "w")
            for current_timeslot in sorted(self.operations_per_timeslot[stereotype].keys()):
                to_print = ""
                for operation in sorted(self.operations_per_timeslot[stereotype][current_timeslot].keys()):
                    to_print += str(self.operations_per_timeslot[stereotype][current_timeslot][operation]) + "\t"
                print >> stereotype_file, to_print
            stereotype_file.close()
            
        for stereotype in sorted(self.operations_per_user.keys()):
            stereotype_file = open(SIMULATION_OUTPUT + stereotype + "_ops_per_user.dat", "w")
            for user in self.operations_per_user[stereotype].keys():
                print >> stereotype_file, self.operations_per_user[stereotype][user]
            stereotype_file.close()
            
