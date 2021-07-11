from ortools.linear_solver import pywraplp
import numpy as np
from utils import is_in_area, midpoint
from DP_tools.maxFlow import getCost

INF=np.inf
# customers,tranCost,path,kitchensPicked,restaurantsPicked
baseCase=0,INF,[]

def estimateDemands(budget,locations,units,areas_demand,dist,radius,capacity,cpd=1):
    if budget<0:
        return baseCase
    restaurantsPicked=[]
    kitchensPicked=[]
    DemandRestaurant=[]
    # if sum(capacity kitchens) < sum(capacity restaurans), return INF
    capacity=0
    for i in range(len(units)):
        if (locations>>(2*i)) & 3 == 1:     #kitchen
            #if kitchen and restaurant capacity are different, make it [i][1]  
            capacity+=units[i]["capacity_kitchen"]
            # kitchensPicked[i]=True
            kitchensPicked.append(i)
        elif (locations>>(2*i)) & 3 == 2:   #Restaurant
            # capacity-=units[i]["capacity_restaurant"]
            # restaurantsPicked[i]=True
            restaurantsPicked.append(i)

    # demand less than ability to supply
    # if capacity<0:
    #     return baseCase

    #if no kitchens or no restaurants, the answer is invalid
    if (len(kitchensPicked)<1 or len(restaurantsPicked)<1):
        return 0,0,[]

    DemandArea=[areas_demand[i][1] for i in range(len(areas_demand))]
    DemandRestaurant=[units[i]["capacity_restaurant"] for i in restaurantsPicked]
    #RestInArea[A][R]=1 if restaurant R is in area A
    RestInArea=[[is_in_area(units[i]["position"],j[0],radius) for i in restaurantsPicked] for j in areas_demand]

    return getCost(units,kitchensPicked,restaurantsPicked,DemandRestaurant,dist,cpd)

    solver = pywraplp.Solver.CreateSolver('GLOP')
    #variables
    #   demandAR[A][R] is the demand taken for restaurant R to satisfy customers in area A
    demandAR=[[solver.NumVar(0, solver.infinity(), 'x') for _ in restaurantsPicked] for _ in DemandArea]
   
    # Constraint 0: for all A, sum_r(RestInArea) <= DemandArea.
    for a in range(len(areas_demand)):
        c=0
        for r in range(len(restaurantsPicked)):
            c+=RestInArea[a][r]*demandAR[a][r]
        solver.Add( c <= DemandArea[a])

    # Constraint 1: for all r, sum_a(RestInArea) <= DemandRestaurant.
    for r in range(len(restaurantsPicked)):
        c=0
        for a in range(len(areas_demand)):
            c+=RestInArea[a][r]*demandAR[a][r]
        solver.Add( c <= DemandRestaurant[r])
    
    # Constraint 2: sum(demands) <= Capacity
    c=0
    for a in range(len(areas_demand)):
        for r in range(len(restaurantsPicked)):
            c+=RestInArea[a][r]*demandAR[a][r]
    solver.Add(c<=capacity)
    # Objective function: sum_a(sum_r(demandAR)).
    z=0
    for a in range(len(areas_demand)):
        for r in range(len(restaurantsPicked)):
            z+=RestInArea[a][r]*demandAR[a][r]
    solver.Maximize(z)

    # Solve the system.
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        # print('Solution: Optimal')
        # print('Number of customers =', solver.Objective().Value())
        finalRestaurantDemand=[]
        for r in range(len(restaurantsPicked)):
            rest=0
            for a in range(len(areas_demand)):
                rest+=demandAR[a][r].solution_value()
            finalRestaurantDemand.append(rest)
        # out=[((locations>>(2*i)) &3) for i in range(len(units))]
        # print(kitchensPicked,restaurantsPicked,'Number of customers =',solver.Objective().Value(),finalRestaurantDemand,", Capacity=",capacity)
        transCost,path=getCost(units,kitchensPicked,restaurantsPicked,finalRestaurantDemand,dist)
        # return solver.Objective().Value(),transCost,path,kitchensPicked,restaurantsPicked,capacity
        # custR,transCostR,pathR
        # print(locations)
        return solver.Objective().Value(),transCost,path
    else:
        print('*'*100)
        return baseCase


