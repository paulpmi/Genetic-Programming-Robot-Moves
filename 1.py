from random import random, randint, sample
from math import sin, cos
from copy import deepcopy

class Chromosome:
    def __init__(self):
        self.maxDepth = 3
        self.statement = [0 for i in range(2**self.maxDepth)]
        self.size = len(self.statement)
        self.terminals = ['x', 'y']
        self.functions = ['+', '-', '*', 'sin', 'cos']
        self.fitness = 0

        self.createStatement()

    # CREATE STATEMENT USING TERMINALS AND FUNCTIONS:
    # NEGATIVE VALUES = TERMINALS; POSITIVE VALUES = FUNCTIONS
    def createStatement(self):
        self.statement[0] = randint(1, len(self.functions))
        for i in range(1, self.size):
            if random() < 0.4:
                self.statement[i] = -randint(1, len(self.terminals))
            else:
                self.statement[i] = randint(1, len(self.functions))
        return self.statement

    # EVALUATE STATEMENT SEEING WHAT FUNCTION SHOULD BE USED WITH THE KNOWN DATA
    # IN ORDER TO BRING A SOLUTION
    def evalStatement(self, pos, knownData):

        if pos < len(self.statement):
            if self.statement[pos] < 0:
                if abs(self.statement[pos]) > len(self.terminals):
                    self.statement[pos] = -2
                return knownData[abs(self.statement[pos]) - 1], pos
            else:
                if self.functions[self.statement[pos]-1] == '+':
                    tillTerminal = self.evalStatement(pos+1, knownData)
                    afterTerminal = self.evalStatement(tillTerminal[1]+1, knownData)
                    return tillTerminal[0] + afterTerminal[0], afterTerminal[1]
                elif self.functions[self.statement[pos]-1] == '-':
                    tillTerminal = self.evalStatement(pos+1, knownData)
                    afterTerminal = self.evalStatement(tillTerminal[1]+1, knownData)
                    return tillTerminal[0] - afterTerminal[0], afterTerminal[1]
                elif self.functions[self.statement[pos]-1] == '*':
                    tillTerminal = self.evalStatement(pos+1, knownData)
                    afterTerminal = self.evalStatement(tillTerminal[1]+1, knownData)
                    return tillTerminal[0] * afterTerminal[0], afterTerminal[1]
                elif self.functions[self.statement[pos]-1] == 'sin':
                    tillTerminal = self.evalStatement(pos+1, knownData)
                    afterTerminal = self.evalStatement(tillTerminal[1]+1, knownData)
                    return sin(tillTerminal[0]), afterTerminal[1]
                elif self.functions[self.statement[pos]-1] == 'cos':
                    tillTerminal = self.evalStatement(pos+1, knownData)
                    afterTerminal = self.evalStatement(tillTerminal[1]+1, knownData)
                    return cos(tillTerminal[0]), afterTerminal[1]
        else:
            return [0,len(self.statement)+1]

    # CHECK GLOBAL ERROR
    def checkFitness(self, knownData, expectedOutput):
        error = 0
        for i in range(len(expectedOutput)):
            error += abs(expectedOutput[i]) - abs(self.evalStatement(0, knownData[i])[0])
        self.fitness = deepcopy(error)
        return error

    def findNewBranch(self, startPoint):
        for i in range(startPoint, self.size):
            if self.statement[i] < 0:
                return i
        return -1

    def crossover(self, c1, c2):
        branchC1 = randint(1, self.size-1)
        branchC2 = randint(1, self.size-1)

        endC1 = self.findNewBranch(branchC1)
        endC2 = self.findNewBranch(branchC2)
        for i in range(branchC1):
            self.statement[i] = c1.statement[i]
        for i in range(branchC2, endC2):
            self.statement[i] = c1.statement[i]
        for i in range(endC1, len(self.statement)):
            self.statement[i] = c1.statement[i]
        return self.statement

    def mutation(self):
        selectedBranch = randint(1, self.size-1)
        if self.statement[selectedBranch] < 0:
            new = -randint(1, len(self.terminals))
            while self.statement[selectedBranch] == new:
                new = -randint(1, len(self.terminals))
            self.statement[selectedBranch] = new
        else:
            new = randint(1, len(self.functions))
            while self.statement[selectedBranch] == new:
                new = -randint(1, len(self.functions))
            self.statement[selectedBranch] = new

    def __str__(self):
        graph = []
        for i in range(self.size):
            if self.statement[i] < 0:
                graph.append(self.terminals[abs(self.statement[i]) -1])
            else:
                graph.append(self.functions[self.statement[i]-1])
        return str(graph)

class Population:
    def __init__(self):
        self.size = 10
        self.population = [Chromosome() for i in range(self.size)]

        self.kO = None
        self.nO = None
        self.oO = None

    def readData(self, fileName):
        f = open(fileName, 'r')
        data = []
        first = []
        otherData = []
        i = 0
        for line in f:
            data.append(line.strip().split(','))

            for j in range(0, len(data[i]) - 1,3):
                first.append([float(data[i][j]), float(data[i][j+1])])
            otherData.append(data[-1][-1])
            i += 1
        return first, otherData

    def normalize(self, output):
        trueOutput = []
        for i in output:
            if i == 'Slight-Right-Turn':
                trueOutput.append(randint(-165, -151))
            elif i == 'Move-Forward':
                trueOutput.append(180)
            elif i == 'Sharp-Right-Turn':
                trueOutput.append(randint(-179, -166))
            elif i == 'Slight-Left-Turn':
                trueOutput.append(randint(-150, -1))
            elif i == 'Sharp-Left-Turn':
                trueOutput.append(randint(0, 150))
            else:
                trueOutput.append(randint(150, 180))
        return trueOutput

    def evolve(self, data, normalize, otherData):
        toAdd = []
        for c in range(len(self.population)):
            mother, father = sample(self.population, 2)
            child = Chromosome()
            child.crossover(mother, father)
            child.mutation()
            toAdd.append(child)
            child.checkFitness(data, normalize)
        self.population = self.reunion(toAdd)
        self.population = self.selection(0, data, normalize, otherData)
        return self.population

    def reunion(self, toAdd):
        sizePop = len(toAdd) + len(self.population)
        self.population += toAdd
        return self.population

    def selection(self, n, data, normalize, otherData):
        if n < len(self.population):
            population = sorted(self.population, key=lambda Chromosome: Chromosome.checkFitness(self.kO, self.nO), reverse=False)
            population = population[:n]
            sizePop = n
        return self.population

    def best(self, n):
        aux = sorted(self.population, key=lambda Chromosome: Chromosome.checkFitness(self.kO, self.nO))
        return self.population[:n]

    def run(self):
        dataInput, dataOutput = self.readData('input.in')
        normalizedData = self.normalize(dataOutput)

        self.kO = dataInput
        self.oO =dataOutput
        self.nO = normalizedData

        for i in range(5):
            self.evolve(data=dataInput, normalize=normalizedData, otherData=dataOutput)

    def __str__(self):
        g = []
        for i in self.population:
            g.append((i.statement, ' ', i.checkFitness(self.kO, self.nO)))
        return str(g)
p = Population()
p.run()
for i in p.best(5):
    print(i, ' ', i.fitness)