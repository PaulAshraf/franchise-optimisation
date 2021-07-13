from generate_data import generate_data
from utils import eucledian_distance, is_in_area, midpoint
from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt
from DP import callDP, plotDP, init
from genetics import geneticsAlgo
import time


def mip(units, areas_demand, budget=4e6, radius=10, cpd=1, r=5, timeLimit=1e9):
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
    # Constraints
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
    # 9: for each i,j: sum Ti,j <= R_j * M
    for i in range(n):
        c = 0
        for j in range(n):
            c += transport[i][j]
        solver.Add(c <= M * kitchen[i])
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
    solver.Maximize(customers * r - cost)
    solver.set_time_limit(timeLimit)
    solver.Solve()
    restaurant_solution = [int(v.solution_value()) for v in restaurant]
    kitchen_solution = [int(v.solution_value()) for v in kitchen]
    transport_solution = [[int(v.solution_value()) for v in arr] for arr in transport]
    area_flow_solution = [[int(v.solution_value()) for v in arr] for arr in area_flow]
    return restaurant_solution, kitchen_solution, transport_solution, area_flow_solution


def greedy(budget, r):
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
            'initial_restaurant'] + eucledian_distance(kitch_pos, unit['position']) * 365 * min(kitch_cap, unit[
            'capacity_restaurant'] - rest_cap_sofar[unit['initial_index']])) / unit['capacity_restaurant'])
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
            trans_cost = eucledian_distance(kitch_pos, rest_pos) * 365 * min(kitch_cap,
                                                                             rest_cap - rest_cap_sofar[rest_ind])
            if budget < trans_cost:
                transfer = int(budget // (eucledian_distance(kitch_pos, rest_pos) * 365))
            transport[kitch_ind][rest_ind] = transfer
            areas_demand_sofar[rest_area] += transfer
            rest_cap_sofar[rest_ind] += transfer
            kitch_cap -= transfer
            budget -= eucledian_distance(kitch_pos, rest_pos) * 365 * transfer
            used = True
        if not used:
            kitchen[kitch_ind] = 0
            budget += kitch_price
    return restaurant, kitchen, transport


def gui(solution):
    customers = 0
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    locations = 0
    cost = 0
    distCost = 0
    plt.figure('MIP')
    plt.title('Mixed Integer Programming')
    for i in range(len(solution[2])):
        for j in range(len(solution[2])):
            if solution[2][i][j] > 0:
                p1 = (units[i]['position'][0], units[i]['position'][1])
                p2 = (units[j]['position'][0], units[j]['position'][1])
                # Distance
                distCost += eucledian_distance(p1, p2) * 365 * solution[2][i][j]
                plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r--', alpha=.2)
                plt.text(midpoint(p1, p2)[0], midpoint(p1, p2)[1], solution[2][i][j], fontsize='small')
                customers += solution[2][i][j]
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=radius, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='${}$'.format(str(area[1])), s=200)
    for i, (x_, y_) in enumerate(zip(x, y)):
        if solution[0][i] == 1:
            locations = locations | 2 << (2 * i)
            cost += units[i]['rent'] + units[i]['initial_restaurant']
        if solution[1][i] == 1:
            locations = locations | 1 << (2 * i)
            cost += units[i]['rent'] + units[i]['initial_kitchen']
        plt.scatter([x_], [y_],
                    marker='${}$'.format(units[i]['capacity_restaurant']) if solution[0][i] == 1 else '${}$'.format(
                        units[i]['capacity_kitchen']) if solution[1][i] == 1 else 'x',
                    lw=.5,
                    s=200,
                    c='g' if solution[0][i] == 1 else 'r' if solution[1][i] == 1 else 'black')
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    return customers, cost, distCost


if __name__ == '__main__':
    areas = 6
    radius = 10
    units, demand = 0, 0
    maxCities = 12
    minCities = 12
    budget = int(4e6)
    r = 1e6
    cpd = 1
    while True:
        units, areas_demand = generate_data(
            areas=areas,
            radius=radius,
            demand_range=(1000, 1500),
            capacity_kitchen_range=(1000, 1200),
            capacity_restaurant_range=(300, 400),
            num_units_per_area=(1, 4),
            sparcity=-10)
        n = len(units)
        if n > maxCities or n < minCities:
            continue
        # break
        init(Units=units, Areas_demand=areas_demand, radii=radius)
        # budget = 500000*(n-1)
        print('*' * 100)
        print('total Number of cities =', n)
        print(' Solver ', ' time ', ' Cust ', ' Cost ')

        # solution = greedy(budget, r)
        # greedysolution = gui(solution)
        # print('Greedy', 0, greedysolution[0], round(greedysolution[1] + greedysolution[2], 2))

        # Meta-Heuresticcs
        t = time.time()
        geneticsSol = geneticsAlgo(budget, units, areas_demand, radius, maxTimes=n, CpD=1, family=n ** 2, r=r)
        t_GEN = (time.time() - t) * 1000
        cust_GEN = geneticsSol[0]
        cost_GEN = geneticsSol[1]
        plotDP(geneticsSol)
        print('Genetics', round(t_GEN, 2), cust_GEN, round(cost_GEN, 2))

        # DP
        t = time.time()
        DPsol = callDP(budget=budget,
                       usememory=True,  # To make the DP work
                       useBudgetApproximation=500000,  # budget in memory to the factor of factor*(budget//factor)
                       useCapacityApproximation=1)  # kitchenCapacity in memory to the factor of factor*(kitchenCapacity//factor)
        t_DP = (time.time() - t) * 1000
        cust_DP = DPsol[0]
        cost_DP = DPsol[1] + DPsol[2]
        plotDP(DPsol)
        print('   DP   ', round(t_DP, 2), cust_DP, round(cost_DP, 2))

        # MIP
        t = time.time()
        # maximum DP_time+1minute
        solution = mip(units, areas_demand, radius=radius, budget=budget, r=int(r), timeLimit=int(t_DP + 60 * 1000))
        t_MIP = (time.time() - t) * 1000
        mipsol = gui(solution)
        cust_MIP = mipsol[0]
        cost_MIP = mipsol[1] + mipsol[2]
        # print('MIP done, time = ',t_MIP,', customers=',mipsol[0],', cost = ',mipsol[1],', transCost = ',mipsol[2])
        print('  MIP   ', round(t_MIP, 2), cust_MIP, round(cost_MIP, 2))

        print('TransCost diff = ', (mipsol[2] - DPsol[2]) / DPsol[0])
        # t=time.time()
        # DPsol = callDP(budget=budget,Units=units,Areas_demand=areas_demand,radii=radius,usememory=False)
        # print('BF done, time = ',time.time()-t,', customers = ',DPsol[0],', cost = ',DPsol[1],', transCost = ',DPsol[2])
        # plotDP(DPsol)

        if cust_MIP != cust_DP:
            break
        break

    plt.show()
