#! /usr/bin/env python

from distanceMatrix import *
from sys import argv, exit
from json import JSONDecodeError, loads

def chooseInitializers(cities, problem):
    print()

    nIterInicial = len(cities)
    print('> Numero de Iteracoes por temperatura INICIAL <')
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
    print("*=" * 20)

    print("\t> Temperatura INICIAL <")
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
    return Configs(nIterInicial, temperaturaInicial), nIterInicial, temperaturaInicial


def chooseTerminalTest(config):
    print("\t> Criterio de paragem <")
    print("1: Temperatura mínima")
    print("2: Limite de iterações")
    print("3: Percentagem de soluções aceites")
    print("Default: Limite de iteracoes (2000 iteracoes)")
    ans = input(">> ")
    if ans == "1":
        n = -1.0
        done = False
        while not done:
            try:
                value = input("Temperatura Limite: ")
                n = float(value)
                done = True
            except ValueError:
                pass

        return MinTempTerminalTest(config, n), "Temperatura Minima Limite: " + str(n)
    elif ans == "2":
        n = ""
        while not n.isnumeric():
            n = input("Limite de Iteracoes: ")
        return MaxIterTerminalTest(config, int(n)), "Numero Maximo de Iteracoes: " + n
    elif ans == "3":
        n = ""
        while not n.isnumeric():
            n = input("Aceites / Total < 0.")
        ratio = "0." + n
        return AcceptFactorTerminalTest(config, float(ratio)), "Fator de aceitacao: " + ratio
    else:
        print(" >> Defalut escolhido: Limite de iteracoes (2000 iteracoes) <<")
        return MaxIterTerminalTest(config, 2000), "Numero Maximo de Iteracoes: 2000"


def chooseDecaimentoTemp(config):
    print("\t> Decaimento da Temperatura <")
    print("1: Geometrica")
    print("2: Aritmetica")
    print("3: Gradual")
    print("Default: Geometrica (alpha = 0.84)")
    ans = input(">> ")
    if ans == "1":
        n = ""
        while not n.isnumeric():
            n = input("alpha: 0.")
        alpha = "0." + n
        return GeometricLowerTemp(config, float(alpha)), "Geometrica, alpha: "+alpha
    elif ans == "2":
        n = ""
        while not n.isnumeric():
            n = input("Decremento por iteracao: ")
        return ArithmeticLowerTemp(config, int(n)), "Aritmetica, n: "+n
    elif ans == "3":
        n = ""
        while not n.isnumeric():
            n = input("beta: 0.")
        beta = "0." + n
        return GradualLowerTemp(config, float(beta)), "Gradual, beta: "+beta
    else:
        print(" >> Defalut escolhido: Geometrica (alpha = 0.84) <<")
        return GeometricLowerTemp(config, 0.84), "Geometrica, alpha: 0.84"


def chooseNIterPerTemp(config):
    print("\t> Variacao de nIter por cada Temp <")
    print("1: Constante (sempre igual ao valor inicial)")
    print("2: Linear")
    print("Default: Constante")
    ans = input(">> ")
    if ans == "1":
        return ConstantNIterVar(config), "Constante igual ao inicial"
    elif ans == "2":
        n = ""
        while not n.isnumeric():
            n = input("fator: 1.")
        fator = "1." + n
        return LinearNIterVar(config, float(fator)), "Linear, fator: "+fator
    else:
        print(" >> Defalut escolhido: Constante <<")
        return ConstantNIterVar(config), "Constante igual ao inicial"


def addCities(dm):
    print("Selecione as cidades para adicionar ao caminho (a primeira lettra da cidade)")
    allCities = dm[0]
    desiredCities = []
    for city in allCities:
        print('-', city)
    print("Se quiser adicionar todas insira um ponto de exclamacao (!)")
    print("Quando estiver pronto insere um ponto (.)")
    while True:
        print("Cidades escolhidas: ", desiredCities)
        i = input(">> ").strip().upper()
        if i == "!":
            print("> Todas as cidades adicionadas! <")
            return allCities
        if i == ".":
            if len(desiredCities) < 2:
                print("Erro 001: Muito poucas cidades escolhidas")
                continue
            break

        if  len(i) != 1:
            print("Erro 002: Escolhe uma letra")
            continue

        city = getCity(allCities, i)

        if city == None:
            print(f'Erro 003: Nenhuma cidade comeca com', i)
            continue

        if city in desiredCities:
            print("Erro 004: Cidade ja adicionada!")
            continue
        desiredCities.append(city)
    return desiredCities

GEOMETRIC_LT  = 1
ARITHMETIC_LT = 2
GRADUAL_LT    = 3

def defaultLowerTemp(cfg):
    return GeometricLowerTemp(cfg, 0.84)

