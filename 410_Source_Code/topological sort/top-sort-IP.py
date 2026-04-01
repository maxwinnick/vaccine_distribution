# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""

from gurobipy import *
import time as tm

arcs=set()

with open('top-sort2k.txt') as file:
# with open('top-sort-eg.txt') as file:
    n=int(next(file))
    for i in range(n):
        line  = next(file).split()
        for k in range(len(line)-2):
            j = int(line[k+2])
            arcs.add((i,j))
nodes=range(n)

t1=tm.time()        #start time of the IP algorithm

################## Integer Program model ####################

IPmod = Model("topological sort")
x = IPmod.addVars(nodes, vtype=GRB.INTEGER, name="x")
IPmod.setObjective(0, GRB.MINIMIZE)
for (i,j) in arcs:
    IPmod.addConstr(x[j]-x[i] >= 1, name="prec"+str(i)+","+str(j))
IPmod.optimize()
xsol= IPmod.getAttr('x', x)   
t2=tm.time()        #end time of the IP algorithm

print("time taken (sec) "+str(t2-t1))