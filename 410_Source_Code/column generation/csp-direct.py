from gurobipy import *
import numpy as np

m = 4
weight = [2, 3, 4, 5]
# b = [4, 5, 5, 4]

b = [7000, 9000, 7000, 3000]
L = 9

ipmod = Model("Cutting stock IP")

T = 0

for i in range(m):
    T = T+ math.ceil(b[i] / math.floor(L/weight[i]))

print("Number of `place holder' bins = "+str(T))
    
y = ipmod.addVars(range(T),obj=1, vtype=GRB.BINARY, name="bin use")
#these are binary variables indicating whether/not each bin is used

z = ipmod.addVars(range(m), range(T), vtype=GRB.INTEGER, name="assignment")
#these are integer variables for the number of units of each item in each bin

ipmod.modelSense = GRB.MINIMIZE

for j in range(T):
    ipmod.addConstr(quicksum(weight[i]*z[i,j] for i in range(m)) - L*y[j] <= 0, name="bin"+str(j))
    #the weight limit constraint for each bin

for i in range(m):
    ipmod.addConstr(quicksum(z[i,j] for j in range(T)) == b[i], name="demand"+str(i))
    #the demand constraint for each item

ipmod.optimize()
