# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""
import time as tm

arcs=set()

with open('top-sort2k.txt') as file:
    n=int(next(file))
    for i in range(n):
        line  = next(file).split()
        for k in range(len(line)-2):
            j = int(line[k+2])
            arcs.add((i,j))
nodes=range(n)

t1=tm.time()        #start time of the top sort algorithm

################## Algorithm ####################
indeg=[0 for i in nodes]
for (i,j) in arcs:
    indeg[j]+=1
sinks=[]
for i in nodes:
    if(indeg[i]==0):
        sinks.append(i)
seq=[-1 for i in range(n)]
for k in range(n):
    if(len(sinks)==0):
        print("No valid sequence")
        break
    s=sinks[0]
    sinks.remove(s)
    seq[k]=s        #assign node s to position k
    for i in nodes:
        if((s,i) in arcs):
            indeg[i]-=1
            if(indeg[i]==0):
                sinks.append(i)
print(seq)

t2=tm.time()        #end time of the top sort algorithm
print("time taken (sec) "+str(t2-t1))