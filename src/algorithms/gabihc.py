from src.algorithms.ga import AlgorithmGa


class AlgorithmGaBihc(AlgorithmGa):
    def getName(self):
        return ('Genetic Algorithm boostrapped with post-BIHC (Binary), popSize = ' +
                str(self.popSize) +
                ' pm = ' +
                str(self.pm) +
                ' pcx = ' +
                str(self.pcx) +
                ' selPressureExponent = ' +
                str(self.selPressure))

    def solveStep(self):
        if self.genCurr >= self.repeats:
            if self.br > self.genCurr - self.genGrace:
                self.repeats += self.genGrace
            else:
                if self.bootstrapBihc():
                    return ()  # additional solutions are evaluated inside the bootstrap
                if self.doForever == 1:
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

    def bootstrapBihc(self):  # TODO: divide into steps
        if hasattr(self, 'bootstrapIdx') == False:
            self.bootstrapIdx = 0
            self.repeats += len(self.pop)
        if self.bootstrapIdx >= len(self.pop):
            return (False)
        ii = self.bootstrapIdx
        improved = True
        # we're in the post-generational phase
        self.genCurr += 1
        while improved:
            improved = False
            te, tp, tv = self.getBestMut(self.pop[ii])
            if self.cmp(te, self.popE[ii]):
                improved = True
                self.pop[ii][tp] = 1 - self.pop[ii][tp]
                self.popE[ii] = te
                self.popV[ii] = tv
        if self.cmp(self.popE[ii], self.be):
            self.be = self.popE[ii]
            self.bb = self.pop[ii][:]
            self.bv = self.popV[ii]
            self.br = self.genCurr
        self.bootstrapIdx += 1
        return (True)
