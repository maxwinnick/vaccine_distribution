from gurobipy import *
import numpy as np

m = 4
weight = [2, 3, 4, 5]
b = [7000, 9000, 7000, 3000]
L = 9

#master LP
master = Model("CSP column generation LP")
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
    #initial patterns for a basic-feasible-solution
    demand[i] = master.addConstr( int(L/weight[i]) * x[i] >= b[i], name="dem[%d]"%i)

n=m  #initially number of patterns equals #items
master.update()
master.setParam("OutputFlag",0)   #turn off output reporting

while 1:
#resolve master LP
    master.optimize()
    profit = [demand[i].Pi for i in range(m)]    #optimal dual vars
    
#knapsack instance for the reduced-cost oracle
    kmod = Model("knapsack")
    print("knapsack profits "+str(profit))
    select = kmod.addVars(range(m), vtype=GRB.INTEGER, name="sel")
    kmod.setObjective(quicksum(profit[i]*select[i] for i in range(m)), GRB.MAXIMIZE)
    kmod.addConstr(quicksum(weight[i]*select[i] for i in range(m)) <= L, "weight-limit")
    kmod.setParam("OutputFlag",0)   #turn off output reporting
    kmod.optimize()     #solve knapsack IP
    s= kmod.getAttr('x', select)    #get the optimal knapsack solution (pattern)
  
#add column to master LP
    if(kmod.ObjVal < 1.000001): break   #no negative reduced cost

    svalues = [int(s[i]) for i in range(m)]
    print("new pattern "+str(svalues))
    A.append(svalues)   #add new column (pattern) to constraint matrix
    
    col = Column()
    for i in range(m):
        col.addTerms(s[i], demand[i])        
    x[n] = master.addVar(obj=1, vtype=GRB.CONTINUOUS, name="x[%d]"%n, column=col)
    #add the new variable (pattern) to model 
    master.update()   
    n += 1  #number of decision variables increases

xsol = master.getAttr('x', x)    

print("Optimal value ="+str(master.ObjVal))
print("Final constraint matrix:")
print(np.transpose(np.matrix(A)))
print("Optimal LP solution "+str(xsol))    #optimal solution to column-generation LP

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
