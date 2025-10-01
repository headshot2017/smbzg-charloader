import math

def Linear(x):
    return x

def In(x):
    return x * x

def Out(x):
    return 1 - (1-x) * (1-x)

def InOut(x):
    return 2*x*x if x < 0.5 else 1 - math.pow(-2*x+2, 2) / 2


Funcs = {
    0: Linear,
    1: In,
    2: Out,
    3: InOut,
}
