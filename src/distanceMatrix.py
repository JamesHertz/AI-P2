#! /usr/bin/env python
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
class ArithmeticLowerTemp(CompositeConfig):

    def __init__(self, base_cfg, beta):
        super().__init__(base_cfg)
        self.beta = beta

    def lower_temp(self, temp):
        return 0  # do the arithmetic thing TODO


class GeometricLowerTemp(CompositeConfig):
    def __init__(self, base_cfg, alpha):
        super().__init__(base_cfg)
        self.alpha = alpha

    def lower_temp(self, temp):
        return self.alpha * temp


# var_n_iter
class ConstantNIterVar(CompositeConfig):
    def __init__(self, base_cfg):
        super().__init__(base_cfg)

    def var_n_iter(self, n_iter):
        return super().get_n_iter()


class LinearNIterVar(CompositeConfig):
    def __init__(self, base_cfg, factor):
        super().__init__(base_cfg)
        self.factor = factor

    def var_n_iter(self, n_iter):
        return n_iter * self.factor


# terminal test
class MaxIterTerminalTest(CompositeConfig):

    def __init__(self, base_cfg, max_iter):
        super().__init__(base_cfg)
        self.max_iter = max_iter

    def terminal_test(self, info):
        return info[0] >= self.max_iter


class MinTempTerminalTest(CompositeConfig):

    def __init__(self, base_cfg, min_temp):
        super().__init__(base_cfg)
        self.min_temp = min_temp

    def terminal_test(self, info):
        return info[3] <= self.min_temp


class AcceptFactorTerminalTest(CompositeConfig):

    def __init__(self, base_cfg, accept_factor):
        super().__init__(base_cfg)
        self.accept_factor = accept_factor

    def terminal_test(self, info):
        return info[1]/info[2] < self.accept_factor


# an object with all that is needed to run the search
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
                current = next if prob >= random() else current

            #old = best
            best = next if problem.cost_func(best) > problem.cost_func(next) else best
            #if old != best:
            #    print('switched :)')

        tot_iter += n_iter

        # updates some stuffs :)
        temperature = cfg.lower_temp(temperature)
        n_iter = cfg.var_n_iter(n_iter)

        #print('accepted:', accepted/n_iter)
        #print('temp:', temperature)
        #print(tot_iter)

        if cfg.terminal_test([tot_iter, n_iter, accepted]):
            return best

    return best


def chooseInitializers(cities, problem):
    print()

    nIterInicial = len(cities)

    print("\tnIter por temperatura INICIAL")
    print("1: Constante que eu escolho")
    print("2: Numero de cidades")
    print("Default: Numero de cidades")
    ans = input(">> ")
    if ans == "1":
        const = ""
        while not const.isnumeric():
            const = input("Constante: ")
        nIterInicial = int(const)
    else:
        if ans != "2":
            print(" >> Defalut escolhido: Numero de cidades <<")
    print("nIterInicial: ", nIterInicial)
    print()

    temperaturaInicial = 0
    print("\tTemperatura INICIAL")
    print("1: Constante que eu escolho")
    print("2: Calculado automatico")
    print("Default: Calculado automatico")
    ans = input(">> ")
    if ans == "1":
        const = ""
        while not const.isnumeric():
            const = input("Constante: ")
        temperaturaInicial = int(const)
    elif ans == "2":
        temperaturaInicial = problem.calc_init_temp()
    else:
        print(" >> Defalut escolhido: Calculado automatico <<")
        temperaturaInicial = problem.calc_init_temp()
    print("Temperatura inicial: ", temperaturaInicial)
    print()
    return Configs(nIterInicial, temperaturaInicial)


def chooseTerminalTest(config):
    print("\tCriterio de paragem")
    print("1: Temperatura mínima")
    print("2: Limite de iterações")
    print("3: Percentagem de soluções aceites")
    print("Default: Limite de iteracoes (2000 iteracoes)")
    ans = input(">> ")
    if ans == "1":
        n = ""
        while not n.isnumeric():
            n = input("Temperatura limite: ")
        return MinTempTerminalTest(config, int(n))
    elif ans == "2":
        n = ""
        while not n.isnumeric():
            n = input("Limite de Iteracoes: ")
        return MaxIterTerminalTest(config, int(n))
    elif ans == "3":
        n = ""
        while not n.isnumeric():
            n = input("Aceites / Total < 0.")
        ratio = "0." + n
        print(ratio)
        print(float(ratio))
        return AcceptFactorTerminalTest(config, float(ratio))
    else:
        print(" >> Defalut escolhido: Limite de iteracoes (2000 iteracoes) <<")
        return MaxIterTerminalTest(config, 2000)


if __name__ == '__main__':
    dm = readDistanceMatrix(FILE_NAME)

    # path = 'Belmar, Cerdeira, Douro, Encosta, Freita, Gonta, Horta, Infantado, Lourel, Monte, Nelas, Oura, Pinhal, Quebrada, Roseiral, Serra, Teixoso, Ulgueira'
    # path = 'Atroeira, Douro, Pinhal, Teixoso, Ulgueira, Vilar'
    # cities = path.split(', ')

    cities = dm[0]  # Todas as cidades

    problem = TravSalemanProblem(cities, dm)

    # config = Configs(len(cities), problem.calc_init_temp())  # Inicializar nInterPerTemp e Temp
    config = chooseInitializers(cities, problem)  # Inicializar nInterPerTemp e Temp

    # config = MaxIterTerminalTest(config, 2000)  # Terminal test
    config = chooseTerminalTest(config)  # Terminal test

    config = GeometricLowerTemp(config, 0.84)  # Decaimento da temp

    config = ConstantNIterVar(config)  # Variacao do numero de iteracoes por temperatura

    sol = searchSolution(problem, config)

    print(sol, 'cost:', problem.cost_func(sol))
