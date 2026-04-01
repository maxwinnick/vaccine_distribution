# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""
arcs=set()
cost={}     #arc costs (possibly negative)
nbr={}
with open('spn-eg.txt') as file:
    n=int(next(file))
    for i in range(n):
        nbr[i]=[]
        line  = next(file).split()
        for k in range(0,len(line)-2,2):
            j = int(line[k+2])
            arcs.add((i,j))
            nbr[i].append(j)
            cost.update({(i,j): float(line[k+3])})
            
nodes=range(n)
s=0
t=n-1
stages = range(n+1)



#################### DP ############################
d=[[float('inf') for u in nodes] for i in stages]     #value function
sel=[[float('inf') for u in nodes] for i in stages]  #selection decision in DP

d[0][s]=0
sel[0][s]=s

for i in range(1,n+1):
    for w in nodes:
        d[i][w]=d[i-1][w]
        sel[i][w]=w        
    for (u,w) in arcs:
        if(d[i][w] > d[i-1][u] + cost[u,w]):
            d[i][w] = d[i-1][u] + cost[u,w]
            sel[i][w] = u

same=True
chg=-1
for u in nodes:
    if(d[n][u] != d[n-1][u]):
        same=False
        chg=u        #node whose value changed in the last stage

if(same):
    print("shortest path costs "+str(d[n-1][t]))
    b=t
    walk=[t]
    for i in range(n-1,-1,-1):      #Consider stages in reverse order
        if(b!=sel[i][b]):
            walk.append(sel[i][b])
        b=sel[i][b]
    print("shortest path (reverse) is")
    print(walk) #shortest path (in reverse)
else:
    print("there is a negative cycle (reverse) contained in")
    b=chg                 #backtrack from chg to recover negative cycle
    i=n
    visited=[b]
    no_cycle=True
    while no_cycle:
        if ((sel[i][b] in visited) and (sel[i][b] != b)):
            no_cycle=False     #keep going back until a node is repeated
        if(b!=sel[i][b]):
            visited.append(sel[i][b])     
        b=sel[i][b]
        i=i-1
    print(visited)     
    #all nodes seen in backtracking: this is not a cycle, but contains a negative cycle (in reverse)
