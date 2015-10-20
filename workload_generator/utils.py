'''
Created on 6/7/2015

@author: Raul
'''
from constants import STEREOTYPE_RECIPES_PATH
from scipy import stats
import random
from workload_generator import constants

def translate_matlab_fitting_to_scipy(fitting, parameters):
    
    if fitting == "generalized extreme value": 
            fitting = "genextreme"
            parameters = parameters.replace("k=", "'shape'=-")
            parameters = parameters.replace("sigma", "'scale'")
            parameters = parameters.replace("mu", "'loc'") 
            
    if fitting == "birnbaumsaunders": 
        fitting = "fatiguelife"
        parameters = parameters.replace("beta", "'scale'")
        parameters = parameters.replace("gamma", "'shape'")
        
    if fitting == "generalized pareto": 
        fitting = "genpareto"
        parameters = parameters.replace("k", "'shape'")
        parameters = parameters.replace("sigma", "'scale'")
        parameters = parameters.replace("theta", "'threshold'")
        
    if fitting == "inversegaussian": 
        fitting = "invgauss"
        parameters = parameters.replace("mu", "'shape'")
        parameters = parameters.replace("lambda", "'scale'")
        
    #TODO: fittings that sooner or later it would be good to implement
    if fitting == "lognormal": raise NotImplementedError
    if fitting == "loglogistic": raise NotImplementedError
    if fitting == "logistic": raise NotImplementedError
    
    parameters = parameters[:-1].replace("=", ":")
    parameters = "{" + parameters.replace(" ", ",") + "}"
    
    return fitting, parameters

def get_random_value_from_fitting(function, kv_params):
    fitting = getattr(stats, function)
    if function == "genextreme":
        return fitting(kv_params['shape'], loc=kv_params['loc'], scale=kv_params['scale']).rvs()
    elif function == "fatiguelife" or function =="invgauss":
        return fitting(kv_params['shape'], scale=kv_params['scale']).rvs()
    elif function == "genpareto": 
        return fitting(kv_params['shape'], scale=kv_params['scale'], threshold=kv_params['threshold']).rvs()
    elif function == "randint": 
        return fitting.rvs(kv_params['low'], kv_params['high'])
    else: 
        return fitting(**kv_params).rvs()

'''Utility method to clean and provide a better format to user stereotype recipes from results
collected in Impala queries and matlab fittings'''
def build_stereotype(stereotype_name, markov_chain_file, interarrival_fittings_file, activity_distribution_file):
    #for markov_chain_file in sorted(glob.glob(markov_chain_directory + "*.csv")):
    #output_markov_chain = file(STEREOTYPE_RECIPES_PATH + markov_chain_file.split("_")[-1].split(".")[0] + ".txt", "w")
    output_markov_chain = file(STEREOTYPE_RECIPES_PATH + stereotype_name, "w")
    interarrivals = open(interarrival_fittings_file, "r")
    first_line = True
    for mc_line in open(markov_chain_file, "r"):                        
        if first_line:
            first_line = False 
            continue
        
        state1, state2, num_transitions, mean_transition_time = mc_line[:-1].split(",")
        interarrival_line = interarrivals.readline()[:-1]
        
        print 'Reading line from markov chain: ', mc_line
        print 'Reading line from inter-arrivals fittings: ', interarrival_line
        
        fitting, parameters = interarrival_line.split(",")        
        fitting, parameters = translate_matlab_fitting_to_scipy(fitting, parameters)       
        
        print 'Resulting scipy generator function: ', fitting, parameters
            
        print >> output_markov_chain, state1 + "," + state2 + "," + num_transitions + "," + fitting + "," + parameters
    
    for ad_line in open(activity_distribution_file, "r"):
        fitting, parameters = ad_line.split(",")        
        fitting, parameters = translate_matlab_fitting_to_scipy(fitting, parameters)
        print >> output_markov_chain, "activity distribution" + "," + fitting + "," + parameters 
        
    output_markov_chain.close()
    
    interarrivals.close()
    
def get_random_alphanumeric_string(str_length=10):
    return ''.join(random.choice('0123456789ABCDEF') for i in range(str_length))
        
if __name__ == '__main__':
    build_stereotype("backupsample", constants.STEREOTYPE_RECIPES_PATH + "backupsample_markov.csv", 
                      constants.STEREOTYPE_RECIPES_PATH + "backupsample_interarrivals.csv",
                      constants.STEREOTYPE_RECIPES_PATH + "backupsample_activity_distribution.csv")
    