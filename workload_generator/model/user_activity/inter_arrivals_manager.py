'''
Created on 30/6/2015

@author: Raul
'''

from workload_generator.utils import get_random_value_from_fitting

class InterArrivalsManager(object):
    
    def __init__(self):
        self.transition_interarrival_fittings = dict()
            
    '''Get the waiting time between operations based on the statistical fittings'''
    def get_waiting_time(self, state1, state2):
        (function, kv_params) = self.transition_interarrival_fittings[state1][state2]
        return get_random_value_from_fitting(function, kv_params)        
        
    def add_interarrival_transition_fitting(self, state1, state2, function, params):
        #If there is no entry for this transition, create one
        if state1 not in self.transition_interarrival_fittings:
            self.transition_interarrival_fittings[state1] = dict()     
        if state2 not in self.transition_interarrival_fittings[state1]:
            self.transition_interarrival_fittings[state1][state2] = None    
        self.transition_interarrival_fittings[state1][state2] = (function, params)

    '''Get the inter-arrival inforation from stereotype recipe'''
    def initialize_from_recipe(self, stereotype_recipe):
        for l in open(stereotype_recipe, "r"):
            model_attribute = l.split(',')[0]
            if model_attribute == 'chain':
                state1, state2, transitions, fitting = l[:-1].split(',')[1:5]
                kw_params = eval(l[l.index('{'):])
                self.add_interarrival_transition_fitting(state1, state2, fitting, kw_params)
            
if __name__ == '__main__':
    
    '''generalized extreme OK
    birnbaumsaunders OK
    fatiguelife OK
    inversegaussian OK
    
    generalized pareto NOT EXACT
    
    lognormal NO
    logistic NO
    loglogistic/fisk NO '''
    
    #v = numpy.random.gumbel(loc=1.20212649309532, scale=0.932804666751013, size=10000)
    #fitting = stats.genextreme(0.718044067607244, loc=1.20212649309532, scale=0.932804666751013)
    #fitting = stats.genextreme(-0.698811055279666, scale=942.089026948802, loc=1200.79721156363)
    #fitting = stats.lognorm(4.67861713792556, scale=13.8272913665692)
    #fitting = stats.invgauss(5.3146e+06, scale=927.7)
    #fitting = stats.fatiguelife(20.6005318028672, scale=559477.198848146) #(1.4064e+006, scale=34.0631)
    #fitting = stats.cauchy(1488.0640353570552, 596.42456464706072)
    #fitting = stats.fisk(0.4190, shape=0.5201)   
    #mu=9.31524829249769 sigma=41.5219061720147 
    #fitting = stats.lognorm(0.8491, loc=-0.089)
    #fitting = stats.genextreme(-0.4408, scale=624.2910, loc=860.450)
    #print stats.genpareto.fit(rvs)
    #fitting = stats.genpareto(0.1, scale=3000)
    #shape=0.853515926272757 scale=1.39900305679406 threshold=-2.22044604925031e-015 
    #fitting = stats.genpareto()
    
    #test = open("test.dat", "w")
    #for i in range(1000):
    #    print >> test, fitting.rvs()
        #print stats.genpareto(2.9948, scale=2.4671, loc=0.0250).rvs()
        #c=[0.7180, 0.9328, 1.2021]
        #print stats.fisk.rvs(0.5201, 0.4190)
    #test.close()
