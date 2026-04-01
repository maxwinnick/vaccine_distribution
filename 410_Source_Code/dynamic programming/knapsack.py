# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 13:26:28 2019

@author: viswa
"""
import random
'''
n=4        #number of items
T=4        #target on total benefit
c=[2, 4, 5, 8]     #costs
h=[1, 2, 2, 3]     #benefits

'''
n=3
T=4
c=[4,6,7]
h=[2,1,3]

stage = range(n)
state=range(T+1)


#################   DP with only value functions ################

v=[[float('inf') for t in state] for i in stage]     #value function

for t in state:
    if (t==0):
        v[0][t]=0
    if((t>=1)and(t<=h[0])):
        v[0][t]=c[0]
    
for i in range(1,n):
    for t in state:
        w = max(0, t-h[i])      #remaining target if item i selected
        v[i][t] = min(v[i-1][t] , c[i] + v[i-1][w])
                                #better of the two options for item i
print("optimal value is "+str(v[n-1][T]))

########     DP with selection decisions     #######################

v=[[float('inf') for t in state] for i in stage]     #value function
s=[[float('inf') for t in state] for i in stage]     #best decisions
        
for t in state:
    if (t==0):
        v[0][t]=0
        s[0][t]=0       #don't select item 0
    if((t>=1)and(t<=h[0])):
        v[0][t]=c[0]
        s[0][t]=1       #select item 0

for i in range(1,n):
    for t in state:
        w = max(0, t-h[i])
        if (v[i-1][t] <= c[i]+v[i-1][w]):
            v[i][t] = v[i-1][t]
            s[i][t]=0       #don't select item i
        else:
            v[i][t]=c[i]+v[i-1][w]
            s[i][t]=1       #select item i

############ Backtrack to find the optimal solution ###########
b=T
soln = []
for i in range(n-1,-1,-1):      #Consider items in reverse order
    if(s[i][b]==1):
        soln.append(i)
        b=max(b-h[i] , 0)       #update remaining target
print("optimal solution is "+str(soln))
















