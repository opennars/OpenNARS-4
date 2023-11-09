"""
This file implements the four global evaluations mentioned in [the design report of OpenNARS 3.1.0](https://cis.temple.edu/tagit/publications/PAGI-TR-11.pdf)

- satisfaction: the extent to which the current situation meet the system’s desires,
- alertness: the extent to which the system’s knowledge is insufficient,
- busyness: the extent to which the system’s time resource is insufficient,
- well-being: the extent to which the system’s “body” functions as expected.
"""


class GlobalEval:
    S: float = 0.5  # Satisfaction
    A: float = 0.0  # Alertness
    B: float = 0.5  # Busyness
    W: float = 0.5  # Well-being
    r: float = 0.05  # This is a global parameter

    def __init__(self) -> None:
        pass

    def update_satisfaction(self, s, p):
        ''''''
        r = GlobalEval.r * p
        self.S = r*s + (1-r)*self.S

    def update_alertness(self, a, p=1):
        ''''''
        r = GlobalEval.r * p
        self.A = r*a + (1-r)*self.A

    def update_busyness(self, b, p=1):
        ''''''
        r = GlobalEval.r * p
        self.B = r*b + (1-r)*self.B

    def update_wellbeing(self, w, p=1):
        ''''''
        r = GlobalEval.r * p
        self.W = r*w + (1-r)*self.W
