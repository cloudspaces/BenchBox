'''
Created on 1/7/2015

@author: Raul
'''
import simpy
import time
from workload_generator.constants import SIMULATION_DURATION, \
                STEREOTYPE_DISTRIBUTION, STEREOTYPE_RECIPES_PATH, NODES,\
    SIMULATION_TIME_SLOT
from workload_generator.simulator.statistics import StatisticsManager
from workload_generator import constants
from workload_generator.model.user_activity.stereotype_executor import StereotypeExecutor

#TODO: Updates should be better modeled than they are. In fact, we need
#the distribution of updates per file, and probably the relationship between
#file updates and file size and content.

index = 0

'''Dummy class to emulate the calls of the real one, for simulation purposes'''
class SimulatedStereotypeExecutorU1(StereotypeExecutor):
    
    def __init__(self, env):
        super(SimulatedStereotypeExecutorU1, self).__init__()
        self.environment = env
    
    '''Do an execution step as a client'''
    def execute(self):    
        to_execute = getattr(self, 'do' + self.next_action)
        result = to_execute()
        return result
        
    def doOnline(self):
        #print '''Online wait: ''', self.get_waiting_time()       
        return self.get_waiting_time()
        
    def doOffline(self):
        #print '''Offline wait. Theoretically, diconnect the client: ''', self.get_waiting_time(), "State: ", self.state_chain.previous_state        
        return self.get_waiting_time()
        
    def doActive(self):
        #print '''Active state, so do not wait and start doing storage operations!'''
        return 0.0
        
    '''Operations that should connect to the Cristian's Benchmarking Framework'''        
    def doMakeResponse(self):
        '''Get the time to wait for this transition in millis''' 
        #print "Make: ", self.get_waiting_time(), "State: ", self.state_chain.previous_state      
        return self.get_waiting_time()

    def doPutContentResponse(self):
        '''Get the time to wait for this transition in millis''' 
        #print "Put: ", self.get_waiting_time(), "State: ", self.state_chain.previous_state        
        return self.get_waiting_time()
        
    def doSync(self):
        #print "Sync: ", self.get_waiting_time(), "State: ", self.state_chain.previous_state
        return self.get_waiting_time()
        
    def doUnlink(self):
        '''Get the time to wait for this transition in millis'''  
        #print "Unlink: ", self.get_waiting_time(), "State: ", self.state_chain.previous_state    
        return self.get_waiting_time()
        
    def doMoveResponse(self):
        '''Get the time to wait for this transition in millis'''        
        #print "Move: ", self.get_waiting_time(), "State: ", self.state_chain.previous_state
        return self.get_waiting_time()
        
    def doGetContentResponse(self):
        '''Get the time to wait for this transition in millis'''  
        #print "Get: ", self.get_waiting_time(), "State: ", self.state_chain.previous_state    
        return self.get_waiting_time()
    
    def update_current_time(self):
        self.current_time = self.environment.now

class BenchmarkingProcess():
    
    def __init__(self, process_id, stereotype, stereotype_recipe, statistics_manager, env):
        self.stereotype_executor = SimulatedStereotypeExecutorU1(env)
        self.stereotype_executor.initialize_from_stereotype_recipe(stereotype_recipe)
        self.process_id = process_id
        self.stereotype = stereotype
        '''Logging'''
        self.statistics = statistics_manager                
        
def do_simulation_step(env, node):
    
    while env.now < SIMULATION_DURATION:
        
        global index
        if env.now/SIMULATION_TIME_SLOT > index:
            print "Simulation time: ", env.now/SIMULATION_TIME_SLOT, "hrs"
            index+=1
        #print "Proc: ", node.process_id, " Time: ", env.now, node.stereotype
        previous_node_state = node.stereotype_executor.state_chain.previous_state
        node.stereotype_executor.next_operation()
        wait_time = -1
        try:
            while wait_time < 0.0:
                wait_time = node.stereotype_executor.execute() #* 1000
                                
                is_active = node.stereotype_executor.state_chain.previous_state == 'Active'
                has_operation_to_log = node.stereotype_executor.operation_chain.previous_state!= None
                '''Log operation'''
                if is_active and has_operation_to_log:
                    node.statistics.trace_operations_per_user(node.stereotype, node.process_id,
                        node.stereotype_executor.operation_chain.previous_state, env.now)
                    '''Log interarrival times'''
                    node.statistics.trace_operation_transitions_and_interarrivals(node.stereotype, 
                        node.stereotype_executor.operation_chain.previous_state, 
                            node.stereotype_executor.operation_chain.current_state, wait_time)
                    
                '''Log session length'''  
                if previous_node_state != node.stereotype_executor.state_chain.previous_state:
                    previous_node_state = node.stereotype_executor.state_chain.previous_state
                    node.statistics.trace_session_length(node.stereotype, node.process_id,
                         node.stereotype_executor.state_chain.previous_state, node.stereotype_executor.session_duration)                    
                    '''Nodes per timeslot and state '''           
                    node.statistics.trace_nodes_state_per_timeslot(node.stereotype, node.process_id,
                         node.stereotype_executor.state_chain.previous_state, env.now, node.stereotype_executor.session_duration)

            yield env.timeout(wait_time)
        except (Exception):
            print node.stereotype_executor.operation_chain.previous_state, node.stereotype_executor.operation_chain.current_state
            print "Next action: ", node.stereotype_executor.next_action
            print "WARNING: bad call to generator function! Wait time:", wait_time     
                  
        if wait_time < 0:
            print node.stereotype_executor.operation_chain.previous_state, node.stereotype_executor.operation_chain.current_state
            print "WARNING: Negative inter-arrival time!", wait_time
                  

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
            user = BenchmarkingProcess(i, stereotype, STEREOTYPE_RECIPES_PATH + stereotype_recipe, statistics_manager, env)
            env.process(do_simulation_step(env, user))
            nodes.append(user)            
    env.run(until=SIMULATION_DURATION)
    print "Writing statistics..."
    statistics_manager.finish_statistics()
    print "Finishing simulation...", time.time()-start_time
    
if __name__ == '__main__':
    execute_simulation()
