from generate_data import generate_data
from utils import eucledian_distance, is_in_area
from ortools.linear_solver import pywraplp
from itertools import combinations

def mip(units, areas_demand, radius, budget, cpd, r):

    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Decision Variables

    n = len(units)
    
    restaurant = []
    kitchen = []
    restaurant_production = []
    kitchen_production = []

    for i, unit in enumerate(units):
        restaurant.append(solver.IntVar(0, 1, 'R' + str(i)))
        kitchen.append(solver.IntVar(0, 1, 'K' + str(i)))
        restaurant_production.append(solver.IntVar(0, unit["capacity_restaurant"], 'X' + str(i)))
        kitchen_production.append(solver.IntVar(0, unit["capacity_kitchen"], 'Y' + str(i)))

    transport = []

    for i in range(n):
        transport.append([])
        for j in range(n):
            if i != j:
                transport[i].append(solver.IntVar(0, 1, 'T' + str(i) + str(j)))
            else:
                transport[i].append(solver.IntVar(0, 0, 'T' + str(i) + str(j)))

    # Constraints

    for i in range(n):
        solver.Add(kitchen[i] + restaurant[i] <= 1)

    for area in areas_demand:
        c1 = 0
        for i in range(n):
            c1 += restaurant_production[i] * is_in_area(area[0], units[i]["position"], radius)
        solver.Add(c1 <= area[1])

    for i in range(n):
        for j in range(n):
            solver.Add(kitchen[i] + restaurant[j] >= 2 * transport[i][j])

    for i in range(n):
        c2 = 0
        for j in range(n):
            c2 += transport[i][j] * restaurant_production[j]
        solver.Add(c2 <= kitchen[i] * kitchen_production[i])

    for i in range(n):
        c3 = 0
        for j in range(n):
            c3 += transport[i][j] * kitchen[j]
        solver.Add(c3 <= restaurant[i])
        solver.Add(c3 >= restaurant[i])

    cost = 0
    for i in range(n):
        cost += kitchen[i] * (units[i]["rent"] + units[i]["initial_kitchen"])
        cost += restaurant[i] * (units[i]["rent"] + units[i]["initial_restaurant"])

    transport_cost = 0
    for i in range(n):
        for j in range(n):
            transport_cost += transport[i][j] * eucledian_distance(units[i]["position"], units[j]["position"]) * cpd

    cost += transport_cost * 365

    customers = 0
    for i in range(n):
        customers += restaurant[i] * restaurant_production[i]

    solver.Maximise(r * customers - (1-r) * cost)

    status = solver.Solve()
    print('OPTIMAL:', status == pywraplp.Solver.OPTIMAL)


if __name__ == '__main__':
    units, areas_demand = generate_data(areas=4, radius=5)
    mip(units, areas_demand, 5, 100000000000, 50, 0.9)







