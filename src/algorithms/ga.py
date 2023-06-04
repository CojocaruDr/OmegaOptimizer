import math
import operator
import random

from src.algorithms.bihc import AlgorithmBihc


class AlgorithmGa(AlgorithmBihc):
    def __init__(
            self,
            func,
            optimumIsMinimum=True,
            precision=5,
            dimensions=2,
            steps=1,
            popSize=100,
            genNo=1000,
            genGrace=200,
            pm=0.01,
            pcx=0.2,
            selPressure=1,
            doForever=0):
        super().__init__(
            func,
            optimumIsMinimum,
            precision,
            dimensions,
            steps,
            0,
            doForever)
        self.popSize = popSize
        self.genNo = genNo
        self.repeats = self.genNo
        self.genGrace = genGrace
        self.genCurr = 0
        self.pm = pm
        self.pcx = pcx
        self.pop = None
        self.popV = None  # population decoded values: X
        self.popE = None  # population evaluated values: f(X)
        self.popF = None  # population fitnesses
        self.genMin = math.inf
        self.genMax = -math.inf
        self.selPressure = selPressure

    def getName(self):
        return ('Genetic Algorithm (Binary), popSize = ' +
                str(self.popSize) +
                ' pm = ' +
                str(self.pm) +
                ' pcx = ' +
                str(self.pcx) +
                ' selPressureExponent = ' +
                str(self.selPressure))

    def restart(self):
        self.genCurr = 0
        self.repeats = self.genNo
        self.pop = None
        self.br = 0
        self.be = self.optInit  # best eval
        self.bb = None  # bitstring
        self.bv = []  # values
        self.bstep = 0  # at which eval did we achieve this best
        self.br = 0  # repeat when best was found
        self.exploredPoints = []
        self.evals = 0
        self.repCurr = 0

    def solveStep(self):
        if self.genCurr >= self.repeats:
            if self.br > self.genCurr - self.genGrace:
                self.repeats += self.genGrace
            elif self.doForever == 1:
                self.restart()
            else:
                return ()
        self.genCurr += 1
        self.repCurr = self.genCurr
        if self.pop is None or len(self.pop) == 0:
            self.pop = self.generatePop()
        self.mutation()
        self.crossOver()
        self.evalPop()
        self.pop = self.selection()

    def evalPop(self):
        self.popV = []
        self.popE = []
        self.genMin = math.inf
        self.genMax = -math.inf
        for c in self.pop:
            v = self.decode(c)
            e = self.eval(v)
            if e < self.genMin:
                self.genMin = e
            if e > self.genMax:
                self.genMax = e
            if self.cmp(e, self.be):
                self.be = e
                self.bb = c
                self.bv = v
                self.bstep = self.evals
                self.br = self.genCurr
            self.popV.append(v)
            self.popE.append(e)

    def selection(self):
        evalDistance = self.genMax - self.genMin
        if evalDistance == 0:
            evalDistance = 1
        epsilon = evalDistance * 0.01
        div = evalDistance / 2
        newPop = []
        self.popF = []
        if len(self.pop) == 0:
            return ([])
        for e in self.popE:
            if self.optimumIsMinimum:
                f = (self.genMax - e + epsilon) / div
            else:
                f = (e - self.genMin + epsilon) / div
            f = math.pow(f, self.selPressure)
            self.popF.append(f)
        self.partialSums = [self.popF[0]]
        for ii in range(1, len(self.popF)):
            self.partialSums.append(self.partialSums[ii - 1] + self.popF[ii])
        selectVal = []
        for _ in range(self.popSize):
            val = random.random() * self.partialSums[-1]
            selectVal.append(val)
        selectVal.sort()
        lookStart = 0
        for ii, ps in enumerate(self.partialSums):
            for jj in range(lookStart, len(selectVal)):
                if selectVal[jj] < ps:
                    newPop.append(self.pop[ii])
                    lookStart += 1
                else:
                    break
        return (newPop)

    def crossOver(self):
        cxScore = []
        for ii in range(len(self.pop)):
            cxScore.append([ii, random.random()])
        cxScore.sort(key=operator.itemgetter(1))
        cxChosen = 0
        cxFlip = 0
        for ii, score in cxScore:
            if score < self.pcx:
                if cxFlip == 1:
                    self.pop.extend(
                        self.crossChromosomes(
                            self.pop[cxChosen],
                            self.pop[ii]))
                    cxFlip = 0
                else:
                    cxChosen = ii
                    cxFlip = 1
            else:
                if cxFlip == 1:
                    if random.random() < 0.5:
                        self.pop.extend(
                            self.crossChromosomes(
                                self.pop[cxChosen],
                                self.pop[ii]))
                break

    def crossChromosomes(self, c0, c1):
        pos = int(1 + random.random() * (len(c0) - 2))
        c01 = c0[:pos] + c1[pos:]
        c10 = c1[:pos] + c0[pos:]
        return (c01, c10)

    def mutation(self):
        for c in self.pop:
            self.mutateChromsome(c)

    def mutateChromsome(self, c):
        for ii, _ in enumerate(c):
            if random.random() < self.pm:
                c[ii] = 1 - c[ii]

    def generatePop(self):
        pop = []
        for ii in range(self.popSize):
            pop.append(self.generateCandidate())
        return (pop)
