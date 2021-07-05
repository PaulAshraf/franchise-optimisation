from generate_data import generate_data
from utils import eucledian_distance, is_in_area, midpoint
from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
import math


def mip(units, areas_demand, budget=4e6, radius=10, cpd=1, r=5):
    
    M = int(1e5)
    n = len(units)
    num_areas = len(areas_demand)
    
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    restaurant = []
    kitchen = []
    for i in range(n):
        restaurant.append(solver.IntVar(0, 1, 'R' + str(i)))
        kitchen.append(solver.IntVar(0, 1, 'K' + str(i)))
    
    transport = []
    z = []
    for i in range(n):
        transport.append([])
        z.append([])
        for j in range(n):
            if i != j:
                transport[i].append(solver.IntVar(0, solver.infinity(), 'T' + str(i) + str(j)))
                z[i].append(solver.IntVar(0, solver.infinity(), 'Z' + str(i) + str(j)))
            else:
                transport[i].append(solver.IntVar(0, 0, 'T' + str(i) + str(j)))
                z[i].append(solver.IntVar(0, 0, 'Z' + str(i) + str(j)))
    
    area_flow = []
    for i in range(n):
        area_flow.append([])
        for a in range(num_areas):
            if is_in_area(areas_demand[a][0], units[i]["position"], radius) == 1:
                area_flow[i].append(solver.IntVar(0, solver.infinity(), 'Y' + str(i) + str(a)))
            else:
                area_flow[i].append(solver.IntVar(0, 0, 'Y' + str(i) + str(a)))
    
    # Constraints

    # Zij <--> Tij
    for i in range(n):
        for j in range(n): 
            solver.Add(transport[i][j] <= M * z[i][j])
            solver.Add(z[i][j] <= M * transport[i][j])
    
    for i in range(n):
        solver.Add(kitchen[i] + restaurant[i] <= 1)
    
    # for each a: sum_r Yr,a <= d_a
    for a in range(num_areas):
        c = 0
        for i in range(n):
            c += area_flow[i][a]
        solver.Add(c <= areas_demand[a][1])

    # for each j (restaurant): sum_a (sum all areas) Yj,a == sum_i (sum all kitchens) Tij
    for j in range(n):
        c1 = 0
        c2 = 0
        for a in range(num_areas):
            c1 += area_flow[j][a]
        for i in range(n):
            c2 += transport[i][j]
        solver.Add(c1 == c2)

    for a in range(num_areas):
        for i in range(n):
            solver.Add(area_flow[i][a] <= restaurant[i] * units[i]["capacity_restaurant"])

    # for each i: sum_j Ti,j <= capK_i
    for i in range(n):
        c = 0
        for j in range(n):
            c += transport[i][j]
        solver.Add(c <= units[i]["capacity_kitchen"])

    # for each j: sum_i Ti,j <= capR_j
    for j in range(n):
        c = 0
        for i in range(n):
            c += transport[i][j]
        solver.Add(c <= units[j]["capacity_restaurant"])

    # for each i:  sum_j Ti,j <= K_i * M
    # for each i,j: sum Ti,j <= R_j * M
    for i in range(n):
        c = 0
        for j in range(n):
            c += transport[i][j]
        solver.Add(c <= M * kitchen[i])
        solver.Add(c <= M * restaurant[j])
    
    cost = 0
    for i in range(n):
        cost += kitchen[i] * (units[i]["rent"] + units[i]["initial_kitchen"])
        cost += restaurant[i] * (units[i]["rent"] + units[i]["initial_restaurant"])
    
    transport_cost = 0
    for i in range(n):
        for j in range(n):
            transport_cost += z[i][j] * eucledian_distance(units[i]["position"], units[j]["position"]) * cpd
    
    cost += transport_cost * 365
    solver.Add(cost <= budget)
    
    customers = 0
    for a in range(num_areas):
        for i in range(n):
            customers += area_flow[i][a] * 365
    
    solver.Maximize(customers * r - cost)
    # solver.Maximize(customers)
    status = solver.Solve()


    
    restaurant_solution = [int(v.solution_value()) for v in restaurant]
    kitchen_solution = [int(v.solution_value()) for v in kitchen]
    transport_solution = [[int(v.solution_value()) for v in arr] for arr in transport]
    area_flow_solution = [[int(v.solution_value()) for v in arr] for arr in area_flow]
    return restaurant_solution, kitchen_solution, transport_solution, area_flow_solution