def chooseLowerTemp(cfg, type, par):
    # check type of par ....
    if type == GEOMETRIC_LT:
        return GeometricLowerTemp(cfg, par)
    elif type == ARITHMETIC_LT:
        return ArithmeticLowerTemp(cfg, par)
    elif type  == GRADUAL_LT:
        return GradualLowerTemp(cfg, par)

    return defaultLowerTemp(cfg)

MIN_TEMP_TT      = 1
MAX_ITER_TT      = 2
ACCEPT_FACTOR_TT = 3

def defaultTerminalTest(cfg):
    return MaxIterTerminalTest(cfg, 2000)

def chooseTTest(cfg, type, par):
    if type == MIN_TEMP_TT:
        return MinTempTerminalTest(cfg, par)
    elif type == MAX_ITER_TT:
        return MaxIterTerminalTest(cfg, par)
    elif type == ACCEPT_FACTOR_TT:
        return AcceptFactorTerminalTest(cfg, par)

    return defaultTerminalTest(cfg)

CONSTANT_VAR_IT = 1
LINEAR_VAR_IT   = 2

def defaultVarNIter(cfg):
    return ConstantNIterVar(cfg)

def chooseVarNIter(cfg, type, par):
    if type == CONSTANT_VAR_IT:
        return ConstantNIterVar(cfg)
    elif type == LINEAR_VAR_IT:
        return LinearNIterVar(cfg, float(par))

    return defaultVarNIter(cfg)

def parse_cities(dm, clist : list[str] | str):
    cities = []
    for c in clist:
        c = c.upper()
        city = getCity(dm[0], c)
        if city == None:
            raise Exception('No city starts with ', c)
        if city in cities:
            raise Exception('City', city, 'already added')
        
        cities.append(city)
    return cities

def parse_file(file_name):
    dm = readDistanceMatrix(FILE_NAME)
    print('parsing:', file_name)
    with open(file_name, 'r') as f:
        info = loads(f.read())

        # gets the cities
        clist = info.get('cities')

        cities = parse_cities(dm, clist) if clist else dm[0]

        print('cities:', cities)
        # get's the rest
        problem = TravSalemanProblem(cities, dm) 
        nIter = info.get('nIter', len(cities))
        initTemp = info.get('initTemp', problem.calc_init_temp())

        # chooses other parameters :)
        config = Configs(nIter, initTemp)
        aux = info.get('varTemp', {})
        config = chooseLowerTemp(config, aux.get('type'), aux.get('parameter'))

        aux = info.get('varNIter', {})
        config = chooseVarNIter(config, aux.get('type'), aux.get('parameter'))

        aux = info.get('terminalTest', {})
        config = chooseTTest(config, aux.get('type'), aux.get('parameter'))

    return problem, config 

if __name__ == '__main__':

    if len(argv) > 1:
        file_name = argv[1]
        try:
            problem, config =  parse_file(file_name)
        except Exception as e:
            if type(e) == JSONDecodeError:
                print('invalid json')
            else:
                print('erro parsing file:')

            print(*e.args)
    else:
        print('getting user input :)')


'''
if __name__ == '__main__':

    # cities = dm[0]  # Todas as cidades
    cities = addCities(dm)

    problem = TravSalemanProblem(cities, dm)

    config, nIterInicial, tempInicial = chooseInitializers(cities, problem)  # Inicializar nInterPerTemp e Temp
    print("*=" * 20)

    config, terminalChoice = chooseTerminalTest(config)  # Terminal test
    print("*=" * 20)

    config, decaimentoChoice = chooseDecaimentoTemp(config)  # Decaimento da temp
    print("*=" * 20)

    config, nIterVarChoice = chooseNIterPerTemp(config)  # Variacao do numero de iteracoes por temperatura
    print("*=" * 20)

    negrito = '\033[1m'
    normal = '\033[0m'

    print('{:*^19}'.format(" Informacoes "))
    print("•Temperatura inicial: ", negrito, tempInicial, normal)
    print("•Numero de iteracoes inicial: ", negrito, nIterInicial, normal)
    print("•Criterio de paragem: ", negrito, terminalChoice, normal)
    print("•Metodo decaimento temperatura: ", negrito, decaimentoChoice, normal)
    print("•Metodo de variacao do numero\n de iteracoes por temperatura: ", negrito, nIterVarChoice, normal)
    print()
    cost = 99999
    
    # think about this ....
    for i in range(100):  # Vai repetindo ate chegar a melhor...
        sol = searchSolution(problem, config)
        newcost = problem.cost_func(sol)
        if newcost < cost:
            cost = newcost
            print(f'Tentativa {i+1} | ', end="")
            print('cost:', problem.cost_func(sol), " : ", sol)
    print("Ended")
'''