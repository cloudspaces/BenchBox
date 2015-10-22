'''
Created on 6/7/2015

@author: Raul
'''
import getpass

'''Raul configuration'''
PROJECT_PATH = '/home/user/workspace/BenchBox/'

'''Chenglong configuration'''
username = getpass.getuser()
PROJECT_PATH = None
TEMP_PATH = {
    'vagrant': '/home/vagrant/',
    'anna': '/home/anna/CloudSpaces/Dev/BenchBox/',
    'user': '/home/user/workspace/BenchBox/'
}

PROJECT_PATH = TEMP_PATH[username]

DEBUG = True

SIMULATION_DURATION = 31*24*3600.
SIMULATION_TIME_SLOT = 3600
NODES = 200
STEREOTYPE_RECIPES_PATH = PROJECT_PATH + 'workload_generator/user_stereotypes/'

STEREOTYPE_DISTRIBUTION = {"backupsample": 1.0}
                           #"xl_markov_min_regular.csv": 0.2,
                           #"xl_markov_min_cdn.csv": 0.2,
                           #"xl_markov_min_sync.csv": 0.2,
                           #"xl_markov_min_idle.csv": 0.2}

SIMULATION_OUTPUT = "./small_simulation_output/"
TRACE_REPLAY_OUTPUT = "./trace_replay_output/"
TRACE_REPLAY_PATH = PROJECT_PATH + 'workload_generator/traces/200_users_backup.csv'
SIMULATOR_TRACE_PATH = PROJECT_PATH + 'workload_generator/traces/200_users_backup.csv'

#EXTERNAL PROGRAMS USED BY BENCHBOX
DATA_GENERATOR_PATH = PROJECT_PATH + "workload_generator/external/sdgen.jar"
DATA_CHARACTERIZATIONS_PATH = PROJECT_PATH + "workload_generator/external/sdgen_characterizations/"
FS_SNAPSHOT_PATH = PROJECT_PATH + "output"
DIRECTORY_DEPTH_PROBABILITY = 0.1
FS_IMAGE_PATH = PROJECT_PATH + "workload_generator/external/impressions"
FS_IMAGE_CONFIG_PATH = PROJECT_PATH + "workload_generator/external/impressions_config"