def greedy(budget=4e6):
    units_kitchen = sorted(units, key=lambda unit: unit["rent"] + unit["initial_kitchen"])
    units_restaurant = sorted(units, key=lambda unit: unit["rent"] + unit["initial_restaurant"])
    kitchen = [0 for _ in units]
    restaurant = [0 for _ in units]
    transport = [[0 for _ in units] for _ in units]
    areas_demand_sofar = [0 for _ in range(areas)]
    for i in range(n):
        kitch_ind = units_kitchen[i]['initial_index']
        kitch_cap = units_kitchen[i]['capacity_kitchen']
        kitch_price = units[i]["rent"] + units[i]["initial_kitchen"]
        if kitch_price > budget or kitchen[kitch_ind] or restaurant[kitch_ind]:
            continue
        budget -= kitch_price
        kitchen[kitch_ind] = 1
        used = False
        for j in range(n):
            rest_ind = units_restaurant[j]['initial_index']
            rest_cap = units_restaurant[j]['capacity_restaurant']
            rest_price = units[j]["rent"] + units[j]["initial_restaurant"]
            rest_area = units_restaurant[j]['area']
            if rest_price > budget or kitch_cap < rest_cap or kitchen[rest_ind] or restaurant[rest_ind] or \
                    areas_demand_sofar[rest_area] + rest_cap > areas_demand[rest_area][1]:
                continue
            budget -= rest_price
            kitch_cap -= rest_cap
            restaurant[rest_ind] = 1
            transport[kitch_ind][rest_ind] = 1
            areas_demand_sofar[rest_area] += rest_cap
            used = True
        if not used:
            kitchen[kitch_ind] = 0
    return restaurant, kitchen, transport


def calc_cost(kitchen, restaurant, transport, cpd=1):
    cost = 0
    n = len(units)
    for i in range(n):
        if kitchen[i] == 1:
            cost += units[i]["initial_kitchen"] + units[i]["rent"]
        if restaurant[i] == 1:
            cost += units[i]["initial_restaurant"] + units[i]["rent"]
    transport_cost = 0
    for i in range(n):
        for j in range(n):
            if transport[i][j] == 1:
                transport_cost += eucledian_distance(units[i]["position"], units[j]["position"]) * cpd
    cost += transport_cost * 365
    return cost


def gui(solution):
    x = [unit["position"][0] for unit in units]
    y = [unit["position"][1] for unit in units]
    
    for i in range(len(solution[2])):
        for j in range(len(solution[2])):
            if solution[2][i][j] > 0:
                p1 = (units[i]["position"][0], units[i]["position"][1])
                p2 = (units[j]["position"][0], units[j]["position"][1])
                
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r--', alpha=.2)
                plt.text(midpoint(p1, p2)[0], midpoint(p1, p2)[1], solution[2][i][j], fontsize='small')
    
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=10, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker="${}$".format(str(area[1])), s=200)
    for i, (x_, y_) in enumerate(zip(x, y)):
        ###
        # val = 0
        # for a in range(len(areas_demand)):
        #     val += solution[3][i][a]
        ###
        plt.scatter([x_], [y_],
                    marker="${}$".format(units[i]["capacity_restaurant"]) if solution[0][i] == 1 else "${}$".format(
                        units[i]["capacity_kitchen"]) if solution[1][i] == 1 else "x",
                    lw=.5,
                    s=200,
                    c="g" if solution[0][i] == 1 else "r" if solution[1][i] == 1 else "black")
    
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()


if __name__ == '__main__':
    areas = 6
    radius = 10
    units, areas_demand = generate_data(
        areas=areas,
        radius=radius,
        demand_range=(1000, 1500),
        capacity_kitchen_range=(1000, 1200),
        capacity_restaurant_range=(300, 400),
        num_units_per_area=(2, 3),
        sparcity=-10)
    n = len(units)
    solution = mip(units, areas_demand, radius=radius, budget=int(1e7), r=10)
    print(solution[0])
    print(solution[1])
    print(solution[2])
    print(solution[3])
    gui(solution)
    # solution = greedy()
    # gui(solution)
