from DP_tools.demandEstimator import estimateDemands
from DP import getDist, INF
import random

units = 0
areas_demand = 0
dist, radius, cpd = [], 0, 0
budget = 0


def getSolution(r):
    global units, areas_demand, budget, radius, dist, cpd

    locations = 0
    cost = 0
    for i, unit in enumerate(units):
        probabilityGene = random.randint(0, 7)
        # if 0: do nothing, 1,2: take kitchen, 3+: take restaurant
        if 1 <= probabilityGene <= 2:
            # kitchen
            locations |= 1 << (2 * i)
            cost += units[i]['rent'] + units[i]['initial_kitchen']
        elif 3 <= probabilityGene:
            # restaurant
            locations |= 2 << (2 * i)
            cost += units[i]['rent'] + units[i]['initial_restaurant']
    cust, transCost, path = estimateDemands(
        budget,
        locations,
        units, areas_demand, dist, radius, cpd)
    return locations, cust, cost + transCost, path, cust * r - (cost + transCost)


def isValid(solution):
    global budget
    # cost < infinity
    return solution[2] <= budget


def getValidSolution(r):
    while True:
        solution = getSolution(r)
        if isValid(solution):
            return solution


def costGene(i, gene):
    global units
    cost = 0
    if gene == 1:
        cost = units[i]['rent'] + units[i]['initial_kitchen']
    elif gene == 2:
        cost = units[i]['rent'] + units[i]['initial_restaurant']
    return cost


def introduceOffspring(father, mother, r):
    global units, areas_demand, budget, radius, dist, cpd
    locations = 0
    cost = 0
    while True:
        locations = 0
        cost = 0
        for i, unit in enumerate(units):
            # fittness(father) is always more than fittness(mother)
            # probability of inheritence:
            # 1/6 mutation, 2/6 inherit from mother, 3/6 inherit from father
            probabilityInherit = random.randint(1, 6)
            # mutation 1/6
            if probabilityInherit == 1:
                probabilityGene = random.randint(0, 7)
                # if 0: do nothing, 1,2: take kitchen, 3+: take restaurant
                if 1 <= probabilityGene <= 2:
                    # kitchen
                    locations |= 1 << (2 * i)
                    cost += units[i]['rent'] + units[i]['initial_kitchen']
                elif 3 <= probabilityGene:
                    # restaurant
                    locations |= 2 << (2 * i)
                    cost += units[i]['rent'] + units[i]['initial_restaurant']
            # 2/6 inherit from mother
            elif 2 <= probabilityInherit <= 3:
                motherGene = (mother[0] >> (2 * i)) & 3
                locations |= motherGene << (2 * i)
                cost += costGene(i, motherGene)
            # 3/6 inherit from father
            else:
                fatherGene = (father[1] >> (2 * i)) & 3
                locations |= fatherGene << (2 * i)
                cost += costGene(i, fatherGene)
        cust, transCost, path = estimateDemands(
            budget,
            locations,
            units, areas_demand, dist, radius, cpd)
        if isValid((locations, cust, cost + transCost, path, cust * r - (cost + transCost))):
            break
    # fatherLocs=[((father[0]>>(2*i)) &3) for i in range(len(units))]
    # motherLocs=[((mother[0]>>(2*i)) &3) for i in range(len(units))]
    # child=[((locations>>(2*i)) &3) for i in range(len(units))]
    # print(father[1],mother[1],cust)
    # print(fatherLocs,'x',motherLocs,'->',child)
    return locations, cust, cost + transCost, path, cust * r - (cost + transCost)


def geneticsAlgo(Budget, Units, Areas_demand, radii, maxTimes=10, CpD=1, family=4, r=1e6):
    global units, areas_demand, dist, radius, cpd, budget

    units = Units
    areas_demand = Areas_demand
    budget = Budget
    radius = radii
    cpd = CpD
    dist = getDist()

    family = min(len(units), family)
    currFamily = []
    solution = 0, 0, INF, [], -1
    repeatedTimes = 0
    for i in range(family):
        currFamily.append(getValidSolution(r))
    while repeatedTimes != maxTimes:

        # [((currFamily[0]>>(2*i)) &3),currFamily[1] for i in range(len(units))]

        # introduce new blood to the family as a parent
        currFamily.append(getValidSolution(r))
        currFamily = sorted(currFamily, key=lambda solution: solution[4], reverse=True)

        offSprings = []
        # introduce offsprings (Give Birth)
        for i in range(len(currFamily)):
            for j in range(i + 1, len(currFamily)):
                # fittness(father) is always more than fittness(mother)
                offSprings.append(introduceOffspring(currFamily[i], currFamily[j], r))

        # sort population by fittness
        population = currFamily + offSprings
        population = sorted(population, key=lambda solution: solution[4], reverse=True)

        # highest fitness
        if population[0] == solution:
            repeatedTimes += 1
        else:
            repeatedTimes = 0
            solution = population[0]

        # Survive of the fittest
        currFamily = population[:family + 1]
    #       customers,cost        ,path
    return solution[1], solution[2], solution[3]
