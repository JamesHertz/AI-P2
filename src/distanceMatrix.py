#! /usr/bin/env python
from random import randrange, random
from math import exp

FILE_NAME = '../Distancias.txt'

# parameters

# reads a distance matrix (composed of a list of cities and the matrix itself)
# given file name fName
def readDistanceMatrix(fName):
    cities = []
    distances = []
    with open(fName, 'r') as f:
        i=0
        for line in f:
            if i == 0:
                l = [line.rstrip().split()]
                city = l[0][1]
                cities.append(city)
            else:
                row = []
                l = [line.rstrip().split()]
                city = l[0][0]
                cities.append(city)
                j = 1
                while j<= i:
                    row.append(float(l[0][j]))
                    j += 1
                distances.append(row)
            i += 1
    f.close()   
    dm = []
    dm.append(cities)
    dm.append(distances)
    return dm

# from a list of cities cityList return a String with their initials
def getInitials(cityList):
    initials = ""
    for city in cityList:
        initials += city[0]
    return initials

# creates a distance matrix given another, m, and a list clist containing a subset
# of the cities occurring in m
def createReducedMatrix(m,clist):
    cities = clist
    distances = []
    for c in range(1,len(cities)):
        row = []
        for v in range(0,c):
            row.append(distance(m,cities[c],cities[v]))      
        distances.append(row)  
    dm = []
    dm.append(cities)
    dm.append(distances)
    return dm

# creates a distance matrix given another, m, and a String, filter, containing 
# the initals of a subset of the cities occurring in m
def createFilterMatrix(m,filter):
    return createReducedMatrix(m,getCities(m,filter))
    
# returns the distance between two cities c1 and c2, given distance matrix m
def distance (m,c1,c2):
    index1 = m[0].index(c1)
    index2 = m[0].index(c2)
    if index1<index2:
        return int(m[1][index2-1][index1])
    else:
        return int(m[1][index1-1][index2])
        
# presents the given distance matrix m
def showDistances(m):
    cities = '         '
    for i in range(0,len(m[0])-1):
        cities = cities + ' ' + "{:>9}".format(m[0][i])
    print(cities)
    for i in range(0,len(m[1])):
        row = "{:>9}".format(m[0][i+1])
        for j in range(0,len(m[1][i])):
            row = row + ' ' + "{:>9}".format(m[1][i][j])
        print(row)

# from a distance matrix m returns a list of all the cites of m
def getAllCities(m):
    return m[0]

# from a distance matrix m and a String filter returns a subset of cites of m
# with initials in filter 
def getCities(m,filter):	
    cityList = []
    for initial in filter:
        cityList.append(getCity(m[0],initial))
    return cityList
    
# from a list of cities cityList return the one with the first letter initial
def getCity(cityList,initial):	
    for city in cityList:
        if city[0] == initial:
            return city
    return None

# from a list of cities cityList return a String with their initials
def getInitials(cityList):
    initials = ""
    for city in cityList:
        initials += city[0]
    return initials

# -----------------------------------------------------------------
#                   Our solution starts from here
# -----------------------------------------------------------------

# [1, 2, 3] => 1-2, 2-3, 3-1
def pathCost(m, path):
    totcost = distance(m,path[0], path[-1])
    prev = path[0]
    for curr in path[1:]:
        totcost += distance(m, prev, curr)
        prev = curr

    return totcost


# problem formulation
def initialState(cities):
    aux = cities[:]
    initial = []
    while len(aux) != 0:
        idx = randrange(len(aux))
        initial.append(aux[idx])
        del aux[idx]

    return initial


def randomNeighbour(path):
    '''basically it chooses two cities and switches them'''

    def randomIdx():
        return randrange(len(path))

    idx1 = randomIdx()
    idx2 = randomIdx()

    while abs(idx1 - idx2) <= 1: # while the idxs are adjacent
        idx2 = randomIdx() 

    i = min(idx1, idx2)
    j = max(idx1, idx2)

    return path[:i + 1] + path[j: i: -1] + path[j+1:]


