from generate_data import generate_data
from utils import eucledian_distance, is_in_area
from ortools.linear_solver import pywraplp
import matplotlib.pyplot as plt

def mip_simple(units, areas_demand, radius, budget, cpd, r):

    solver = pywraplp.Solver.CreateSolver('SCIP')

    # Decision Variables

    n = len(units)
    
    restaurant = []
    kitchen = []

    for i in range(n):
        restaurant.append(solver.IntVar(0, 1, 'R' + str(i)))
        kitchen.append(solver.IntVar(0, 1, 'K' + str(i)))

    transport = []

    for i in range(n):
        transport.append([])
        for j in range(n):
            if i != j:
                transport[i].append(solver.IntVar(0, 1, 'T' + str(i) + str(j)))
            else:
                transport[i].append(solver.IntVar(0, 0, 'T' + str(i) + str(j)))

    # Constraints

    for area in areas_demand:
        c1 = 0
        for i in range(n):
            c1 += restaurant[i] * units[i]["capacity_restaurant"] * is_in_area(area[0], units[i]["position"], radius)
        # 2
        solver.Add(c1 <= area[1])

    for i in range(n):
        # 1
        solver.Add(kitchen[i] + restaurant[i] <= 1)
        sum1 = 0
        sum2 = 0
        for j in range(n):
            sum1 += transport[i][j] + transport[j][i]
            sum2 += transport[i][j] * units[j]["capacity_restaurant"]
            # 3
            solver.Add(transport[i][j] + transport[j][i] <= 1)
            # 4
            solver.Add(2 * transport[i][j] <= kitchen[i] + restaurant[j])
        # 5
        solver.Add(restaurant[i] == sum1)
        # 6
        solver.Add(kitchen[i] >= sum1)
        # 7
        solver.Add(sum2 <= units[i]["capacity_kitchen"])

    cost = 0
    transport_cost = 0
    for i in range(n):
        cost += kitchen[i] * (units[i]["rent"] + units[i]["initial_kitchen"])
        cost += restaurant[i] * (units[i]["rent"] + units[i]["initial_restaurant"])
        for j in range(n):
            transport_cost += transport[i][j] * eucledian_distance(units[i]["position"], units[j]["position"]) * cpd
    cost += transport_cost * 365
    # 8
    solver.Add(cost <= budget)

    customers = 0
    for i in range(n):
        customers += restaurant[i] * units[i]["capacity_restaurant"] * 365

    solver.Maximize(customers * r - cost)

    status = solver.Solve()
    print('OPTIMAL:', status == pywraplp.Solver.OPTIMAL)
    
    restaurant_solution = [ v.solution_value() for v in restaurant ]
    kitchen_solution = [ v.solution_value() for v in kitchen ]
    transport_solution = [ [ v.solution_value() for v in arr ] for arr in transport ]

    return (restaurant_solution, kitchen_solution, transport_solution)

if __name__ == '__main__':
    units, areas_demand = generate_data(
        areas=6,
        radius=5, 
        demand_range=(1e8,1e9), 
        capacity_kitchen_range=(2000, 3000),
        capacity_restaurant_range=(300, 301),
        sparcity=5)
    
    solution = mip_simple(units, areas_demand, radius=5, budget=100000000, cpd=1, r=10)

    print(solution[0])
    print(solution[1])
    print(solution[2])

    x = [ unit["position"][0] for unit in units ]
    y = [ unit["position"][1] for unit in units ]

    for i in range(len(solution[2])):
        for j in range(len(solution[2])):
            if solution[2][i][j] ==  1:
                    plt.plot([units[i]["position"][0], units[j]["position"][0]],
                             [units[i]["position"][1], units[j]["position"][1]], 'r-', alpha=.25)

    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=5, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='+')

    for i, (x_, y_) in enumerate(zip(x, y)):
        plt.scatter([x_], [y_], 
        marker="$R$" if solution[0][i] == 1 else "$K$" if solution[1][i] == 1 else "x",
        lw=.5, 
        s=75,
        c= "g" if solution[0][i] == 1 else "r" if solution[1][i] == 1 else "black")
    plt.grid(color='gray', ls = '--', lw = 0.25)
    plt.show()









