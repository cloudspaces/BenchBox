'''
Created on 6/7/2015

@author: Raul
'''
import getpass
import os


PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# hardcode due to no convention with closing slash or not for directory this may fail if the directory is root
if os.name == 'posix':
    PROJECT_PATH+= '/'
else:
    PROJECT_PATH+= '\\'
'''In debug mode the system works without doing changes in the local file system'''
DEBUG = False

SIMULATION_DURATION = 15*24*3600.
SIMULATION_TIME_SLOT = 3600.
NODES = 63492
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

username = getpass.getuser()
FS_SNAPSHOT_PATH = None
SNAPSHOT_PATH = {
    username: PROJECT_PATH + "output",
    'Raul': "C:\\Users\\Raul\\Desktop\\test"
}

FS_SNAPSHOT_PATH = SNAPSHOT_PATH[username]



UPDATES_CONTENT_GENERATION_PATH = PROJECT_PATH + "workload_generator/updates_content/"
DIRECTORY_DEPTH_PROBABILITY = 0.1
FS_IMAGE_PATH = PROJECT_PATH + "workload_generator/external/impressions"
FS_IMAGE_CONFIG_PATH = PROJECT_PATH + "workload_generator/external/impressions_config"


# executor constants

SANDBOX_IP = '192.168.56.101'
BENCHBOX_IP = '192.168.56.2'
CPU_MONITOR_PORT = 11000
TO_WAIT_STATIC_MAX = 6
TO_WAIT_STATIC_MIN = 1


# FTP SENDER CONSTANTS

FTP_SENDER_IP = SANDBOX_IP
FTP_SENDER_PORT = 21
FTP_SENDER_INTERFACE = 'eth1'
FTP_SENDER_USER = 'vagrant'
FTP_SENDER_PASS = 'vagrant'