def get_inital_temp(m, cities):
    [_, distances] = createReducedMatrix(m, cities)
    d_max =  distances[0][0]
    d_min = distances[0][0]
    for r in distances:
        for d in r:
            d_min = min(d, d_min)
            d_max = max(d, d_max)

    return 2*d_max  - 2*d_min

# an object with all that is needed to run the search
def searchSolution(cfg):

    # constants to take from user
    # alpha =  0.89 
    # init_temp = get_inital_temp(m, cities)# calculate the value later
    # accept_factor = 0.001
    # max_accepted = max_n_iter * 0.7
    # other variables

    #m = readDistanceMatrix(FILE_NAME)


    cost_func = cfg.cost_func 
    neighbour = cfg.neighbour 

    current = cfg.init_sol #initialState(cities)
    temperature = cfg.init_temp 
    n_iter  = cfg.n_iter

    best = current
    tot_iter = 0 

    while temperature:
        num_last_iter = 0
        accepted = 0
        for i in range(n_iter):
            num_last_iter += 1
            next = neighbour(current)
            diff = cost_func(current) - cost_func(next)
            if diff > 0:
                current = next
                accepted += 1
                
                # what about this ???
                # I think just have to drop this thing down :)
                '''
                if accepted > max_accepted:
                    break
                '''
            else:
                prob = exp(diff/temperature)
                current = next if prob >= random() else current
                n_iter += 1

            best = next if cost_func(best) - cost_func(next) > 0 else best

        tot_iter += num_last_iter

        # updates some stuffs :)
        temperature = cfg.lower_temp(temperature) 
        n_iter = cfg.var_n_iter(n_iter)

        if cfg.terminal_test([tot_iter, accepted, num_last_iter]):
            return best

    return best

# IDEA BUT PROBABLY BAD
'''
class Settings:
    def __init__(self, cities):
        pass

    def set_max_terminal(self, max):
        self.terminal_test = lambda info : info[0] >= max

    def set_accept_terminal(self, accept_factor):
        self.terminal_test = lambda info : info[1]/info[2] < accept_factor

    def set_init_temp(self, init_temp):
        self.init_temp = init_temp
    
    def set_linear_var_iter(self, factor):
        self.var_n_iter = lambda old_t : old_t * factor

    def set_const_var_iter(self, const):
        self.var_n_iter = lambda old_t : const 

    def set_geo_lower_temp(self, alpha):
        self.lower_temp = lambda temp : temp * alpha

    def set_arith_lower_temp(self, alpha):
        self.lower_temp = lambda temp : temp * alpha
'''

class Configs:
    pass


if __name__ == '__main__':

    m = readDistanceMatrix(FILE_NAME)

    #path = 'Belmar, Cerdeira, Douro, Encosta, Freita, Gonta, Horta, Infantado, Lourel, Monte, Nelas, Oura, Pinhal, Quebrada, Roseiral, Serra, Teixoso, Ulgueira'
    #path = 'Atroeira, Douro, Pinhal, Teixoso, Ulgueira, Vilar'
    #cities = path.split(', ')

    cities = m[0]

    config = Configs()

    # CHANGE THE FOLLOWING FOR THE USER INPUT :)
    # we gotta change both the strategy and 
    # the parameters for each one of them
    config.init_temp = get_inital_temp(m, cities)
    config.n_iter = len(cities)
    config.init_sol = initialState(cities)
    # set of functions that are needed :)
    config.var_n_iter = lambda _ : config.n_iter
    config.lower_temp  = lambda t : t * 0.84
    config.terminal_test = lambda info : info[0] >= 2e3

    # this are all up to the problem so don't touch :)
    # THINK ABOUT THIS...
    config.cost_func = lambda city : pathCost(m, city) 
    config.neighbour =  lambda city : randomNeighbour(city)

    sol = searchSolution(config)

    print(sol, ' cost: ', pathCost(m, sol))

