from gurobipy import *
from itertools import product
import random
import time as tm

arcs=set()
cap={}
nbr={}

with open('flow-lec-eg.txt') as file:
    n=int(next(file))
    for i in range(n):
        nbr[i]=[]
        line  = next(file).split()
        for k in range(0,len(line)-2,2):
            j = int(line[k+2])
            arcs.add((i,j))
            nbr[i].append(j)
            cap.update({(i,j): int(line[k+3])})
nodes = range(n)
s=0         #source node
t=n-1       #destination node

################## Integer Program model ####################
it1=tm.time()
arcsIP=tuplelist(arcs)    
IPmod = Model("shortest path")
x = IPmod.addVars(arcsIP, vtype=GRB.CONTINUOUS, ub = cap, name="flow")
for i in set(nodes)- {s,t}:
    IPmod.addConstr(quicksum(x[i,j] for i,j in arcsIP.select(i,'*')) - 
                  quicksum(x[j,i] for j,i in arcsIP.select('*',i)) == 0, name="flow conserve"+str(i))
IPmod.setObjective(quicksum(x[i,j] for i,j in arcsIP.select(s,'*')) - 
                  quicksum(x[j,i] for j,i in arcsIP.select('*',s)), GRB.MAXIMIZE)
IPmod.setParam("OutputFlag",0)
IPmod.optimize()
it2=tm.time()
print("IP opt="+str(IPmod.objVal)+" in time "+str(it2-it1))

