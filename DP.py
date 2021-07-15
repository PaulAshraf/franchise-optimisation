import numpy as np
from utils import eucledian_distance, is_in_area
from DP_tools.demandEstimator import estimateDemands

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


def DPSolver(Budget, Units, Areas_demand, radii, CpD=1, r=1e6):
    global memo, cur_locationBudgetMemo, counter, units, areas_demand, radius, cpd, budget
    units = Units
    areas_demand = Areas_demand
    budget = Budget
    radius = radii
    cpd = CpD
    memo = {}
    cur_locationBudgetMemo = [[] for _ in range(len(units))]
    counter = 0
    makeDistances()
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


def callDP(usememory=True, useBudgetApproximation=500000, useCapacityApproximation=1):
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
    global units, areas_demand, radius, dist, counter, processed, normalTime, useMemory, budgetApproximation, restsDoNotExceedDemand
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
        return memo[index]
    processed += 1
    cust0, cost0, transCost0, path0, locations0, capacity0 = dp(
        budget,
        curr_location + 1,
        locations,
        kitchenCapacity)
    locations0 = locations | locations0
    chosenK = 1 << (2 * curr_location)
    custK, costK, transCostK, pathK, locationsK, capacityK = dp(
        budget - units[curr_location]['rent'] + units[curr_location]['initial_kitchen'],
        curr_location + 1,
        locations | chosenK,
        kitchenCapacity + units[curr_location]['capacity_kitchen'])
    costK += units[curr_location]['rent'] + units[curr_location]['initial_kitchen']
    locationsK = locationsK | locations | chosenK
    custR, costR, transCostR, pathR, locationsR, capacityR = dp(
        budget - units[curr_location]['rent'] + units[curr_location]['initial_restaurant'],
        curr_location + 1,
        locations | 2 << (2 * curr_location),
        kitchenCapacity - units[curr_location]['capacity_restaurant'])
    costR += units[curr_location]['rent'] + units[curr_location]['initial_restaurant']
    locationsR = locationsR | locations | (2 << (2 * curr_location))
    comparison = [
        (cust0, cost0, transCost0, path0, locations0, capacity0),
        (custK, costK, transCostK, pathK, locationsK, capacityK),
        (custR, costR, transCostR, pathR, locationsR, capacityR)
    ]
    counterVal = 0
    finalKitchenCapacity = INF
    finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity = -INF, INF, INF, [], 0, -INF
    for i, (cust, cost, transCost, path, location, cap) in enumerate(comparison):
        if budget >= cost + transCost:
            if cust > finalCust or (cust == finalCust and cost + transCost < finalCost + finalTransCost):
                finalCapacity = cap
                finalKitchenCapacity = cap - cust
                finalCust, finalCost, finalTransCost, finalPath, finalLocation = cust, cost, transCost, path, location
                counterVal = i
    if finalKitchenCapacity == INF:
        counterVal = 0
        finalCust, finalCost, finalTransCost, finalPath, finalLocation = -INF, INF, INF, [], 0
    if useMemory:
        memo[index] = finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity
    return finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity
