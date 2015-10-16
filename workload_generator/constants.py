'''
Created on 6/7/2015

@author: Raul
'''

SIMULATION_DURATION = 31*24*3600.
SIMULATION_TIME_SLOT = 3600
NODES = 200

STEREOTYPE_RECIPES_PATH = "D://Documentos//Recerca//Proyectos//IOStack//Code//BenchBox//stereotypes//" #Publicaciones/2015/user_stereotypes/Stereotype_Analysis/"

STEREOTYPE_DISTRIBUTION = {"backupsample": 1.0}
                           #"xl_markov_min_regular.csv": 0.2,
                           #"xl_markov_min_cdn.csv": 0.2,
                           #"xl_markov_min_sync.csv": 0.2,
                           #"xl_markov_min_idle.csv": 0.2}

SIMULATION_OUTPUT = "./small_simulation_output/"


#EXTERNAL PROGRAMS USED BY BENCHBOX
DATA_GENERATOR_PATH = "/home/user/workspace/BenchBox/external/sdgen.jar"
DATA_CHARACTERIZATIONS_PATH = "/home/user/workspace/BenchBox/external/sdgen_characterizations/"
DIRECTORY_DEPTH_PROBABILITY = 0.1
FS_IMAGE_PATH = "/home/user/workspace/BenchBox/external/impressions"
FS_IMAGE_CONFIG_PATH = "/home/user/workspace/BenchBox/external/impressions_config"

MY_CONSTANT = 50
STEREOTYPE_RECIPES_PATH = './data'