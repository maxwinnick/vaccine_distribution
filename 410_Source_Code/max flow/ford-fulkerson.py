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

################## Ford-Fulkerson Algorithm ####################
        
at1=tm.time()

rarcs=set()
rcap={}
rnbr={}
for i in nodes:
    rnbr[i]=[]
for (i,j) in arcs:
    rarcs.add((i,j))
    rcap.update({(i,j) : cap[(i,j)]})
    rnbr[i].append(j)
    if (j,i) not in arcs:
        rarcs.add((j,i))
        rcap.update({(j,i) : 0})
        rnbr[j].append(i)
value=0
flow={}
for (i,j) in rarcs:
    flow[(i,j)]=0

def distance():
    global dist
    dist=[n for j in nodes]         #current distance (number of arcs) to t
    level={t}
    d=0
    while True:
        nextl=set()
        for i in level:
            dist[i]=d
        for i in level:
            for j in rnbr[i]:
                if (rcap[(j,i)] > 0 and dist[j]==n):
                    nextl.add(j)
        if (not nextl):
            break
        d=d+1
        level=nextl
    
dist=[]
distance()
v=s
aug=[s]
while dist[s]<n:
    if v==t:
                #augment flow as the current augmenting path has reached t
        newflow=float('inf')
        aug_arcs=set()
        for k in range(len(aug)-1):
            i=aug[k]
            j=aug[k+1]
            aug_arcs.add((i,j))
            newflow=min(newflow, rcap[(i,j)])
        value = value + newflow
        for (i,j) in aug_arcs:
            flow[(i,j)] = flow[(i,j)]+newflow
            rcap[(i,j)] = rcap[(i,j)] - newflow
            rcap[(j,i)] = rcap[(j,i)] + newflow
        v=s
        aug=[s]     #reset the augmenting path to start at s
            
    advanced=False
    for w in rnbr[v]:   #try to advance the augmenting path from v 
        if (rcap[(v,w)]==0) or (dist[w] != dist[v]-1):
            continue
        aug.append(w)
        v=w             #augmenting path extended from v to w
        advanced=True
        break
    if not advanced:        #update the distance label of v as we could not extend augmenting path
        newdist=n-1
        for w in rnbr[v]:
            if (rcap[(v,w)]>0):
                newdist = min(newdist, dist[w])
        dist[v]=1+newdist
        if v!=s:
            aug.pop()
            v=aug[-1]       #backtrack the augmenting path to the node before v
        else:
            distance()      #recalculate all distance labels

for (i,j) in arcs:
    if ((flow[(i,j)] >0 ) and (flow[(j,i)] >0 )):
        cancel=min(flow[(i,j)] , flow[(j,i)])
        flow[(i,j)]=flow[(i,j)] - cancel            #cancel 2-cycles
        flow[(j,i)]=flow[(j,i)] - cancel
                
at2=tm.time()
print("max flow is "+str(value)+" found in time "+str(at2-at1))

for (i,j) in arcs:
    if (flow[(i,j)] > 0):
        print(str(i)+" "+str(j)+" arc has flow "+str(flow[(i,j)]))

######### finding the minimum cut ##############
k=0
for v in nodes:         #find the highest level of nodes connected to t
    if (dist[v]<n):
        k=max(k,dist[v])
Snodes=[]
for v in nodes:
    if (dist[v]>k):
        Snodes.append(v)
print("minimum cut has nodes on source side = "+str(Snodes))

cut_arcs=set()
for u in Snodes:
    for v in rnbr[u]:
        if (((u,v) in arcs) and (v not in Snodes)):
            cut_arcs.add((u,v))
cut_value=sum(cap[(i,j)] for (i,j) in cut_arcs)
print("minimum cut has arcs  "+str(cut_arcs))
print("cut value = "+str(cut_value))