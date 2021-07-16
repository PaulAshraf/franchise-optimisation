from ortools.linear_solver import pywraplp
import numpy as np
from utils import is_in_area
from DP_tools.maxFlow import getCost

INF = np.inf
baseCase = 0, INF, []
memoNotExceed = {}
memoResult = {}


def init():
    global memoNotExceed, memoResult
    memoNotExceed = {}
    memoResult = {}


def estimateDemands(budget, locations, units, areas_demand, dist, radius, cpd=1, restsDoNotExceedDemand=False):
    if budget < 0:
        return baseCase
    restaurantsPicked = []
    kitchensPicked = []
    # if sum(capacity kitchens) < sum(capacity restaurans), return INF
    capacity = 0
    indexRests = 0
    for i in range(len(units)):
        if (locations >> (2 * i)) & 3 == 1:  # kitchen
            # if kitchen and restaurant capacity are different, make it [i][1]
            capacity += units[i]['capacity_kitchen']
            kitchensPicked.append(i)
        elif (locations >> (2 * i)) & 3 == 2:  # Restaurant
            indexRests = indexRests | 2 << (2 * i)
            restaurantsPicked.append(i)
    if len(kitchensPicked) < 1 or len(restaurantsPicked) < 1:
        return 0, 0, []
    indexResult = (indexRests, capacity)
    if indexResult in memoResult:
        return getCost(units, kitchensPicked, restaurantsPicked, memoResult[indexResult], dist, cpd)
    DemandArea = [areas_demand[i][1] for i in range(len(areas_demand))]
    DemandRestaurant = [units[i]['capacity_restaurant'] for i in restaurantsPicked]
    # RestInArea[A][R]=1 if restaurant R is in area A
    RestInArea = [[is_in_area(units[i]['position'], j[0], radius) for i in restaurantsPicked] for j in areas_demand]
    # for optimization purposes
    # if chosen restaurants' demands inside an area do not exceed the area's demand:
    if indexRests in memoNotExceed:
        restsDoNotExceedDemand = memoNotExceed[indexRests]
    elif not restsDoNotExceedDemand:
        restsDoNotExceedDemand = True
        for a in areas_demand:
            areaDemand = 0
            for r in restaurantsPicked:
                if is_in_area(units[r]['position'], a[0], radius):
                    areaDemand += units[r]['capacity_restaurant']
            if areaDemand > a[1]:
                restsDoNotExceedDemand = False
                break
        memoNotExceed[indexRests] = restsDoNotExceedDemand
    if restsDoNotExceedDemand:
        return getCost(units, kitchensPicked, restaurantsPicked, DemandRestaurant, dist, cpd)
    solver = pywraplp.Solver.CreateSolver('GLOP')
    # variables
    # demandAR[A][R] is the demand taken for restaurant R to satisfy customers in area A
    demandAR = [[solver.NumVar(0, solver.infinity(), 'x') for _ in restaurantsPicked] for _ in DemandArea]
    # Constraint 0: for all A, sum_r(RestInArea) <= DemandArea.
    for a in range(len(areas_demand)):
        c = 0
        for r in range(len(restaurantsPicked)):
            c += RestInArea[a][r] * demandAR[a][r]
        solver.Add(c <= DemandArea[a])
    # Constraint 1: for all r, sum_a(RestInArea) <= DemandRestaurant.
    for r in range(len(restaurantsPicked)):
        c = 0
        for a in range(len(areas_demand)):
            c += RestInArea[a][r] * demandAR[a][r]
        solver.Add(c <= DemandRestaurant[r])
    # Constraint 2: sum(demands) <= Capacity
    c = 0
    for a in range(len(areas_demand)):
        for r in range(len(restaurantsPicked)):
            c += RestInArea[a][r] * demandAR[a][r]
    solver.Add(c <= capacity)
    # Objective function: sum_a(sum_r(demandAR)).
    z = 0
    for a in range(len(areas_demand)):
        for r in range(len(restaurantsPicked)):
            z += RestInArea[a][r] * demandAR[a][r]
    solver.Maximize(z)
    # Solve the system.
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        finalRestaurantDemand = []
        for r in range(len(restaurantsPicked)):
            rest = 0
            for a in range(len(areas_demand)):
                rest += demandAR[a][r].solution_value()
            finalRestaurantDemand.append(rest)
        memoResult[indexResult] = finalRestaurantDemand
        return getCost(units, kitchensPicked, restaurantsPicked, finalRestaurantDemand, dist, cpd)
    else:
        print('*' * 100)
        return baseCase
