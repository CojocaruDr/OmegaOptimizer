import math
from enum import IntEnum


class Functions:
    zeroDimRange = [-1, 1]

    # TODO: Compute this from tradingview exports
    # These are the returns from today
    expectedReturns = [7.1, 0.8, 3.1, -0.2, 1.1]
    currentReturns = [9.67, 0.32, 2.69, -0.53, -0.83]

    # Computed as yesterday's returns % times allocation for each strategy we're trying to optimize for.
    # The reasoning is to consider the profitability limit as yesterday's baseline. Not exactly correct, but will update later.
    # L = 9.67 * 8.87 + 0.32 * 0 + 2.69 * 5.81 - 0.53 * 44.88 - 0.83 * 40.44
    L = 0

    @staticmethod
    def omega(weights):
        """Omega-optimized portfolio"""
        wESum = 0
        wSum = 0
        for i, w in enumerate(weights):
            wESum += w * Functions.expectedReturns[i]
            wSum += w * Functions.currentReturns[i]

        return (wESum - Functions.L) / (abs(Functions.L - wSum) + 0.0000001)

    omegaRange = [4, 25]
