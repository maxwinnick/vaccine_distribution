# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""

n=4
c=3
h=2
d=[2,1,2,2]
k=[3,10,4,5]

days = range(n)
state=range(c+1)

v=[[float('inf') for t in state] for i in days]     #value function
s=[[float('inf') for t in state] for i in days]     #decisions

for t in range(c-d[0]+1):
    v[0][t]=k[0]                #initialization
    s[0][t]=t+d[0]
    
for i in range(1,n):
    for t in state:
        if(t>c-d[i]):
            continue
        if(v[i][t] > v[i-1][t+d[i]] + h*(t+d[i])):
            v[i][t] = v[i-1][t+d[i]] + h*(t+d[i])       #Bellman Equation
            s[i][t]=0                               #calculate V_i from V_i-1
        for e in range(1,t+d[i]+1):
            if(v[i][t] > v[i-1][t+d[i]-e] + k[i] + h*(t+d[i]-e)):
                v[i][t] = v[i-1][t+d[i]-e] + k[i] + h*(t+d[i]-e)
                s[i][t] = e

################# backtrack to find optimal order quantities ##########
b=0
soln = [-1 for i in days]
for i in range(n-1,-1,-1):      #Consider days in reverse order
    soln[i] = s[i][b]           #optimal decision for day i
    b = b + d[i] - soln[i]
print("optimal solution is "+str(soln))
