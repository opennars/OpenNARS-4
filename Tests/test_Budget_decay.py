from opennars.NAL.Functions.BudgetFunctions import Budget_decay
from opennars.Narsese import Budget
import matplotlib.pyplot as plt
from opennars.Config import Config
import math

def Budget_decay2(budget: Budget):
    ''''''
    Q = Config.quality_min
    q = budget.quality * Q
    budget.priority = q + (budget.priority - q)*math.sqrt(budget.durability)


def main():
    d = 0.999
    n=1000
    budget = Budget(0.1, d, 1.0)

    priorities = []
    for _ in range(n):
        priorities.append(budget.priority)
        Budget_decay(budget)
    plt.figure()
    plt.plot(priorities)
    budget = Budget(0.1, d, 1.0)
    priorities = []
    for _ in range(n):
        priorities.append(budget.priority)
        Budget_decay2(budget)
    plt.figure()
    plt.plot(priorities)
    plt.show()

if __name__ == '__main__':
    main()
