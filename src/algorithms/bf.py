from src.algorithms.algorithm import Algorithm


class AlgorithmBf(Algorithm):
    def getName(self):
        return ('Brute Force Algorithm (Binary)')

    def restart(self):
        self.candidate = [0] * self.candidateBitSize
        self.be = self.optInit  # best eval
        self.bb = None  # bitstring
        self.bv = []  # values
        self.bstep = 0  # at which eval did we achieve this best
        self.br = 0  # repeat when best was found
        self.exploredPoints = []
        self.evals = 0
        self.repCurr = 0
        self.cr = 0

    def solveStep(self):
        if self.candidate is None:
            self.candidate = [0] * self.candidateBitSize
            self.cr = 0
            self.repeats = 1 << self.candidateBitSize
        else:
            if self.cr == 1:
                self.restart()
                if not self.doForever:
                    self.cr = 1
                    return ()
            self.repCurr += 1
            cr = 1
            for ii, _ in enumerate(self.candidate):
                if cr == 0:
                    break
                cr = 0
                self.candidate[ii] += 1
                if self.candidate[ii] > 1:
                    self.candidate[ii] = 0
                    cr = 1
            self.cr = cr
        v = self.decode(self.candidate)
        e = self.eval(v)
        if self.cmp(e, self.be):
            self.be = e
            self.bb = self.candidate[:]
            self.bv = v
            self.bstep = self.evals
            self.br = self.repCurr
