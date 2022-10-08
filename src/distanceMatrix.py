from random import randrange, random
from math import exp 

FILE_NAME = '../'

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
                    row.append(l[0][j])
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
#                   My solution starts from here
# -----------------------------------------------------------------

def pathCost(m, path):
    totcost = 0
    prev = path[0]
    for curr in path:
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

    neighbour = path[::]

    idx1 = path[randrange(len(path))]
    idx2 = path[randrange(len(path))]

    while abs(idx1 - idx2) <= 1:
        idx2 = path[randrange(len(path))]
    
    neighbour[idx1] = path[idx2]
    neighbour[idx2] = path[idx1]

    return neighbour


def searchSolution(cities):
    m = readDistanceMatrix(FILE_NAME)
    current = initialState(cities)
    best = current
    temperature = 999 # calculate the value later
    while True:
        next = randomNeighbour(current)
        diff = pathCost(m, current) - pathCost(m, next)
        if diff > 0:
            current = next
        else:
            prob = exp(diff/temperature)/exp(1)
            if (1 - prob) < random():
                current = next
        
        best = next if pathCost(m, best) - pathCost(m, next) > 0 else best
        # decreate the temperature

    return best

searchSolution([0, 1, 3]) # a solution :)