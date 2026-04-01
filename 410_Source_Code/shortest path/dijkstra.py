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

################## Algorithm with adjacency list ####################
at1=tm.time()
d=dict({i : float('inf')  for i in nodes})
d[s]=0
p=[-1 for i in nodes]
sd=[float('inf')  for i in nodes]
for k in range(n):
    v=min(d, key=d.get)
    sd[v]=d[v]
    d.pop(v, None)
    for w in nbr[v]:        #all arcs (u,v) out of u
        if(w in d.keys()):
            if(d[w] > sd[v] + cost[(v,w)]):
                d[w]=sd[v] + cost[(v,w)]
                p[w]=v
at2=tm.time()
print("shortest path costs "+str(sd[t])+" in time "+str(at2-at1))


