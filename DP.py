import copy
import numpy as np
from generate_data import generate_data
from utils import eucledian_distance
import matplotlib.pyplot as plt


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
            out = eucledian_distance(units[i]["position"], units[j]["position"])
            out = round(out, 2)
            dist[i][j] = out
            dist[j][i] = out


def transport(locations, kitchens, curr_kitchen, restaurants, restaurantsTaken, remainingKitchenCapacity):
    global units, dist
    if curr_kitchen == len(kitchens) and (restaurantsTaken != ((1 << len(restaurants)) - 1)):
        return INF, []
    if remainingKitchenCapacity == INF:
        return transport(locations, kitchens, curr_kitchen, restaurants, restaurantsTaken,
                         units[kitchens[curr_kitchen]]["capacity_kitchen"])
    if remainingKitchenCapacity < 0:
        return INF, []
    if restaurantsTaken == ((1 << len(restaurants)) - 1):
        return 0, [[] for _ in range(len(kitchens))]
    index = (locations, restaurantsTaken)
    if index in transportMemo:
        return transportMemo[index]
    minSoFar = INF
    optimalPath = []
    for i in range(len(restaurants)):
        if (restaurantsTaken >> i) & 1 == 0 and remainingKitchenCapacity - units[restaurants[i]][
            "capacity_restaurant"] >= 0:
            t1, path = transport(locations, kitchens, curr_kitchen, restaurants, restaurantsTaken | (1 << i),
                                 remainingKitchenCapacity - units[restaurants[i]]["capacity_restaurant"])
            t1 += dist[kitchens[curr_kitchen]][restaurants[i]]
            if t1 < INF and t1 < minSoFar:
                minSoFar = t1
                optimalPath = copy.deepcopy(path)
                optimalPath[curr_kitchen].append(restaurants[i])
    t2, path2 = transport(locations, kitchens, curr_kitchen + 1, restaurants, restaurantsTaken, INF)
    if t2 < INF and t2 < minSoFar:
        minSoFar = t2
        optimalPath = copy.deepcopy(path2)
    transportMemo[index] = minSoFar, optimalPath
    return transportMemo[index]


def tCost(budget, locations):
    global units
    if budget < 0:
        return INF, [], [], []
    index = (budget, locations)
    restaurantsPicked = []
    kitchensPicked = []
    capacity = 0
    for i in range(len(units)):
        if (locations >> (2 * i)) & 3 == 1:
            capacity += units[i]["capacity_kitchen"]
            kitchensPicked.append(i)
        elif (locations >> (2 * i)) & 3 == 2:
            capacity -= units[i]["capacity_restaurant"]
            restaurantsPicked.append(i)
    if capacity < 0:
        tCostMemo[index] = INF, [], [], []
        return tCostMemo[index]
    if len(kitchensPicked) < 1 or len(restaurantsPicked) < 1:
        tCostMemo[index] = INF, [], [], []
        return tCostMemo[index]
    tranCost, path = transport(locations, kitchensPicked, 0, restaurantsPicked, 0, INF)
    if tranCost > budget:
        tCostMemo[index] = INF, [], [], []
    else:
        tCostMemo[index] = tranCost, path, kitchensPicked, restaurantsPicked
    return tCostMemo[index]


def estimateCustomers(locations, areas):
    global units, areas_demand
    if locations in customerMemo:
        return customerMemo[locations]
    customers = 0
    for i in range(len(areas)):
        customers += min(areas_demand[i][1], areas[i])
    customerMemo[locations] = customers
    return customers


def callDP(budget):
    global units, areas_demand, x, y
    x = [unit["position"][0] for unit in units]
    y = [unit["position"][1] for unit in units]
    return dp(budget, [0] * len(areas_demand), 0, 0)


