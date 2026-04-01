# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""

from gurobipy import *
from itertools import product
import random
import time as tm

cost={}
nbr={}

with open('mst-eg.txt') as file:
    n=int(next(file))
    line = file.readline()
    while line:
        i,j,c = [float(a) for a in line.split()]
        i=int(i)
        j=int(j)
        cost.update({(i,j): c})
        line = file.readline()
    
nodes=range(n)
s=0
################## Greedy Algorithm  ####################
scost = dict(sorted(cost.items(),key=lambda x:x[1]))
comp = list(range(n))
tree = []   #partial tree
for (i,j) in scost:
    if comp[i]==comp[j]:
        continue
    tree.append((i,j))   #add edge to partial tree 
    c=comp[i]
    b=comp[j]
    for k in nodes:
        if comp[k]==c:
            comp[k]=b

print(tree)
