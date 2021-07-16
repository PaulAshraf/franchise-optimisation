import numpy as np
from utils import eucledian_distance, is_in_area
from DP_tools.demandEstimator import estimateDemands, init

radius = 0
locations = 0
INF = np.inf
dist = []
memo = {}
cur_locationBudgetMemo = []
useMemory = True
budgetApproximation = 1
capacityApproximation = 1
cpd = 1
restsDoNotExceedDemand = False
counter = 0
processed = 0
normalTime = 0
units = []
areas_demand = []
budget = 0
r = 1e6


def DPSolver(Budget, Units, Areas_demand, radii, CpD, R):
    global memo, cur_locationBudgetMemo, counter, units, areas_demand, radius, cpd, budget, r
    units = Units
    areas_demand = Areas_demand
    budget = Budget
    radius = radii
    cpd = CpD
    memo = {}
    cur_locationBudgetMemo = [[] for _ in range(len(units))]
    counter = 0
    r = R
    makeDistances()
    init()
    return callDP()


def makeDistances():
    global units, dist
    dist = []
    for i in range(len(units)):
        row = []
        for j in range(len(units)):
            row.append(0)
        dist.append(row)
    for i in range(len(units)):
        for j in range(i, len(units)):
            out = eucledian_distance(units[i]['position'], units[j]['position'])
            out = round(out, 2)
            dist[i][j] = out
            dist[j][i] = out


def callDP(usememory=True, useBudgetApproximation=1000000, useCapacityApproximation=1):
    global budget, units, areas_demand, memo, radius, cur_locationBudgetMemo, counter, normalTime, useMemory, budgetApproximation, capacityApproximation, processed, restsDoNotExceedDemand
    capacityApproximation = useCapacityApproximation
    budgetApproximation = useBudgetApproximation
    useMemory = usememory
    restsDoNotExceedDemand = True
    for a in areas_demand:
        areaDemand = 0
        for r in units:
            if is_in_area(r['position'], a[0], radius):
                areaDemand += r['capacity_restaurant']
        if areaDemand > a[1]:
            restsDoNotExceedDemand = False
            break
    finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity = dp(budget, 0, 0, 0)
    return finalCust, finalCost, finalTransCost, finalPath


def dp(budget, curr_location, locations, kitchenCapacity):
    global units, areas_demand, radius, dist, counter, processed, normalTime, useMemory, budgetApproximation, restsDoNotExceedDemand, r
    if budget < 0:
        return -INF, INF, INF, [], 0, -INF
    if budget == 0 or curr_location == len(units):
        cust, transCost, path = estimateDemands(
            budget,
            locations,
            units, areas_demand, dist, radius, cpd, restsDoNotExceedDemand)
        return cust, 0, transCost, path, locations, kitchenCapacity
    indexCapacity = capacityApproximation * (kitchenCapacity // capacityApproximation)
    indexBudget = budgetApproximation * (budget // budgetApproximation)
    index = (indexBudget, curr_location, indexCapacity)
    if index in memo and memo[index][1] + memo[index][2] <= budget:
        counter += 1
        currLocations = locations | ((memo[index][4] << curr_location) >> curr_location)
        cost = memo[index][1]
        budget -= cost
        cust, transCost, path = estimateDemands(
            budget,
            currLocations,
            units, areas_demand, dist, radius, cpd, restsDoNotExceedDemand)
        return cust, cost, transCost, path, currLocations, 0
    processed += 1
    cust0, cost0, transCost0, path0, locations0, capacity0 = dp(
        budget,
        curr_location + 1,
        locations,
        kitchenCapacity)
    locations0 = locations | locations0
    chosenK = 1 << (2 * curr_location)
    custK, costK, transCostK, pathK, locationsK, capacityK = dp(
        budget - units[curr_location]['rent'] - units[curr_location]['initial_kitchen'],
        curr_location + 1,
        locations | chosenK,
        kitchenCapacity + units[curr_location]['capacity_kitchen'])
    costK += units[curr_location]['rent'] + units[curr_location]['initial_kitchen']
    locationsK = locationsK | locations | chosenK
    custR, costR, transCostR, pathR, locationsR, capacityR = dp(
        budget - units[curr_location]['rent'] - units[curr_location]['initial_restaurant'],
        curr_location + 1,
        locations | 2 << (2 * curr_location),
        kitchenCapacity - units[curr_location]['capacity_restaurant'])
    costR += units[curr_location]['rent'] + units[curr_location]['initial_restaurant']
    locationsR = locationsR | locations | (2 << (2 * curr_location))
    comparison = [
        (cust0, cost0, 2e9 if transCost0 > budget else transCost0, path0, locations0, capacity0),
        (custK, costK, 2e9 if transCostK > budget else transCostK, pathK, locationsK, capacityK),
        (custR, costR, 2e9 if transCostR > budget else transCostR, pathR, locationsR, capacityR)
    ]
    comparison = sorted(comparison, key=lambda solution: solution[0] * r - (solution[1] + solution[2]), reverse=True)
    sol = comparison[0]
    if sol[1] + sol[2] > budget:
        return 0, 2e9, 2e9, [], locations, 0
    if useMemory:
        memo[index] = comparison[0]
    return comparison[0]
