
from utils import eucledian_distance, get_random, get_random_positions, get_random_areas
import matplotlib.pyplot as plt

def generate_data(
    sparcity = 10,
    radius = 7,
    num_units_per_area = (5, 10),
    areas = 3,
    demand_range = (3000, 10000),
    rent_range = (3000, 15000),
    capacity_kitchen_range = (1000, 2000), 
    capacity_restaurant_range = (300, 600),
    initial_kitchen_range = (500000, 1000000), 
    initial_restaurant_range = (100000, 200000)):
    
    units = []
    areas_demand = []

    for i, area in enumerate(get_random_areas(areas, sparcity, radius)):
        demand = get_random(demand_range)
        areas_demand.append((area, demand))
        positions = get_random_positions(area, radius, get_random(num_units_per_area))
        for pos in positions: 
            units.append({
                "position": pos,
                "area": i,
                "rent": get_random(rent_range),
                "capacity_kitchen": get_random(capacity_kitchen_range),
                "capacity_restaurant": get_random(capacity_restaurant_range),
                "initial_restaurant": get_random(initial_restaurant_range),
                "initial_kitchen": get_random(initial_kitchen_range)
            })

    return units, areas_demand

def plot_units(units, areas_demand, radius):
    x = [ unit["position"][0] for unit in units ]
    y = [ unit["position"][1] for unit in units ]

    for area in areas_demand:
        plt.gca().add_patch(plt.Circle(area[0], radius, alpha=.1))
        plt.scatter([area[0][0]], [area[0][1]], lw=.4, c='blue', marker='+')

    plt.scatter(x, y, marker='x', lw=.5)
    plt.grid(color='gray', ls = '--', lw = 0.25)
    plt.show()

if __name__ == "__main__":
    units, areas_demand = generate_data(areas=12, sparcity=2)
    plot_units(units, areas_demand, radius = 7)

