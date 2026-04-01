from gurobipy import *
import random
import numpy as np
import math

n=30
m=50

elements = range(n)
sets = range(m)

cost = []
for r in sets:
    # cost.append(1)
    cost.append(np.random.randint(1,1000))

A = [[0 for p in elements] for r in sets]
for r in sets:
    for p in elements:
        if(np.random.rand() < 0.1):
            A[r][p] = 1

###################### integer program ################
IPmod = Model("set cover")

x = IPmod.addVars(sets, vtype=GRB.BINARY, name="x")

IPmod.setObjective(quicksum(cost[r]*x[r] for r in sets), GRB.MINIMIZE)

for p in elements:
    IPmod.addConstr(quicksum(A[r][p]*x[r] for r in sets) >= 1)

# IPmod.Params.timeLimit = 50.0
IPmod.optimize()

xint=[]
xint= IPmod.getAttr('x', x)    

for r in sets:
    if (xint[r]>0):
        print(r)


