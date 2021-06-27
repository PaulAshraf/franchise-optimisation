import random
import math
import time

def eucledian_distance(p1, p2):
    return math.dist(p1, p2)

def is_in_area(area, point, radius):
    return eucledian_distance(point, area) <= radius

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

def timed(func):
    def _w(*a, **k):
        then = time.time()
        solution = func(*a, **k)
        elapsed = time.time() - then
        return elapsed, solution
    return _w

        