def dp(budget, areas, locations, curr_location):
    global units, areas_demand
    allAreasTaken = [False] * len(areas_demand)
    for i in range(len(areas)):
        if areas[i] >= areas_demand[i][1]:
            allAreasTaken[i] = True
    if budget <= 0 or allAreasTaken == [True] * len(areas_demand) or curr_location == len(units):
        cost, path, kitchensPicked, restaurantsPicked = tCost(budget, locations)
        return estimateCustomers(locations, areas), cost, path, kitchensPicked, restaurantsPicked
    index = locations
    if index in memo:
        return memo[index]
    cust0, cost0, path0, kitchensPicked0, restaurantsPicked0 = dp(budget, areas, locations, curr_location + 1)
    custK, costK, pathK, kitchensPickedK, restaurantsPickedK = dp(budget - units[curr_location]["initial_kitchen"],
                                                                  areas, locations | 1 << (2 * curr_location),
                                                                  curr_location + 1)
    areaBelonging = units[curr_location]["area"]
    if areas[areaBelonging] < areas_demand[areaBelonging][1]:
        areasCopy = copy.deepcopy(areas)
        areasCopy[areaBelonging] += units[curr_location]["capacity_restaurant"]
        custR, costR, pathR, kitchensPickedR, restaurantsPickedR = dp(
            budget - units[curr_location]["initial_restaurant"], areasCopy, locations | 2 << (2 * curr_location),
            curr_location + 1)
    else:
        custR, costR, pathR, kitchensPickedR, restaurantsPickedR = 0, INF, [], [], []
    comparison = [
        (cust0, cost0, path0, kitchensPicked0, restaurantsPicked0),
        (custK, costK + units[curr_location]["initial_kitchen"], pathK, kitchensPickedK, restaurantsPickedK),
        (custR, costR + units[curr_location]["initial_restaurant"], pathR, kitchensPickedR, restaurantsPickedR)]
    finalCust, finalCost, finalPath, kitchensPicked, restaurantsPicked = 0, INF, [], [], []
    for cust, cost, path_, kitchens, restaurants in comparison:
        if cost < INF:
            if cust > finalCust or (cust == finalCust and cost < finalCost):
                finalCust = cust
                finalCost = cost
                finalPath = path_
                kitchensPicked = kitchens
                restaurantsPicked = restaurants
    memo[index] = finalCust, finalCost, finalPath, kitchensPicked, restaurantsPicked
    return finalCust, finalCost, finalPath, kitchensPicked, restaurantsPicked


def plotDP(DPsol):
    global units, areas_demand, x, y
    finalCust, finalCost, path, kitchens, restaurants = DPsol
    plt.figure("DP")
    plt.title("Dynamic Programming")
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=5, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='+')
    for i, (x_, y_) in enumerate(zip(x, y)):
        plt.scatter([x_], [y_],
                    marker="${}$".format(units[i]["capacity_restaurant"]) if i in restaurants else "${}$".format(
                        units[i]["capacity_kitchen"]) if i in kitchens else "$X$",
                    lw=.5,
                    s=75,
                    c="g" if i in restaurants else "r" if i in kitchens else "black")
    plt.grid(color='gray', ls='--', lw=0.25)
    for i in range(len(path)):
        kitchen = kitchens[i]
        for j in range(len(path[i])):
            rest = path[i][j]
            plt.plot([units[kitchen]["position"][0], units[rest]["position"][0]],
                     [units[kitchen]["position"][1], units[rest]["position"][1]], 'r-', alpha=.25)
    plt.show()


if __name__ == '__main__':
    locations = 0
    INF = np.inf
    transportMemo = {}
    tCostMemo = {}
    dist = []
    customerMemo = {}
    memo = {}
    x = []
    y = []
    units, areas_demand = generate_data(
        areas=4,
        radius=5,
        demand_range=(1e8, 1e9),
        capacity_kitchen_range=(2000, 3000),
        capacity_restaurant_range=(300, 500),
        sparcity=5)
    makeDistances()
    DPsol = callDP(budget=100000000)
    plotDP(DPsol)
