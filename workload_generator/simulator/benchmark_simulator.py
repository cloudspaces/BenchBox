'''
Created on 1/7/2015

@author: Raul
'''

import simpy
from workload_generator.executor import SimulatedStereotypeExecutorU1
import os
import time
from workload_generator.constants import SIMULATION_DURATION, SIMULATION_OUTPUT,\
    SIMULATION_TIME_SLOT, STEREOTYPE_DISTRIBUTION, STEREOTYPE_RECIPES_PATH, NODES

#TODO: Our model does not capture the rate of activity of clients!
#That is, both inactive and active nodes will execute a similar
#number of operations in our markov chain. This should be controlled.

#TODO: We can also model correlations using a 24h activity or session lengths.

#TODO: Updates should be better modeled than they are. In fact, we need
#the distribution of updates per file, and probably the relationship between
#file updates and file size and content.

class BenchmarkingProcess():
    
    def __init__(self, process_id, stereotype, stereotype_recipe, statistics_manager):
        self.stereotype_executor = SimulatedStereotypeExecutorU1()
        self.stereotype_executor.initialize_from_stereotype_recipe(stereotype_recipe)
        self.process_id = process_id
        self.stereotype = stereotype
        '''Logging'''
        self.statistics = statistics_manager
                
        
def do_simulation_step(env, node):
    
    while env.now < SIMULATION_DURATION:
        print "Proc: ", node.process_id, " Time: ", env.now, node.stereotype
        node.stereotype_executor.next_operation()
        wait_time = -1
        try:
            while wait_time < 0.0:
                wait_time = node.stereotype_executor.get_waiting_time() * 1000.0
            yield env.timeout(wait_time)
        except (Exception):
            print node.stereotype_executor.markov_chain.previous_state, node.stereotype_executor.markov_chain.current_state
            print "bad call to generator function"            
        if wait_time < 0:
            print node.stereotype_executor.markov_chain.previous_state, node.stereotype_executor.markov_chain.current_state
            print "tiempo de espera negativo!"
        
        '''Log operation'''
        node.statistics.add_operation_to_log(node.stereotype, 
            node.stereotype_executor.markov_chain.previous_state, env.now)
        '''Log interarrival times'''
        node.statistics.add_interarrival_to_log(node.stereotype, 
            node.stereotype_executor.markov_chain.previous_state, 
                node.stereotype_executor.markov_chain.current_state, wait_time)
        
class StatisticsManager(object):
    
    def __init__(self):
        self.operations_per_timeslot = dict()
        self.inter_arrivals_per_transition = dict()
        self.all_operations = set()
        if not os.path.exists(SIMULATION_OUTPUT):
            os.makedirs(SIMULATION_OUTPUT)        
        
    def add_operation_to_log(self, stereotype, operation, timestamp):
        current_timeslot = int(timestamp/SIMULATION_TIME_SLOT)
        
        self.all_operations.add(operation)
        '''Time-series operations per stereotype'''
        if stereotype not in self.operations_per_timeslot:
            self.operations_per_timeslot[stereotype] = dict()  
        if current_timeslot not in self.operations_per_timeslot[stereotype]:
            self.operations_per_timeslot[stereotype][current_timeslot] = dict() 
        if operation not in self.operations_per_timeslot[stereotype][current_timeslot]:
            self.operations_per_timeslot[stereotype][current_timeslot][operation] = 0      
            
        self.operations_per_timeslot[stereotype][current_timeslot][operation] += 1
        
    def add_interarrival_to_log(self, stereotype, previous_state, current_state, interarrival):
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
                total = 0
                for operation in sorted(self.operations_per_timeslot[stereotype][current_timeslot].keys()):
                    if operation in self.all_operations:
                        to_print += str(self.operations_per_timeslot[stereotype][current_timeslot][operation]) + "\t"
                        total += self.operations_per_timeslot[stereotype][current_timeslot][operation]
                    else:to_print += "0\t"
                print >> stereotype_file, to_print + str(total)
            stereotype_file.close()
            
def execute_simulation():  
    #Create the nodes
    print "Starting simulation..."
    nodes = list()
    env = simpy.Environment()
    start_time = time.time()
    statistics_manager = StatisticsManager()
    for stereotype_recipe in STEREOTYPE_DISTRIBUTION:
        for i in range(int(STEREOTYPE_DISTRIBUTION[stereotype_recipe] * NODES)):
            stereotype = stereotype_recipe
            user = BenchmarkingProcess(i, stereotype, STEREOTYPE_RECIPES_PATH + stereotype_recipe, statistics_manager)
            env.process(do_simulation_step(env, user))
            nodes.append(user)            
    env.run(until=SIMULATION_DURATION)
    print "Writing statistics..."
    statistics_manager.finish_statistics()
    print "Finishing simulation...", time.time()-start_time
    
if __name__ == '__main__':
    execute_simulation()
