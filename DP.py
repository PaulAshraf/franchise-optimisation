import copy
import numpy as np
import matplotlib.pyplot as plt
from generate_data import generate_data, plot_units
from utils import eucledian_distance, midpoint, is_in_area
from DP_tools.demandEstimator import estimateDemands
import bisect

units, areas_demand, radius = [], [], 0
# locations are 0,1,2 (not taken, restaurant, area)
locations = 0
INF = np.inf


def init(Units, Areas_demand, radii, cpd=1):
    global units, areas_demand, x, y, memo, radius, cur_locationBudgetMemo
    global counter, normalTime, useMemory, budgetApproximation, capacityApproximation, processed, restsDoNotExceedDemand
    radius = radii
    memo = {}
    cur_locationBudgetMemo = [[] for _ in range(len(units))]
    units, areas_demand = Units, Areas_demand
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    counter = 0
    makeDistances()


# calculate distance between an area center and location

dist = []


def getDist():
    global dist
    return dist


def makeDistances():
    global units, dist
    dist = []  # 2d matrix
    for i in range(len(units)):
        row = []
        for j in range(len(units)):
            row.append(0)
        dist.append(row)
    # dist=[[0]*len(locations)]*len(locations) #2d matrix
    for i in range(len(units)):
        for j in range(i, len(units)):
            # p_1=units[i]['position']
            # p_2=units[j]['position']
            out = eucledian_distance(units[i]['position'], units[j]['position'])
            # round to second decimal point
            out = round(out, 2)
            dist[i][j] = out
            dist[j][i] = out


memo = {}
cur_locationBudgetMemo = []
useMemory = True
budgetApproximation = 1
capacityApproximation = 1
cpd = 1
restsDoNotExceedDemand = False


# to do: sheel areas
def callDP(budget, usememory=True, useBudgetApproximation=1, useCapacityApproximation=1):
    global units, areas_demand, x, y, memo, radius, cur_locationBudgetMemo
    global counter, normalTime, useMemory, budgetApproximation, capacityApproximation, processed, restsDoNotExceedDemand
    capacityApproximation = useCapacityApproximation
    budgetApproximation = useBudgetApproximation
    useMemory = usememory
    # if sum(demand) restaurants in an area does not exceed it's demand, problem is much easier
    restsDoNotExceedDemand = True
    for a in areas_demand:
        areaDemand = 0
        for r in units:
            if is_in_area(r['position'], a[0], radius):
                areaDemand += r['capacity_restaurant']
        if areaDemand > a[1]:
            restsDoNotExceedDemand = False
            break
    # print('restsDoNotExceedDemand =',restsDoNotExceedDemand)
    finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity = dp(budget, 0, 0, 0)
    # print('Number of times calculated: ',processed)
    # print('DP Number of times Executed: ',processed,', Number of times not entered due to memory: ',counter)
    # print('sum = ',processed+counter)
    return finalCust, finalCost, finalTransCost, finalPath


counter = 0
processed = 0
normalTime = 0


