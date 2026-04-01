# -*- coding: utf-8 -*-
"""
Created on Wed Oct  3 13:04:18 2018

@author: viswa
"""

from gurobipy import *

with open('match-eg.txt') as file:
    n=int(next(file))   #number of residents
    m=int(next(file))   #number of hospitals
    c=[0 for i in range(m)]     #number of positions in each hospital
    a=[[0 for j in range(n)] for i in range(m)]
    for i in range(m):
        line  = next(file).split()
        c[i] = int(line[2])     #capacity of hospital i
        for k in range(0,len(line)-3):
            j = int(line[k+3])
            print(str(i)+" "+str(j))
            a[i][j] = 1

hospitals=range(m)
residents=range(n)

#  Set up and solve IP model for matching
            
mod = Model("matching")
x = mod.addVars(hospitals, residents, vtype=GRB.BINARY)
        #binary decision variables

mod.setObjective(quicksum(a[i][j]*x[i,j] for i in hospitals for j in residents), GRB.MAXIMIZE)
        #objective is to maximize the total matched
######################################
for i in hospitals:
    mod.addConstr(quicksum(x[i,j] for j in residents)<= c[i])

for j in residents:
    mod.addConstr(quicksum(x[i,j] for i in hospitals)<= 1)

mod.optimize()
####################################
print("incidence matrix")
for row in a:
    print(row)
soln = mod.getAttr('x', x)   #store the optimal matching
print("maximum matching")
placed=[-1 for j in residents]
for j in residents:
    for i in hospitals:
        if (soln[i,j] > 0.0):
            placed[j]=i
            print("assign resident "+str(j)+" to hospital "+str(i))
    