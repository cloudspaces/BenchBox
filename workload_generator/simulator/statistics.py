'''
Created on 19/10/2015

@author: Raul
'''

import os
from workload_generator.constants import SIMULATION_TIME_SLOT,\
    SIMULATION_DURATION

class StatisticsManager(object):
    
    def __init__(self, output_dir):
        self.operations_per_user = dict()
        self.operations_per_timeslot = dict()
        self.inter_arrivals_per_transition = dict()
        self.session_per_stereotype = dict()
        self.users_per_timeslot = dict()
        self.operation_types = set()
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)        
        
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
        
        self.operation_types.add(operation)
        
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
            self.inter_arrivals_per_transition[stereotype][transition] = open(self.output_dir 
                    + stereotype + "_" + transition + ".dat", "w")            
        print >> self.inter_arrivals_per_transition[stereotype][transition], interarrival 
        
    def trace_session_length(self, stereotype, process_id, current_state, session_length):
        if stereotype not in self.session_per_stereotype:
            self.session_per_stereotype[stereotype] = dict()
        
        if current_state not in self.session_per_stereotype[stereotype]:
            self.session_per_stereotype[stereotype][current_state] = open(self.output_dir 
                    + stereotype + "_" + current_state + ".dat", "w")       
            
        print >> self.session_per_stereotype[stereotype][current_state], session_length
        
    def trace_nodes_state_per_timeslot(self, stereotype, process_id, current_state, timestamp, session_len):
        start_timeslot = int(timestamp/SIMULATION_TIME_SLOT)
        end_timeslot = int((timestamp+session_len)/SIMULATION_TIME_SLOT)
        
        while start_timeslot <= end_timeslot: 
            if current_state not in self.users_per_timeslot:
                self.users_per_timeslot[current_state] = dict()              
            if start_timeslot not in self.users_per_timeslot[current_state]:
                self.users_per_timeslot[current_state][start_timeslot] = set()             
            
            self.users_per_timeslot[current_state][start_timeslot].add(process_id)
            start_timeslot+=1
        
    def finish_statistics(self):
        for stereotype in self.inter_arrivals_per_transition.keys():
            for transition in self.inter_arrivals_per_transition[stereotype].keys():
                self.inter_arrivals_per_transition[stereotype][transition].close()
        
        for stereotype in self.session_per_stereotype.keys():
            for state in self.session_per_stereotype[stereotype].keys():
                self.session_per_stereotype[stereotype][state].close()
        
        for stereotype in sorted(self.operations_per_timeslot.keys()):
            stereotype_file = open(self.output_dir + stereotype + "_ops_per_timeslot.dat", "w")            
            simulation_timeslot_len = int(SIMULATION_DURATION/SIMULATION_TIME_SLOT)
            for i in range(simulation_timeslot_len):  
                to_print = dict()
                if i in self.operations_per_timeslot[stereotype]:      
                    for operation in sorted(self.operations_per_timeslot[stereotype][i].keys()):
                        to_print[operation] = self.operations_per_timeslot[stereotype][i][operation]
                str_output = ''
                total_per_timeslot = 0
                for operation in sorted(self.operation_types):
                    if operation not in to_print:
                        to_print[operation] = 0
                    total_per_timeslot += to_print[operation]
                    str_output += str(to_print[operation]) + "\t"
                print >> stereotype_file, str_output + "\t" + str(total_per_timeslot)
            stereotype_file.close()
            
        for state in sorted(self.users_per_timeslot.keys()):
            state_file = open(self.output_dir + state + "_users_per_timeslot.dat", "w")
            for current_timeslot in sorted(self.users_per_timeslot[state].keys()):
                print >> state_file, len(self.users_per_timeslot[state][current_timeslot])
            state_file.close()
            
        for stereotype in sorted(self.operations_per_user.keys()):
            stereotype_file = open(self.output_dir + stereotype + "_ops_per_user.dat", "w")
            for user in self.operations_per_user[stereotype].keys():
                print >> stereotype_file, self.operations_per_user[stereotype][user]
            stereotype_file.close()