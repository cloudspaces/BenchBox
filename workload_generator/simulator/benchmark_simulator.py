'''
Created on 1/7/2015

@author: Raul
'''

import simpy
from workload_generator.executor import SimulatedStereotypeExecutorU1
import time
from workload_generator.constants import SIMULATION_DURATION, \
                STEREOTYPE_DISTRIBUTION, STEREOTYPE_RECIPES_PATH, NODES
from workload_generator.simulator.statistics import StatisticsManager
from workload_generator import constants

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
        #print "Proc: ", node.process_id, " Time: ", env.now, node.stereotype
        node.stereotype_executor.next_operation()
        wait_time = -1
        try:
            while wait_time < 0.0:
                wait_time = node.stereotype_executor.get_waiting_time() #* 1000
            yield env.timeout(wait_time)
        except (Exception):
            print node.stereotype_executor.markov_chain.previous_state, node.stereotype_executor.markov_chain.current_state
            print "WARNING: bad call to generator function!"           
        if wait_time < 0:
            print node.stereotype_executor.markov_chain.previous_state, node.stereotype_executor.markov_chain.current_state
            print "WARNING: Negative inter-arrival time!"
        
        '''Log operation'''
        node.statistics.trace_operations_per_user(node.stereotype, node.process_id,
            node.stereotype_executor.markov_chain.previous_state, env.now)
        '''Log interarrival times'''
        node.statistics.trace_operation_transitions_and_interarrivals(node.stereotype, 
            node.stereotype_executor.markov_chain.previous_state, 
                node.stereotype_executor.markov_chain.current_state, wait_time)
            
def execute_simulation():  
    #Create the nodes
    print "Starting simulation..."
    nodes = list()
    env = simpy.Environment()
    start_time = time.time()
    statistics_manager = StatisticsManager(constants.SIMULATION_OUTPUT)
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
