import random
import math
import time
import matplotlib.pyplot as plt


def eucledian_distance(p1, p2):
    return math.dist(p1, p2)


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


def plot_solution(solution, units, areas_demand):
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    for i in range(len(solution[2])):
        for j in range(len(solution[2])):
            if solution[2][i][j] == 1:
                plt.plot([units[i]['position'][0], units[j]['position'][0]],
                         [units[i]['position'][1], units[j]['position'][1]], 'r--', alpha=.2)
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=10, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='+')
    for i, (x_, y_) in enumerate(zip(x, y)):
        plt.scatter([x_], [y_],
                    marker='${}$'.format(units[i]['capacity_restaurant']) if solution[0][i] == 1 else '${}$'.format(
                        units[i]['capacity_kitchen']) if solution[1][i] == 1 else 'x',
                    lw=.5,
                    s=200 if solution[0][i] == 1 or solution[1][i] == 1 else 50,
                    c='g' if solution[0][i] == 1 else 'r' if solution[1][i] == 1 else 'black')
    plt.grid(color='gray', ls='--', lw=0.25)
    plt.gca().set_aspect('equal', adjustable='box')
    return plt.gcf()


def plot_units(units, areas_demand):
    x = [unit['position'][0] for unit in units]
    y = [unit['position'][1] for unit in units]
    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius=10, alpha=.1))
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
