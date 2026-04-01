from gurobipy import *
import numpy as np

m = 4
weight = [2, 3, 4, 5]
b = [7000, 9000, 7000, 3000]
L = 9

#master LP
master = Model("Cutting stock")
A = []
s = []
for i in range(m):
    s=[0]*m
    s[i] = int(L/weight[i])
    A.append(s)

demand = {}
x = {}
for i in range(m):
    x[i] = master.addVar(obj=1, vtype=GRB.CONTINUOUS, name="num[%d]"%i)
    demand[i] = master.addConstr( int(L/weight[i]) * x[i] >= b[i], name="dem[%d]"%i)
n=m
master.update()
master.setParam("OutputFlag",0)   #turn off output reporting

while 1:
#resolve master LP
    master.optimize()
    profit = [demand[i].Pi for i in range(m)]    #optimal dual vars
    print("iteration "+str(n-m+1))
    print(profit)
#knapsack instance
    T = [0]*(L+1)           #DP value function
    choice = [-1]*(L+1)     #DP "best" decisions
    for c in range(L+1):
        T[c] = 0
        if (c==0): continue
        for i in range(m):
            if(c<weight[i]): continue
            if(T[c] < profit[i]+T[c-weight[i]]):
                T[c] = profit[i]+T[c-weight[i]]     #Bellman Equation 
                choice[c] = i

    if (T[L] < 1.0000001): break    #no negative reduced cost
    s = [0]*m
    B=L
    while(T[B] > 0):
        s[choice[B]] = s[choice[B]] +1
        B = B - weight[choice[B]]
    print(s)

#add column to master LP

    svalues = [int(s[i]) for i in range(m)]
    A.append(svalues)
    
    col = Column()
    for i in range(m):
        col.addTerms(s[i], demand[i])        
    x[n] = master.addVar(obj=1, vtype=GRB.CONTINUOUS, name="x[%d]"%n, column=col)
    master.update()   
    n += 1

xsol = master.getAttr('x', x)    
print(xsol)    #optimal solution to column-generation LP

print("Optimal value ="+str(master.ObjVal))
print("Final constraint matrix:")
print(np.transpose(np.matrix(A)))

############ Get approximate solution ##############

#Method 1: round-up

apx1 = [math.ceil(xsol[j]) for j in range(n)]
print("Approximate solution (by roundup) has value " + str(sum(apx1[j] for j in range(n))))

#Method 2: re-solve model with integer restrictions on the generated columns/variables

for j in range(n):
    x[j].setAttr("vtype", GRB.INTEGER)  #enforce integer restriction for IP
master.update()
master.optimize()
apx2 = master.getAttr('x', x)    
print("Approximate solution (by IP) has value " + str(sum(apx2[j] for j in range(n))))
