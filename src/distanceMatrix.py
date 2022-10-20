from abc import ABCMeta, abstractmethod
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
        i = 0
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
                while j <= i:
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
def createReducedMatrix(m, clist):
    cities = clist
    distances = []
    for c in range(1, len(cities)):
        row = []
        for v in range(0, c):
            row.append(distance(m, cities[c], cities[v]))
        distances.append(row)
    dm = []
    dm.append(cities)
    dm.append(distances)
    return dm


# creates a distance matrix given another, m, and a String, filter, containing
# the initals of a subset of the cities occurring in m
def createFilterMatrix(m, filter):
    return createReducedMatrix(m, getCities(m, filter))


# returns the distance between two cities c1 and c2, given distance matrix m
def distance(m, c1, c2):
    index1 = m[0].index(c1)
    index2 = m[0].index(c2)
    if index1 < index2:
        return int(m[1][index2 - 1][index1])
    else:
        return int(m[1][index1 - 1][index2])


# presents the given distance matrix m
def showDistances(m):
    cities = '         '
    for i in range(0, len(m[0]) - 1):
        cities = cities + ' ' + "{:>9}".format(m[0][i])
    print(cities)
    for i in range(0, len(m[1])):
        row = "{:>9}".format(m[0][i + 1])
        for j in range(0, len(m[1][i])):
            row = row + ' ' + "{:>9}".format(m[1][i][j])
        print(row)


# from a distance matrix m returns a list of all the cites of m
def getAllCities(m):
    return m[0]


# from a distance matrix m and a String filter returns a subset of cites of m
# with initials in filter
def getCities(m, filter):
    cityList = []
    for initial in filter:
        cityList.append(getCity(m[0], initial))
    return cityList


# from a list of cities cityList return the one with the first letter initial
def getCity(cityList, initial):
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

# (metaclass=ABCMeta)
class Problem:

    @abstractmethod
    def init_sol(self):
        pass

    # think about this
    @abstractmethod
    def calc_init_temp(self):
        pass

    @abstractmethod
    def cost_func(self, node):
        pass

    @abstractmethod
    def neighbour(self, node):
        pass


class TravSalemanProblem(Problem):

    def __init__(self, cities, dm):
        self.dm = createReducedMatrix(dm, cities)
        self.cities = cities  # think about this

    def cost_func(self, node):
        totcost = distance(self.dm, node[0], node[-1])

        prev = node[0]
        for curr in node[1:]:
            totcost += distance(self.dm, prev, curr)
            prev = curr

        return totcost

    def neighbour(self, node):

        def randomIdx():
            return randrange(len(node))

        idx1 = randomIdx()
        idx2 = randomIdx()

        while abs(idx1 - idx2) <= 1:  # while the idxs are adjacent
            idx2 = randomIdx()

        i = min(idx1, idx2)
        j = max(idx1, idx2)

        return node[:i + 1] + node[j: i: -1] + node[j + 1:]

    # think about this :)
    def init_sol(self):
        aux = self.cities[:]
        initial = []
        while len(aux) != 0:
            idx = randrange(len(aux))
            initial.append(aux[idx])
            del aux[idx]

        return initial

    def calc_init_temp(self):
        distances = self.dm[1]
        d_max = distances[0][0]
        d_min = distances[0][0]
        for r in distances:
            for d in r:
                d_min = min(d, d_min)
                d_max = max(d, d_max)

        return 2 * d_max - 2 * d_min


# we used decorator a pattern that we have studied at SE's leactures
class Configs:
    def __init__(self, n_iter, init_temp):
        self.n_iter = n_iter
        self.init_temp = init_temp

    def get_init_temp(self):
        return self.init_temp

    def get_n_iter(self):
        return self.n_iter

    def lower_temp(self, temp):
        pass

    def var_n_iter(self, n_iter):
        pass

    def terminal_test(self, info):
        pass


class CompositeConfig:
    def __init__(self, base_cfg: Configs):
        self.base = base_cfg

    def get_init_temp(self):
        return self.base.get_init_temp()

    def get_n_iter(self):
        return self.base.get_n_iter()

    def lower_temp(self, temp):
        return self.base.lower_temp(temp)

    def var_n_iter(self, n_iter):
        return self.base.var_n_iter(n_iter)

    def terminal_test(self, info):
        return self.base.terminal_test(info)


# lower_temp

class LowerTemp(CompositeConfig):
    def __init__(self, base_cfg):
        super().__init__(base_cfg)


class ArithmeticLowerTemp(LowerTemp):

    def __init__(self, base_cfg, n):
        super().__init__(base_cfg)
        self.n = n

    def lower_temp(self, temp):
        return temp - self.n


class GradualLowerTemp(LowerTemp):

    def __init__(self, base_cfg, beta):
        super().__init__(base_cfg)
        self.beta = beta

    def lower_temp(self, temp):
        return temp / (1 + self.beta * temp)


class GeometricLowerTemp(LowerTemp):
    def __init__(self, base_cfg, alpha):
        super().__init__(base_cfg)
        self.alpha = alpha

    def lower_temp(self, temp):
        return self.alpha * temp


# var_n_iter

class NIterVar(CompositeConfig):
    def __init__(self, base_cfg):
        super().__init__(base_cfg)

class ConstantNIterVar(NIterVar):
    def __init__(self, base_cfg):
        super().__init__(base_cfg)

    def var_n_iter(self, n_iter):
        return super().get_n_iter()


class LinearNIterVar(NIterVar):
    def __init__(self, base_cfg, factor):
        super().__init__(base_cfg)
        self.factor = factor

    def var_n_iter(self, n_iter):
        return int(n_iter * self.factor)


# terminal test
class TerminalTest(CompositeConfig):
    def __init__(self, base_cfg):
        super().__init__(base_cfg)

class MaxIterTerminalTest(TerminalTest):

    def __init__(self, base_cfg, max_iter):
        super().__init__(base_cfg)
        self.max_iter = max_iter

    def terminal_test(self, info):
        return info[0] >= self.max_iter


class MinTempTerminalTest(TerminalTest):

    def __init__(self, base_cfg, min_temp):
        super().__init__(base_cfg)
        self.min_temp = min_temp

    def terminal_test(self, info):
        return info[3] <= self.min_temp


class AcceptFactorTerminalTest(TerminalTest):

    def __init__(self, base_cfg, accept_factor):
        super().__init__(base_cfg)
        self.accept_factor = accept_factor

    def terminal_test(self, info):
        return info[2] / info[1] < self.accept_factor

# searches for solution
def searchSolution(problem: Problem, cfg: Configs):
    current = problem.init_sol()
    temperature = cfg.get_init_temp()
    n_iter = cfg.get_n_iter()

    best = current
    tot_iter = 0

    while temperature:
        accepted = 0

        for i in range(n_iter):
            next = problem.neighbour(current)
            diff = problem.cost_func(current) - problem.cost_func(next)

            if diff > 0:
                current = next
                accepted += 1
            else:
                prob = exp(diff / temperature)
                if prob >= random():
                    current = next
                    accepted += 1

            best = next if problem.cost_func(best) > problem.cost_func(next) else best

        tot_iter += n_iter

        # updates some stuffs :)
        temperature = cfg.lower_temp(temperature)
        n_iter = cfg.var_n_iter(n_iter)

        if cfg.terminal_test([tot_iter, n_iter, accepted, temperature]):
            return best

    return best