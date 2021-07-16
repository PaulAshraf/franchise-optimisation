import random
import math
import time
import matplotlib.pyplot as plt


def eucledian_distance(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return math.hypot(x1 - x2, y1 - y2)


def midpoint(p1, p2):
    return (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2


def is_in_area(area, point, radius):
    return 1 if eucledian_distance(point, area) <= radius else 0


def get_random(range):
    return random.randrange(range[0], range[1])


def get_random_positions(point, radius, number):
    p_x = point[0]
    p_y = point[1]
    x_positions = random.sample(range(p_x - radius, p_x + radius + 1), math.ceil(number * 1.1))
    y_positions = random.sample(range(p_y - radius, p_y + radius + 1), math.ceil(number * 1.1))
    positions = zip(x_positions, y_positions)
    positions = filter(lambda x: is_in_area(x, point, radius), positions)
    return positions


def get_random_areas(num, sparcity, radius):
    positions = []
    side = math.ceil(math.sqrt(num))
    curr_x = 0
    curr_y = 0
    for i in range(side):
        for j in range(side):
            if i * side + j < num:
                positions.append((curr_x, curr_y))
                curr_x += sparcity + 2 * radius
        curr_y += sparcity + 2 * radius
        curr_x = 0
    return positions


def plot_solution(solution, units, areas_demand, radius):
    customers = 0
    locations = 0
    cost = 0
    distCost = 0
    path = []
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    for i in range(len(solution[2])):
        for j in range(len(solution[2])):
            if solution[2][i][j] > 0:
                p1 = (units[i]['position'][0], units[i]['position'][1])
                p2 = (units[j]['position'][0], units[j]['position'][1])
                path.append((i, j, solution[2][i][j]))
                distCost += eucledian_distance(p1, p2) * 1 * solution[2][i][j]
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
                    s=200 if solution[0][i] == 1 or solution[1][i] == 1 else 50,
                    c='g' if solution[0][i] == 1 else 'r' if solution[1][i] == 1 else 'black')
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    kitchens = []
    restaurants = []
    if len(path) > 0:
        kitchens, restaurants, _ = zip(*path)
    kitchens = set(list(kitchens))
    restaurants = set(list(restaurants))
    averageUtilization = customers / sum([units[i]['capacity_restaurant'] for i in restaurants])
    distancePerMeal = distCost / customers
    return plt.gcf(), customers, cost, distCost, kitchens, restaurants, path, averageUtilization * 100, distancePerMeal


def plot_units(units, areas_demand, radius):
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=radius, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='+')
    for i, (x_, y_) in enumerate(zip(x, y)):
        plt.scatter([x_], [y_],
                    marker='x',
                    lw=.5,
                    s=50,
                    c='black')
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    return plt.gcf()


def timed(func):
    def _w(*a, **k):
        then = time.time()
        solution = func(*a, **k)
        elapsed = time.time() - then
        return elapsed, solution

    return _w


def human_format(num):
    num = float('{:.3g}'.format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])


def plot_solution_2(path, units, areas_demand, radius):
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    kitchens, restaurants = [], []
    if len(path) > 0:
        kitchens, restaurants, _ = zip(*path)
    kitchens = set(list(kitchens))
    restaurants = set(list(restaurants))
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=radius, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='${}$'.format(str(area[1])), s=200)
    for i, (x_, y_) in enumerate(zip(x, y)):
        plt.scatter([x_], [y_],
                    marker='${}$'.format(units[i]['capacity_restaurant']) if i in restaurants else '${}$'.format(
                        units[i]['capacity_kitchen']) if i in kitchens else 'x',
                    lw=.5,
                    s=200 if i in restaurants or i in kitchens else 50,
                    c='g' if i in restaurants else 'r' if i in kitchens else 'black')
    for kitchen, rest, flow in path:
        p1 = units[kitchen]['position']
        p2 = units[rest]['position']
        plt.plot([p1[0], p2[0]], [p1[1], p2[1]], 'r--', alpha=.2)
        plt.text(midpoint(p1, p2)[0], midpoint(p1, p2)[1], flow, fontsize='small')
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    averageUtilization = sum([i[2] for i in path]) / sum([units[i]['capacity_restaurant'] for i in restaurants])
    return plt.gcf(), kitchens, restaurants, path, averageUtilization * 100
