from enum import Enum

class Tense(Enum):
    Past        = r":\:"
    Present     = r":|:"
    Future      = r":/:"
    Eternal     = r":-:"
    
# class TemporalOrder(Enum):
#     '''for temporal reasoning'''
#     NONE = 2
#     FORWARD = 1
#     CONCURRENT = 0
#     BACKWARD = -1
#     INVALID = 
