import math
import operator
import random


class Algorithm:
    def __init__(
            self,
            func,
            optimumIsMinimum=True,
            precision=5,
            dimensions=2,
            steps=1,
            doForever=0,
            repeats=1):
        self.func = func[0]
        self.dimRange = func[1]
        self.dimIntervalLength = self.dimRange[1] - self.dimRange[0]
        self.optimumIsMinimum = optimumIsMinimum
        if optimumIsMinimum:
            self.optInit = math.inf
            self.cmp = operator.lt
            self.getOpt = min
        else:
            self.optInit = -math.inf
            self.cmp = operator.gt
            self.getOpt = max
        self.dimensions = dimensions
        self.precision = precision
        self.steps = steps
        self.dimensionBitSize = math.ceil(
            math.log2(
                self.dimIntervalLength * 10 ** precision,
            )
        )
        self.candidateBitSize = self.dimensions * self.dimensionBitSize
        self.dimMaxInt = 2 ** self.dimensionBitSize - 1
        self.candidate = None
        self.be = self.optInit  # best eval
        self.bb = None  # bitstring
        self.bv = []  # values
        self.bstep = 0  # at which eval did we achieve this best
        self.br = 0  # repeat when best was found
        self.exploredPoints = []
        self.evals = 0
        self.repeats = repeats
        self.repCurr = 0
        self.doForever = doForever

    def __str__(self):
        return self.getName() + ' ' + self.func.__doc__

    def getName(self):
        return 'Random Search Algorithm (Binary)'

    def gimmeSomeEval(self):
        c0 = [self.dimRange[0]] * self.dimensions
        c1 = [self.dimRange[1]] * self.dimensions
        c2 = [self.dimRange[0] +
              (self.dimRange[1] - self.dimRange[0]) / 2] * self.dimensions
        e0 = self.func(c0)
        e1 = self.func(c1)
        e2 = self.func(c2)
        e = self.getOpt(e0, e1, e2)
        return e

    def getRepCurr(self):
        return self.repCurr

    def getRepMax(self):
        return self.repeats

    def getRepBest(self):
        return self.br

    def generateCandidate(self):
        candidate = [0] * self.candidateBitSize
        avBits = 0
        bitBlockSize = 64
        for ii in reversed(range(self.candidateBitSize)):
            if avBits == 0:
                avBits = min(bitBlockSize, ii + 1)
                randBits = random.getrandbits(avBits)
            candidate[ii] = 1 & randBits
            randBits >>= 1
            avBits -= 1
        return candidate

    def decode(self, candidate):
        values = [0] * self.dimensions
        a0 = 0
        a1 = self.dimensionBitSize
        for ii in range(self.dimensions):
            values[ii] = self.decodeDimension(candidate[a0:a1])
            a0 = a1
            a1 += self.dimensionBitSize
        return (values)

    def decodeDimension(self, dimensionBits):
        s = 0
        for b in dimensionBits:
            s = (s << 1) | b
        v = s / self.dimMaxInt * self.dimIntervalLength + self.dimRange[0]
        return (v)

    def eval(self, values):
        self.evals += 1
        e = self.func(values)
        self.exploredPoints.append([e, *values])
        return (e)

    def restart(self):
        self.candidate = None
        self.be = self.optInit  # best eval
        self.bb = None  # bitstring
        self.bv = []  # values
        self.bstep = 0  # at which eval did we achieve this best
        self.br = 0  # repeat when best was found
        self.exploredPoints = []
        self.evals = 0
        self.repCurr = 0

    def solveStep(self):
        if self.repCurr >= self.repeats:
            if self.doForever:
                self.restart()
            else:
                return ()
        self.repCurr += 1
        self.candidate = self.generateCandidate()
        v = self.decode(self.candidate)
        e = self.eval(v)
        if self.cmp(e, self.be):
            self.br = self.repCurr - 1
            self.be = e
            self.bb = self.candidate[:]
            self.bv = v
            self.bstep = self.evals

    def run(self):
        self.exploredPoints = []
        for ii in range(self.steps):
            self.solveStep()
        return (self.exploredPoints)
