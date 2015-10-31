'''
Created on 6/7/2015

@author: Raul
'''
import getpass

'''Raul configuration'''
PROJECT_PATH = 'D:\\Documentos\\Recerca\\Proyectos\\IOStack\\Code\\BenchBox\\' #'/home/user/workspace/BenchBox/'

'''Chenglong configuration'''
username = getpass.getuser()
PROJECT_PATH = None
TEMP_PATH = {
    'vagrant': '/home/vagrant/',
    'anna': '/home/anna/CloudSpaces/Dev/BenchBox/',
    'user': '/home/user/workspace/BenchBox/',
    'Raul': 'D:\\Documentos\\Recerca\\Proyectos\\IOStack\\Code\\BenchBox\\'
}

PROJECT_PATH = TEMP_PATH[username]

'''In debug mode the system works without doing changes in the local file system'''
DEBUG = False

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
DATA_GENERATOR_PROPERTIES_DIR = PROJECT_PATH + "workload_generator/model/data_layer" #/application.properties
DATA_CHARACTERIZATIONS_PATH = PROJECT_PATH + "workload_generator/external/sdgen_characterizations/"

FS_SNAPSHOT_PATH = None
SNAPSHOT_PATH = {
    'vagrant': PROJECT_PATH + "output",
    'anna': PROJECT_PATH + "output",
    'user': PROJECT_PATH + "output",
    'Raul': "C:\\Users\\Raul\\Desktop\\test"
}

FS_SNAPSHOT_PATH = SNAPSHOT_PATH[username]



UPDATES_CONTENT_GENERATION_PATH = PROJECT_PATH + "workload_generator/updates_content/"
DIRECTORY_DEPTH_PROBABILITY = 0.1
FS_IMAGE_PATH = PROJECT_PATH + "workload_generator/external/impressions"
FS_IMAGE_CONFIG_PATH = PROJECT_PATH + "workload_generator/external/impressions_config"
