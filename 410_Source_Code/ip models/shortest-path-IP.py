# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""

from gurobipy import *
from itertools import product
import random
import time as tm


arcs=set()
cost={}
nbr={}
with open('sp-eg.txt') as file:
    n=int(next(file))
    for i in range(n):
        nbr[i]=[]
        line  = next(file).split()
        for k in range(0,len(line)-2,2):
            j = int(line[k+2])
            arcs.add((i,j))
            nbr[i].append(j)
            cost.update({(i,j): int(line[k+3])})
            
nodes=range(n)
s=0
t=n-1

################## Integer Program model ####################

arcsIP=tuplelist(arcs)    
IPmod = Model("shortest path")
path = IPmod.addVars(arcsIP, vtype=GRB.BINARY)
for i in set(nodes)- {s,t}:
    IPmod.addConstr(quicksum(path[i,j] for i,j in arcsIP.select(i,'*')) - 
                  quicksum(path[j,i] for j,i in arcsIP.select('*',i)) == 0)
IPmod.addConstr(quicksum(path[i,j] for i,j in arcsIP.select(s,'*')) - 
                  quicksum(path[j,i] for j,i in arcsIP.select('*',s)) == 1)
IPmod.setObjective(quicksum(cost[a]*path[a] for a in arcsIP), GRB.MINIMIZE)
IPmod.setParam("OutputFlag",0)
IPmod.optimize()


sol= IPmod.getAttr('x', path)
print("IP opt="+str(IPmod.objVal))
for a in arcsIP:
    if(int(sol[a])==1):
        print(a)
