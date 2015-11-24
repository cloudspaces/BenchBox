'''
Created on 20/11/2015

@author: Raul
'''

dataset_path = "D:\\Documentos\\Recerca\\Publicaciones\\2015\\benchmarking_stereotypes\\Stereotype_Analysis\\sessions\\definitive\\"
dataset = "xls_sessions_sync_uid.csv"

active_sessions = open(dataset_path + "sync_active.dat", 'w')
online_sessions = open(dataset_path + "sync_online.dat", 'w')
offline_sessions = open(dataset_path + "sync_offline.dat", 'w')

#last_user_sessions = dict()
#day = 3600.*24 #seconds of a day
#initial_time = 1389398400.0 #1389421503.500 #01/11/2014 @ 6:25am (UTC)

for line in open(dataset_path + dataset, "r"):
    [user_id, session_type, timestamp, session_length] = line[:-1].split(",")
    timestamp = float(timestamp)
    session_length = float(session_length)/1000.0
    #print user_id, timestamp, session_length, session_type, (timestamp%day)/3600.
    
    if session_type == "noop": 
        print >> online_sessions, str(user_id) + "," + str(timestamp) + "," + str(session_length) + "," + str(timestamp%24.)
    elif session_type == "active":
        print >> active_sessions, str(user_id) + "," + str(timestamp) + "," + str(session_length) + "," + str(timestamp%24.)
    else:
        print >> offline_sessions, str(user_id) + "," + str(timestamp) + "," + str(session_length) + "," + str(timestamp%24.)
    
    #if user_id in last_user_sessions:
    #    old_timestamp, old_session_length = last_user_sessions[user_id]
    #    offline_session_start = old_timestamp+old_session_length
    #    print >> offline_sessions, str(user_id) + "," + str(offline_session_start) + "," + str(timestamp - offline_session_start) + "," + str(offline_session_start%24.) 
    #last_user_sessions[user_id] = (timestamp, session_length)
    