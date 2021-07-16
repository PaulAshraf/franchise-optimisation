from utils import eucledian_distance, is_in_area
from ortools.linear_solver import pywraplp
from genetics import genetics
from DP import DPSolver


def MIP(units, areas_demand, budget, radius, cpd, r):
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
            if is_in_area(areas_demand[a][0], units[i]['position'], radius) == 1:
                area_flow[i].append(solver.IntVar(0, solver.infinity(), 'Y' + str(i) + str(a)))
            else:
                area_flow[i].append(solver.IntVar(0, 0, 'Y' + str(i) + str(a)))
    # 1: Zij <--> Tij
    for i in range(n):
        for j in range(n):
            solver.Add(transport[i][j] <= M * z[i][j])
            solver.Add(z[i][j] <= M * transport[i][j])
    # 2: Zij <--> Tij
    for i in range(n):
        solver.Add(kitchen[i] + restaurant[i] <= 1)
    # 3: for each a: sum_r Yr,a <= d_a
    for a in range(num_areas):
        c = 0
        for i in range(n):
            c += area_flow[i][a]
        solver.Add(c <= areas_demand[a][1])
    # 4: for each j (restaurant): sum_a (sum all areas) Yj,a == sum_i (sum all kitchens) Tij
    for j in range(n):
        c1 = 0
        c2 = 0
        for a in range(num_areas):
            c1 += area_flow[j][a]
        for i in range(n):
            c2 += transport[i][j]
        solver.Add(c1 == c2)
    # 5:
    for a in range(num_areas):
        for i in range(n):
            solver.Add(area_flow[i][a] <= restaurant[i] * units[i]['capacity_restaurant'])
    # 6: for each i: sum_j Ti,j <= capK_i
    for i in range(n):
        c = 0
        for j in range(n):
            c += transport[i][j]
        solver.Add(c <= units[i]['capacity_kitchen'])
    # 7: for each j: sum_i Ti,j <= capR_j
    for j in range(n):
        c = 0
        for i in range(n):
            c += transport[i][j]
        solver.Add(c <= units[j]['capacity_restaurant'])
    # 8: for each i:  sum_j Ti,j <= K_i * M
    for i in range(n):
        c = 0
        for j in range(n):
            c += transport[i][j]
        solver.Add(c <= M * kitchen[i])
        solver.Add(c >= kitchen[i])
    # 9: for each i,j: sum Ti,j <= R_j * M
    for j in range(n):
        c = 0
        for i in range(n):
            c += transport[i][j]
        solver.Add(c <= M * restaurant[j])
    # 10:
    cost = 0
    for i in range(n):
        cost += kitchen[i] * (units[i]['rent'] + units[i]['initial_kitchen'])
        cost += restaurant[i] * (units[i]['rent'] + units[i]['initial_restaurant'])
    # 11:
    transport_cost = 0
    for i in range(n):
        for j in range(n):
            transport_cost += transport[i][j] * eucledian_distance(units[i]['position'], units[j]['position']) * cpd
    cost += transport_cost * 365
    solver.Add(cost <= budget)
    customers = 0
    for a in range(num_areas):
        for i in range(n):
            customers += area_flow[i][a] * 365
    solver.set_time_limit(60000)
    solver.Maximize(customers * (1 - 1.0 / r) - cost * 1.0 / r)
    solver.Solve()
    restaurant_solution = [int(v.solution_value()) for v in restaurant]
    kitchen_solution = [int(v.solution_value()) for v in kitchen]
    transport_solution = [[int(v.solution_value()) for v in arr] for arr in transport]
    area_flow_solution = [[int(v.solution_value()) for v in arr] for arr in area_flow]
    return restaurant_solution, kitchen_solution, transport_solution, area_flow_solution


def Greedy(units, areas_demand, budget, radius, cpd, r):
    r = r / float(1e4)
    n = len(units)
    areas = len(areas_demand)
    units_kitchen = sorted(units, key=lambda unit: (unit['rent'] + unit['initial_kitchen']) / unit['capacity_kitchen'])
    kitchen = [0 for _ in units]
    restaurant = [0 for _ in units]
    rest_cap_sofar = [0 for _ in units]
    transport = [[0 for _ in units] for _ in units]
    areas_demand_sofar = [0 for _ in range(areas)]
    for i in range(n):
        kitch_ind = units_kitchen[i]['initial_index']
        kitch_cap = units_kitchen[i]['capacity_kitchen']
        kitch_price = units_kitchen[i]['rent'] + units_kitchen[i]['initial_kitchen']
        kitch_pos = units_kitchen[i]['position']
        if kitch_price > budget or kitchen[kitch_ind] or restaurant[kitch_ind]:
            continue
        budget -= kitch_price
        kitchen[kitch_ind] = 1
        used = False
        units_restaurant = sorted(units, key=lambda unit: (unit['rent'] + unit[
            'initial_restaurant'] + eucledian_distance(kitch_pos, unit['position']) * (1.0 / r) * 365 * cpd * min(kitch_cap, unit[
            'capacity_restaurant'] - rest_cap_sofar[unit['initial_index']])) / unit['capacity_restaurant'] * (1 - 1.0 / r))
        for j in range(n):
            rest_ind = units_restaurant[j]['initial_index']
            rest_cap = units_restaurant[j]['capacity_restaurant']
            rest_price = units_restaurant[j]['rent'] + units_restaurant[j]['initial_restaurant']
            rest_area = units_restaurant[j]['area']
            rest_pos = units_restaurant[j]['position']
            if rest_price > budget or kitch_cap == 0 or rest_cap == rest_cap_sofar[rest_ind] \
                    or kitchen[rest_ind] or areas_demand_sofar[rest_area] + \
                    min(kitch_cap, rest_cap - rest_cap_sofar[rest_ind]) > areas_demand[rest_area][1]:
                continue
            if restaurant[rest_ind] == 0:
                budget -= rest_price
                restaurant[rest_ind] = 1
            transfer = min(kitch_cap, rest_cap - rest_cap_sofar[rest_ind])
            trans_cost = eucledian_distance(kitch_pos, rest_pos) * 365 * cpd * min(kitch_cap,
                                                                                   rest_cap - rest_cap_sofar[rest_ind])
            if budget < trans_cost:
                transfer = int(budget // (eucledian_distance(kitch_pos, rest_pos) * 365 * cpd))
            transport[kitch_ind][rest_ind] = transfer
            areas_demand_sofar[rest_area] += transfer
            rest_cap_sofar[rest_ind] += transfer
            kitch_cap -= transfer
            budget -= eucledian_distance(kitch_pos, rest_pos) * 365 * cpd * transfer
            used = True
        if not used:
            kitchen[kitch_ind] = 0
            budget += kitch_price
    return restaurant, kitchen, transport


def Genetics(units, areas_demand, budget, radius, cpd, r):
    n = len(units)
    return genetics(budget, units, areas_demand, radius, n, cpd, n ** 2, r)


def DP(units, areas_demand, budget, radius, cpd, r):
    return DPSolver(budget, units, areas_demand, radius, cpd, r)
