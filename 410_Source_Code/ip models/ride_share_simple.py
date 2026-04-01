from gurobipy import *
import time as tm
import numpy as np
from scipy.spatial import distance
import matplotlib.pyplot as plt
import math

depot_coordinate = (0, 0)

################## Generate random nodes ####################
number_of_points = 20
coordinates = np.random.randint(-100, 100, size=(number_of_points, 2))
points = range(coordinates.shape[0])


################## Plot the points #######################
plt.figure()
plt.scatter(coordinates[:, 0], coordinates[:, 1])
plt.scatter([depot_coordinate[0]], [depot_coordinate[1]], color='red')
plt.show()
################## Generate set cover instance #######################

A = []
costs = []
route_locations = []

for i in points:
    costs.append(distance.euclidean(depot_coordinate, coordinates[i]) 
                 + distance.euclidean(coordinates[i], depot_coordinate))
    route_locations.append([i])
    A.append([0]*number_of_points)
    A[-1][i] = 1

    for j in points:
        if i != j:
            route_locations.append([i, j])
            A.append([0]*number_of_points)
            A[-1][i] = 1
            A[-1][j] = 1
            two_destination_cost = (distance.euclidean(depot_coordinate, coordinates[i]) 
                                    + distance.euclidean(coordinates[i], coordinates[j]) 
                                    + distance.euclidean(coordinates[j], depot_coordinate))
            costs.append(two_destination_cost)
        for k in points:
            if i != j and j != k and i != k:
                route_locations.append([i, j, k])
                A.append([0]*number_of_points)
                A[-1][i] = 1
                A[-1][j] = 1
                A[-1][k] = 1
                three_destination_cost = (distance.euclidean(depot_coordinate, coordinates[i]) 
                                          + distance.euclidean(coordinates[i], coordinates[j]) 
                                          + distance.euclidean(coordinates[j], coordinates[k]) 
                                          + distance.euclidean(coordinates[k], depot_coordinate))
                costs.append(three_destination_cost)

routes = range(len(A))
################## Integer Program model ####################

IPmod = Model("set cover")
x = IPmod.addVars(routes, vtype=GRB.BINARY, name="x")
IPmod.setObjective(quicksum(costs[r]*x[r] for r in routes), GRB.MINIMIZE)
for p in points:
    IPmod.addConstr(quicksum(A[r][p]*x[r] for r in routes) >= 1, str(p))
IPmod.optimize()
xint=[]
xint= IPmod.getAttr('x', x)
for r in routes:
    if (xint[r]>0):
        print(r)

################## Plot the solution #######################
plt.figure()
plt.scatter(coordinates[:, 0], coordinates[:, 1])
plt.scatter([depot_coordinate[0]], [depot_coordinate[1]], color='red')
for r in routes:
    if xint[r] > 0:
        route = route_locations[r]
        for i in range(len(route)-1):
            plt.plot([coordinates[route[i], 0], coordinates[route[i+1], 0]], [coordinates[route[i], 1], coordinates[route[i+1], 1]])
        plt.plot([coordinates[route[-1], 0], depot_coordinate[0]], [coordinates[route[-1], 1], depot_coordinate[1]])
        plt.plot([depot_coordinate[0], coordinates[route[0], 0]], [depot_coordinate[1], coordinates[route[0], 1]])
plt.show()
