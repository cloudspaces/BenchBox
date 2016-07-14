'''
Created on 6/7/2015

@author: Raul
'''
from workload_generator.constants import RANDOM_SEED
try:
    from constants import PROJECT_PATH
    from constants import STEREOTYPE_RECIPES_PATH
except ImportError as ex:
    print ex.message
    from workload_generator.constants import PROJECT_PATH
    from workload_generator.constants import STEREOTYPE_RECIPES_PATH
from scipy import stats
import numpy
import random
import os
import sys

def translate_matlab_fitting_to_scipy(fitting, parameters):
    
    if fitting == "generalized extreme value":
        fitting = "genextreme"
        parameters = parameters.replace("k=", "'shape'=-")
        parameters = parameters.replace("sigma", "'scale'")
        parameters = parameters.replace("mu", "'loc'")

    if fitting == "extreme value":
        fitting = "gumbel_r"
        parameters = parameters.replace("sigma", "'scale'")
        parameters = parameters.replace("mu", "'loc'")

    if fitting == "birnbaumsaunders": 
        fitting = "fatiguelife"
        parameters = parameters.replace("beta", "'scale'")
        parameters = parameters.replace("gamma", "'shape'") # c as shape parameter
        
    if fitting == "generalized pareto": 
        fitting = "genpareto"
        parameters = parameters.replace("k", "'shape'")
        parameters = parameters.replace("sigma", "'scale'")
        parameters = parameters.replace("theta", "'threshold'")
        
    if fitting == "inversegaussian":
        fitting = "invgauss"
        parameters = parameters.replace("mu", "'shape'")
        parameters = parameters.replace("lambda", "'scale'")
        
    if fitting == "lognormal": 
        fitting = "lognorm"
        parameters = parameters.replace("sigma", "'scale'")  # log scale
        parameters = parameters.replace("mu", "'loc'")   # log location
    
    if fitting == "logistic":
        fitting = "logistic"
        parameters = parameters.replace("sigma", "'scale'")
        parameters = parameters.replace("mu", "'loc'")

    if fitting == "tlocationscale":
        fitting = "t"
        parameters = parameters.replace("mu","'loc'")
        parameters = parameters.replace("sigma","'scale'")
        parameters = parameters.replace("nu","'df'")

    if fitting == "normal":
        fitting = "norm"
        parameters = parameters.replace("sigma", "'scale'")
        parameters = parameters.replace("mu", "'loc'")

    if fitting == "exponential":
        fitting = "expon"
        parameters = parameters.replace("mu","'loc'") # mean
        # rvs(loc=0, scale=1, size=1, random_state=None)

    if fitting == "nakagami":
        fitting = "nakagami"
        parameters = parameters.replace("mu","'loc'")
        parameters = parameters.replace("omega","'scale'")

    if fitting == "gamma":
        fitting = "gamma"
        parameters = parameters.replace("a","'loc'")
        parameters = parameters.replace("b","'scale'")

    if fitting == "loglogistic":
        fitting = "fisk"
        parameters = parameters.replace("mu", "'loc'")
        parameters = parameters.replace("sigma", "'scale'")

    if fitting == "weibull": # this one is not sure
        fitting = "exponweib"
        parameters = parameters.replace("A", "'scale'")  # scale
        parameters = parameters.replace("B", "'loc'")  # shape

    if fitting == "rayleigh":
        fitting = "rayleigh"
        parameters = parameters.replace("B", "'scale'")

    if fitting == "rician":  # not exactly the same
        fitting = "rice"
        parameters = parameters.replace("s", "'nu'")  # none centrality ??? # Non-central moment of order n
        parameters = parameters.replace("sigma", "'scale'")

    parameters = parameters[:-1].replace("=", ":")
    parameters = "{" + parameters.replace(" ", ",") + "}"
    
    return fitting, parameters

def get_random_value_from_fitting(function, kv_params):
    fitting = getattr(stats, function)
    if function == "genextreme":
        return fitting(kv_params['shape'], loc=kv_params['loc'], scale=kv_params['scale']).rvs()
    elif function == "gumbel_r":
        return fitting(loc=kv_params['loc'], scale=kv_params['scale']).rvs()
    elif function == "fatiguelife" or function =="invgauss":
        return fitting(kv_params['shape'], scale=kv_params['scale']).rvs()
    elif function == "genpareto":
        # return fitting(kv_params['shape'], scale=kv_params['scale'], threshold=kv_params['threshold']).rvs()
        return fitting(kv_params['shape'], scale=kv_params['scale'], loc=kv_params['threshold']).rvs()
    elif function == "lognorm":
        # http://stackoverflow.com/questions/8747761/scipy-lognormal-distribution-parameters
        scale=numpy.exp(kv_params['loc'])
        return fitting(kv_params['scale'], loc=0, scale=scale).rvs()
    elif function == "randint": 
        return fitting.rvs(kv_params['low'], kv_params['high'])
    elif function == "tlocationscale":
        return fitting.rvs(kv_params['df'], loc=kv_params['loc'], scale=kv_params['scale'])
    elif function == "expon":
        return fitting.rvs(loc=kv_params['loc'])
    elif function == "norm":
        return fitting.rvs(loc=kv_params['loc'], scale=kv_params['scale'])
    elif function == "fisk":  # logistic NO funciona
        # c = 3.08575486223  # calculate  a few first moments???
        scale=numpy.exp(kv_params['loc'])
        return fitting(kv_params['scale'], loc=0, scale=scale).rvs()
    elif function == "logistic": # no funciona
        return fitting().rvs(kv_params['loc'], scale=kv_params['scale'])
    else: 
        return fitting(**kv_params).rvs()


'''Utility method to clean and provide a better format to user stereotype recipes from results
collected in Impala queries and matlab fittings'''
def build_stereotype(stereotype_name, fittings_file, no_offline=False):
    output_recipe = file(STEREOTYPE_RECIPES_PATH + stereotype_name, "w")
    
    for fitting_line in open(fittings_file):      
        transition_descriptor, num_transitions, fitting, parameters = fitting_line[:-1].split(",")
        if no_offline and "OFF" in transition_descriptor:
            continue
        state1, state2 = transition_descriptor.split("_")[-2], transition_descriptor.split("_")[-1].split(".")[0]
        fitting, parameters = translate_matlab_fitting_to_scipy(fitting, parameters)              
        print 'Resulting line: ', state1 + "," + state2 + "," + num_transitions + "," + fitting + "," + parameters            
        print >> output_recipe, "operation_chain," + state1 + "," + state2 + "," + num_transitions + "," + fitting + "," + parameters

    output_recipe.close()
    
def get_random_alphanumeric_string(str_length=10):
    return ''.join(random.choice('0123456789ABCDEF') for i in range(str_length))

def split_list_into_chunks(a, n):
    k, m = len(a) / n, len(a) % n
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in xrange(n)]

def appendParentDir(num, currdir):
    print currdir
    if num is 0:
        print 'return value'
        sys.path.append(currdir)
        return currdir
    else:
        dirname, basename = os.path.split(currdir)
        num-=1
        return appendParentDir(num, dirname)
        
if __name__ == '__main__':
    build_stereotype("sync-occasional", PROJECT_PATH + "workload_generator/simulator/trace_replay_output_1k_sync_occasional/interarrivals_fittings.txt", no_offline=True)

    