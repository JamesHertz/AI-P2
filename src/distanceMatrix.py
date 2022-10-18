#! /usr/bin/env python
from os import access
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


# problem formunation

def initialState(cities):
    aux = cities[:]
    initial = []
    while len(aux) != 0:
        idx = randrange(0, len(aux))
        initial.append(aux[idx])
        del aux[idx]
    return initial



def randomNeighbour(path):
    '''basically it chooses two cities and switches them'''

    def randomIdx():
        return randrange(len(path))


    neighbour = path[:]

    idx1 = randomIdx()#randrange(len(path))
    idx2 = randomIdx()

    while abs(idx1 - idx2) <= 1:
        idx2 = randomIdx() 
    
    neighbour[idx1] = path[idx2]
    neighbour[idx2] = path[idx1]

    return neighbour


def get_inital_temp(m, cities):
    [_, distances] = createReducedMatrix(m, cities)
    d_max =  distances[0][0]
    d_min = distances[0][0]
    for r in distances:
        for d in r:
            d_min = min(d, d_min)
            d_max = max(d, d_max)

    return 2*d_max  - 2*d_min


def searchSolution(cities):

    m = readDistanceMatrix(FILE_NAME)
    #constants to take from user
    max_tot_iter = 1e3
    max_n_iter = len(cities) 
    init_temp = get_inital_temp(m, cities)# calculate the value later
    alpha = random() * (0.99 - 0.8) + 0.8
    max_accepted = max_n_iter * 0.7
    accept_factor = 0.3

    pars = {'max_n_iter':max_n_iter,
            'init_temp': init_temp,
            'alpha': alpha,
            'max_accepted': max_accepted,
            'accept_factor': accept_factor,
    }

    for p in pars:
        print(p, '=', pars[p])

    # other variables
    current = initialState(cities)
    temperature = init_temp
    best = current
    accepted = 0
    tot_iter = 0 

    while temperature:
        n_iter = 0
        for i in range(max_n_iter):
            n_iter += 1
            next = randomNeighbour(current)
            diff = pathCost(m, current) - pathCost(m, next)
            if diff > 0:
                current = next
                accepted += 1

                if accepted > max_accepted:
                    break

            else:
                prob = exp(diff/temperature)
                current = next if prob >= random() else current
                n_iter += 1

            best = next if pathCost(m, best) - pathCost(m, next) > 0 else best

        temperature *= alpha # decreate the temperature
        tot_iter += n_iter

        if accepted / n_iter < accept_factor or tot_iter >= max_tot_iter:
            return best


    return best


m = readDistanceMatrix(FILE_NAME)

path = 'Atroeira, Douro, Pinhal, Teixoso, Ulgueira, Vilar'
sol = searchSolution(path.split(', '))

print(sol, ' cost: ', pathCost(m, sol))


# 1436.0


