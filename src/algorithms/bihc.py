from src.algorithms.algorithm import Algorithm


class AlgorithmBihc(Algorithm):
    def __init__(
            self,
            func,
            optimumIsMinimum=True,
            precision=5,
            dimensions=2,
            steps=1,
            repeats=10000,
            doForever=0):
        super().__init__(func, optimumIsMinimum, precision, dimensions, steps, doForever)
        self.repeats = repeats
        self.ce = 0  # current eval
        self.cv = []  # current values
        self.tbe = 0  # temp best eval, position
        self.tbp = 0

    def getName(self):
        return ('Best Improvement Hill-Climbing Algorithm (Binary)')

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
        self.ce = 0
        self.cv = []

    def getBestMut(self, c):
        tbe = self.optInit
        tbp = -1
        tbv = []
        for ii in range(len(c)):
            c[ii] = 1 - c[ii]
            tv = self.decode(c)
            te = self.eval(tv)
            if self.cmp(te, self.tbe):
                tbe = te
                tbp = ii
                tbv = tv
            c[ii] = 1 - c[ii]  # reset the change
        return (tbe, tbp, tbv)

    def solveStep(self):
        if self.repCurr >= self.repeats and self.doForever == 0:
            return ()
        if self.candidate is None:
            self.repCurr += 1
            self.candidate = self.generateCandidate()
            self.cv = self.decode(self.candidate)
            self.ce = self.eval(self.cv)
        self.tbe, self.tbp, self.tbv = self.getBestMut(self.candidate)
        if self.cmp(self.tbe, self.ce):
            self.ce = self.tbe
            self.cv = self.tbv
            self.candidate[self.tbp] = 1 - self.candidate[self.tbp]
        else:
            if self.cmp(self.ce, self.be):
                self.be = self.ce
                self.bb = self.candidate[:]
                self.bv = self.cv
                self.bstep = self.evals
                self.br = self.repCurr
            self.candidate = None
