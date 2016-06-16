'''
Created on Sep 21, 2015

@author: user
'''
import time
from benchmark_simulator import StatisticsManager
import calendar
from workload_generator import constants

STEREOTYPE_USED = 'backup_heavy'

class TraceNode():
    
    def __init__(self):
        self.last_operation = ''
        self.last_operation_time = ''
        self.existing_files = set()

def replay_trace():
    users = dict()
    statistics = StatisticsManager(constants.TRACE_REPLAY_OUTPUT)
    initial_time = -1
    users_set = set()
    last_timestamp = 0
    
    processed = 0
    mb = 0
    
    for l in open(constants.TRACE_REPLAY_PATH,'r'):
        processed+=len(l)
        sid,ext,size,tstamp,req_t,node_id, user_id = l.replace('\r','').replace('\n','').split(',')
        
        users_set.add(user_id)
        
        if node_id == 'node_id' or node_id == '': continue
        
        if initial_time == -1: 
            initial_time = time.strptime(tstamp[0:tstamp.rfind('.')+4], '%Y-%m-%d %H:%M:%S.%f')
            
        if not req_t in {'MoveResponse', 'PutContentResponse', 'GetContentResponse', 'Unlink'}: continue
        
        #print l
        if '.' not in tstamp:
            tstamp = tstamp + '.000'
        this_time = time.strptime(tstamp[0:tstamp.rfind('.')+4], '%Y-%m-%d %H:%M:%S.%f')
        t0_epoch = (float(calendar.timegm(this_time) - calendar.timegm(initial_time)) + float(tstamp[tstamp.index('.'):]))
        
        if last_timestamp != 0:
            if t0_epoch < last_timestamp:
                print l
                print str(last_timestamp) + " " + str(t0_epoch)
            
        last_timestamp = t0_epoch
        
        if user_id not in users:
            users[user_id] = TraceNode()
            users[user_id].last_operation = req_t
            users[user_id].last_operation_time = t0_epoch             
        else:            
            '''Log operation'''
            statistics.trace_operations_per_user(STEREOTYPE_USED, user_id,
                users[user_id].last_operation, t0_epoch) #users[user_id].last_operation_time)
            '''Log interarrival times'''
            statistics.trace_operation_transitions_and_interarrivals(STEREOTYPE_USED, 
                users[user_id].last_operation, req_t, t0_epoch-users[user_id].last_operation_time)
            
            users[user_id].last_operation = req_t
            users[user_id].last_operation_time = t0_epoch 
            
        if int(processed/(1024*1024)) != mb:
            print "Processed MBytes: ", mb
            mb = int(processed/(1024.*1024.))
            
    statistics.finish_statistics()
    print len(users_set)

replay_trace()