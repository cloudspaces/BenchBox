'''
Created on Sep 21, 2015

@author: user
'''
import time
from benchmark_simulator import StatisticsManager
import calendar

class TraceNode():
    
    def __init__(self):
        self.last_operation = ''
        self.last_operation_time = ''
        self.existing_files = set()

def replay_trace():
    users = dict()
    statistics = StatisticsManager()
    initial_time = -1
    for l in open('D://Documentos//Recerca//Proyectos//IOStack//Code//BenchBox//traces//200_users_backup.csv','r'):
        t,ext,size,tstamp,req_t,node_id, user_id = l.replace('\r','').replace('\n','').split(',')
        
        if node_id == 'node_id' or node_id == '' or t!='storage_done': continue
        
        if initial_time == -1: 
            initial_time = time.strptime(tstamp[0:tstamp.rfind('.')+4], '%Y-%m-%d %H:%M:%S.%f')
            
        if not req_t in {'MoveResponse', 'PutContentResponse', 'GetContentResponse', 'Unlink'}: continue
        
        print l
        if '.' not in tstamp:
            tstamp = tstamp + '.000'
        this_time = time.strptime(tstamp[0:tstamp.rfind('.')+4], '%Y-%m-%d %H:%M:%S.%f')
        t0_epoch = (float(calendar.timegm(this_time) - calendar.timegm(initial_time)) + float(tstamp[tstamp.index('.'):]))
        print t0_epoch
        
        if user_id not in users:
            users[user_id] = TraceNode()
            users[user_id].last_operation = req_t
            users[user_id].last_operation_time = t0_epoch             
        else:            
            if users[user_id].last_operation == 'Unlink' and req_t == 'Unlink':
                print l
            '''Log operation'''
            statistics.trace_operations_per_user('backup', user_id,
                users[user_id].last_operation, users[user_id].last_operation_time)
            '''Log interarrival times'''
            statistics.trace_operation_transitions_and_interarrivals('backup', 
                users[user_id].last_operation, req_t, t0_epoch-users[user_id].last_operation_time)
            
            users[user_id].last_operation = req_t
            users[user_id].last_operation_time = t0_epoch 
            
    statistics.finish_statistics()

replay_trace()