# remaining budget, demands left in areas,
def dp(budget, curr_location, locations, kitchenCapacity):
    global units, areas_demand, radius, dist
    global counter, processed, normalTime, useMemory, budgetApproximation, restsDoNotExceedDemand
    if budget < 0:
        # finalCust,finalCost,finalTransCost,finalPath,finalLocation,finalCapacity
        return -INF, INF, INF, [], 0, -INF

    # no more budget left / all areas are taken / passed final location
    if budget == 0 or curr_location == len(units):
        # finalCust,finalCost,finalTransCost,finalPath,finalLocation,finalCapacity
        # return 0,0,0,[],0,kitchenCapacity
        cust, transCost, path = estimateDemands(
            budget,
            locations,
            units, areas_demand, dist, radius, cpd, restsDoNotExceedDemand)
        return cust, 0, transCost, path, locations, kitchenCapacity

    # print(curr_location,'{0:b}'.format(locations))
    # appFactor=3000
    # appFactor*(budget//appFactor),

    # approximate kitchen capacity to increase overlap
    indexCapacity = capacityApproximation * (kitchenCapacity // capacityApproximation)
    # approximate budget to get faster results
    indexBudget = budgetApproximation * (budget // budgetApproximation)
    index = (indexBudget, curr_location, indexCapacity)
    # have enough budget to buy the optimal sol
    if index in memo and memo[index][1] + memo[index][2] <= budget:
        counter += 1
        # if counter%1==0:
        #     print(counter)
        return memo[index]
    processed += 1
    # print('*'*100)
    # either take a place as kitchen/restaurant/not at all
    # do not take this location
    cust0, cost0, transCost0, path0, locations0, capacity0 = dp(
        budget,
        curr_location + 1,
        locations,
        kitchenCapacity)
    locations0 = locations | locations0
    # take this as kitchen
    # each location is in 2 bits
    chosenK = 1 << (2 * curr_location)
    custK, costK, transCostK, pathK, locationsK, capacityK = dp(
        budget - units[curr_location]['rent'] + units[curr_location]['initial_kitchen'],
        curr_location + 1,
        locations | chosenK,
        kitchenCapacity + units[curr_location]['capacity_kitchen'])
    # LAST WORKING VERSION#######################################################################
    costK += units[curr_location]['rent'] + units[curr_location]['initial_kitchen']
    locationsK = locationsK | locations | chosenK
    # take this as restaurant
    custR, costR, transCostR, pathR, locationsR, capacityR = dp(
        budget - units[curr_location]['rent'] + units[curr_location]['initial_restaurant'],
        curr_location + 1,
        locations | 2 << (2 * curr_location),
        kitchenCapacity - units[curr_location]['capacity_restaurant'])
    costR += units[curr_location]['rent'] + units[curr_location]['initial_restaurant']
    locationsR = locationsR | locations | (2 << (2 * curr_location))
    # custR,transCostR,pathR = estimateDemands(
    #     budget-units[curr_location]['rent'] + units[curr_location]['initial_restaurant'],
    #     locationsR,
    #     units,areas_demand,dist,radius,capacityR)
    # print()
    comparison = [
        (cust0, cost0, transCost0, path0, locations0, capacity0),
        (custK, costK, transCostK, pathK, locationsK, capacityK),
        (custR, costR, transCostR, pathR, locationsR, capacityR)
    ]
    # Care more about customers. get highest customers, then get minimum cost
    # print([((locationsR>>(2*i)) &3) for i in range(len(units))],custR,kitchenCapacity)
    counterVal = 0
    finalKitchenCapacity = INF
    finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity = -INF, INF, INF, [], 0, -INF
    # print([((locations>>(2*i)) &3) for i in range(len(units))],kitchenCapacity,budget)
    # for i,(cust,cost,transCost,path,location,cap) in enumerate(comparison):
    #     print(curr_location,i,[((location>>(2*i)) &3) for i in range(len(units))],cap,cust,cap-cust)
    for i, (cust, cost, transCost, path, location, cap) in enumerate(comparison):
        if budget >= cost + transCost:
            if cust > finalCust \
                    or (cust == finalCust and cost + transCost < finalCost + finalTransCost):
                # or (cust==finalCust and cap-cust>finalKitchenCapacity)\
                # or (cust==finalCust and cap-cust==finalKitchenCapacity and cost+transCost<finalCost+finalTransCost):
                finalCapacity = cap
                finalKitchenCapacity = cap - cust
                finalCust, finalCost, finalTransCost, finalPath, finalLocation = cust, cost, transCost, path, location
                counterVal = i
                # print(i,end=', ')
    if finalKitchenCapacity == INF:
        counterVal = 0
        finalCust, finalCost, finalTransCost, finalPath, finalLocation = -INF, INF, INF, [], 0
    # print('Chosen: ',counterVal)
    # finalLocation=locations|finalLocation
    # print([((finalLocation>>(2*i)) &3) for i in range(len(units))])
    if useMemory:
        memo[index] = finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity
    return finalCust, finalCost, finalTransCost, finalPath, finalLocation, finalCapacity
    # return memo[index]


units = []
areas_demand = []
x = []
y = []


def plotDP(DPsol):
    global units, areas_demand, x, y, radius, useMemory
    if len(DPsol) == 4:  # DP or BF
        if useMemory:
            plt.figure('DP')
            plt.title('Dynamic Programming')
        else:
            plt.figure('BF')
            plt.title('Brute Force')
        finalCust, finalCost, finalTransCost, path = DPsol
    else:
        plt.figure('Meta-Heurestics')
        plt.title('Genetics')
        finalCust, finalCost, path = DPsol
    kitchens, restaurants, _ = zip(*path)
    kitchens = set(list(kitchens))
    restaurants = set(list(restaurants))
    # print(kitchens,restaurants)
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=10, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='${}$'.format(str(area[1])), s=200)
    for i, (x_, y_) in enumerate(zip(x, y)):
        plt.scatter([x_], [y_],
                    marker='${capacity}$'.format(
                        capacity=units[i]['capacity_restaurant']) if i in restaurants else '${capacity}$'.format(
                        capacity=units[i]['capacity_kitchen']) if i in kitchens else '${}$'.format(i),
                    lw=.5,
                    s=200,
                    c='g' if i in restaurants else 'r' if i in kitchens else 'black')
    # print(path)
    # draw lines
    for kitchen, rest, flow in path:
        p1 = units[kitchen]['position']
        p2 = units[rest]['position']
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r--', alpha=.2)
        plt.text(midpoint(p1, p2)[0], midpoint(p1, p2)[1], flow, fontsize='small')
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    # plt.show()


if __name__ == '__main__':
    units, areas_demand = generate_data(
        areas=4,
        radius=5,
        demand_range=(1e8, 1e9),
        capacity_kitchen_range=(2000, 3000),
        capacity_restaurant_range=(300, 500),
        sparcity=5)

    DPsol = callDP(budget=100000000)
    plotDP(DPsol)
    # print(finalCust,finalCost,path,kitchens,restaurants)
