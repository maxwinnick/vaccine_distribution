# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 13:04:18 2018

@author: viswa
"""

from gurobipy import *

with open('ad-data.txt') as file:
    n=int(next(file))   #number of advertisers
    m=int(next(file))   #number of slots
    B=[0 for i in range(n)]
    r=[[0 for j in range(m)] for i in range(n)]
    for i in range(n):
        line  = next(file).split()
        B[i] = int(line[0])     #budget of advertiser i
        for j in range(m):
            r[i][j] = int(line[j+1])
            #revenue from advertiser i if slot j is given to them

slots=range(m)
ads=range(n)

#  Set up and solve IP model for ad allocation
            
mod = Model("ad allocation")
x = mod.addVars(ads, slots, vtype=GRB.BINARY, name="x")
        #binary decision variables

mod.setObjective(quicksum(r[i][j]*x[i,j] for i in ads for j in slots), GRB.MAXIMIZE)
        #objective is to maximize the total revenue
######################################
#add in the constraints and solve the model
for i in ads:
    mod.addConstr(quicksum(r[i][j]*x[i,j] for j in slots)<= B[i], name="budget"+str(i))

for j in slots:
    mod.addConstr(quicksum(x[i,j] for i in ads)<= 1, name="capacity"+str(j))

mod.optimize()
####################################
soln = mod.getAttr('x', x)   #store the optimal allocation
used=[0 for i in ads]
for i in ads:
    used[i]=int(sum(r[i][j]*soln[i,j] for j in slots))
    for j in slots:
        if (soln[i,j] > 0.0):
            print("allocate slot "+str(j)+" to advertiser "+str(i))
    print("advertiser "+str(i)+" uses "+str(used[i])+" from their budget")
