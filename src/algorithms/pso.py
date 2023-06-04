import math
import random

from src.algorithms.algorithm import Algorithm


class AlgorithmPso(Algorithm):
    # w = [intertia, cognitive, social, inertiaMulPerGeneration, speedMul, randAccel]
    # speedProportion:
    # if each dimension is given by the interval [a, b]
    # v = random(-1, 1) * (b - a) * speedMul
    def __init__(self,
                 func,
                 optimumIsMinimum=True,
                 dimensions=2,
                 steps=1,
                 popSize=100,
                 genNo=1000,
                 genGrace=200,
                 w=[1,
                    2,
                    2,
                    0.9,
                    0.5,
                    0.1],
                 doForever=0):
        super().__init__(func, optimumIsMinimum, 0, dimensions, steps, doForever)
        self.w = w
        self.w0Init = self.w[0]
        self.popSize = popSize
        self.genNo = genNo
        self.repeats = self.genNo
        self.genGrace = genGrace
        self.genCurr = self.repCurr = 0
        self.pop = None
        self.popV = None  # population speed
        # population past (best previous value for that particle)
        self.popP = None
        self.popE = None  # population evaluated values: f(X)
        self.popPE = None  # population past evaluated values
        self.genMin = math.inf
        self.genMax = -math.inf
        self.g = self.optInit
        self.gp = None

    def getName(self):
        return ('Particle Swarm Optimisation Algorithm (Floating-point), popSize = ' +
                str(self.popSize) +
                ' w[inertia, cognition, social, inertia/random decayMultiplier, maxSpeedAsDimensionProportion, randomNoise] = ' +
                str([self.w0Init, *
                     self.w[1:]]))

    def restart(self):
        self.genCurr = 0
        self.repeats = self.genNo
        self.pop = None
        self.br = 0
        self.be = self.optInit  # best eval
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
            self.pop, self.popV = self.generatePop()
            self.evalPop()
            self.popP = self.pop[:]
            self.popPE = self.popE[:]
        self.evalPop()
        self.updatePop()
        self.simPop()

    def updatePop(self):
        for ii in range(len(self.popE)):
            if self.cmp(self.popE[ii], self.popPE[ii]):
                self.popP[ii] = self.pop[ii][:]
                self.popPE[ii] = self.popE[ii]

    def simPop(self):
        for ii in range(len(self.pop)):
            inertia = self.mul(self.popV[ii], self.w[0])
            pastDiff = self.diff(self.popP[ii], self.pop[ii])
            cognition = self.mul(pastDiff, self.w[1] * random.random())
            greatestDiff = self.diff(self.gp, self.pop[ii])
            social = self.mul(greatestDiff, self.w[2] * random.random())
            randSpeed = self.mul(self.genRandSpeed(), self.w[5] * self.w[0])
            self.popV[ii] = self.sum(inertia, cognition, social, randSpeed)
        for ii in range(len(self.pop)):
            p = self.sum(self.pop[ii], self.popV[ii])
            for jj, pv in enumerate(p):
                if pv < self.dimRange[0]:
                    p[jj] = self.dimRange[0]
                    self.popV[ii][jj] = 0
                if pv > self.dimRange[1]:
                    p[jj] = self.dimRange[1]
                    self.popV[ii][jj] = 0
            self.pop[ii] = p

        self.w[0] *= self.w[3]

    def genRandSpeed(self):
        s = []
        for _ in range(self.dimensions):
            s.append(self.w[4] * self.dimIntervalLength *
                     (random.random() * 2 - 1))
        return (s)

    def sum(self, *args):
        '''vector sum'''
        r = []
        for v in zip(*args):
            r.append(sum(v))
        return (r)

    def diff(self, v0, v1):
        '''vector difference, v0 - v1'''
        r = []
        for ii, jj in zip(v0, v1):
            r.append(ii - jj)
        return (r)

    def mul(self, v, s):
        '''vector * scalar'''
        r = []
        for ii in v:
            r.append(ii * s)
        return (r)

    def generatePop(self):
        pop = []
        popV = []
        for ii in range(self.popSize):
            p = []
            v = []
            for jj in range(self.dimensions):
                pd = self.dimRange[0] + self.dimIntervalLength * \
                    (random.random() * 2 - 1)
                vd = self.w[4] * self.dimIntervalLength * \
                    (random.random() * 2 - 1)
                p.append(pd)
                v.append(pd)
            pop.append(p)
            popV.append(v)
        return pop, popV

    def decode(self, p):
        return p

    def evalPop(self):
        self.g = self.optInit
        self.popE = []
        self.genMin = math.inf
        self.genMax = -math.inf
        for p in self.pop:
            e = self.eval(p)
            if e < self.genMin:
                self.genMin = e
            if e > self.genMax:
                self.genMax = e
            if self.cmp(e, self.g):
                self.g = e
                self.gp = p[:]
            if self.cmp(e, self.be):
                self.be = e
                self.bb = None
                self.bv = p[:]
                self.bstep = self.evals
                self.br = self.genCurr
            self.popE.append(e)
